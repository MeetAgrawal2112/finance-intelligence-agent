from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from datetime import datetime, timezone

def get_system_prompt() -> str:
    return f"""You are a helpful personal finance AI assistant for Indian users.
Always respond in the same language the user used (Hindi/English/Hinglish).
Use INR (Rs.) for all amounts. Be friendly and conversational.
Current date: {datetime.now(timezone.utc).strftime("%B %d, %Y")}"""

def get_llm():
    from app.core.config import settings
    if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.1,
        )
    elif settings.OPENAI_API_KEY:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.1,
        )
    else:
        raise ValueError("No LLM API key! Set GROQ_API_KEY in .env")

def get_finance_context(query: str, db: Session, user_id: str) -> str:
    context_parts = []
    query_lower = query.lower()

    try:
        from app.models.transaction import Transaction, TransactionType
        from app.models.category import Category
        from sqlalchemy import func, extract

        now = datetime.now(timezone.utc)
        month = now.month
        year = now.year

        income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.CREDIT,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        ).scalar() or 0

        expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.DEBIT,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        ).scalar() or 0

        txn_count = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        ).count()

        savings = float(income) - float(expenses)
        savings_rate = (savings / float(income) * 100) if income > 0 else 0

        context_parts.append(f"""CURRENT MONTH SUMMARY ({month}/{year}):
- Total Income: Rs.{float(income):,.0f}
- Total Expenses: Rs.{float(expenses):,.0f}
- Net Savings: Rs.{savings:,.0f}
- Savings Rate: {savings_rate:.1f}%
- Transactions: {txn_count}""")

        cat_data = db.query(
            Category.name,
            func.sum(Transaction.amount).label('total'),
            func.count(Transaction.id).label('count')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == TransactionType.DEBIT,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        ).group_by(Category.name).order_by(
            func.sum(Transaction.amount).desc()
        ).all()

        if cat_data:
            context_parts.append("\nCATEGORY-WISE SPENDING:")
            for cat in cat_data:
                context_parts.append(
                    f"- {cat.name}: Rs.{float(cat.total):,.0f} ({cat.count} transactions)"
                )

        if any(w in query_lower for w in
               ['transaction', 'recent', 'last', 'latest',
                'dikhao', 'dikha', 'history', 'pichli']):
            recent = db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(Transaction.transaction_date.desc()).limit(10).all()

            if recent:
                context_parts.append("\nRECENT TRANSACTIONS:")
                for t in recent:
                    date = t.transaction_date.strftime("%d %b")
                    icon = "💸" if t.transaction_type.value == "debit" else "💰"
                    merchant = t.merchant_name or t.description[:25]
                    flag = " 🚨SUSPICIOUS" if t.is_anomaly else ""
                    context_parts.append(
                        f"{icon} {date} | {merchant} | Rs.{t.amount:,.0f}{flag}"
                    )

        if any(w in query_lower for w in
               ['suspicious', 'anomaly', 'unusual', 'fraud',
                'alert', 'strange', 'संदिग्ध']):
            anomalies = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_anomaly == True
            ).order_by(Transaction.anomaly_score.desc()).limit(5).all()

            if anomalies:
                context_parts.append("\nSUSPICIOUS TRANSACTIONS:")
                for t in anomalies:
                    sev = "🔴HIGH" if t.anomaly_score > 0.75 else "🟡MEDIUM"
                    context_parts.append(
                        f"{sev} | {t.transaction_date.strftime('%d %b')} | "
                        f"{t.merchant_name or t.description[:25]} | "
                        f"Rs.{t.amount:,.0f}"
                    )
            else:
                context_parts.append(
                    "\nNo suspicious transactions found. All normal! ✅"
                )

        if any(w in query_lower for w in
               ['forecast', 'predict', 'next month', 'future',
                'agla', 'save', 'savings', 'kitna bacha', 'kitna bache']):
            from app.services.prediction_service import predictor
            if predictor.is_loaded:
                forecast = predictor.predict_next_month()
                predictions = forecast.get("predictions", [])
                total = forecast.get("total_predicted", 0)
                savings_pot = forecast.get("savings_potential", 0)
                context_parts.append("\nNEXT 30 DAYS FORECAST:")
                for p in predictions[:5]:
                    trend = "↑" if p['trend']=='increasing' else \
                            "↓" if p['trend']=='decreasing' else "→"
                    context_parts.append(
                        f"{trend} {p['category']}: Rs.{p['predicted_amount']:,.0f}"
                    )
                context_parts.append(f"Total Predicted: Rs.{total:,.0f}")
                context_parts.append(
                    f"Savings Potential: Rs.{savings_pot:,.0f}"
                )

    except Exception as e:
        context_parts.append(f"Note: Some data unavailable - {str(e)[:100]}")

    return "\n".join(context_parts)

def run_finance_query(
    query: str,
    db: Session,
    user_id: str,
    chat_history: list = None
) -> dict:
    try:
        context = get_finance_context(query, db, user_id)
        llm = get_llm()

        messages = [
            SystemMessage(content=get_system_prompt()),
            HumanMessage(content=f"""
User's Financial Data:
{context}

User Question: {query}

Answer based on the data above. Be specific with numbers.
Give actionable advice. Respond in same language as question.
""")
        ]

        response = llm.invoke(messages)

        return {
            "answer": response.content,
            "success": True,
            "error": None,
            "query": query,
        }

    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
            friendly = "LLM API key missing. .env mein GROQ_API_KEY set karo."
        elif "rate_limit" in error_msg.lower():
            friendly = "API rate limit. Thodi der baad try karo."
        else:
            friendly = f"Query process nahi ho saki: {error_msg[:200]}"

        return {
            "answer": friendly,
            "success": False,
            "error": error_msg,
            "query": query,
        }
