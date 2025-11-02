# Quantity Column - Quick Reference Guide

## 📊 Understanding Units, Pieces, and Quantity

### Column Relationship

```
┌─────────────────────────────────────────────────────────────┐
│  UNITS     PIECES     QUANTITY                              │
│  (int)     (int)      (float - can be fractional)           │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Common Scenarios

### Scenario 1: Full Unit Sale
```
┌──────────────────────────────────────────────┐
│ Item: Paracetamol 500mg Box (10 tablets)    │
│ Customer buys: 1 complete box                │
├──────────────────────────────────────────────┤
│ Units:    1    (1 box)                       │
│ Pieces:   10   (10 tablets in the box)      │
│ Quantity: 1    (sold 1 unit)                 │
└──────────────────────────────────────────────┘
```

### Scenario 2: Fractional Sale (Half Unit)
```
┌──────────────────────────────────────────────┐
│ Item: Aspirin Blister (2 tablets per strip) │
│ Customer buys: 1 tablet (opened the strip)  │
├──────────────────────────────────────────────┤
│ Units:    0    (no complete unit)            │
│ Pieces:   0    (not measured in pieces)      │
│ Quantity: 0.50 (sold half a unit)            │
└──────────────────────────────────────────────┘
```

### Scenario 3: Fractional Sale (80% of Unit)
```
┌──────────────────────────────────────────────┐
│ Item: Vitamin D3 Strip (5 capsules)         │
│ Customer buys: 4 capsules from the strip    │
├──────────────────────────────────────────────┤
│ Units:    0    (no complete unit)            │
│ Pieces:   0    (not measured in pieces)      │
│ Quantity: 0.80 (sold 4/5 = 80% of unit)     │
└──────────────────────────────────────────────┘
```

### Scenario 4: Multiple Pieces Sale
```
┌──────────────────────────────────────────────┐
│ Item: Amoxicillin (sold individually)       │
│ Customer buys: 4 individual capsules         │
├──────────────────────────────────────────────┤
│ Units:    0    (no boxed unit)               │
│ Pieces:   4    (4 individual pieces)         │
│ Quantity: 4    (sold 4 pieces)               │
└──────────────────────────────────────────────┘
```

### Scenario 5: Multiple Full Units
```
┌──────────────────────────────────────────────┐
│ Item: Insulin Cartridge (3ml per cartridge) │
│ Customer buys: 3 complete cartridges         │
├──────────────────────────────────────────────┤
│ Units:    3    (3 cartridges)                │
│ Pieces:   0    (not measured in pieces)      │
│ Quantity: 3    (sold 3 units)                │
└──────────────────────────────────────────────┘
```

## 🎯 Decision Tree: Which Column to Use?

```
                    ┌─────────────────────┐
                    │  Is "Quantity"      │
                    │  column present     │
                    │  in your data?      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
            ┌───▼───┐                    ┌────▼────┐
            │  YES  │                    │   NO    │
            └───┬───┘                    └────┬────┘
                │                             │
        ┌───────▼────────┐         ┌──────────▼─────────┐
        │  Use Quantity  │         │  Auto-calculate:   │
        │  as-is         │         │  If Pieces > 0:    │
        │  (can be 0.50, │         │    quantity=pieces │
        │   0.80, etc.)  │         │  Else:             │
        │                │         │    quantity=units  │
        └────────────────┘         └────────────────────┘
```

## 📋 Excel File Examples

### With Quantity Column (Recommended for Fractional Sales)
```csv
Item Code,Item Name,Units,Pieces,Quantity,Price,Total
MED001,Paracetamol 500mg,1,10,1,12.50,12.50
MED002,Aspirin Blister,0,0,0.50,8.00,4.00
MED003,Vitamin D3 Strip,0,0,0.80,25.00,20.00
MED004,Amoxicillin,0,4,4,15.00,60.00
MED005,Insulin Cartridge,3,0,3,120.00,360.00
```

### Without Quantity Column (System Calculates)
```csv
Item Code,Item Name,Units,Pieces,Price,Total
MED001,Paracetamol 500mg,1,10,12.50,12.50
MED004,Amoxicillin,0,4,15.00,60.00
MED005,Insulin Cartridge,3,0,120.00,360.00
```
*Note: This format cannot represent fractional quantities like 0.50 or 0.80*

## 🔍 Data Validation Rules

| Column | Type | Required | Can be 0? | Can be Fractional? |
|--------|------|----------|-----------|-------------------|
| Units | Integer | Yes | Yes | **No** |
| Pieces | Integer | Yes | Yes | **No** |
| Quantity | Float | No* | Yes | **Yes** |

*Quantity column is optional - system calculates if missing

## 💡 Best Practices

### ✅ DO:
- Use Quantity column when selling fractional units
- Keep Units and Pieces as whole numbers (integers)
- Use common fractions: 0.25, 0.33, 0.50, 0.75, 0.80
- Ensure Quantity × Price = Total for accurate revenue tracking

### ❌ DON'T:
- Don't put fractional values in Units or Pieces columns
- Don't leave all three columns at zero
- Don't use arbitrary decimals (prefer standard fractions)
- Don't change column meanings mid-dataset

## 🚀 Implementation Checklist

- [x] System updated to support Quantity column
- [x] Backward compatibility maintained
- [x] Units and Pieces enforced as integers
- [x] Quantity supports fractional values (float)
- [x] All analytics modules updated
- [x] Sample data generator updated
- [x] Documentation created
- [x] Testing completed successfully

## 📞 Need Help?

**If you have Quantity column:** System will automatically use it  
**If you don't have Quantity column:** System calculates from Units/Pieces  
**Want to add Quantity column:** Just add it to your Excel - system auto-detects

---

**Status**: ✅ Ready to Use  
**Version**: 2.1  
**Last Updated**: November 2, 2025

