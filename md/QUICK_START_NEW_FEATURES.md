# Quick Start: New Features

## What Changed?

Your pharmacy sales system now supports:

### 1. ✅ Receipt Column (Order IDs from Excel)
- Add a "Receipt" column to your Excel file
- The system will use it directly as order_id
- No more automatic order ID computation needed

### 2. ✅ Optional Customer Names
- Customer column can be **empty or null**
- Empty customers = "Unknown Customer"
- All analytics still work perfectly

## Excel File Format

### Required Columns
- **Receipt** (new!) - Your order/receipt ID
- **Item Code** - Product code
- **Item Name** - Product name  
- **Date** - Sale date
- **Total** - Sale amount

### Optional Columns
- **Customer Name** - Can be empty!
- Time, Units, Pieces, Selling Price, Sale Type, Category

### Example

```csv
Receipt,Item Code,Item Name,Customer Name,Date,Total
1001,ITEM001,Paracetamol,John Doe,2024-01-15,25.50
1001,ITEM002,Vitamin D3,John Doe,2024-01-15,35.00
1002,ITEM001,Paracetamol,,2024-01-15,12.75
1003,ITEM003,Aspirin,Jane Smith,2024-01-15,8.50
```

**Note:** Receipt 1002 has an empty customer - this is OK!

## What Happens Behind the Scenes?

### When You Upload Your Excel:

1. **Receipt Column Detection**
   - ✓ Has "Receipt" column → Uses it as order_id
   - ✗ No "Receipt" column → Computes order_id (old way)

2. **Customer Name Processing**
   - Empty/null customer → "Unknown Customer"
   - All other customers → Keep as-is

3. **Analytics**
   - Everything works normally
   - "Unknown Customer" treated like any other customer
   - Can track purchases, trends, etc.

## Backward Compatibility

**Old Excel files still work!**
- No "Receipt" column? System computes order IDs automatically
- All customer names filled? Nothing changes
- Your existing files work without modification

## Test It

```bash
# Optional: Run tests to verify everything works
python test_new_features.py
```

Or just upload your Excel file - it will work! 🎉

## Files Changed

1. **config.py** - Added Receipt column mapping
2. **data_loader.py** - New logic for receipts & unknown customers
3. **RECEIPT_AND_UNKNOWN_CUSTOMER_UPDATE.md** - Full documentation

## Need Help?

- See `RECEIPT_AND_UNKNOWN_CUSTOMER_UPDATE.md` for detailed documentation
- Run `python test_new_features.py` to verify setup
- Upload your file and check for any errors

## Summary

✅ Add "Receipt" column to Excel  
✅ Leave customer names empty if unknown  
✅ Upload and use normally  
✅ Everything else works the same!

