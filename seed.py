"""Seed data for AIC Kapsowar Hospital Asset Management.
Runs once on first startup if the database is empty.
"""
from datetime import datetime
import uuid

from db import coll
from auth import hash_password


async def seed_if_empty():
    users_count = await coll('users').count_documents({})
    if users_count > 0:
        return False  # already seeded

    now = datetime.utcnow()

    # Default admin user
    admin_id = str(uuid.uuid4())
    await coll('users').insert_one({
        'id': admin_id,
        'name': 'Admin User',
        'email': 'admin@kapsowar.org',
        'role': 'Super Admin',
        'password_hash': hash_password('demo1234'),
        'created_at': now,
    })

    categories = [
        {'name': 'Medical Equipment', 'code': 'MED', 'color': '#D9501E'},
        {'name': 'IT & Computers', 'code': 'IT', 'color': '#1E3A5F'},
        {'name': 'Furniture', 'code': 'FUR', 'color': '#7C3AED'},
        {'name': 'Vehicles', 'code': 'VEH', 'color': '#059669'},
        {'name': 'Laboratory', 'code': 'LAB', 'color': '#DC2626'},
        {'name': 'Surgical Instruments', 'code': 'SUR', 'color': '#0891B2'},
        {'name': 'Office Equipment', 'code': 'OFF', 'color': '#A16207'},
        {'name': 'Generators & Power', 'code': 'PWR', 'color': '#475569'},
    ]
    cat_map = {}
    for c in categories:
        c['id'] = str(uuid.uuid4())
        c['created_at'] = now
        cat_map[c['name']] = c['id']
    await coll('categories').insert_many(categories)

    locations = [
        'Main Hospital Building', 'Maternity Ward', "Children's Ward",
        'Operating Theatre 1', 'Operating Theatre 2', 'Outpatient Clinic',
        'Laboratory', 'Radiology / X-Ray', 'Pharmacy', 'Administration Block',
        'Nursing School', 'Staff Housing', 'Mortuary', 'Kitchen & Laundry', 'Workshop / Biomed',
    ]
    loc_docs = []
    loc_map = {}
    for name in locations:
        d = {'id': str(uuid.uuid4()), 'name': name, 'code': name[:3].upper(), 'site': 'Kapsowar Main', 'created_at': now}
        loc_docs.append(d)
        loc_map[name] = d['id']
    await coll('locations').insert_many(loc_docs)

    departments = [
        ('Administration', 'Dr. Joseph Kiptoo'),
        ('Internal Medicine', 'Dr. Mary Chebet'),
        ('Surgery', 'Dr. Daniel Kibet'),
        ('Obstetrics & Gynaecology', 'Dr. Grace Jepkemboi'),
        ('Paediatrics', 'Dr. Samuel Rotich'),
        ('Nursing Services', 'Sr. Esther Chemutai'),
        ('Pharmacy', 'Pharm. Wilson Kiprop'),
        ('Laboratory', 'Mr. Eric Cheruiyot'),
        ('Radiology', 'Mr. Peter Kipkurui'),
        ('Biomedical Engineering', 'Eng. Brian Kimutai'),
        ('Finance & Accounts', 'Mr. John Kipkemoi'),
        ('IT Department', 'Mr. Kevin Ruto'),
    ]
    await coll('departments').insert_many([
        {'id': str(uuid.uuid4()), 'name': n, 'head': h, 'created_at': now} for n, h in departments
    ])

    vendors = [
        ('Philips Healthcare East Africa', 'sales@philips.co.ke', '+254 20 555 0101'),
        ('GE Healthcare Kenya', 'info@ge.co.ke', '+254 20 555 0202'),
        ('Surgipharm Ltd', 'orders@surgipharm.co.ke', '+254 20 555 0303'),
        ('Crown Healthcare', 'sales@crownhealth.co.ke', '+254 20 555 0404'),
        ('Mediquip Kenya', 'info@mediquip.co.ke', '+254 20 555 0505'),
        ('Davis & Shirtliff', 'sales@dayliff.com', '+254 20 555 0606'),
    ]
    vendor_map = {}
    for n, c, p in vendors:
        vid = str(uuid.uuid4())
        vendor_map[n] = vid
        await coll('vendors').insert_one({'id': vid, 'name': n, 'contact': c, 'phone': p, 'created_at': now})

    funding = [
        ('Hospital Operations Budget', 'Internal'),
        ("Samaritan's Purse Donation", 'Donor'),
        ('AIC Mission USA Grant', 'Donor'),
        ('World Medical Mission', 'Donor'),
        ('Kenya Ministry of Health', 'Government'),
        ('Private Donor — Anonymous', 'Donor'),
        ('County Government Elgeyo-Marakwet', 'Government'),
    ]
    fund_map = {}
    for n, t in funding:
        fid = str(uuid.uuid4())
        fund_map[n] = fid
        await coll('funding_sources').insert_one({'id': fid, 'name': n, 'type': t, 'created_at': now})

    persons = [
        ('Dr. Joseph Kiptoo', 'Medical Director', 'jkiptoo@kapsowar.org', 'Administration', '+254 722 100 001'),
        ('Dr. Mary Chebet', 'Physician', 'mchebet@kapsowar.org', 'Internal Medicine', '+254 722 100 002'),
        ('Dr. Daniel Kibet', 'Surgeon', 'dkibet@kapsowar.org', 'Surgery', '+254 722 100 003'),
        ('Sr. Esther Chemutai', 'Matron', 'echemutai@kapsowar.org', 'Nursing Services', '+254 722 100 004'),
        ('Eng. Brian Kimutai', 'Biomedical Engineer', 'bkimutai@kapsowar.org', 'Biomedical Engineering', '+254 722 100 005'),
        ('Pharm. Wilson Kiprop', 'Chief Pharmacist', 'wkiprop@kapsowar.org', 'Pharmacy', '+254 722 100 006'),
        ('Mr. Kevin Ruto', 'IT Manager', 'kruto@kapsowar.org', 'IT Department', '+254 722 100 007'),
        ('Dr. Grace Jepkemboi', 'OBGYN', 'gjepkemboi@kapsowar.org', 'Obstetrics & Gynaecology', '+254 722 100 008'),
    ]
    await coll('persons').insert_many([
        {'id': str(uuid.uuid4()), 'name': n, 'role': r, 'email': e, 'department': d, 'phone': p, 'created_at': now}
        for n, r, e, d, p in persons
    ])

    await coll('sites').insert_one({
        'id': str(uuid.uuid4()), 'name': 'Kapsowar Main',
        'address': 'Kapsowar Town, Elgeyo-Marakwet County',
        'country': 'Kenya', 'timezone': 'Africa/Nairobi', 'created_at': now,
    })

    security_groups = [
        ('Super Admin', 'Full access to all modules and settings', 2),
        ('Asset Manager', 'Add/edit/delete assets, run reports', 3),
        ('Department Head', 'View department assets, request maintenance', 12),
        ('Biomedical Engineer', 'Maintenance, audits, full equipment access', 2),
        ('Read-Only Auditor', 'View-only access for external audits', 4),
    ]
    await coll('security_groups').insert_many([
        {'id': str(uuid.uuid4()), 'name': n, 'permissions': p, 'members': m, 'created_at': now}
        for n, p, m in security_groups
    ])

    # Sample assets
    sample_assets = [
        ('AICK-MED-00001', 'Philips IntelliVue MX450 Patient Monitor', 'Medical Equipment', 'Operating Theatre 1', 'Surgery', 'In Service', '2023-03-12', 485000, "Samaritan's Purse Donation", 'Philips Healthcare East Africa', 'PH-MX450-K2023-0012', '2026-03-12', 'Dr. Daniel Kibet'),
        ('AICK-MED-00002', 'GE Logiq P9 Ultrasound', 'Medical Equipment', 'Maternity Ward', 'Obstetrics & Gynaecology', 'In Service', '2022-08-20', 1250000, 'World Medical Mission', 'GE Healthcare Kenya', 'GE-LP9-2022-0445', '2025-08-20', 'Dr. Grace Jepkemboi'),
        ('AICK-MED-00003', 'Anaesthesia Machine — Mindray WATO EX-65', 'Medical Equipment', 'Operating Theatre 2', 'Surgery', 'In Service', '2024-01-15', 920000, 'AIC Mission USA Grant', 'Mediquip Kenya', 'MR-WATO-2024-0089', '2027-01-15', 'Dr. Daniel Kibet'),
        ('AICK-IT-00001', 'Dell OptiPlex 7090 Desktop', 'IT & Computers', 'Administration Block', 'Administration', 'In Service', '2024-05-10', 95000, 'Hospital Operations Budget', 'Crown Healthcare', 'DL-OPX-7090-K0234', '2027-05-10', 'Dr. Joseph Kiptoo'),
        ('AICK-VEH-00001', 'Toyota Land Cruiser Ambulance', 'Vehicles', 'Main Hospital Building', 'Administration', 'In Service', '2021-11-05', 6800000, "Samaritan's Purse Donation", 'Crown Healthcare', 'KCA-123X', '2024-11-05', 'Hospital Pool'),
        ('AICK-LAB-00001', 'Sysmex XN-550 Haematology Analyzer', 'Laboratory', 'Laboratory', 'Laboratory', 'Under Maintenance', '2023-06-18', 1450000, 'World Medical Mission', 'Mediquip Kenya', 'SYS-XN550-2023-0078', '2026-06-18', 'Mr. Eric Cheruiyot'),
        ('AICK-PWR-00001', 'Cummins 250kVA Diesel Generator', 'Generators & Power', 'Main Hospital Building', 'Administration', 'In Service', '2020-02-14', 3200000, 'AIC Mission USA Grant', 'Davis & Shirtliff', 'CUM-250-2020-0011', '2023-02-14', 'Eng. Brian Kimutai'),
        ('AICK-MED-00004', 'Drager Babylog 8000 Ventilator', 'Medical Equipment', "Children's Ward", 'Paediatrics', 'In Service', '2022-12-01', 780000, 'World Medical Mission', 'Philips Healthcare East Africa', 'DR-BL8K-2022-0034', '2025-12-01', 'Dr. Samuel Rotich'),
        ('AICK-SUR-00001', 'Surgical Operating Table — Mizuho OSI', 'Surgical Instruments', 'Operating Theatre 1', 'Surgery', 'In Service', '2021-04-22', 1850000, 'AIC Mission USA Grant', 'Mediquip Kenya', 'MZ-OSI-2021-0009', '2024-04-22', 'Dr. Daniel Kibet'),
        ('AICK-IT-00002', 'HP LaserJet Pro M404dn Printer', 'IT & Computers', 'Outpatient Clinic', 'Internal Medicine', 'Checked Out', '2024-02-28', 38000, 'Hospital Operations Budget', 'Crown Healthcare', 'HP-M404-K0567', '2026-02-28', 'Dr. Mary Chebet'),
        ('AICK-FUR-00001', 'Hospital Bed — Hill-Rom 900', 'Furniture', 'Maternity Ward', 'Obstetrics & Gynaecology', 'In Service', '2023-09-05', 285000, "Samaritan's Purse Donation", 'Surgipharm Ltd', 'HR-900-2023-0156', '2026-09-05', 'Sr. Esther Chemutai'),
        ('AICK-MED-00005', 'Defibrillator — Philips HeartStart XL+', 'Medical Equipment', 'Operating Theatre 1', 'Surgery', 'Reserved', '2024-07-12', 425000, 'World Medical Mission', 'Philips Healthcare East Africa', 'PH-HSXL-2024-0023', '2027-07-12', 'Dr. Daniel Kibet'),
    ]
    asset_docs = []
    for tag, name, cat, loc, dept, status, pdate, cost, fund, vendor, sn, warr, assigned in sample_assets:
        asset_docs.append({
            'id': str(uuid.uuid4()),
            'tag': tag, 'name': name,
            'category_id': cat_map.get(cat), 'category': cat,
            'location_id': loc_map.get(loc), 'location': loc,
            'department': dept,
            'status': status, 'condition': 'Excellent',
            'assigned_to': assigned, 'serial_number': sn,
            'purchase_date': pdate, 'purchase_cost': cost,
            'warranty_expiry': warr,
            'vendor_id': vendor_map.get(vendor), 'vendor': vendor,
            'funding_id': fund_map.get(fund), 'funding_source': fund,
            'created_at': now, 'updated_at': now,
        })
    await coll('assets').insert_many(asset_docs)

    # Create indexes for large-scale performance
    await coll('assets').create_index('tag')
    await coll('assets').create_index('serial_number')
    await coll('assets').create_index('status')
    await coll('assets').create_index('category_id')
    await coll('assets').create_index('location_id')
    await coll('assets').create_index('created_at')
    await coll('users').create_index('email', unique=True)
    await coll('transactions').create_index('created_at')
    await coll('transactions').create_index('asset_id')

    return True
