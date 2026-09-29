"""
extract_data.py — IMS Dashboard Data Extraction & HTML Generation
Reads IMS_June_2026_-_Leafs.xlsx, aggregates data, and produces IMS_Dashboard.html
"""
import openpyxl
import json
import base64
import os
import sys
from collections import defaultdict

EXCEL_FILE = r'd:\HPG\Project AI\Marketing\IMS\IMS June AG\IMS June 2026 - Leafs.xlsx'
LOGO_FILE  = r'd:\HPG\Project AI\Marketing\IMS\IMS June AG\HPG logo.jpg'
OUTPUT_DIR = r'd:\HPG\Project AI\Marketing\IMS\IMS June AG'

HEFNY_CORP = 'HEFNY GROUP*'

# Column indices in the Excel (0-based)
COL_CORP    = 0
COL_ATC4    = 1
COL_PRODUCT = 2
COL_PACK    = 3
COL_SECTOR  = 4
COL_LEVEL   = 5
COL_PERIOD  = 6
COL_LCVAL   = 7
COL_LCMS    = 8
COL_LCGR    = 9
COL_UNITS   = 10
COL_UNMS    = 11
COL_UNGR    = 12


def safe_float(v, default=0.0):
    """Convert value to float, handling None and non-numeric."""
    if v is None:
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def read_excel():
    """Read all data rows from the Excel file."""
    print("Reading Excel file...")
    wb = openpyxl.load_workbook(EXCEL_FILE, read_only=True, data_only=True)
    ws = wb['IMS Leafs']

    rows = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        corp    = str(row[COL_CORP] or '').strip()
        atc4    = str(row[COL_ATC4] or '').strip()
        product = str(row[COL_PRODUCT] or '').strip()
        pack    = str(row[COL_PACK] or '').strip()
        sector  = str(row[COL_SECTOR] or '').strip()
        period  = str(row[COL_PERIOD] or '').strip()
        lc_val  = safe_float(row[COL_LCVAL])
        lc_ms   = safe_float(row[COL_LCMS])
        lc_gr   = safe_float(row[COL_LCGR])
        units   = safe_float(row[COL_UNITS])
        un_ms   = safe_float(row[COL_UNMS])
        un_gr   = safe_float(row[COL_UNGR])

        if not corp or not product:
            continue

        rows.append({
            'corp': corp,
            'atc4': atc4,
            'product': product,
            'pack': pack,
            'sector': sector,
            'period': period,
            'lc_val': lc_val,
            'lc_gr': lc_gr,
            'units': units,
            'un_gr': un_gr,
        })

    wb.close()
    print(f"  Read {len(rows)} data rows")
    return rows


def compute_growth(metric_sum, growth_values_and_metrics):
    """
    Back-calculate growth from individual rows:
    prior_i = metric_i / (1 + growth_i)
    prior_agg = SUM(prior_i)
    growth_agg = (metric_agg - prior_agg) / prior_agg
    """
    prior_agg = 0.0
    for metric_i, growth_i in growth_values_and_metrics:
        denom = 1.0 + growth_i
        if abs(denom) < 1e-12:
            # growth was -100%, prior is undefined — skip
            continue
        prior_agg += metric_i / denom

    if abs(prior_agg) < 1e-12:
        return 0.0

    return (metric_sum - prior_agg) / prior_agg


def aggregate_data(rows):
    """
    Aggregate pack-level rows to product level.
    Group by (Corporation, ATC4, Product, Sector, Period).
    """
    print("Aggregating to product level...")

    # Group rows
    groups = defaultdict(list)
    for r in rows:
        key = (r['corp'], r['atc4'], r['product'], r['sector'], r['period'])
        groups[key].append(r)

    product_rows = []
    pack_rows = []

    for key, pack_list in groups.items():
        corp, atc4, product, sector, period = key

        lc_val_sum = sum(p['lc_val'] for p in pack_list)
        units_sum  = sum(p['units'] for p in pack_list)

        lc_gr_agg = compute_growth(
            lc_val_sum,
            [(p['lc_val'], p['lc_gr']) for p in pack_list]
        )
        un_gr_agg = compute_growth(
            units_sum,
            [(p['units'], p['un_gr']) for p in pack_list]
        )

        product_rows.append({
            'c': corp,
            'a': atc4,
            'p': product,
            's': sector,
            't': period,
            'v': round(lc_val_sum, 2),
            'vg': round(lc_gr_agg, 6),
            'u': round(units_sum, 2),
            'ug': round(un_gr_agg, 6),
        })

        # Keep pack-level details for drill-down
        for pk in pack_list:
            pack_rows.append({
                'c': corp,
                'a': atc4,
                'p': product,
                'k': pk['pack'],
                's': pk['sector'],
                't': pk['period'],
                'v': round(pk['lc_val'], 2),
                'vg': round(pk['lc_gr'], 6),
                'u': round(pk['units'], 2),
                'ug': round(pk['un_gr'], 6),
            })

    print(f"  {len(product_rows)} product-level rows")
    print(f"  {len(pack_rows)} pack-level rows")
    return product_rows, pack_rows


def encode_logo():
    """Read and base64-encode the HPG logo."""
    print("Encoding logo...")
    if not os.path.exists(LOGO_FILE):
        print("  Logo not found, skipping")
        return ''
    with open(LOGO_FILE, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    return f"data:image/jpeg;base64,{b64}"


def build_lookup_data(product_rows):
    """Build lookup lists for search autocomplete."""
    hefny_products = sorted(set(
        r['p'] for r in product_rows if r['c'] == HEFNY_CORP
    ))
    all_atc4s = sorted(set(r['a'] for r in product_rows))
    all_corps = sorted(set(r['c'] for r in product_rows))

    # Map each HEFNY product to its list of ATC4s
    hefny_product_atc4 = defaultdict(list)
    for r in product_rows:
        if r['c'] == HEFNY_CORP and r['a'] not in hefny_product_atc4[r['p']]:
            hefny_product_atc4[r['p']].append(r['a'])

    print(f"  {len(hefny_products)} HEFNY products")
    print(f"  {len(all_atc4s)} ATC4 categories")
    print(f"  {len(all_corps)} corporations")

    return {
        'hefnyProducts': hefny_products,
        'allAtc4s': all_atc4s,
        'allCorps': all_corps,
        'hefnyProductAtc4': dict(hefny_product_atc4),
    }


def generate_html(product_data_json, pack_data_json, lookup_json, logo_b64):
    """Read the HTML template and inject data."""
    print("Generating HTML file...")

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace('/*__PRODUCT_DATA__*/', product_data_json)
    html = html.replace('/*__PACK_DATA__*/', pack_data_json)
    html = html.replace('/*__LOOKUP_DATA__*/', lookup_json)
    html = html.replace('/*__LOGO_B64__*/', logo_b64)

    output_path = os.path.join(OUTPUT_DIR, 'IMS_Dashboard.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Written {output_path} ({size_mb:.1f} MB)")
    return output_path


def main():
    print("=" * 60)
    print("IMS Dashboard — Data Extraction & HTML Generation")
    print("=" * 60)

    rows = read_excel()
    product_rows, pack_rows = aggregate_data(rows)
    lookup = build_lookup_data(product_rows)
    logo_b64 = encode_logo()

    print("\nSerializing JSON...")
    product_json = json.dumps(product_rows, separators=(',', ':'))
    pack_json = json.dumps(pack_rows, separators=(',', ':'))
    lookup_json = json.dumps(lookup, separators=(',', ':'))
    print(f"  Product JSON: {len(product_json) / 1024:.0f} KB")
    print(f"  Pack JSON: {len(pack_json) / 1024:.0f} KB")
    print(f"  Lookup JSON: {len(lookup_json) / 1024:.0f} KB")

    output_path = generate_html(product_json, pack_json, lookup_json, logo_b64)

    print(f"\nDone! Open {output_path} in a browser.")


if __name__ == '__main__':
    main()
