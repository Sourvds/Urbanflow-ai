from fastapi import APIRouter
from app.api.v1 import auth, dashboard, electricity, traffic, water, alerts, predictions, optimization, admin, chatbot, maps

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(electricity.router, prefix="/electricity", tags=["Electricity"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["Traffic"])
api_router.include_router(water.router, prefix="/water", tags=["Water"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(optimization.router, prefix="/optimization", tags=["Optimization"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["AI Chatbot"])
api_router.include_router(maps.router, prefix="/maps", tags=["Maps"])
