from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from datetime import datetime
import csv
import io
import uuid

from db import coll
from auth import get_current_user

router = APIRouter(prefix='/tools', tags=['tools'])


@router.post('/import-assets')
async def import_assets(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Bulk import assets from CSV.
    Expected columns (header row required):
    name, tag, category, location, department, status, condition, assigned_to,
    serial_number, purchase_date, purchase_cost, vendor, funding_source, warranty_expiry, notes
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(400, 'File must be a .csv')

    content = (await file.read()).decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(content))

    # Pre-load lookups for ID resolution
    cats = {c['name'].lower(): c['id'] async for c in coll('categories').find({})}
    locs = {l['name'].lower(): l['id'] async for l in coll('locations').find({})}
    vendors = {v['name'].lower(): v['id'] async for v in coll('vendors').find({})}
    funding = {f['name'].lower(): f['id'] async for f in coll('funding_sources').find({})}

    now = datetime.utcnow()
    inserted = 0
    skipped = 0
    errors = []

    for i, row in enumerate(reader, start=2):  # row 1 is header
        name = (row.get('name') or '').strip()
        tag = (row.get('tag') or '').strip()
        if not name or not tag:
            skipped += 1
            errors.append(f"Row {i}: missing name or tag")
            continue
        # Skip duplicates by tag
        existing = await coll('assets').find_one({'tag': tag})
        if existing:
            skipped += 1
            errors.append(f"Row {i}: tag '{tag}' already exists")
            continue
        category = (row.get('category') or '').strip()
        location = (row.get('location') or '').strip()
        vendor = (row.get('vendor') or '').strip()
        funding_source = (row.get('funding_source') or '').strip()
        try:
            cost = float(row.get('purchase_cost') or 0) or 0
        except Exception:
            cost = 0
        doc = {
            'id': str(uuid.uuid4()),
            'name': name, 'tag': tag,
            'category': category, 'category_id': cats.get(category.lower()),
            'location': location, 'location_id': locs.get(location.lower()),
            'department': (row.get('department') or '').strip(),
            'status': (row.get('status') or 'In Service').strip(),
            'condition': (row.get('condition') or 'Good').strip(),
            'assigned_to': (row.get('assigned_to') or '').strip(),
            'serial_number': (row.get('serial_number') or '').strip(),
            'purchase_date': (row.get('purchase_date') or '').strip(),
            'purchase_cost': cost,
            'vendor': vendor, 'vendor_id': vendors.get(vendor.lower()),
            'funding_source': funding_source, 'funding_id': funding.get(funding_source.lower()),
            'warranty_expiry': (row.get('warranty_expiry') or '').strip(),
            'notes': (row.get('notes') or '').strip(),
            'created_at': now, 'updated_at': now,
        }
        await coll('assets').insert_one(doc)
        inserted += 1

    return {
        'inserted': inserted,
        'skipped': skipped,
        'errors': errors[:50],  # cap to avoid huge responses
    }


@router.get('/import-assets/template')
async def csv_template(user: dict = Depends(get_current_user)):
    return {
        'columns': [
            'name', 'tag', 'category', 'location', 'department', 'status', 'condition',
            'assigned_to', 'serial_number', 'purchase_date', 'purchase_cost',
            'vendor', 'funding_source', 'warranty_expiry', 'notes',
        ],
        'sample_row': {
            'name': 'Sample Equipment',
            'tag': 'AICK-MED-99999',
            'category': 'Medical Equipment',
            'location': 'Main Hospital Building',
            'department': 'Administration',
            'status': 'In Service',
            'condition': 'Good',
            'assigned_to': 'Dr. Joseph Kiptoo',
            'serial_number': 'SN-12345',
            'purchase_date': '2024-01-15',
            'purchase_cost': '250000',
            'vendor': 'Crown Healthcare',
            'funding_source': 'Hospital Operations Budget',
            'warranty_expiry': '2027-01-15',
            'notes': 'Demo asset',
        }
    }
