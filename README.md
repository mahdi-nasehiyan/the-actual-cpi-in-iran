# نماگر قیمت مصرف‌کننده

A price index for Iran, built from real e-commerce transactions.

Tracks price movements across thousands of products — food, dairy, cooking oil, meat, electronics, and more — using data from Torob, the country's largest online price aggregator.

**Live dashboard:** https://mahdi-nasehiyan.github.io/the-actual-cpi-in-iran/dashboard/

## Why

Official inflation numbers haven't aligned with what people actually pay at the checkout. This project is an attempt to build a transparent, reproducible price index from publicly available market data — no assumptions, no adjustments. Just median prices, tracked over time, per category.

## Data

| Field | Description |
|-------|-------------|
| `cat_level_1/2/3` | Category hierarchy (e.g. مواد غذایی > لبنیات > شیر) |
| `product_title` | Product name as listed on Torob |
| `date` | Jalali date of the price observation |
| `date_gregorian` | Gregorian equivalent |
| `price` | Price in Tomans |

Data is cleaned to include only months with sufficient coverage, keeping a consecutive date range. Each product is normalized to its first observed price (index = 100) so all products contribute equally regardless of price level.

## Repository structure

```
data/
├── prices.csv          ← cleaned, normalized price data
└── metadata.json       ← summary stats and coverage info
dashboard/
└── index.html          ← interactive chart
```

## Usage

Download `data/prices.csv` and use it with any analysis tool:

```python
import pandas as pd
df = pd.read_csv("data/prices.csv")
df.groupby(["cat_level_1", "date"]).price_index.median().plot()
```

Or visit the [dashboard](https://yourname.github.io/the-actual-cpi-in-iran/dashboard/) to explore visually.

## Methodology

1. **Collection:** Prices are scraped from Torob, which aggregates listings from thousands of online shops across Iran.
2. **Cleaning:** Months with sparse data are excluded. Only the longest consecutive run of well-populated months is kept.
3. **Normalization:** Each product's price is expressed as a percentage of its first observed price. This gives equal weight to cheap and expensive products within the same category.
4. **Aggregation:** The median of normalized prices is taken per category per month.

## Source

All data is sourced from [Torob](https://torob.com), Iran's largest e-commerce price aggregator. Torob scans thousands of online stores and unifies product listings.

## License

MIT