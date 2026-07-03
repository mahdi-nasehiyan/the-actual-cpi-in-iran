import pandas as pd
import numpy as np

df = pd.read_csv('data/prices.csv')

# ── 1. Extract ym from jdatetime objects ──
def extract_ym(d):
    """Handle jdatetime.date, jdatetime.datetime, or string."""
    if hasattr(d, 'year') and hasattr(d, 'month'):
        return f"{d.year}-{d.month:02d}"
    s = str(d).strip()
    if not s:
        return None
    parts = s.split('-')
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1].zfill(2)}"
    return None

df['ym'] = df['date'].apply(extract_ym)

# ── 2. Monthly median per product ──
monthly = (
    df.groupby(['product_title', 'cat_level_1', 'cat_level_2', 'cat_level_3', 'ym'])['price']
    .median()
    .reset_index()
)

# ── 3. Pivot to wide panel ──
panel = monthly.pivot_table(
    index=['product_title', 'cat_level_1', 'cat_level_2', 'cat_level_3'],
    columns='ym',
    values='price'
)

# ── 4. Forward-fill then interpolate gaps ──
panel = panel.ffill(axis=1).interpolate(axis=1, limit_direction='both')

# ── 5. Matched-sample index ──
def matched_index(panel_slice, base_month, min_n=3):
    if base_month not in panel_slice.columns:
        return {}
    
    base = panel_slice[base_month].dropna()
    out = {}
    
    for month in panel_slice.columns:
        valid = panel_slice[month].notna() & base.notna()
        n = valid.sum()
        if n < min_n:
            continue
        relatives = panel_slice.loc[valid, month] / base[valid]
        out[month] = {
            'median': round(float(relatives.median()), 4),
            'mean': round(float(relatives.mean()), 4),
            'n': int(n),
            'q25': round(float(relatives.quantile(0.25)), 4),
            'q75': round(float(relatives.quantile(0.75)), 4),
        }
    return out

# ── 6. Compute per L3 category ──
#    Keep cat_level_1, cat_level_2, cat_level_3 as separate columns
base_month = '1404-01'
records = []

for (l1, l2, l3), group in panel.groupby(level=[1, 2, 3]):
    idx = matched_index(group.droplevel([1, 2, 3]), base_month)
    for ym, vals in idx.items():
        records.append({
            'cat_level_1': l1,
            'cat_level_2': l2,
            'cat_level_3': l3,
            'ym': ym,
            **vals
        })

out_df = pd.DataFrame(records)

# Add percentage columns for easier plotting
out_df['median_pct'] = out_df['median'] * 100
out_df['q25_pct'] = out_df['q25'] * 100
out_df['q75_pct'] = out_df['q75'] * 100

out_df.to_csv('data/cpi_indices.csv', index=False)
print(f"Wrote {len(out_df)} rows with columns: {list(out_df.columns)}")