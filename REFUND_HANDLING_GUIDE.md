# Refund Handling Implementation Guide

## Overview

This system now comprehensively handles refund transactions (negative total values) throughout all analysis modules. Refunds are identified, tracked, and appropriately processed to ensure accurate financial reporting and customer behavior analysis.

## Table of Contents

1. [What is a Refund?](#what-is-a-refund)
2. [How Refunds are Identified](#how-refunds-are-identified)
3. [Impact on Each Module](#impact-on-each-module)
4. [Key Metrics](#key-metrics)
5. [API Reference](#api-reference)
6. [Best Practices](#best-practices)

---

## What is a Refund?

A **refund** is a transaction where a previously sold item is returned, and money is credited back to the customer. In the data:

- **Negative `total` value** indicates a refund
- Refunds reduce revenue and quantity sold
- Refunds are tracked separately from regular sales

**Example:**
```
Item: Paracetamol 500mg
Sale:   Total = $10.00   (positive)
Refund: Total = -$10.00  (negative)
```

---

## How Refunds are Identified

### Data Loader (data_loader.py)

During data preprocessing, the system automatically:

1. **Identifies refunds** by checking if `total < 0`
2. **Adds `is_refund` flag** to each transaction
3. **Ensures quantity consistency** - refund quantities are made negative
4. **Reports refund statistics** during loading

```python
df['is_refund'] = df['total'] < 0
df.loc[df['is_refund'], 'quantity'] = -abs(df.loc[df['is_refund'], 'quantity'])
```

**Console Output Example:**
```
⚠ Identified 45 refund transactions (total: $-1,234.56)
```

---

## Impact on Each Module

### 1. Sales Analysis (sales_analysis.py)

**Refund Handling:**
- Separates sales from refunds for accurate metrics
- Calculates both **gross** and **net** revenue
- Tracks refund rates and trends

**New Metrics:**
- `gross_revenue`: Total from sales only
- `refund_amount`: Total refunds (absolute value)
- `net_revenue`: Gross revenue minus refunds
- `refund_rate_pct`: Percentage of sales that were refunded
- `refund_transaction_rate_pct`: Percentage of transactions that are refunds

**New Methods:**
- `get_refund_analysis()`: Comprehensive refund pattern analysis
  - Top refunded products
  - Customers with most refunds
  - Refund trends over time
  - Monthly refund patterns

**Example Usage:**
```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)

# Get overall metrics with refund handling
metrics = analyzer.get_overall_metrics()
print(f"Gross Revenue: ${metrics['gross_revenue']:,.2f}")
print(f"Refund Amount: ${metrics['refund_amount']:,.2f}")
print(f"Net Revenue: ${metrics['net_revenue']:,.2f}")
print(f"Refund Rate: {metrics['refund_rate_pct']:.2f}%")

# Detailed refund analysis
refund_analysis = analyzer.get_refund_analysis()
if refund_analysis['has_refunds']:
    print(f"\nTop Refunded Products:")
    print(refund_analysis['top_refunded_products'])
```

---

### 2. Customer Analysis (customer_analysis.py)

**Refund Handling:**
- Separates customer sales from refunds
- Calculates net spending per customer
- Tracks customer refund rates

**New Metrics:**
- `gross_spent`: Total customer purchases before refunds
- `refund_amount`: Total refunds by customer
- `total_spent`: Net spending (gross - refunds)
- `refund_rate_pct`: Customer's refund rate
- `refund_orders`: Number of refund transactions
- `net_items`: Net quantity purchased (sales - refunds)

**Impact:**
- High-value customers now accurately reflect net spending
- Customer lifetime value (CLV) accounts for refunds
- Refund patterns can indicate satisfaction issues

**Example Usage:**
```python
from customer_analysis import CustomerAnalyzer

analyzer = CustomerAnalyzer(data)

# Get customer summary with refund handling
customers = analyzer.get_customer_summary()

# Identify customers with high refund rates
high_refund_customers = customers[customers['refund_rate_pct'] > 10].sort_values(
    'refund_rate_pct', ascending=False
)

print("Customers with >10% refund rate:")
print(high_refund_customers[['customer_name', 'gross_spent', 'refund_amount', 
                              'total_spent', 'refund_rate_pct']])
```

---

### 3. Product Analysis (product_analysis.py)

**Refund Handling:**
- Tracks refund rates per product
- Calculates net revenue and quantity per product
- Identifies problematic products with high refund rates

**New Metrics:**
- `gross_revenue`: Product revenue before refunds
- `refund_amount`: Total refunds for product
- `revenue`: Net revenue (gross - refunds)
- `refund_rate_pct`: Percentage of product sales refunded
- `refund_orders`: Number of orders with refunds
- `refund_quantity`: Total quantity refunded
- `net_quantity`: Net quantity sold

**New Methods:**
- `get_high_refund_products(min_sales, min_refund_rate)`: Identify products with quality/satisfaction issues

**Example Usage:**
```python
from product_analysis import ProductAnalyzer

analyzer = ProductAnalyzer(data)

# Get product summary with refund metrics
products = analyzer.get_product_summary()

# Identify products with high refund rates (potential quality issues)
high_refund_products = analyzer.get_high_refund_products(
    min_sales=10,        # At least 10 sales
    min_refund_rate=5.0  # At least 5% refund rate
)

print("Products with potential quality issues:")
print(high_refund_products[['item_name', 'orders', 'refund_orders', 
                            'refund_rate_pct', 'refund_amount']])
```

**Use Cases:**
- Quality control: Identify products frequently returned
- Supplier evaluation: Track refund rates by supplier
- Inventory decisions: Consider refund rates when ordering

---

### 4. RFM Analysis (rfm_analysis.py)

**Refund Handling:**
- Uses **net monetary value** (sales - refunds) for RFM scoring
- Excludes refund transactions from frequency calculation
- Provides more accurate customer segmentation

**Impact:**
- **Recency (R)**: Based on last purchase (sales only)
- **Frequency (F)**: Counts only actual purchases, not refunds
- **Monetary (M)**: Net spending after refunds

**Why This Matters:**
- Customers who buy and return shouldn't be classified as high-value
- Net spending is the true indicator of customer value
- More accurate segmentation for marketing campaigns

**Example Usage:**
```python
from rfm_analysis import RFMAnalyzer

analyzer = RFMAnalyzer(data)

# Calculate RFM with refund handling
rfm = analyzer.calculate_rfm()

# The 'monetary' column now represents net spending
print("\nRFM Scores (with refund handling):")
print(rfm[['customer_name', 'frequency', 'monetary', 'rfm_score']].head(10))

# Segment customers
rfm = analyzer.segment_customers()
segment_summary = analyzer.get_segment_summary()
print("\nCustomer Segments:")
print(segment_summary)
```

---

### 5. Cross-Sell Analysis (cross_sell_analysis.py)

**Refund Handling:**
- **Excludes refunds entirely** from basket analysis
- Only analyzes actual purchase patterns
- More accurate product association rules

**Why Exclude Refunds?**
- Refunds don't represent purchase intent
- Including refunds distorts association patterns
- Cross-sell opportunities should be based on satisfied purchases

**Impact:**
- More accurate product recommendations
- Better bundle suggestions
- Cleaner association rules

**Example Usage:**
```python
from cross_sell_analysis import CrossSellAnalyzer

analyzer = CrossSellAnalyzer(data)
# Refunds are automatically excluded in __init__

# The analysis metadata shows how many refunds were excluded
print(f"Refunds excluded: {analyzer.analysis_metadata['refunds_excluded']}")

# Generate association rules (based on actual purchases only)
rules = analyzer.generate_association_rules()
print("\nProduct Association Rules (refunds excluded):")
print(rules.head())
```

---

### 6. Refill Prediction (refill_prediction.py)

**Refund Handling:**
- **Excludes refunds** from purchase interval calculations
- Only tracks actual consumption patterns
- More accurate refill predictions

**Why Exclude Refunds?**
- Refunds don't represent actual product consumption
- Including refunds would distort usage patterns
- Refill timing should be based on actual purchases

**Example Usage:**
```python
from refill_prediction import RefillPredictor

predictor = RefillPredictor(data)
# Refunds are automatically excluded

# Calculate intervals (based on purchases only)
intervals = predictor.calculate_purchase_intervals()

# Get overdue refills
overdue = predictor.get_overdue_refills(tolerance_days=7)
print("\nOverdue Refills (excluding refunds from analysis):")
print(overdue.head())
```

---

## Key Metrics

### Revenue Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Gross Revenue** | Total sales before refunds | Sum of all positive totals |
| **Refund Amount** | Total refunds (absolute) | Absolute value of negative totals |
| **Net Revenue** | Actual revenue after refunds | Gross Revenue - Refund Amount |
| **Refund Rate %** | Percentage of sales refunded | (Refund Amount / Gross Revenue) × 100 |

### Transaction Metrics

| Metric | Description |
|--------|-------------|
| **Sales Transactions** | Number of transactions with positive total |
| **Refund Transactions** | Number of transactions with negative total |
| **Refund Transaction Rate %** | Percentage of all transactions that are refunds |

### Customer Metrics

| Metric | Description |
|--------|-------------|
| **Customer Gross Spent** | Total purchases before refunds |
| **Customer Refund Amount** | Total refunds for customer |
| **Customer Net Spent** | Actual spending (gross - refunds) |
| **Customer Refund Rate %** | Customer's refund rate |

### Product Metrics

| Metric | Description |
|--------|-------------|
| **Product Gross Revenue** | Sales revenue before refunds |
| **Product Refund Amount** | Refunds for this product |
| **Product Net Revenue** | Actual revenue (gross - refunds) |
| **Product Refund Rate %** | Percentage of product sales refunded |

---

## API Reference

### Data Loader

```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
data = loader.load_data()
data = loader.preprocess_data()

# Refund flag is automatically added
# data['is_refund'] = True/False for each row

summary = loader.get_data_summary()
# Returns:
# - gross_revenue
# - refund_amount
# - net_revenue
# - refund_rate_pct
# - num_refunds
# - num_sales
```

### Sales Analysis

```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)

# Overall metrics with refund handling
metrics = analyzer.get_overall_metrics()
# Returns all standard metrics plus:
# - gross_revenue
# - refund_amount
# - net_revenue
# - refund_rate_pct
# - num_refund_transactions
# - refund_transaction_rate_pct

# Detailed refund analysis
refund_analysis = analyzer.get_refund_analysis()
# Returns:
# - total_refund_amount
# - refund_rate_pct
# - top_refunded_products (DataFrame)
# - top_refund_customers (DataFrame)
# - refunds_by_month (DataFrame)
# - daily_refunds (DataFrame)
```

### Customer Analysis

```python
from customer_analysis import CustomerAnalyzer

analyzer = CustomerAnalyzer(data)

customers = analyzer.get_customer_summary()
# Returns DataFrame with columns:
# - gross_spent
# - refund_amount
# - total_spent (net)
# - refund_rate_pct
# - refund_orders
# - net_items
```

### Product Analysis

```python
from product_analysis import ProductAnalyzer

analyzer = ProductAnalyzer(data)

products = analyzer.get_product_summary()
# Returns DataFrame with columns:
# - gross_revenue
# - refund_amount
# - revenue (net)
# - refund_rate_pct
# - refund_orders
# - refund_quantity
# - net_quantity

# Identify problematic products
high_refund = analyzer.get_high_refund_products(
    min_sales=10,
    min_refund_rate=5.0
)
```

---

## Best Practices

### 1. Always Use Net Metrics for Financial Reporting

❌ **Incorrect:**
```python
total_revenue = data['total'].sum()  # Includes negative refunds
```

✅ **Correct:**
```python
metrics = analyzer.get_overall_metrics()
net_revenue = metrics['net_revenue']  # Accurate net revenue
```

### 2. Monitor Refund Rates

High refund rates may indicate:
- Product quality issues
- Customer satisfaction problems
- Incorrect product descriptions
- Supplier problems

**Action Items:**
```python
# Get refund analysis
refund_analysis = sales_analyzer.get_refund_analysis()

# Check overall refund rate
if refund_analysis['refund_rate_pct'] > 5.0:
    print("⚠ Warning: Refund rate exceeds 5%")
    
# Investigate top refunded products
print(refund_analysis['top_refunded_products'])
```

### 3. Track Customer Refund Patterns

**Identify problematic customers:**
```python
customers = customer_analyzer.get_customer_summary()

# High refund rate customers
problem_customers = customers[customers['refund_rate_pct'] > 15]

# Many refund transactions
frequent_refunders = customers[customers['refund_orders'] > 3]
```

### 4. Product Quality Control

**Monthly product refund monitoring:**
```python
high_refund_products = product_analyzer.get_high_refund_products(
    min_sales=10,
    min_refund_rate=5.0
)

# Alert for investigation
if len(high_refund_products) > 0:
    print("⚠ Products requiring quality review:")
    print(high_refund_products[['item_name', 'refund_rate_pct', 'refund_orders']])
```

### 5. Exclude Refunds from Behavior Analysis

When analyzing customer behavior patterns:
- ✅ Use sales data for purchase patterns
- ✅ Use net metrics for customer value
- ✅ Exclude refunds from cross-sell analysis
- ✅ Exclude refunds from refill predictions

### 6. Financial Reconciliation

**Monthly reconciliation checklist:**
```python
summary = data_loader.get_data_summary()
metrics = sales_analyzer.get_overall_metrics()

print("=== Financial Reconciliation ===")
print(f"Gross Revenue: ${summary['gross_revenue']:,.2f}")
print(f"Refunds: -${summary['refund_amount']:,.2f}")
print(f"Net Revenue: ${summary['net_revenue']:,.2f}")
print(f"Refund Rate: {summary['refund_rate_pct']:.2f}%")

# Verify calculation
assert abs(summary['gross_revenue'] - summary['refund_amount'] - summary['net_revenue']) < 0.01
```

---

## Data Quality Checks

### Verify Refund Handling

```python
# Check that refunds are properly flagged
refunds = data[data['is_refund']]
print(f"Total refunds: {len(refunds)}")
print(f"Refund amount: ${abs(refunds['total'].sum()):,.2f}")

# Verify quantity consistency
assert (refunds['quantity'] <= 0).all(), "Refund quantities should be negative"

# Verify all negative totals are flagged
negative_totals = data[data['total'] < 0]
assert (negative_totals['is_refund']).all(), "All negative totals should be flagged as refunds"
```

---

## Common Issues and Solutions

### Issue 1: Refund Metrics Not Showing

**Problem:** Refund-related columns missing in output

**Solution:** Clear analysis caches and recalculate:
```python
# Clear caches
analyzer._customer_summary_cache = None
analyzer._product_summary_cache = None

# Recalculate
summary = analyzer.get_customer_summary()
```

### Issue 2: Unexpected Negative Quantities

**Problem:** Quantities showing as negative in reports

**Solution:** This is expected for refunds. Use net quantities:
```python
# For products
products = analyzer.get_product_summary()
net_quantity = products['net_quantity']  # Excludes refunds

# For overall
sales_only = data[~data['is_refund']]
total_sold = sales_only['quantity'].sum()
```

### Issue 3: Revenue Doesn't Match Expected

**Problem:** Revenue totals seem incorrect

**Solution:** Verify you're using net revenue:
```python
metrics = analyzer.get_overall_metrics()

print(f"Gross: ${metrics['gross_revenue']:,.2f}")
print(f"Refunds: -${metrics['refund_amount']:,.2f}")
print(f"Net: ${metrics['net_revenue']:,.2f}")

# Net revenue should equal gross - refunds
assert abs(metrics['gross_revenue'] - metrics['refund_amount'] - metrics['net_revenue']) < 0.01
```

---

## Migration Guide

### For Existing Code

If you have existing code that doesn't handle refunds:

**Before:**
```python
total_revenue = data['total'].sum()
total_quantity = data['quantity'].sum()
```

**After:**
```python
sales_data = data[~data['is_refund']]
refunds_data = data[data['is_refund']]

gross_revenue = sales_data['total'].sum()
refund_amount = abs(refunds_data['total'].sum())
net_revenue = gross_revenue - refund_amount

total_quantity = sales_data['quantity'].sum()
```

---

## Summary

The refund handling system provides:

✅ **Accurate financial metrics** - Net revenue after refunds  
✅ **Customer behavior insights** - True spending patterns  
✅ **Product quality monitoring** - Refund rate tracking  
✅ **Better segmentation** - RFM based on net value  
✅ **Cleaner analysis** - Refunds excluded from pattern analysis  

All refund handling is **automatic** and **transparent** - just use the standard analysis methods and refunds are properly accounted for.

---

## Support

For questions or issues:
1. Check if `is_refund` column exists in your data
2. Verify refunds are being detected during data loading
3. Ensure you're using the latest versions of analysis modules
4. Review the console output for refund detection messages

---

**Last Updated:** 2025-11-02  
**Version:** 1.0

