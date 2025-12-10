from __future__ import annotations

import os
import socket
from datetime import datetime, UTC
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Response
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from models.address import AddressRead, AddressCreate, AddressUpdate
from models.health import Health
from db import SessionLocal
from address_repo import AddressRepository, AddressNotFound

port = int(os.environ.get("FASTAPIPORT", 8001))

app = FastAPI(
    title="Customer Address Atomic Microservice",
    description="Atomic service for managing address data (keyed by address_id, linked by university_id).",
    version="0.0.1",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_health() -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.now(UTC).isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
    )


@app.get("/health", response_model=Health)
def get_health():
    return make_health()


@app.post("/addresses", response_model=AddressRead, status_code=201)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    created = repo.create(address)
    return created


@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address_by_id(address_id: str, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    try:
        return repo.get(address_id)
    except AddressNotFound:
        raise HTTPException(status_code=404, detail="Address not found")


@app.get("/customers/{university_id}/addresses", response_model=List[AddressRead])
def list_customer_addresses(university_id: str, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    result = repo.list_by_university_id(university_id)
    if not result:
        raise HTTPException(status_code=404, detail="No addresses found for this university_id")
    return result


@app.patch("/customers/{university_id}/addresses/{address_id}", response_model=AddressRead)
def update_address(university_id: str, address_id: str, update: AddressUpdate, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    try:
        existing = repo.get(address_id)
    except AddressNotFound:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")
    if existing.university_id != university_id:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")
    saved = repo.update(address_id, update)
    return saved


@app.delete("/customers/{university_id}/addresses/{address_id}", status_code=204)
def delete_address(university_id: str, address_id: str, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    try:
        existing = repo.get(address_id)
    except AddressNotFound:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")
    if existing.university_id != university_id:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")
    repo.delete(address_id)
    return Response(status_code=204)


@app.delete("/customers/{university_id}/addresses", status_code=204)
def delete_all_addresses_for_customer(university_id: str, db: Session = Depends(get_db)):
    repo = AddressRepository(db)
    existing = repo.list_by_university_id(university_id)
    if not existing:
        raise HTTPException(status_code=404, detail="No addresses found for this university_id")
    repo.delete_by_university_id(university_id)
    return Response(status_code=204)


@app.get("/")
def root():
    return {
        "message": "Address Atomic Service. See /docs for OpenAPI UI.",
        "endpoints": [
            "/health",
            "/addresses",
            "/addresses/{address_id}",
            "/customers/{university_id}/addresses",
            "/customers/{university_id}/addresses/{address_id}",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
