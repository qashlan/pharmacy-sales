# Refund Handling - Quick Start Guide

## 🚀 Quick Overview

The system now **automatically handles refunds** (negative total values) in all analysis modules. No configuration needed!

## ✨ What Changed?

### Automatic Detection
- Refunds are identified when `total < 0`
- `is_refund` flag added to all transactions
- Console shows refund count during data loading

### Key Improvements

| Module | How Refunds Are Handled |
|--------|------------------------|
| **Sales Analysis** | Separates gross/net revenue, tracks refund rates |
| **Customer Analysis** | Calculates net spending, tracks customer refund rates |
| **Product Analysis** | Tracks product refund rates, identifies problem products |
| **RFM Analysis** | Uses net spending for monetary value |
| **Cross-Sell** | Excludes refunds (they don't show intent) |
| **Refill Prediction** | Excludes refunds (they don't show usage) |

## 📊 New Metrics Available

### Overall Metrics
```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)
metrics = analyzer.get_overall_metrics()

# New metrics:
metrics['gross_revenue']          # Sales before refunds
metrics['refund_amount']          # Total refunds
metrics['net_revenue']            # Actual revenue
metrics['refund_rate_pct']        # % of sales refunded
```

### Customer Metrics
```python
from customer_analysis import CustomerAnalyzer

analyzer = CustomerAnalyzer(data)
customers = analyzer.get_customer_summary()

# New columns:
customers['gross_spent']          # Before refunds
customers['refund_amount']        # Customer refunds
customers['total_spent']          # Net spending
customers['refund_rate_pct']      # Customer refund rate
```

### Product Metrics
```python
from product_analysis import ProductAnalyzer

analyzer = ProductAnalyzer(data)
products = analyzer.get_product_summary()

# New columns:
products['gross_revenue']         # Before refunds
products['refund_amount']         # Product refunds
products['revenue']               # Net revenue
products['refund_rate_pct']       # Product refund rate
```

## 🎯 Common Use Cases

### 1. Financial Reporting
```python
# Get accurate revenue numbers
summary = data_loader.get_data_summary()

print(f"Gross Revenue: ${summary['gross_revenue']:,.2f}")
print(f"Refunds: ${summary['refund_amount']:,.2f}")
print(f"Net Revenue: ${summary['net_revenue']:,.2f}")
print(f"Refund Rate: {summary['refund_rate_pct']:.2f}%")
```

### 2. Identify Problem Products
```python
from product_analysis import ProductAnalyzer

analyzer = ProductAnalyzer(data)

# Products with high refund rates
problem_products = analyzer.get_high_refund_products(
    min_sales=10,
    min_refund_rate=5.0
)

print("Products with >5% refund rate:")
print(problem_products)
```

### 3. Track Customer Refund Patterns
```python
from customer_analysis import CustomerAnalyzer

analyzer = CustomerAnalyzer(data)
customers = analyzer.get_customer_summary()

# Customers with high refund rates
high_refund_customers = customers[
    customers['refund_rate_pct'] > 10
].sort_values('refund_rate_pct', ascending=False)

print("Customers with >10% refund rate:")
print(high_refund_customers[['customer_name', 'refund_rate_pct', 'refund_amount']])
```

### 4. Detailed Refund Analysis
```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)
refund_analysis = analyzer.get_refund_analysis()

if refund_analysis['has_refunds']:
    print(f"Total Refund Amount: ${refund_analysis['total_refund_amount']:,.2f}")
    print(f"Refund Rate: {refund_analysis['refund_rate_pct']:.2f}%")
    
    print("\nTop Refunded Products:")
    print(refund_analysis['top_refunded_products'])
    
    print("\nCustomers with Most Refunds:")
    print(refund_analysis['top_refund_customers'])
```

## ⚠️ Important Notes

### What You Need to Know

1. **Net vs Gross**
   - Always use **net** metrics for accurate reporting
   - Net = Gross - Refunds

2. **Negative Quantities**
   - Refund quantities are negative (this is correct!)
   - Use `net_quantity` or filter `~is_refund` for positive counts

3. **Pattern Analysis**
   - Refunds are **excluded** from cross-sell and refill predictions
   - This gives more accurate behavior patterns

4. **Customer Value**
   - RFM analysis uses **net spending**
   - More accurate customer segmentation

## 🔍 Quick Checks

### Verify Refunds are Detected
```python
# After loading data
print(f"Total records: {len(data)}")
print(f"Refunds: {data['is_refund'].sum()}")
print(f"Sales: {(~data['is_refund']).sum()}")

# Check refund amount
refunds = data[data['is_refund']]
print(f"Refund amount: ${abs(refunds['total'].sum()):,.2f}")
```

### Monitor Refund Rate
```python
from sales_analysis import SalesAnalyzer

analyzer = SalesAnalyzer(data)
metrics = analyzer.get_overall_metrics()

# Alert if refund rate is high
if metrics['refund_rate_pct'] > 5.0:
    print(f"⚠️ High refund rate: {metrics['refund_rate_pct']:.2f}%")
    
    # Investigate
    refund_analysis = analyzer.get_refund_analysis()
    print("\nTop refunded products:")
    print(refund_analysis['top_refunded_products'].head())
```

## 📈 Dashboard Integration

If using the dashboard, it will automatically:
- Show gross, net, and refund amounts
- Display refund rates
- Highlight products/customers with high refunds
- Exclude refunds from behavior analysis

## 🛠️ Troubleshooting

### Issue: Can't find refund columns

**Solution:** Reload and preprocess data:
```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
data = loader.load_data()
data = loader.preprocess_data()  # Adds is_refund flag
```

### Issue: Revenue seems incorrect

**Solution:** Use net revenue, not total:
```python
# ❌ Wrong
revenue = data['total'].sum()  # Includes negative refunds

# ✅ Correct
metrics = analyzer.get_overall_metrics()
revenue = metrics['net_revenue']
```

### Issue: Want to see only sales (no refunds)

**Solution:** Filter by is_refund flag:
```python
sales_only = data[~data['is_refund']]
refunds_only = data[data['is_refund']]
```

## 📚 Learn More

For detailed documentation, see:
- `REFUND_HANDLING_GUIDE.md` - Complete guide
- Console output during data loading
- Method docstrings in code

## 💡 Best Practices

1. ✅ Always check refund rate in reports
2. ✅ Monitor products with high refund rates
3. ✅ Track customer refund patterns
4. ✅ Use net metrics for financial reporting
5. ✅ Investigate sudden refund spikes

---

**That's it!** Refund handling is automatic and transparent. Just use the standard analysis methods and refunds are properly accounted for. 🎉

