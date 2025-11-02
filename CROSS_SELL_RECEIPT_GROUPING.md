# Cross-Sell Analysis: Receipt Grouping Explanation

## Overview

The Cross-Sell & Bundle Analysis **correctly uses the Receipt column** to identify which items were sold together. This document explains how it works and how to verify it.

---

## How It Works

### 1. Data Loading Phase

**In `data_loader.py`:**
```python
def _process_order_ids(self, df: pd.DataFrame):
    """Process order IDs from receipt column or compute if not present."""
    
    # If 'receipt' column exists, use it as order_id
    if 'receipt' in df.columns and df['receipt'].notna().any():
        df['order_id'] = df['receipt']  # Receipt → order_id
        print(f"Using receipt column as order_id: {df['order_id'].nunique()} unique orders")
```

**Result:** Your **Receipt column** becomes `order_id` in the processed data.

### 2. Cross-Sell Analysis Phase

**In `cross_sell_analysis.py`:**
```python
def create_basket_matrix(self):
    """Create basket matrix using order_id (from Receipt column)."""
    
    # Group items by order_id (which is Receipt number)
    baskets = self.data.groupby('order_id')['item_name'].apply(
        lambda x: [str(item) for item in x]
    ).reset_index()
```

**Result:** Items with the **same Receipt number** are grouped together in one "basket".

### 3. Pattern Discovery

The analysis then finds:
- Which items appear together in the same Receipt
- How often product combinations occur
- Association rules between products

---

## Verification

### Automatic Verification (Console Output)

When you initialize CrossSellAnalyzer, you'll see:

```
ℹ Cross-sell analysis: Using order_id (from Receipt column) to group 1,234 orders with 5,678 items
```

This confirms Receipt grouping is active.

### Manual Verification Method 1: Using Built-in Method

```python
from cross_sell_analysis import CrossSellAnalyzer

analyzer = CrossSellAnalyzer(data)

# Verify receipt grouping
analyzer.verify_receipt_grouping(sample_size=5)
```

**Output:**
```
======================================================================
RECEIPT/ORDER GROUPING VERIFICATION
======================================================================

📋 Grouping Method: order_id (from Receipt column)

📊 Order Statistics:
   • Total Orders: 1,234
   • Single-Item Orders: 890 (72.1%)
   • Multi-Item Orders: 344 (27.9%)
   • Average Basket Size: 1.45 items
   • Largest Basket: 8 items

🔍 Sample Multi-Item Orders (Receipt Grouping):
   Order #12345:
      Customer: John Doe
      Date: 2024-01-15
      Items (3):
         - Paracetamol 500mg
         - Vitamin D3
         - Aspirin 100mg
      Total: $25.50
```

### Manual Verification Method 2: Check Grouping Info

```python
# Get detailed grouping information
info = analyzer.get_receipt_grouping_info()

print(f"Grouping Method: {info['grouping_method']}")
print(f"Multi-Item Orders: {info['multi_item_orders']}")
print(f"Average Basket Size: {info['avg_basket_size']:.2f}")

# See sample orders
for order in info['sample_multi_item_orders'][:3]:
    print(f"\nReceipt #{order['order_id']}:")
    print(f"  Items: {', '.join(order['item_name'])}")
```

### Manual Verification Method 3: Run Verification Script

```bash
cd /path/to/pharmacy_sales
python verify_receipt_grouping.py
```

This script will:
1. Load your data
2. Verify Receipt → order_id mapping
3. Show sample receipts with their items
4. Display cross-sell patterns based on receipts
5. Generate bundle suggestions

---

## Examples

### Example 1: Receipt with Multiple Items

**Raw Data (Excel):**
```
Receipt | Item Name           | Quantity | Total
12345   | Paracetamol 500mg  | 1        | 10.00
12345   | Vitamin D3         | 2        | 15.00
12345   | Aspirin 100mg      | 1        | 8.00
```

**After Processing:**
```
order_id: 12345
basket: ['Paracetamol 500mg', 'Vitamin D3', 'Aspirin 100mg']
```

**Cross-Sell Analysis Result:**
- These 3 items were bought together in Receipt #12345
- If this pattern repeats, an association rule will be created:
  - "When customer buys Paracetamol, they often buy Vitamin D3"

### Example 2: Multiple Receipts from Same Customer

**Raw Data:**
```
Receipt | Customer | Item Name           | Date
10001   | John Doe | Paracetamol 500mg  | 2024-01-10
10001   | John Doe | Vitamin D3         | 2024-01-10
10002   | John Doe | Omeprazole 20mg    | 2024-01-15
10002   | John Doe | Aspirin 100mg      | 2024-01-15
```

**Analysis:**
- Receipt 10001: `['Paracetamol', 'Vitamin D3']` - one basket
- Receipt 10002: `['Omeprazole', 'Aspirin']` - another basket

Even though it's the same customer, different receipts = different baskets.

---

## Why Receipt Grouping Matters

### ✅ Correct Approach (Using Receipt)

Items grouped by Receipt represent:
- **Actual purchase decisions** made at the same time
- **True shopping baskets** that customers created
- **Reliable patterns** for cross-selling

**Example:**
```
Receipt #100: [Paracetamol, Bandages, Antiseptic]
→ These were bought together, so they're related
```

### ❌ Wrong Approach (Time-based grouping)

If we grouped by time windows instead:
- Items from different customers might be mixed
- Random coincidences would appear as patterns
- Unreliable recommendations

**Example:**
```
Time 10:00-10:30: [Customer A's Paracetamol, Customer B's Insulin]
→ These are NOT related, just bought at similar times
```

---

## Common Questions

### Q: How do I know it's using Receipt and not time-based grouping?

**A:** Multiple ways to verify:

1. **Console output** when initializing:
   ```
   ℹ Cross-sell analysis: Using order_id (from Receipt column)
   ```

2. **Check diagnostics:**
   ```python
   analyzer.print_diagnostics()
   # Shows: "Grouping Method: order_id (from Receipt column)"
   ```

3. **Verify in code:**
   ```python
   info = analyzer.get_receipt_grouping_info()
   print(info['grouping_method'])
   # Output: "order_id (from Receipt column)"
   ```

### Q: What if my data doesn't have a Receipt column?

**A:** The system will fall back to computing order_id from customer and time:
- Same customer
- Same date
- Within 30-minute window

But if you have a Receipt column, it will always use that (which is more accurate).

### Q: Can I see which items are in each receipt?

**A:** Yes! Use:

```python
# Method 1: Built-in verification
analyzer.verify_receipt_grouping(sample_size=10)

# Method 2: Get raw data
info = analyzer.get_receipt_grouping_info()
for order in info['sample_multi_item_orders']:
    print(f"Receipt {order['order_id']}: {order['item_name']}")

# Method 3: Direct query
receipt_items = data[data['order_id'] == 12345]
print(receipt_items[['item_name', 'quantity', 'total']])
```

### Q: How can I verify a specific receipt?

**A:**

```python
from data_loader import DataLoader

# Load data
loader = DataLoader('pharmacy_sales.xlsx')
data = loader.load_data()
data = loader.preprocess_data()

# Check specific receipt
receipt_id = 12345
receipt_items = data[data['order_id'] == receipt_id]

print(f"\nReceipt #{receipt_id}:")
print(receipt_items[['item_name', 'quantity', 'total', 'customer_name', 'date']])
```

---

## Impact on Analysis Results

### Association Rules

**Based on Receipt Grouping:**
```
Rule: {Paracetamol} → {Vitamin D3}
Confidence: 65%
```

**Meaning:** In 65% of receipts that contain Paracetamol, Vitamin D3 also appears.

### Bundle Suggestions

**Bundles Found:**
```
Bundle: [Paracetamol, Vitamin D3, Aspirin]
Frequency: 45 times
```

**Meaning:** These 3 items appeared together in 45 different receipts.

### Product Recommendations

**When customer adds Paracetamol to cart:**
```
Recommended: Vitamin D3 (bought together in 65% of receipts)
```

---

## Code Reference

### Key Methods

```python
# Initialize with automatic Receipt grouping
analyzer = CrossSellAnalyzer(data)

# Verify receipt grouping
analyzer.verify_receipt_grouping(sample_size=5)

# Get grouping information
info = analyzer.get_receipt_grouping_info()

# Show diagnostics (includes grouping method)
analyzer.print_diagnostics()

# Generate rules (based on Receipt grouping)
rules = analyzer.generate_association_rules()

# Get bundles (items bought together in same Receipt)
bundles = analyzer.get_bundle_suggestions()
```

### Data Flow

```
Excel File (Receipt Column)
    ↓
DataLoader.preprocess_data()
    ↓
Receipt → order_id mapping
    ↓
CrossSellAnalyzer.__init__()
    ↓
Group items by order_id
    ↓
Create baskets (one per Receipt)
    ↓
Find patterns in baskets
    ↓
Association Rules & Bundles
```

---

## Troubleshooting

### Issue: "Data must have 'order_id' column"

**Cause:** Data wasn't properly preprocessed.

**Solution:**
```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
data = loader.load_data()
data = loader.preprocess_data()  # This creates order_id from Receipt

analyzer = CrossSellAnalyzer(data)
```

### Issue: Not sure if Receipt grouping is working

**Solution:** Run verification:
```python
analyzer.verify_receipt_grouping()
# This shows exactly how items are grouped
```

### Issue: Want to see which receipts have multiple items

**Solution:**
```python
# Count items per receipt
receipt_counts = data.groupby('order_id').size()
multi_item_receipts = receipt_counts[receipt_counts > 1]

print(f"Multi-item receipts: {len(multi_item_receipts)}")
print("\nSample multi-item receipts:")
for receipt_id in multi_item_receipts.head(5).index:
    items = data[data['order_id'] == receipt_id]['item_name'].tolist()
    print(f"  Receipt {receipt_id}: {', '.join(items)}")
```

---

## Summary

✅ **Cross-Sell Analysis USES Receipt Column**
- Receipt → order_id during data loading
- Items grouped by order_id (same receipt)
- Patterns based on items in same receipt
- Bundles show items bought together in receipts

✅ **Verification Methods Available**
- Automatic console messages
- `verify_receipt_grouping()` method
- `get_receipt_grouping_info()` method
- `print_diagnostics()` output
- Verification script

✅ **Accurate & Reliable**
- True shopping baskets
- Actual purchase decisions
- Reliable cross-sell patterns

---

**For more information:**
- Run: `python verify_receipt_grouping.py`
- Check: `CROSS_SELL_README.md`
- See: Cross-sell analysis code documentation

**Last Updated:** November 2, 2025


