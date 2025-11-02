# Inventory Management & Reorder Signals 📦

## Overview

The Inventory Management module provides intelligent reorder recommendations based on your actual sales velocity. It helps you:
- 🎯 Know exactly when to reorder items
- ⚠️ Get alerts for urgent stockouts
- 📊 Optimize inventory levels
- 💰 Reduce lost sales from stockouts
- 📈 Identify slow-moving and overstocked items

## Features

### 1. **Reorder Signal System**
- **OUT_OF_STOCK**: Items with zero inventory
- **URGENT_REORDER**: Items will run out within 3 days (configurable)
- **REORDER_SOON**: Items below reorder point but not yet urgent
- **MONITOR**: Items approaching reorder point
- **OK**: Items with adequate stock

### 2. **Intelligent Calculations**
- **Sales Velocity**: Calculates daily, weekly, and monthly sales rates
- **Reorder Point**: Based on lead time and safety stock
- **Safety Stock**: Adjusted based on sales consistency
- **Optimal Order Quantity**: Recommends economic order quantities
- **Days of Stock**: Shows how long current stock will last

### 3. **Risk Analysis**
- **Stockout Risk**: Predicts which items will run out in next 30 days
- **Potential Lost Revenue**: Estimates revenue loss from stockouts
- **Overstock Detection**: Identifies slow-moving items with excess inventory

### 4. **ABC Analysis**
- **A Items**: Top 20% products generating ~80% revenue
- **B Items**: Next 30% products generating ~15% revenue
- **C Items**: Remaining 50% products generating ~5% revenue

### 5. **Category Insights**
- Stock levels by category
- Inventory turnover rates
- Sales performance by category

## Quick Start

### Method 1: Upload Your Inventory File

1. **Prepare your inventory file** (Excel or CSV) with these columns:
   ```
   Item Code | Item Name | Selling Price | Units | Pieces | Quantity | Category
   ```

2. **Upload the file** in the Inventory Management page
3. **Adjust settings** in the sidebar:
   - Lead Time: Days between ordering and receiving stock
   - Urgency Threshold: Days before stockout to trigger urgent alert

4. **Review the dashboard**:
   - Check reorder alerts
   - Review stockout risks
   - Identify overstocked items
   - Analyze ABC classification

### Method 2: Use Sample Inventory

1. Click "Use Sample Inventory" button
2. System generates sample inventory based on your sales data
3. Review and adjust as needed

## File Format

### Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| **Item Code** | Unique product identifier | ITEM001 |
| **Item Name** | Product name | Paracetamol 500mg |
| **Quantity** | **Current stock quantity (AUTHORITATIVE)** | 1.50 |

### Optional Columns (Recommended)

| Column | Description | Example |
|--------|-------------|---------|
| **Selling Price** | Unit selling price | 10.50 |
| **Units** | Number of full units/boxes (informational) | 1 |
| **Pieces** | Number of loose pieces (informational) | 1 |
| **Category** | Product category | Pain Relief |

### 📦 Understanding Units, Pieces, and Quantity

**CRITICAL:** The system uses **Quantity** as the authoritative stock level!

- **Units** = Full units/boxes in stock (integer) - informational only
- **Pieces** = Loose pieces in stock (integer) - informational only  
- **Quantity** = Total effective quantity (can be fractional) ← **USED FOR ALL CALCULATIONS**

**Examples:**
1. **Units=1, Pieces=1, Quantity=1.50**
   - You have 1 full box + 1 loose piece
   - Total stock = 1.50 units (this is what the system uses)

2. **Units=0, Pieces=1, Quantity=0.50**
   - You have 0 full boxes + 1 loose piece
   - Total stock = 0.50 units (this is what the system uses)

💡 **Recommendation:** Focus on filling the **Quantity** column accurately. Units and Pieces are optional display fields.

### Example File Structure

```csv
Item Code,Item Name,Selling Price,Units,Pieces,Quantity,Category
ITEM001,Paracetamol 500mg,10.50,1,1,1.50,Pain Relief
ITEM002,Amoxicillin 250mg,25.00,0,1,0.50,Antibiotics
ITEM003,Vitamin D3,15.75,3,0,3.00,Vitamins
ITEM004,Omeprazole 20mg,18.25,2,1,2.50,Digestive
ITEM005,Aspirin 100mg,8.50,10,0,10.00,Pain Relief
```

**Note:** In the examples above:
- ITEM001: 1 full unit + 1 piece = Quantity 1.50
- ITEM002: 0 units + 1 piece = Quantity 0.50 (half unit)
- ITEM003: 3 full units = Quantity 3.00
- ITEM004: 2 full units + 1 piece = Quantity 2.50
- ITEM005: 10 full units = Quantity 10.00

## Understanding the Calculations

### 1. Sales Velocity
```
Daily Sales Velocity = Total Quantity Sold / Days on Sale
Weekly Sales Velocity = Daily Velocity × 7
Monthly Sales Velocity = Daily Velocity × 30
```

### 2. Reorder Point
```
Reorder Point = (Lead Time × Daily Velocity) + Safety Stock
```

Where:
- **Lead Time**: Days between placing order and receiving stock (default: 7 days)
- **Safety Stock**: Buffer to prevent stockouts (default: 1.5× lead time demand)

### 3. Safety Stock
```
Safety Stock = Lead Time Demand × Safety Factor × (1 - Consistency × 0.5)
```

- Higher safety stock for inconsistent sales
- Lower safety stock for regular, predictable sales

### 4. Days of Stock
```
Days of Stock = Current Quantity / Daily Sales Velocity
```

### 5. Optimal Order Quantity
```
Optimal Order Quantity = max(Monthly Sales Velocity, 10)
```

## Dashboard Sections

### 1. Inventory Overview
- Total items and inventory value
- Out of stock and urgent reorder counts
- Average days of stock
- Fast movers vs slow movers

### 2. Reorder Alerts Tab
- Visual signal distribution
- Top items needing reorder
- Filterable reorder recommendations
- Downloadable reorder list

### 3. Stockout Risk Tab
- Timeline of predicted stockouts
- Estimated stockout dates
- Potential revenue loss
- Items at risk in next 30 days

### 4. Overstocked Items Tab
- Items with >180 days of stock
- Overstock value analysis
- Slow-moving inventory identification

### 5. ABC Analysis Tab
- Revenue-based classification
- ABC distribution charts
- Item-level ABC details

### 6. Category Analysis Tab
- Stock on hand by category
- Inventory turnover rates
- Sales performance metrics

## Configuration Settings

Edit `config.py` to adjust default settings:

```python
# Inventory management settings
LEAD_TIME_DAYS = 7  # Default lead time for reordering
SAFETY_STOCK_FACTOR = 1.5  # Safety stock multiplier
URGENCY_THRESHOLD_DAYS = 3  # Days threshold for urgent reorders
OVERSTOCK_THRESHOLD_DAYS = 180  # Days of stock to consider overstock
STOCKOUT_FORECAST_DAYS = 30  # Days to forecast stockout risk
```

## Best Practices

### 1. Regular Updates
- Update inventory file weekly or daily
- Keep sales data current
- Review reorder recommendations regularly

### 2. Lead Time Accuracy
- Set realistic lead times for suppliers
- Consider supplier reliability
- Account for shipping delays

### 3. Safety Stock
- Increase for high-demand items
- Increase for items with variable sales
- Decrease for slow-moving items

### 4. Focus Areas
- **Priority 1**: OUT_OF_STOCK items - order immediately
- **Priority 2**: URGENT_REORDER - order within days
- **Priority 3**: REORDER_SOON - order within 1-2 weeks
- **Priority 4**: MONITOR - watch closely
- **Review**: Overstocked items - consider promotions

### 5. ABC Management
- **A Items**: Monitor closely, never stock out
- **B Items**: Regular monitoring, moderate safety stock
- **C Items**: Review less frequently, minimal safety stock

## Integration with Sales Data

The system automatically:
- Matches inventory items with sales records using Item Code
- Calculates real sales velocity from actual transactions
- Considers sales trends and seasonality
- Adjusts for refunds and returns
- Accounts for sales consistency

## Troubleshooting

### Issue: Items showing as "OK" but you know they're running low
**Solution**: Reduce lead time or increase safety stock factor

### Issue: Too many URGENT alerts
**Solution**: Increase urgency threshold days or review lead time settings

### Issue: No sales history for some items
**Solution**: New items will show in "No Sales History" - manually set reorder points

### Issue: Overstock alerts for new products
**Solution**: Normal for new items - system will adjust as sales history builds

### Issue: Item codes don't match between inventory and sales
**Solution**: Ensure Item Code column matches exactly between files

## Testing

Run the test script to verify functionality:

```bash
python test_inventory.py
```

This will:
1. Load your sales data
2. Generate sample inventory
3. Run all inventory analyses
4. Save results to `output/inventory/`

## Output Files

The system generates several CSV files in `output/inventory/`:
- `reorder_signals.csv` - Complete reorder analysis
- `stockout_risk.csv` - Stockout predictions
- `abc_analysis.csv` - ABC classification
- `category_analysis.csv` - Category-level metrics
- `sample_inventory.xlsx` - Sample inventory template

## Tips for Success

### 1. Start Simple
- Begin with sample inventory to understand the system
- Upload your actual inventory file
- Review and adjust settings

### 2. Validate Results
- Compare recommendations with your experience
- Adjust lead time and safety stock as needed
- Monitor accuracy over time

### 3. Take Action
- Download reorder lists weekly
- Use priority scores to focus efforts
- Track results and refine settings

### 4. Prevent Stockouts
- Set up regular review schedule
- Act on URGENT alerts immediately
- Plan ahead with 30-day forecast

### 5. Optimize Inventory
- Review overstocked items monthly
- Consider promotions for slow movers
- Use ABC analysis for focus areas

## Formula Reference Card

| Metric | Formula | Purpose |
|--------|---------|---------|
| Daily Velocity | Total Sold / Days | Sales rate |
| Reorder Point | (Lead Time × Velocity) + Safety Stock | When to order |
| Safety Stock | Lead Demand × Factor × (1 - Consistency × 0.5) | Buffer stock |
| Days of Stock | Current Stock / Daily Velocity | How long stock lasts |
| Optimal Order Qty | max(Monthly Velocity, 10) | How much to order |
| Stockout Date | Today + (Stock / Velocity) | When you'll run out |

## Support

For questions or issues:
1. Check this guide first
2. Run test script to verify setup
3. Review configuration settings
4. Check file format and column names

## Next Steps

1. ✅ Prepare your inventory file
2. ✅ Upload to Inventory Management page
3. ✅ Review reorder recommendations
4. ✅ Download and place orders
5. ✅ Update inventory weekly
6. ✅ Track and refine over time

---

**Happy Inventory Management!** 📦✨

