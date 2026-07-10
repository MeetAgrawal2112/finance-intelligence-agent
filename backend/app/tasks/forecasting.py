# app/tasks/forecasting.py
"""
Weekly forecast model update.
"""

from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.tasks.forecasting.update_forecast_model",
    bind=True,
)
def update_forecast_model(self):
    """
    Sunday raat 1 baje:
    Spending predictor model ko fresh data se update karo.
    """
    try:
        import subprocess
        import os

        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../..')
        )

        result = subprocess.run(
            ["python", "ml/spending_predictor.py"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            # Reload model
            from app.services.prediction_service import predictor
            predictor.load_model()

            logger.info("Forecast model updated successfully")
            return {"status": "success", "output": result.stdout[-500:]}
        else:
            raise Exception(f"Script failed: {result.stderr[-500:]}")

    except Exception as e:
        logger.error(f"Forecast update failed: {e}")
        raise self.retry(exc=e, countdown=3600)