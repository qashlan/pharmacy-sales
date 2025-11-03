# Receipt Column and Unknown Customer Support

## Overview
This document describes the updates made to support the new data structure requirements:
1. **Receipt Column**: Excel sheet now includes a "Receipt" column that contains pre-existing order/receipt IDs
2. **Optional Customer**: The "Customer" column can now be empty, representing sales to unknown customers

## Changes Made

### 1. Configuration (`config.py`)
Added "Receipt" column mapping to support the new column:
```python
COLUMN_MAPPING = {
    # ... existing mappings ...
    'Receipt': 'receipt'
}
```

### 2. Data Loader (`data_loader.py`)

#### A. Column Mapping
- Added "Receipt" to the column mapping
- Removed "customer_name" from required columns (now optional)
- Required columns are now: `item_code`, `item_name`, `date`, `total`

#### B. New Method: `_process_customer_names()`
Handles empty/null customer names:
- If customer_name column doesn't exist → sets all to "Unknown Customer"
- If customer_name is null, empty string, or whitespace → replaces with "Unknown Customer"
- Ensures all records have a valid customer_name value for analysis

#### C. New Method: `_process_order_ids()`
Intelligently handles order ID assignment:
- **If "receipt" column exists and has data**: Uses it directly as `order_id`
  - Fills missing receipt values with -1
  - Converts to integer if possible, otherwise keeps as string
  - Prints: "Using receipt column as order_id: X unique orders"
  
- **If "receipt" column is missing or empty**: Falls back to computing order IDs
  - Uses the existing `_compute_order_ids()` logic
  - Groups by customer and datetime (30-minute window)
  - Prints: "Computed order_id from datetime: X unique orders"

#### D. Updated `_clean_data()`
- No longer drops rows with missing customer_name
- Only drops rows missing critical data: `date` and `total`

### 3. Sample Data Generation
Updated `load_sample_data()` to demonstrate new features:
- Includes "Receipt" column with realistic receipt IDs
- Some items share the same receipt (multi-item orders)
- Includes null and empty customer names to test "Unknown Customer" handling

## Excel File Structure

### New Required Columns
Your Excel file should now have these columns:

| Column Name | Required | Description | Example |
|-------------|----------|-------------|---------|
| Receipt | **Yes** | Order/Receipt ID | 12345 |
| Item Code | Yes | Product code | ITEM001 |
| Item Name | Yes | Product name | Paracetamol 500mg |
| Date | Yes | Sale date | 2024-01-15 |
| Total | Yes | Sale total | 25.50 |
| Customer Name | **No** | Customer name (can be empty) | John Doe or (empty) |
| Time | No | Sale time | 14:30:00 |
| Units | No | Number of units | 2 |
| Pieces | No | Number of pieces | 20 |
| Selling Price | No | Price per unit | 12.75 |
| Sale Type | No | Type of sale | Cash/Insurance |
| Category | No | Product category | Pain Relief |

### Example Data

```csv
Receipt,Item Code,Item Name,Customer Name,Date,Time,Total,Units
12345,ITEM001,Paracetamol 500mg,John Doe,2024-01-15,14:30:00,25.50,2
12345,ITEM002,Vitamin D3,John Doe,2024-01-15,14:30:00,35.00,1
12346,ITEM001,Paracetamol 500mg,,2024-01-15,15:00:00,12.75,1
12347,ITEM003,Aspirin 100mg,Jane Smith,2024-01-15,15:30:00,8.50,1
```

In this example:
- Receipt 12345 has 2 items for the same customer
- Receipt 12346 has an empty customer (will become "Unknown Customer")
- Each receipt represents one transaction

## Behavior

### Receipt Column Present
When the Excel file has a "Receipt" column:
- ✅ Receipt values are used directly as `order_id`
- ✅ No computation needed
- ✅ Multi-item orders share the same receipt ID
- ✅ Missing receipt values are filled with -1

### Receipt Column Missing (Backward Compatible)
When the Excel file doesn't have a "Receipt" column:
- ✅ System automatically computes order IDs (old behavior)
- ✅ Groups transactions by customer and time (30-minute window)
- ✅ Existing Excel files continue to work without changes

### Unknown Customers
When customer name is empty/null:
- ✅ Replaced with "Unknown Customer" during preprocessing
- ✅ All unknown customers are grouped together in analysis
- ✅ Can be filtered, analyzed, and reported like any other customer
- ✅ Customer analytics will show "Unknown Customer" as a segment

## Impact on Analytics

### All Analysis Modules Work Seamlessly
Since empty customers are converted to "Unknown Customer" during preprocessing:

1. **Customer Analysis** (`customer_analysis.py`)
   - "Unknown Customer" appears as a regular customer segment
   - Can see total purchases by unknown customers
   - Can track repeat purchases from unknown customers

2. **RFM Segmentation** (`rfm_analysis.py`)
   - Unknown customers are segmented based on behavior
   - Helps identify value of walk-in/unknown customers

3. **Refill Prediction** (`refill_prediction.py`)
   - Works for unknown customers (limited predictability)
   - Can track product refill patterns for unknown customers

4. **Cross-Sell Analysis** (`cross_sell_analysis.py`)
   - Receipt-based analysis works perfectly
   - Product bundles include unknown customer purchases

5. **Sales Analysis** (`sales_analysis.py`)
   - All sales trends include unknown customers
   - Revenue metrics account for all transactions

## Migration Guide

### For New Files
Create your Excel file with:
1. Add "Receipt" column with your order/receipt IDs
2. Leave "Customer Name" empty for unknown customers
3. Upload and use normally

### For Existing Files
Option 1: **Add Receipt Column**
- Add a new "Receipt" column to your Excel file
- Populate with your actual receipt/order IDs
- Keep or remove customer names as needed

Option 2: **Keep As-Is**
- No changes needed
- System will compute order IDs automatically
- Add empty customer names where applicable

## Testing

To test the new functionality:

```python
from data_loader import load_sample_data, DataLoader

# Test with sample data
df = load_sample_data()
print(df[['Receipt', 'Customer Name', 'Item Name']].head(10))

# Test loading
loader = DataLoader('your_file.xlsx')
data = loader.load_data()
processed = loader.preprocess_data()

# Verify
print(f"Unique receipts/orders: {processed['order_id'].nunique()}")
print(f"Unknown customers: {len(processed[processed['customer_name'] == 'Unknown Customer'])}")
```

## Benefits

1. **Flexibility**: Supports both receipt-based and computed order IDs
2. **Backward Compatibility**: Existing files work without changes
3. **Real-world**: Matches actual pharmacy POS system data
4. **Analytics**: Unknown customers tracked and analyzed properly
5. **Simplicity**: No manual order ID computation needed

## Notes

- Empty customer names are **always** converted to "Unknown Customer"
- Receipt column is **detected automatically** - no configuration needed
- Missing receipts are filled with -1 (can be updated if needed)
- All existing analytics work without modification
- System automatically detects and uses the best approach

## Questions?

If you have questions about:
- **Receipt format**: Any format works (numbers, strings, alphanumeric)
- **Missing receipts**: System handles gaps and missing values
- **Customer names**: Any empty/null value becomes "Unknown Customer"
- **Backward compatibility**: Old files work without any changes

