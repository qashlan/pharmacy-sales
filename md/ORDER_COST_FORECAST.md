# Order Cost & Revenue Forecasting Feature

## What Was Added

You can now see **how much each predicted refill order will cost** across all refill prediction views!

## New Columns Added

### In All Refill Views (Overdue, Upcoming, Customer Schedule):

| Column | Description | Example |
|--------|-------------|---------|
| **predicted_order_value** | Total predicted cost of the order | $245.50 |
| **predicted_unit_price** | Predicted price per unit | $12.28 |
| **predicted_quantity** | Predicted quantity customer will order | 20 units |
| **avg_price_per_unit** | Historical average price | $11.95 |
| **total_lifetime_value** | Total customer has spent on this product | $1,234.56 |

## How It Works

### Price Forecasting
The system uses **linear regression** on historical purchase prices to predict future prices:

```
Example:
- Previous prices: $10.00, $10.50, $11.00, $11.50
- Trend: +$0.50 per purchase
- Predicted next price: $12.00
```

### Quantity Forecasting
Similarly, the system tracks quantity trends:

```
Example:
- Previous quantities: 15, 18, 20, 22
- Trend: +2 units per purchase
- Predicted next quantity: 24 units
```

### Order Value Calculation
```
Predicted Order Value = Predicted Unit Price × Predicted Quantity

Example:
$12.00 × 24 units = $288.00
```

## Enhanced Upcoming Refills Tab

### New Revenue Forecast Metrics

When you open the **Upcoming Refills** tab, you'll now see 4 key metrics:

```
┌────────────────────┬──────────────────────┬─────────────────────┬─────────────────────┐
│ Expected Refills   │ Total Predicted      │ Avg Order Value     │ High Confidence     │
│                    │ Revenue              │                     │ Revenue             │
├────────────────────┼──────────────────────┼─────────────────────┼─────────────────────┤
│ 45 refills         │ $12,345.67           │ $274.35             │ $8,234.50          │
└────────────────────┴──────────────────────┴─────────────────────┴─────────────────────┘
```

**What Each Metric Means:**

1. **Expected Refills** - Total number of refills predicted in the time period
2. **Total Predicted Revenue** - Sum of all predicted order values
3. **Avg Order Value** - Average predicted order value
4. **High Confidence Revenue** - Revenue from predictions with 70+ confidence score (more reliable)

## Enhanced Hover Data

When you hover over points in the scatter plot, you'll now see:
- Average interval days
- First order date
- Days since first order
- **Predicted order value** 💰
- **Predicted quantity** 📦

## Business Use Cases

### 1. Revenue Forecasting
```
Use Case: Plan next month's expected revenue
Action: Set "Look ahead" to 30 days
Result: See total predicted revenue for next 30 days
```

### 2. Inventory Planning
```
Use Case: Know what quantities to stock
Action: Review predicted_quantity column
Result: See how much of each product will be ordered
```

### 3. Cash Flow Management
```
Use Case: Understand payment timings
Action: Sort by predicted_next_purchase date
Result: See when money will come in
```

### 4. Customer Value Analysis
```
Use Case: Identify high-value upcoming orders
Action: Sort by predicted_order_value
Result: Prioritize high-value customers
```

### 5. Price Change Impact
```
Use Case: See if price increases are affecting customers
Action: Compare predicted_unit_price vs avg_price_per_unit
Result: Spot price trend changes
```

## What You Can Do Now

### In Upcoming Refills Tab:

1. **See Total Revenue**
   - Know how much revenue to expect in the next X days
   - Separate view of "high confidence" revenue (more reliable)

2. **Sort by Value**
   - Click on `predicted_order_value` column header
   - Identify highest-value upcoming orders
   - Prioritize high-value customer outreach

3. **Plan Inventory**
   - Review `predicted_quantity` for each product
   - Stock appropriate amounts
   - Avoid stockouts or overstocking

4. **Analyze Trends**
   - Compare `predicted_unit_price` vs `avg_price_per_unit`
   - See if prices are trending up or down
   - Adjust pricing strategy accordingly

### In Overdue Refills Tab:

1. **See Revenue at Risk**
   - View `predicted_order_value` for overdue customers
   - Understand lost revenue impact
   - Prioritize recovery by value

2. **Calculate Opportunity Cost**
   - Sort by `total_lifetime_value`
   - See which lost customers were most valuable
   - Focus recovery efforts on high-value customers

### In Customer Schedule Tab:

1. **Customer Revenue Projection**
   - See all upcoming orders for a customer
   - Calculate customer's future value
   - Identify high-value customer relationships

## Example Insights

### Revenue Forecasting Example:
```
Upcoming 30 Days:
- 45 expected refills
- $12,345.67 total predicted revenue
- $8,234.50 from high-confidence predictions (70+ score)

Insight: Can reliably expect $8,234 in revenue
Action: Plan expenses and inventory accordingly
```

### High-Value Customer Example:
```
Dr. Mona Nawar:
- COBAL 500: $289.50 predicted (65.56% confidence)
- PRONTOGEST: $567.89 predicted (39.90% confidence)
- VIDROP: $145.23 predicted (72.96% confidence)

Total upcoming value: $1,002.62

Insight: High-value customer with mixed confidence
Action: Personal follow-up to ensure orders happen
```

### Overdue Revenue at Risk Example:
```
Likely Lost Customers (6+ months):
- 15 customers
- $3,456.78 in predicted order value at risk
- $25,678.90 in lifetime value lost

Insight: $3,456 in immediate revenue loss
Action: Win-back campaign for high-value ones
```

## Data Columns Explained

### predicted_order_value
**What it is:** Total predicted cost of the next order
**How it's calculated:** `predicted_unit_price × predicted_quantity`
**Use it for:** Revenue forecasting, prioritization, cash flow planning

### predicted_unit_price
**What it is:** Forecasted price per unit based on historical trend
**How it's calculated:** Linear regression on past prices
**Use it for:** Price trend analysis, margin planning

### predicted_quantity
**What it is:** Forecasted quantity customer will order
**How it's calculated:** Linear regression on past quantities, adjusted by trends
**Use it for:** Inventory planning, demand forecasting

### avg_price_per_unit
**What it is:** Historical average price paid
**How it's calculated:** Mean of all past purchase prices
**Use it for:** Comparing predicted vs historical prices

### total_lifetime_value
**What it is:** Total amount customer has spent on this product
**How it's calculated:** Sum of all past orders
**Use it for:** Customer value assessment, prioritization

## Accuracy Considerations

### High Accuracy Scenarios:
✅ Customers with stable purchase quantities
✅ Products with consistent pricing
✅ Regular purchase patterns (high confidence score)
✅ Multiple historical purchases (5+)

### Lower Accuracy Scenarios:
⚠️ Customers with erratic quantities
⚠️ Products with volatile pricing
⚠️ Irregular purchase patterns (low confidence score)
⚠️ Limited purchase history (2-3 only)

**Pro Tip:** Focus on high confidence predictions (70+) for more reliable revenue forecasting.

## Using the Data for Business Decisions

### Weekly Planning:
```python
1. Check "Upcoming Refills" (7 days)
2. Note "Total Predicted Revenue"
3. Identify high-value orders (sort by predicted_order_value)
4. Ensure stock availability for these items
5. Pre-prepare high-value orders
```

### Monthly Forecasting:
```python
1. Set "Look ahead" to 30 days
2. Record "Total Predicted Revenue"
3. Note "High Confidence Revenue" (more reliable)
4. Plan expenses based on high confidence number
5. Prepare for best-case total revenue number
```

### Customer Prioritization:
```python
1. Sort by predicted_order_value (descending)
2. Top customers = highest predicted value
3. Review their confidence scores
4. Personal outreach for high-value + high-confidence
5. Extra follow-up for high-value + low-confidence
```

### Inventory Management:
```python
1. Export predicted_quantity column
2. Group by item_name
3. Sum quantities by product
4. Add safety stock (20-30%)
5. Place orders with suppliers
```

## After Restart

Once you restart the dashboard, you'll see:

### ✅ Upcoming Refills Tab:
- 4 new revenue forecast metrics at the top
- `predicted_order_value`, `predicted_unit_price`, `predicted_quantity` columns
- Enhanced hover data with cost information
- Sortable by any column (click header)

### ✅ Overdue Refills Tab:
- Same cost columns showing revenue at risk
- Sort by value to prioritize recovery
- See lifetime value to understand customer importance

### ✅ Customer Schedule Tab:
- Per-customer revenue projections
- See all upcoming orders and their values
- Calculate customer future value

## Quick Start After Restart

```bash
# Restart command
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales && \
pkill -f streamlit && \
./clear_cache.sh && \
source venv/bin/activate && \
streamlit run dashboard.py
```

Then:
1. Go to **Refill Prediction** section
2. Click **Upcoming Refills** tab
3. See the 4 revenue metrics at the top 🎉
4. Scroll down to see cost columns in the table 💰
5. Sort by `predicted_order_value` to see highest-value orders first 📊

## Summary

### What You Can Now See:
✅ Predicted cost of each refill order
✅ Total expected revenue (by time period)
✅ Average order value
✅ High-confidence revenue (more reliable)
✅ Predicted quantities (for inventory planning)
✅ Price trends (increasing/decreasing/stable)
✅ Customer lifetime value (for prioritization)

### What You Can Now Do:
✅ Forecast monthly revenue accurately
✅ Plan inventory based on predicted quantities
✅ Prioritize customers by order value
✅ Identify high-value at-risk revenue
✅ Make data-driven cash flow decisions
✅ Optimize pricing based on trends
✅ Allocate resources to high-value orders

**Your refill predictions now include complete financial forecasting!** 💰📊

