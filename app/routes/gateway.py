# app/routes/gateway.py
import httpx
from fastapi import APIRouter, HTTPException

gateway_route = APIRouter()

REALTIME_URL = "http://antifraud-realtime:8000/internal/fraud"
BATCH_URL = "http://antifraud-batch:8000/internal/fraud"


@gateway_route.get("/fraud/predict/user/{email}")
async def proxy_realtime(email: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{REALTIME_URL}/predict/user/{email}")
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@gateway_route.post("/fraud/predict/batch")
async def proxy_batch():
    async with httpx.AsyncClient(timeout=300) as client:
        r = await client.post(f"{BATCH_URL}/predict/batch")
        if r.status_code >= 400:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()
