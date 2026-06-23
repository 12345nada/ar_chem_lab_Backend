import requests
from fastapi import HTTPException

from app.schemas.ai import PredictRequest
from app.services.ai_service import get_ai_url, forward_predict

UNITY_FIELDS = [
    "reactant_smiles", "reactant_name",
    "reagent_smiles", "reagent_name",
    "product_smiles", "product_name",
    "reaction_type", "condition",
    "heat_required", "gas_produced",
    "precipitate_color", "hazard_level",
    "confidence",
]


def fetch_raw_payload(req: PredictRequest) -> dict:
    ai_url = get_ai_url()
    if not ai_url:
        raise HTTPException(status_code=503, detail="AI not registered")
    try:
        resp = forward_predict(ai_url, req.reactant, req.reagent)
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="AI unreachable")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI timeout")
    if resp.status_code == 422:
        raise HTTPException(status_code=422, detail=resp.json().get("detail"))
    if not resp.ok:
        raise HTTPException(status_code=502, detail="AI error")
    return resp.json()