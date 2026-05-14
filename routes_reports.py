from fastapi import APIRouter, Depends
from typing import Optional
from collections import Counter

from db import coll
from auth import get_current_user

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/dashboard-stats')
async def dashboard_stats(user: dict = Depends(get_current_user)):
    assets = await coll('assets').find({}).to_list(10000)
    total_value = sum((a.get('purchase_cost') or 0) for a in assets)
    in_service = sum(1 for a in assets if a.get('status') == 'In Service')
    under_maint = sum(1 for a in assets if a.get('status') == 'Under Maintenance')
    checked_out = sum(1 for a in assets if a.get('status') == 'Checked Out')
    reserved = sum(1 for a in assets if a.get('status') == 'Reserved')

    by_status = dict(Counter(a.get('status', 'Unknown') for a in assets))
    by_category = dict(Counter(a.get('category', 'Uncategorized') for a in assets))

    return {
        'total_assets': len(assets),
        'total_value': total_value,
        'in_service': in_service,
        'under_maintenance': under_maint,
        'checked_out': checked_out,
        'reserved': reserved,
        'by_status': [{'name': k, 'count': v} for k, v in by_status.items()],
        'by_category': [{'name': k, 'count': v} for k, v in by_category.items()],
    }


@router.get('/recent-transactions')
async def recent_transactions(limit: int = 10, user: dict = Depends(get_current_user)):
    cursor = coll('transactions').find({}).sort('created_at', -1).limit(limit)
    items = []
    async for x in cursor:
        x.pop('_id', None)
        items.append(x)
    return {'items': items}


@router.get('/upcoming-maintenance')
async def upcoming_maintenance(limit: int = 10, user: dict = Depends(get_current_user)):
    cursor = coll('maintenance_records').find({}).sort('date', 1).limit(limit)
    items = []
    async for x in cursor:
        x.pop('_id', None)
        items.append(x)
    return {'items': items}
