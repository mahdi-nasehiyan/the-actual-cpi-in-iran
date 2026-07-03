import pandas as pd
import gc

df = pd.read_csv('data/prices.csv')

def extract_ym(d):
    if hasattr(d, 'year') and hasattr(d, 'month'):
        return f"{d.year}-{d.month:02d}"
    s = str(d).strip()
    if not s:
        return None
    parts = s.split('-')
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1].zfill(2)}"
    return None

# ── 1. Prep ──
df['ym'] = df['date'].apply(extract_ym)
df['cat_level_2'] = df['cat_level_2'].fillna('__no_l2__')
df['cat_level_3'] = df['cat_level_3'].fillna('__no_l3__')

# ── 2. Monthly median per product (still cheap) ──
monthly = (
    df.groupby(['product_title', 'cat_level_1', 'cat_level_2', 'cat_level_3', 'ym'])['price']
    .median()
    .reset_index()
)

# ── 3. Process one L3 category at a time ──
base_month = '1404-01'
records = []

# Group by L3 category keys once
cat_keys = monthly.groupby(['cat_level_1', 'cat_level_2', 'cat_level_3'])

for (l1, l2, l3), group in cat_keys:
    # Pivot ONLY this category's products (tiny table, not the full dataset)
    panel = group.pivot_table(
        index='product_title',
        columns='ym',
        values='price',
        dropna=False,
    )
    
    # Fill gaps
    panel = panel.ffill(axis=1).interpolate(axis=1, limit_direction='both')
    
    # Matched-sample
    if base_month not in panel.columns:
        continue
    
    base = panel[base_month].dropna()
    if base.empty:
        continue
    
    for month in panel.columns:
        valid = panel[month].notna() & base.notna()
        n = valid.sum()
        if n < 3:
            continue
        relatives = panel.loc[valid, month] / base[valid]
        records.append({
            'cat_level_1': l1,
            'cat_level_2': l2,
            'cat_level_3': l3,
            'ym': month,
            'median': round(float(relatives.median()), 4),
            'mean': round(float(relatives.mean()), 4),
            'n': int(n),
            'q25': round(float(relatives.quantile(0.25)), 4),
            'q75': round(float(relatives.quantile(0.75)), 4),
        })
    
    # Explicitly delete and GC before next iteration
    del panel, group, base, valid, relatives
    gc.collect()

# ── 4. Output ──
out_df = pd.DataFrame(records)
out_df['median_pct'] = out_df['median'] * 100
out_df['q25_pct'] = out_df['q25'] * 100
out_df['q75_pct'] = out_df['q75'] * 100

out_df.to_csv('data/cpi_indices.csv', index=False)
print(f"Wrote {len(out_df)} rows, L1s: {out_df['cat_level_1'].nunique()}")