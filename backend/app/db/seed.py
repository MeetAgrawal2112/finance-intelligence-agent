"""
Default categories seed karo database mein.
Run: python -m app.db.seed
"""
from app.db.session import SessionLocal
from app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Groceries",      "icon": "🛒", "color": "#4CAF50"},
    {"name": "Dining Out",     "icon": "🍕", "color": "#FF5722"},
    {"name": "Rent",           "icon": "🏠", "color": "#2196F3"},
    {"name": "Transport",      "icon": "🚗", "color": "#FF9800"},
    {"name": "Shopping",       "icon": "🛍️", "color": "#E91E63"},
    {"name": "Entertainment",  "icon": "🎬", "color": "#9C27B0"},
    {"name": "Healthcare",     "icon": "💊", "color": "#F44336"},
    {"name": "Utilities",      "icon": "⚡", "color": "#607D8B"},
    {"name": "Subscriptions",  "icon": "📱", "color": "#00BCD4"},
    {"name": "Education",      "icon": "📚", "color": "#3F51B5"},
    {"name": "Travel",         "icon": "✈️", "color": "#009688"},
    {"name": "Salary",         "icon": "💰", "color": "#8BC34A"},
    {"name": "Freelance",      "icon": "💻", "color": "#FFC107"},
    {"name": "Investment",     "icon": "📈", "color": "#673AB7"},
    {"name": "Other",          "icon": "📦", "color": "#9E9E9E"},
]

def seed_categories():
    db = SessionLocal()
    try:
        existing = db.query(Category).count()
        if existing > 0:
            print(f"Categories already exist ({existing} found). Skipping.")
            return

        for cat_data in DEFAULT_CATEGORIES:
            category = Category(
                name=cat_data["name"],
                icon=cat_data["icon"],
                color=cat_data["color"],
                is_system=True,
                user_id=None  # System-wide
            )
            db.add(category)

        db.commit()
        print(f"✅ {len(DEFAULT_CATEGORIES)} default categories seeded!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()
