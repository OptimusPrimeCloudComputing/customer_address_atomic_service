from __future__ import annotations

from typing import List, Any
from uuid import UUID, uuid1

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Session

from db import Base
from models.address import AddressCreate, AddressRead, AddressUpdate


class AddressNotFound(Exception):
    pass


class AddressAlreadyExists(Exception):
    pass


class Address(Base):
    __tablename__ = "addresses"

    address_id = Column(String(36), primary_key=True, nullable=False)
    university_id = Column(String(32), nullable=False)

    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AddressRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_read_model(self, a: Any) -> AddressRead:
        return AddressRead(
            address_id=UUID(str(a.address_id)),
            university_id=a.university_id,
            street=a.street,
            city=a.city,
            state=a.state,
            postal_code=a.postal_code,
            country=a.country,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    def create(self, address_in: AddressCreate) -> AddressRead:
        new_id = uuid1()
        existing = (
            self.db.query(Address)
            .filter(Address.address_id == str(new_id))
            .first()
        )
        if existing:
            raise AddressAlreadyExists(
                f"Address with id '{new_id}' already exists."
            )

        db_address = Address(
            address_id=str(new_id),
            university_id=address_in.university_id,
            street=address_in.street,
            city=address_in.city,
            state=address_in.state,
            postal_code=address_in.postal_code,
            country=address_in.country,
        )
        self.db.add(db_address)
        self.db.commit()
        self.db.refresh(db_address)

        return self._to_read_model(db_address)

    def get(self, address_id: str) -> AddressRead:
        db_address = (
            self.db.query(Address)
            .filter(Address.address_id == address_id)
            .first()
        )
        if db_address is None:
            raise AddressNotFound("Address not found")

        return self._to_read_model(db_address)

    def list_by_university_id(self, university_id: str) -> List[AddressRead]:
        db_addresses = (
            self.db.query(Address)
            .filter(Address.university_id == university_id)
            .all()
        )
        return [self._to_read_model(a) for a in db_addresses]

    def update(self, address_id: str, update_in: AddressUpdate) -> AddressRead:
        db_address = (
            self.db.query(Address)
            .filter(Address.address_id == address_id)
            .first()
        )
        if db_address is None:
            raise AddressNotFound("Address not found")

        data = update_in.model_dump(exclude_unset=True)
        data.pop("address_id", None)
        data.pop("university_id", None)

        for field, value in data.items():
            setattr(db_address, field, value)

        self.db.commit()
        self.db.refresh(db_address)

        return self._to_read_model(db_address)

    def delete(self, address_id: str) -> None:
        db_address = (
            self.db.query(Address)
            .filter(Address.address_id == address_id)
            .first()
        )
        if db_address is None:
            raise AddressNotFound("Address not found")

        self.db.delete(db_address)
        self.db.commit()

    def delete_by_university_id(self, university_id: str) -> None:
        self.db.query(Address).filter(Address.university_id == university_id).delete()
        self.db.commit()
