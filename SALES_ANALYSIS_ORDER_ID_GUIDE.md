# Sales Analysis: Order ID Usage & Anomaly Detection Guide

## Overview

This guide explains:
1. How Sales Analysis uses order_id (Receipt column)
2. Why anomaly detection shows "weird" order_id values
3. How to verify your order_id source
4. The difference between Receipt-based and computed order_ids

---

## The "Weird Order ID" Issue EXPLAINED

### ❓ The Problem

When running anomaly detection, you see output like:

```
date       | order_id | total   | is_anomaly
2024-01-01 | 45       | $1,200  | False
2024-01-02 | 123      | $3,500  | True
2024-01-03 | 38       | $980    | False
```

You think: "Why is order_id 45, 123, 38? My receipt numbers are like 10001, 10002, 10003!"

### ✅ The Explanation

**The column is NOT showing actual order_id values!**

It shows the **COUNT** of unique orders per day:
- Jan 1: There were **45 orders** that day
- Jan 2: There were **123 orders** that day (unusual!)
- Jan 3: There were **38 orders** that day

**The confusing part:** The column was labeled `order_id` but contained counts, not IDs.

**The fix (now implemented):** 
- Column is now labeled `num_orders` to avoid confusion
- Clearly shows it's a count, not actual order_id values

---

## How Order ID Works in Sales Analysis

### Data Flow

```
1. Raw Data (Excel/CSV)
   - Has Receipt column with values like: 10001, 10002, 10003...
   
   ↓
   
2. DataLoader.preprocess_data()
   - If Receipt column exists: Receipt → order_id
   - If no Receipt: Computes order_id from customer + time
   
   ↓
   
3. SalesAnalyzer
   - Uses order_id for aggregations
   - For anomaly detection: COUNTS orders per day
   - Does NOT show actual order_id values in anomaly output
```

### Two Scenarios

#### Scenario A: Your Data HAS Receipt Column ✅

**Data:**
```
Receipt | Item Name         | Total
10001   | Paracetamol      | 10.00
10001   | Vitamin D        | 15.00
10002   | Aspirin          | 8.00
```

**After Processing:**
```
order_id | Item Name        | Total
10001    | Paracetamol     | 10.00
10001    | Vitamin D       | 15.00
10002    | Aspirin         | 8.00
```

**Result:** ✅ order_id = Receipt number (accurate!)

#### Scenario B: Your Data LACKS Receipt Column ⚠️

**Data:**
```
Customer | Item Name    | Date       | Time
John Doe | Paracetamol | 2024-01-01 | 10:00
John Doe | Vitamin D   | 2024-01-01 | 10:05
Jane Doe | Aspirin     | 2024-01-01 | 10:10
```

**After Processing:**
```
order_id | Customer | Item Name   | Date       | Time
0        | John Doe | Paracetamol | 2024-01-01 | 10:00
0        | John Doe | Vitamin D   | 2024-01-01 | 10:05
1        | Jane Doe | Aspirin     | 2024-01-01 | 10:10
```

**Result:** ⚠️ order_id computed (0, 1, 2...) based on customer + time window

**Logic:**
- Same customer + within 30 minutes = same order
- Different customer OR >30 min gap = new order

---

## Verification

### Method 1: Automatic Verification (Console)

When you initialize SalesAnalyzer, it automatically checks:

```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)
```

**Output (if using Receipt):**
```
ℹ️ Sales Analysis: Using RECEIPT-based order_id (range: 10001 to 12500)
   → Orders grouped by actual Receipt numbers
   → Total: 1,234 unique orders from 5,678 transactions
```

**Output (if computed):**
```
ℹ️ Sales Analysis: Using COMPUTED order_id (sequential: 0 to 1233)
   → Orders grouped by customer + time window (30 min)
   → Total: 1,234 unique orders from 5,678 transactions
```

### Method 2: Detailed Verification

```python
analyzer.print_order_id_verification()
```

**Output:**
```
======================================================================
ORDER ID VERIFICATION - SALES ANALYSIS
======================================================================

🔍 Order ID Source: Receipt column
   Grouping Method: Actual Receipt numbers from data

📊 Statistics:
   • Total Transactions: 5,678
   • Unique Orders: 1,234
   • Order ID Range: 10001 to 12500
   • Avg Items per Order: 4.60

📦 Order Distribution:
   • Single-Item Orders: 890 (72.1%)
   • Multi-Item Orders: 344 (27.9%)

🔍 Sample Orders (First 5):
   Order #10001:
      Customer: John Doe
      Items (3):
         - Paracetamol 500mg
         - Vitamin D3
         - Aspirin 100mg
      Total: $33.00

✅ Using RECEIPT-based order IDs (accurate grouping)
```

### Method 3: Run Verification Script

```bash
python verify_sales_order_id.py
```

This script provides:
- Complete order_id verification
- Explanation of anomaly detection
- Sample data
- Comparison of actual vs aggregated values

---

## Understanding Anomaly Detection

### What It Does

Anomaly detection finds unusual days in your sales data.

**It analyzes DAILY aggregates:**
- Total revenue per day
- Number of unique orders per day
- Total items sold per day

**It does NOT analyze individual orders!**

### The Output Explained

```python
anomalies = analyzer.detect_anomalies()
print(anomalies)
```

**Output:**
```
date       | total    | num_orders | quantity | is_anomaly
2024-01-01 | $1,200   | 45         | 150      | False
2024-01-02 | $3,500   | 123        | 420      | True
2024-01-03 | $980     | 38         | 130      | False
```

**Column Meanings:**
- `date`: The day being analyzed
- `total`: Total revenue for that day
- `num_orders`: **COUNT** of unique orders (not order_id values!)
- `quantity`: Total items sold
- `is_anomaly`: True if the day is unusual

**Why Jan 2 is anomaly:**
- Revenue: $3,500 (much higher than usual $1,000-1,200)
- Orders: 123 (much higher than usual 38-45)
- Quantity: 420 (much higher than usual 130-150)

### Why We Show Counts, Not IDs

**Imagine if we showed actual order_id values:**

❌ **Bad (confusing):**
```
date       | order_ids                        | is_anomaly
2024-01-01 | [10001, 10002, 10003, ..., 10045]| False
2024-01-02 | [10046, 10047, 10048, ..., 10168]| True
```

This is:
- Hard to read
- Not useful for analysis
- Takes up too much space

✅ **Good (clear):**
```
date       | num_orders | is_anomaly
2024-01-01 | 45         | False
2024-01-02 | 123        | True
```

This is:
- Easy to understand
- Useful for spotting patterns
- Compact

---

## How to Check Your Data

### Step 1: Check Raw Data

Before loading, verify if your Excel/CSV has a Receipt column:

```python
import pandas as pd

raw_data = pd.read_excel('pharmacy_sales.xlsx')
print("Columns:", raw_data.columns.tolist())
print("Has Receipt:", 'Receipt' in raw_data.columns or 'receipt' in raw_data.columns)
```

### Step 2: Check After Loading

```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
data = loader.load_data()
# Watch console for: "Using receipt column as order_id"

data = loader.preprocess_data()

# Check order_id values
print("\nFirst 10 order_ids:")
print(data['order_id'].unique()[:10])
```

**If using Receipt:**
```
First 10 order_ids:
[10001 10002 10003 10004 10005 10006 10007 10008 10009 10010]
```

**If computed:**
```
First 10 order_ids:
[0 1 2 3 4 5 6 7 8 9]
```

### Step 3: Verify in Sales Analysis

```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)
# Watch console for automatic verification

# Or get details
info = analyzer.verify_order_id_usage()
print(f"\nSource: {info['source']}")
print(f"Range: {info['min_order_id']} to {info['max_order_id']}")
```

---

## Common Issues

### Issue 1: "My receipt numbers are missing from anomaly output"

**Cause:** Anomaly detection shows COUNTS, not individual order_ids

**Solution:** This is by design. To see actual order_ids:

```python
# Get orders for a specific date
date_orders = data[data['date'] == '2024-01-02']['order_id'].unique()
print(f"Actual order IDs on 2024-01-02: {date_orders[:10]}...")
print(f"Total orders: {len(date_orders)}")
```

### Issue 2: "Order IDs are just 0, 1, 2, 3..."

**Cause:** No Receipt column in data, using computed order_ids

**Solution:**
1. Check if your original data has Receipt column
2. Ensure column is named 'Receipt' or 'receipt'
3. Reload data with: `loader.load_data()` and `loader.preprocess_data()`

### Issue 3: "I want to see which orders are in an anomaly day"

**Solution:**

```python
# Find anomaly dates
anomalies = analyzer.detect_anomalies()
anomaly_dates = anomalies[anomalies['is_anomaly']]['date']

# Get orders for first anomaly date
anomaly_date = anomaly_dates.iloc[0]
anomaly_orders = data[data['date'] == anomaly_date]

print(f"\nOrders on anomaly date {anomaly_date.date()}:")
for order_id in anomaly_orders['order_id'].unique()[:10]:
    order_data = anomaly_orders[anomaly_orders['order_id'] == order_id]
    print(f"  Order {order_id}: {len(order_data)} items, ${order_data['total'].sum():.2f}")
```

---

## Best Practices

### 1. Always Verify Order ID Source

```python
analyzer = SalesAnalyzer(data)
# Check console message
# Or use: analyzer.print_order_id_verification()
```

### 2. Use Receipt Column When Available

Ensure your data has a Receipt column for accurate grouping:
- More reliable than time-based grouping
- Matches actual transactions
- Easier to reconcile with physical receipts

### 3. Understand Anomaly Output

Remember:
- `num_orders` = count of orders, not IDs
- Anomalies are about unusual days, not individual orders
- To investigate anomalies, query the date and see actual orders

### 4. Document Your Data Source

Know whether your analysis uses:
- Receipt-based order_ids (preferred)
- Computed order_ids (fallback)

---

## API Reference

### New Methods

```python
# Automatic verification on init
analyzer = SalesAnalyzer(data)

# Get verification info
info = analyzer.verify_order_id_usage()

# Print detailed verification
analyzer.print_order_id_verification()

# Detect anomalies (fixed output)
anomalies = analyzer.detect_anomalies()
# Now uses 'num_orders' instead of confusing 'order_id'
```

### verify_order_id_usage()

Returns dictionary with:
- `source`: "Receipt column" or "Computed (time-based)"
- `grouping_method`: How orders are grouped
- `unique_orders`: Count of unique orders
- `min_order_id`, `max_order_id`: Range of order_id values
- `sample_orders`: List of sample orders with details

### print_order_id_verification()

Prints human-readable verification report including:
- Order ID source
- Statistics
- Order distribution
- Sample orders with items
- Warnings if using computed IDs

### detect_anomalies()

Returns DataFrame with:
- `date`: Day analyzed
- `total`: Revenue for that day
- `num_orders`: COUNT of orders (renamed from order_id)
- `quantity`: Items sold
- `is_anomaly`: True if unusual day

---

## Troubleshooting

### Check if Receipt Column Exists

```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
raw = loader.load_data()

print("Has Receipt:", 'Receipt' in raw.columns or 'receipt' in raw.columns)

if 'Receipt' in raw.columns:
    print(f"Sample receipt values: {raw['Receipt'].unique()[:5]}")
```

### Force Receipt Column Usage

If your data has receipts but they're not being used:

```python
# Check column names (case-sensitive!)
print("Columns:", raw.columns.tolist())

# Rename if needed
if 'receipt' in raw.columns:
    raw = raw.rename(columns={'receipt': 'Receipt'})
```

### Verify Order Grouping

```python
# Check how many items per order
items_per_order = data.groupby('order_id').size()

print(f"Avg items per order: {items_per_order.mean():.2f}")
print(f"Single-item orders: {(items_per_order == 1).sum()}")
print(f"Multi-item orders: {(items_per_order > 1).sum()}")

# Sample order
sample_order_id = data['order_id'].iloc[0]
sample_order = data[data['order_id'] == sample_order_id]

print(f"\nSample order {sample_order_id}:")
print(sample_order[['item_name', 'quantity', 'total']])
```

---

## Summary

### Key Points

✅ **Order ID Source**
- Preferably from Receipt column
- Falls back to computed (customer + time)
- Automatically verified on init

✅ **Anomaly Detection**
- Shows COUNTS of orders per day
- Column `num_orders` (not `order_id`)
- Not showing actual order_id values

✅ **Verification**
- Automatic on analyzer init
- Call `print_order_id_verification()` anytime
- Run `verify_sales_order_id.py` script

### Quick Checks

```python
# 1. Check order_id source
analyzer = SalesAnalyzer(data)
# Watch console message

# 2. Verify in detail
analyzer.print_order_id_verification()

# 3. Run anomaly detection
anomalies = analyzer.detect_anomalies()
print(anomalies[['date', 'num_orders', 'total', 'is_anomaly']])
```

---

**For more information:**
- Run: `python verify_sales_order_id.py`
- Check console output when initializing SalesAnalyzer
- Use `analyzer.print_order_id_verification()` anytime

**Last Updated:** November 2, 2025


