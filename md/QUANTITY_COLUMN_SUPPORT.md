# Quantity Column Support

## Overview

The system now supports a **Quantity** column that represents the actual quantity of items sold. This column can contain fractional values (0.50, 0.80, etc.) to represent partial unit sales.

## Column Definitions

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| **Units** | Integer | Number of full units sold | 0, 1, 2, 3 |
| **Pieces** | Integer | Number of pieces (always integer) | 0, 1, 4, 10 |
| **Quantity** | Float | Actual quantity sold (can be fractional) | 0.50, 0.80, 1, 2 |

## How It Works

### When Quantity Column Exists in Your Data

If your Excel/CSV file contains a "Quantity" column, the system will:
- ✅ Use the Quantity column directly as the actual quantity sold
- ✅ Support fractional values (0.25, 0.33, 0.50, 0.75, 0.80, etc.)
- ✅ Preserve decimal precision for accurate analytics
- ✅ Use quantity for all calculations (revenue, forecasting, etc.)

### When Quantity Column Does NOT Exist (Backward Compatible)

If your data doesn't have a Quantity column, the system will:
- ✅ Calculate quantity automatically from Units and Pieces
- ✅ Logic: If pieces > 0, use pieces; otherwise use units
- ✅ Existing files continue to work without changes

## Example Scenarios

### Scenario 1: Fractional Unit Sale
```
Units: 0
Pieces: 0
Quantity: 0.50
```
**Meaning**: Half a unit was sold (e.g., 1 piece from a 2-piece unit)

### Scenario 2: Fractional Unit Sale (80%)
```
Units: 0
Pieces: 0
Quantity: 0.80
```
**Meaning**: 0.8 of a unit was sold (e.g., 4 pieces from a 5-piece unit)

### Scenario 3: Full Unit Sale
```
Units: 1
Pieces: 10
Quantity: 1
```
**Meaning**: 1 complete unit sold (which happens to contain 10 pieces)

### Scenario 4: Multiple Pieces Sale
```
Units: 0
Pieces: 4
Quantity: 4
```
**Meaning**: 4 individual pieces sold (not a full unit)

### Scenario 5: Multiple Units
```
Units: 3
Pieces: 30
Quantity: 3
```
**Meaning**: 3 complete units sold

## Data File Format

### Excel/CSV with Quantity Column

```csv
Item Code,Item Name,Units,Pieces,Quantity,Selling Price,Total,Date
ITEM001,Paracetamol 500mg,0,0,0.50,12.50,6.25,2024-01-15
ITEM002,Vitamin D3,0,0,0.80,25.00,20.00,2024-01-15
ITEM003,Aspirin 100mg,1,10,1,8.50,8.50,2024-01-15
ITEM004,Amoxicillin,0,4,4,15.00,60.00,2024-01-15
ITEM005,Omeprazole,2,20,2,30.00,60.00,2024-01-15
```

## Configuration

The Quantity column has been added to the column mapping in `config.py`:

```python
COLUMN_MAPPING = {
    'Item Code': 'item_code',
    'Item Name': 'item_name',
    'Units': 'units',
    'Pieces': 'pieces',
    'Quantity': 'quantity',  # ← NEW
    'Selling Price': 'selling_price',
    'Total': 'total',
    # ... other columns
}
```

## Data Processing

The `_process_quantities()` method in `data_loader.py` handles this logic:

1. **Units** → Converted to integer
2. **Pieces** → Converted to integer  
3. **Quantity** → If column exists: kept as float (preserves decimals)
4. **Quantity** → If column missing: calculated from units/pieces

## Impact on Analytics

All analytics modules will use the `quantity` field for calculations:

- ✅ **Sales Analysis**: Revenue calculations use quantity
- ✅ **Product Analysis**: Fast/slow movers based on quantity sold
- ✅ **Refill Prediction**: Purchase patterns based on quantity
- ✅ **Cross-Sell Analysis**: Basket analysis uses quantity
- ✅ **RFM Analysis**: Customer value calculations use quantity

## Usage Examples

### Loading Data with Quantity Column

```python
from data_loader import DataLoader

loader = DataLoader('pharmacy_sales.xlsx')
loader.load_data()
df = loader.preprocess_data()

# The 'quantity' column is now available and contains fractional values
print(df[['item_name', 'units', 'pieces', 'quantity', 'total']].head())
```

### Sample Output
```
                    item_name  units  pieces  quantity    total
0       Paracetamol 500mg         0       0      0.50     6.25
1           Vitamin D3        0       0      0.80    20.00
2          Aspirin 100mg      1      10      1.00     8.50
3          Amoxicillin        0       4      4.00    60.00
4          Omeprazole         2      20      2.00    60.00
```

## Migration Guide

### If You're Adding Quantity Column to Existing Data

1. **Add the Quantity column** to your Excel/CSV file
2. **Populate it** with the actual quantity sold (can be fractional)
3. **Run the system** - it will automatically detect and use the Quantity column

### If You Don't Have Quantity Data Yet

No action needed! The system will continue to work as before, calculating quantity from units and pieces.

## Testing

To test with sample data that includes fractional quantities:

```python
from data_loader import load_sample_data

# Generate sample data with Quantity column
df = load_sample_data()

# Check for fractional quantities
fractional = df[df['Quantity'] < 1]
print(f"Found {len(fractional)} fractional sales:")
print(fractional[['Item Name', 'Units', 'Pieces', 'Quantity', 'Total']])
```

## Benefits

✅ **Accurate tracking** of partial unit sales  
✅ **Better inventory management** with precise quantity data  
✅ **Improved forecasting** based on actual quantities sold  
✅ **Flexible pricing** for products sold in fractions  
✅ **Backward compatible** with existing data files  

## Questions?

- **Q: What if I have both Quantity and Units/Pieces?**  
  A: The system will use Quantity as the authoritative source.

- **Q: Can Quantity be zero?**  
  A: Yes, zero values are handled correctly.

- **Q: What if Quantity column has empty values?**  
  A: Empty values are filled with 0 automatically.

- **Q: Does this affect my existing data files?**  
  A: No, files without Quantity column work exactly as before.

---

**Updated**: November 2025  
**Version**: 2.1

