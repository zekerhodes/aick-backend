from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from db import coll
from auth import get_current_user
from models import (
    Asset, AssetCreate, AssetUpdate,
    CheckOutIn, CheckInIn, MoveIn, MaintenanceIn, DisposeIn, ReserveIn, LeaseIn,
    MaintenanceRecord, Transaction,
)

router = APIRouter(prefix='/assets', tags=['assets'])


def _clean(d: dict) -> dict:
    d.pop('_id', None)
    return d


async def _log_tx(tx_type: str, asset: dict, user: dict, person: Optional[str] = None, notes: Optional[str] = None):
    t = Transaction(
        type=tx_type,
        asset_id=asset['id'],
        asset_name=asset.get('name'),
        person=person or user.get('name'),
        date=datetime.utcnow().strftime('%Y-%m-%d'),
        notes=notes,
        user_id=user.get('id'),
    )
    await coll('transactions').insert_one(t.dict())


@router.get('')
async def list_assets(
    search: Optional[str] = None,
    category_id: Optional[str] = None,
    location_id: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    per_page: int = 50,
    user: dict = Depends(get_current_user),
):
    q = {}
    if category_id and category_id != 'all':
        q['category_id'] = category_id
    if location_id and location_id != 'all':
        q['location_id'] = location_id
    if status and status != 'all':
        q['status'] = status
    if search:
        q['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'tag': {'$regex': search, '$options': 'i'}},
            {'serial_number': {'$regex': search, '$options': 'i'}},
            {'assigned_to': {'$regex': search, '$options': 'i'}},
        ]
    total = await coll('assets').count_documents(q)
    cursor = coll('assets').find(q).sort('created_at', -1).skip((page - 1) * per_page).limit(per_page)
    items = [_clean(x) async for x in cursor]
    return {'items': items, 'total': total, 'page': page, 'per_page': per_page}


@router.post('', response_model=Asset)
async def create_asset(data: AssetCreate, user: dict = Depends(get_current_user)):
    asset = Asset(**data.dict())
    await _resolve_labels(asset)
    doc = asset.dict()
    await coll('assets').insert_one(doc)
    await _log_tx('Add', doc, user, notes=f"New asset registered: {asset.tag}")
    return _clean(doc)


@router.get('/{asset_id}')
async def get_asset(asset_id: str, user: dict = Depends(get_current_user)):
    a = await coll('assets').find_one({'id': asset_id})
    if not a:
        raise HTTPException(404, 'Asset not found')
    return _clean(a)


@router.put('/{asset_id}')
async def update_asset(asset_id: str, data: AssetUpdate, user: dict = Depends(get_current_user)):
    existing = await coll('assets').find_one({'id': asset_id})
    if not existing:
        raise HTTPException(404, 'Asset not found')
    update = {k: v for k, v in data.dict().items() if v is not None}
    # Re-resolve labels whenever an ID changes so the denormalised label
    # never goes stale (fixes the bug where the dropdown updates category_id
    # but the displayed `category` label keeps the old value).
    await _resolve_labels_dict(update, existing)
    update['updated_at'] = datetime.utcnow()
    await coll('assets').update_one({'id': asset_id}, {'$set': update})
    a = await coll('assets').find_one({'id': asset_id})
    return _clean(a)


@router.delete('/{asset_id}')
async def delete_asset(asset_id: str, user: dict = Depends(get_current_user)):
    res = await coll('assets').delete_one({'id': asset_id})
    if res.deleted_count == 0:
        raise HTTPException(404, 'Asset not found')
    return {'ok': True}


# ----- Helpers -----
async def _get_asset_or_404(asset_id: str) -> dict:
    a = await coll('assets').find_one({'id': asset_id})
    if not a:
        raise HTTPException(404, 'Asset not found')
    return a


async def _resolve_labels(asset: Asset):
    if asset.category_id and not asset.category:
        c = await coll('categories').find_one({'id': asset.category_id})
        if c:
            asset.category = c['name']
    if asset.location_id and not asset.location:
        loc = await coll('locations').find_one({'id': asset.location_id})
        if loc:
            asset.location = loc['name']
    if asset.department_id and not asset.department:
        d = await coll('departments').find_one({'id': asset.department_id})
        if d:
            asset.department = d['name']
    if asset.vendor_id and not asset.vendor:
        v = await coll('vendors').find_one({'id': asset.vendor_id})
        if v:
            asset.vendor = v['name']
    if asset.funding_id and not asset.funding_source:
        f = await coll('funding_sources').find_one({'id': asset.funding_id})
        if f:
            asset.funding_source = f['name']


_LABEL_RESOLUTION_MAP = {
    'category_id': ('category', 'categories'),
    'location_id': ('location', 'locations'),
    'department_id': ('department', 'departments'),
    'vendor_id': ('vendor', 'vendors'),
    'funding_id': ('funding_source', 'funding_sources'),
}


async def _resolve_labels_dict(update: dict, existing: Optional[dict] = None):
    """Re-resolve denormalised label fields based on *_id fields in `update`."""
    for id_field, (label_field, collection) in _LABEL_RESOLUTION_MAP.items():
        if id_field in update:
            new_id = update[id_field]
            if new_id:
                doc = await coll(collection).find_one({'id': new_id})
                update[label_field] = doc['name'] if doc else None
            else:
                update[label_field] = None


# ----- Actions -----
@router.post('/{asset_id}/check-out')
async def check_out(asset_id: str, data: CheckOutIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'Checked Out', 'assigned_to': data.person, 'updated_at': datetime.utcnow()}})
    await _log_tx('Check Out', a, user, person=data.person, notes=data.notes)
    return {'ok': True}


@router.post('/{asset_id}/check-in')
async def check_in(asset_id: str, data: CheckInIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    update = {'status': 'In Service', 'updated_at': datetime.utcnow()}
    if data.condition:
        update['condition'] = data.condition
    await coll('assets').update_one({'id': asset_id}, {'$set': update})
    await _log_tx('Check In', a, user, notes=data.notes)
    return {'ok': True}


@router.post('/{asset_id}/move')
async def move(asset_id: str, data: MoveIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    update = {'updated_at': datetime.utcnow()}
    if data.location_id:
        update['location_id'] = data.location_id
        loc = await coll('locations').find_one({'id': data.location_id})
        if loc:
            update['location'] = loc['name']
    elif data.location:
        update['location'] = data.location
    if data.department:
        update['department'] = data.department
    await coll('assets').update_one({'id': asset_id}, {'$set': update})
    await _log_tx('Move', a, user, notes=data.notes or f"Moved to {update.get('location', 'new location')}")
    return {'ok': True}


@router.post('/{asset_id}/maintenance')
async def maintenance(asset_id: str, data: MaintenanceIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    rec = MaintenanceRecord(
        asset_id=asset_id, asset_name=a.get('name'),
        type=data.type, technician=data.technician,
        cost=data.cost or 0, date=data.date or datetime.utcnow().strftime('%Y-%m-%d'),
        status='Scheduled' if data.type == 'Preventive' else 'In Progress',
        notes=data.notes,
    )
    await coll('maintenance_records').insert_one(rec.dict())
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'Under Maintenance', 'updated_at': datetime.utcnow()}})
    await _log_tx('Maintenance', a, user, notes=f"{data.type} - {data.technician}")
    return {'ok': True, 'maintenance_id': rec.id}


@router.post('/{asset_id}/dispose')
async def dispose(asset_id: str, data: DisposeIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'Disposed', 'updated_at': datetime.utcnow()}})
    await _log_tx('Dispose', a, user, notes=f"{data.reason}: {data.notes or ''}")
    return {'ok': True}


@router.post('/{asset_id}/reserve')
async def reserve(asset_id: str, data: ReserveIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'Reserved', 'updated_at': datetime.utcnow()}})
    await _log_tx('Reserve', a, user, person=data.person, notes=data.notes)
    return {'ok': True}


@router.post('/{asset_id}/lease')
async def lease(asset_id: str, data: LeaseIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'Leased', 'assigned_to': data.person, 'updated_at': datetime.utcnow()}})
    await _log_tx('Lease', a, user, person=data.person, notes=data.notes)
    return {'ok': True}


@router.post('/{asset_id}/lease-return')
async def lease_return(asset_id: str, data: CheckInIn, user: dict = Depends(get_current_user)):
    a = await _get_asset_or_404(asset_id)
    await coll('assets').update_one({'id': asset_id}, {'$set': {'status': 'In Service', 'condition': data.condition or 'Good', 'updated_at': datetime.utcnow()}})
    await _log_tx('Lease Return', a, user, notes=data.notes)
    return {'ok': True}
📄 FILE 3 — routes_master.py
Path in your repo: routes_master.py (at root, next to server.py)

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, List
from datetime import datetime
import uuid

from pymongo.errors import DuplicateKeyError

from db import coll
from auth import get_current_user

router = APIRouter(tags=['master'])

# Generic CRUD factory
COLLECTIONS = {
    'categories': 'categories',
    'locations': 'locations',
    'departments': 'departments',
    'vendors': 'vendors',
    'funding-sources': 'funding_sources',
    'persons': 'persons',
    'sites': 'sites',
    'security-groups': 'security_groups',
    'maintenance-records': 'maintenance_records',
    'warranties': 'warranties',
    'transactions': 'transactions',
}


def _clean(d: dict) -> dict:
    d.pop('_id', None)
    return d


@router.get('/{resource}')
async def list_resource(resource: str, search: Optional[str] = None, user: dict = Depends(get_current_user)):
    if resource not in COLLECTIONS:
        raise HTTPException(404, f'Unknown resource: {resource}')
    q = {}
    if search:
        q['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'code': {'$regex': search, '$options': 'i'}},
        ]
    cursor = coll(COLLECTIONS[resource]).find(q).sort('created_at', -1).limit(1000)
    items = [_clean(x) async for x in cursor]
    return {'items': items, 'total': len(items)}


@router.post('/{resource}')
async def create_resource(resource: str, data: dict = Body(...), user: dict = Depends(get_current_user)):
    if resource not in COLLECTIONS:
        raise HTTPException(404, f'Unknown resource: {resource}')
    if resource == 'transactions':
        raise HTTPException(403, 'Transactions are auto-generated')
    if not (data.get('name') or '').strip():
        raise HTTPException(400, 'Name is required')
    data['id'] = data.get('id') or str(uuid.uuid4())
    data['created_at'] = datetime.utcnow()
    try:
        await coll(COLLECTIONS[resource]).insert_one(data)
    except DuplicateKeyError as e:
        key = next(iter(getattr(e, 'details', {}).get('keyValue', {}) or {}), 'value')
        raise HTTPException(409, f"A {resource[:-1] if resource.endswith('s') else resource} with this {key} already exists")
    return _clean(data)


@router.get('/{resource}/{item_id}')
async def get_resource(resource: str, item_id: str, user: dict = Depends(get_current_user)):
    if resource not in COLLECTIONS:
        raise HTTPException(404, f'Unknown resource: {resource}')
    item = await coll(COLLECTIONS[resource]).find_one({'id': item_id})
    if not item:
        raise HTTPException(404, 'Not found')
    return _clean(item)


@router.put('/{resource}/{item_id}')
async def update_resource(resource: str, item_id: str, data: dict = Body(...), user: dict = Depends(get_current_user)):
    if resource not in COLLECTIONS:
        raise HTTPException(404, f'Unknown resource: {resource}')
    data.pop('id', None)
    data.pop('_id', None)
    data['updated_at'] = datetime.utcnow()
    try:
        res = await coll(COLLECTIONS[resource]).update_one({'id': item_id}, {'$set': data})
    except DuplicateKeyError as e:
        key = next(iter(getattr(e, 'details', {}).get('keyValue', {}) or {}), 'value')
        raise HTTPException(409, f"Another record with this {key} already exists")
    if res.matched_count == 0:
        raise HTTPException(404, 'Not found')
    item = await coll(COLLECTIONS[resource]).find_one({'id': item_id})
    return _clean(item)


@router.delete('/{resource}/{item_id}')
async def delete_resource(resource: str, item_id: str, user: dict = Depends(get_current_user)):
    if resource not in COLLECTIONS:
        raise HTTPException(404, f'Unknown resource: {resource}')
    res = await coll(COLLECTIONS[resource]).delete_one({'id': item_id})
    if res.deleted_count == 0:
        raise HTTPException(404, 'Not found')
    return {'ok': True}
