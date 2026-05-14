from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


def _id():
    return str(uuid.uuid4())


def _now():
    return datetime.utcnow()


# Master data models
class NamedItem(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    code: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class Category(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    code: Optional[str] = None
    color: Optional[str] = '#D9501E'
    created_at: datetime = Field(default_factory=_now)


class Location(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    code: Optional[str] = None
    site: Optional[str] = 'Kapsowar Main'
    created_at: datetime = Field(default_factory=_now)


class Department(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    head: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class Vendor(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    contact: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class FundingSource(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    type: Optional[str] = 'Donor'
    created_at: datetime = Field(default_factory=_now)


class Person(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class Site(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    address: Optional[str] = None
    country: Optional[str] = 'Kenya'
    timezone: Optional[str] = 'Africa/Nairobi'
    created_at: datetime = Field(default_factory=_now)


class SecurityGroup(BaseModel):
    id: str = Field(default_factory=_id)
    name: str
    permissions: Optional[str] = None
    members: Optional[int] = 0
    created_at: datetime = Field(default_factory=_now)


# Asset model
class Asset(BaseModel):
    id: str = Field(default_factory=_id)
    tag: str
    name: str
    category_id: Optional[str] = None
    category: Optional[str] = None
    location_id: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[str] = None
    department: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor: Optional[str] = None
    funding_id: Optional[str] = None
    funding_source: Optional[str] = None
    status: str = 'In Service'
    condition: Optional[str] = 'Good'
    assigned_to: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = 0.0
    warranty_expiry: Optional[str] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AssetCreate(BaseModel):
    tag: str
    name: str
    category_id: Optional[str] = None
    category: Optional[str] = None
    location_id: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[str] = None
    department: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor: Optional[str] = None
    funding_id: Optional[str] = None
    funding_source: Optional[str] = None
    status: Optional[str] = 'In Service'
    condition: Optional[str] = 'Good'
    assigned_to: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = 0.0
    warranty_expiry: Optional[str] = None
    notes: Optional[str] = None


class AssetUpdate(BaseModel):
    tag: Optional[str] = None
    name: Optional[str] = None
    category_id: Optional[str] = None
    category: Optional[str] = None
    location_id: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[str] = None
    department: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor: Optional[str] = None
    funding_id: Optional[str] = None
    funding_source: Optional[str] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    assigned_to: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_cost: Optional[float] = None
    warranty_expiry: Optional[str] = None
    notes: Optional[str] = None


# Action payloads
class CheckOutIn(BaseModel):
    person: str
    return_date: Optional[str] = None
    notes: Optional[str] = None


class CheckInIn(BaseModel):
    condition: Optional[str] = 'Good'
    notes: Optional[str] = None


class MoveIn(BaseModel):
    location_id: Optional[str] = None
    location: Optional[str] = None
    department: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceIn(BaseModel):
    type: str = 'Preventive'
    technician: Optional[str] = None
    cost: Optional[float] = 0
    date: Optional[str] = None
    notes: Optional[str] = None


class DisposeIn(BaseModel):
    reason: str
    notes: Optional[str] = None


class ReserveIn(BaseModel):
    person: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None


class LeaseIn(BaseModel):
    person: str
    return_date: Optional[str] = None
    cost: Optional[float] = 0
    notes: Optional[str] = None


# Maintenance record (persisted)
class MaintenanceRecord(BaseModel):
    id: str = Field(default_factory=_id)
    asset_id: str
    asset_name: Optional[str] = None
    type: str = 'Preventive'
    technician: Optional[str] = None
    cost: Optional[float] = 0
    date: Optional[str] = None
    status: Optional[str] = 'Scheduled'
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class Transaction(BaseModel):
    id: str = Field(default_factory=_id)
    type: str
    asset_id: str
    asset_name: Optional[str] = None
    person: Optional[str] = None
    date: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
