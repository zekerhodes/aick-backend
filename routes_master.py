from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, List
from datetime import datetime
import uuid

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
    data['id'] = data.get('id') or str(uuid.uuid4())
    data['created_at'] = datetime.utcnow()
    await coll(COLLECTIONS[resource]).insert_one(data)
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
    res = await coll(COLLECTIONS[resource]).update_one({'id': item_id}, {'$set': data})
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
