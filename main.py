from __future__ import annotations

import os
import socket
from datetime import datetime, UTC
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse

from models.address import AddressRead, AddressCreate, AddressUpdate
from models.health import Health

port = int(os.environ.get("FASTAPIPORT", 8001))

app = FastAPI(
    title="Customer Address Atomic Microservice",
    description="Atomic service for managing address data (keyed by address_id, linked by university_id).",
    version="0.0.1",
)

# In-memory "database": keyed by address_id (string)
addresses: Dict[str, AddressRead] = {}


# ---------
# Health
# ---------

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
def create_address(address: AddressCreate):
    now = datetime.now(UTC)

    addr_obj = AddressRead(
        created_at=now,
        updated_at=now,
        **address.model_dump(),
    )

    key = str(addr_obj.address_id)
    addresses[key] = addr_obj
    return addr_obj


@app.get("/addresses/{address_id}", response_model=AddressRead)
def get_address(address_id: str):
    addr = addresses.get(address_id)
    if addr is None:
        raise HTTPException(status_code=404, detail="Address not found")
    return addr


@app.get("/customers/{university_id}/addresses", response_model=List[AddressRead])
def list_customer_addresses(university_id: str):
    result = [
        addr
        for addr in addresses.values()
        if addr.university_id == university_id
    ]
    if not result:
        raise HTTPException(status_code=404, detail="No addresses found for this university_id")

    return result


@app.patch("/customers/{university_id}/addresses/{address_id}", response_model=AddressRead)
def update_address(university_id: str, address_id: str, update: AddressUpdate):
    existing = addresses.get(address_id)
    if existing is None or existing.university_id != university_id:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")

    update_data = update.model_dump(exclude_unset=True)
    update_data.pop("university_id", None)

    updated = existing.copy(update=update_data)
    updated.updated_at = datetime.now(UTC)

    addresses[address_id] = updated
    return updated


@app.delete("/customers/{university_id}/addresses/{address_id}", status_code=204)
def delete_address(university_id: str, address_id: str):
    """
    Delete a single address, scoped by university_id.
    """
    existing = addresses.get(address_id)
    if existing is None or existing.university_id != university_id:
        raise HTTPException(status_code=404, detail="Address not found for this university_id")

    del addresses[address_id]
    return JSONResponse(status_code=204, content=None)


@app.delete("/customers/{university_id}/addresses", status_code=204)
def delete_all_addresses_for_customer(university_id: str):
    """
    Remove all addresses for a given university_id.
    """
    to_delete = [addr_id for addr_id, addr in addresses.items() if addr.university_id == university_id]

    if not to_delete:
        return JSONResponse(status_code=204, content=None)

    for addr_id in to_delete:
        del addresses[addr_id]

    return JSONResponse(status_code=204, content=None)


# -----
# Root
# -----

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
