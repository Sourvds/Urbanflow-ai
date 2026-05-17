from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.services.analytics import AnalyticsService

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str]


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(
    req: ChatRequest,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    msg = req.message.lower()
    svc = AnalyticsService(db)
    overview = svc.get_dashboard_overview()

    if "electric" in msg or "energy" in msg:
        data = svc.electricity_analytics()
        reply = (
            f"Electricity analytics: {data['summary']['total_kwh']:,.0f} kWh consumed in the last 7 days. "
            f"Forecast confidence: {data['summary']['forecast_confidence']*100:.0f}%. "
            f"Detected {data['summary']['anomaly_count']} anomalies."
        )
    elif "traffic" in msg or "congestion" in msg:
        data = svc.traffic_analytics()
        reply = (
            f"Traffic status: average congestion {data['summary']['avg_congestion']*100:.1f}%, "
            f"peak {data['summary']['peak_congestion']*100:.1f}%. "
            f"I can optimize signal timing at high-congestion intersections."
        )
    elif "water" in msg or "leak" in msg:
        data = svc.water_analytics()
        reply = (
            f"Water distribution: {data['summary']['total_liters']:,.0f} liters consumed. "
            f"{data['summary']['leak_alerts']} zones flagged for potential leaks."
        )
    elif "alert" in msg:
        reply = f"There are currently {overview['active_alerts']} active alerts requiring attention."
    elif "efficiency" in msg or "score" in msg:
        reply = (
            f"City efficiency score: {overview['city_efficiency_score']}/100. "
            f"Energy efficiency: {overview['energy_efficiency_score']}. "
            f"Carbon estimate: {overview['carbon_emission_tons']} tons."
        )
    else:
        reply = (
            f"UrbanFlow AI Command Center online. City efficiency: {overview['city_efficiency_score']}/100. "
            f"Active alerts: {overview['active_alerts']}. "
            f"Ask me about electricity, traffic, water, alerts, or optimization."
        )

    suggestions = [
        "Show electricity forecast",
        "Traffic congestion hotspots",
        "Water leak detection status",
        "Generate optimization plan",
    ]
    return ChatResponse(reply=reply, suggestions=suggestions)
