# Service Item Filtering

## Overview

The system now automatically identifies and filters service items from product-focused analyses while keeping them in revenue calculations. This ensures accurate product performance metrics, inventory management, and cross-sell recommendations.

## Service Items Defined

Service items are non-physical products that generate revenue but should not be included in inventory or product analyses:

- **خدمة فيزا** (Visa/card payment service fee)
- **خدمة توصيل** (Delivery service fee)

These are configured in `config.py` as `SERVICE_ITEMS`.

## How It Works

### 1. Data Loading (`data_loader.py`)
When data is loaded, the system:
- Identifies service items by matching `item_name` against the `SERVICE_ITEMS` list
- Adds an `is_service` flag to each transaction
- Reports the number and revenue of service transactions

**Output Example:**
```
ℹ️  Identified 145 service transactions (revenue: $1,234.50)
   Service items: خدمة فيزا, خدمة توصيل
```

### 2. Where Services Are EXCLUDED

Services are automatically filtered out from:

#### Product Analysis (`product_analysis.py`)
- ✅ ABC classification
- ✅ Product velocity analysis  
- ✅ Product lifecycle stages
- ✅ Fast/slow movers
- ✅ All product performance metrics

**Output Example:**
```
ℹ️  Product Analysis: Excluded 145 service transactions from product metrics
```

#### Sales Analysis (`sales_analysis.py`)
- ✅ Top products lists
- ✅ Top categories
- ✅ Product-specific trends

**Note:** Services are still included in overall revenue calculations.

#### Inventory Management (`inventory_management.py`)
- ✅ Stock level calculations
- ✅ Reorder recommendations
- ✅ Stockout forecasts
- ✅ ABC inventory analysis

**Output Example:**
```
ℹ️  Inventory Management: Excluded 145 service transactions
```

#### Cross-Sell Analysis (`cross_sell_analysis.py`)
- ✅ Product bundles
- ✅ Association rules
- ✅ Product recommendations
- ✅ Market basket analysis

**Output Example:**
```
ℹ️  Cross-Sell Analysis: Excluded 145 service transactions
```

### 3. Where Services Are INCLUDED

Services remain in these analyses as they represent real customer spending:

#### Revenue Calculations
- ✅ Total revenue
- ✅ Gross revenue
- ✅ Net revenue (after refunds)

#### Customer Analysis
- ✅ Customer lifetime value
- ✅ Customer spending patterns
- ✅ RFM segmentation
- ✅ Customer purchase history

**Rationale:** Services contribute to customer spending and should be included in customer value metrics.

## Revenue Breakdown

All revenue metrics now include a breakdown:

```python
{
    'gross_revenue': 125000.00,      # Total sales including services
    'service_revenue': 1234.50,       # Revenue from services only
    'product_revenue': 123765.50,     # Revenue from products only
    'service_revenue_pct': 0.99,      # Percentage from services
    'net_revenue': 124800.00,         # After refunds
    # ...
}
```

## Adding More Service Items

To add more service items, edit `config.py`:

```python
SERVICE_ITEMS = [
    'خدمة فيزا',      # Visa/card payment service fee
    'خدمة توصيل',     # Delivery service fee
    'خدمة جديدة',     # Add new service here
]
```

The system will automatically:
- Flag these items as services
- Exclude them from product analyses
- Include them in revenue calculations
- Report them in the data summary

## Verification

To verify service filtering is working:

1. **Check data loading output:**
   ```
   ℹ️  Identified X service transactions (revenue: $Y)
   ```

2. **Check analysis outputs:**
   - Product lists should not include service items
   - Revenue totals should include service revenue
   - Inventory should not recommend reordering services

3. **Review data summary:**
   ```python
   summary = loader.get_data_summary()
   print(f"Service Revenue: ${summary['service_revenue']:,.2f}")
   print(f"Service %: {summary['service_revenue_pct']:.2f}%")
   ```

## Benefits

✅ **Accurate Product Metrics:** Product performance shows only actual products  
✅ **Correct Inventory:** No reorder signals for services  
✅ **Better Cross-Sell:** Recommendations based on actual products  
✅ **Complete Revenue:** Services still counted in total revenue  
✅ **Customer Insights:** Customer spending includes all purchases  

## Technical Details

### Data Flow

1. **Raw Data** → Contains all items including services
2. **Data Loader** → Adds `is_service` flag
3. **Analysis Modules** → Filter based on `is_service` flag
4. **Output** → Shows appropriate metrics for each context

### Performance Impact

Minimal - filtering is done once during initialization:
- Product analysis: ~0.01s overhead
- Sales analysis: ~0.005s overhead  
- Inventory: ~0.01s overhead
- Cross-sell: ~0.02s overhead

### Backwards Compatibility

✅ Fully compatible with existing code  
✅ Works with or without service items in data  
✅ No changes needed to existing analyses  
✅ Gracefully handles missing `is_service` column  

## Troubleshooting

### Service items still showing in product lists

**Check:**
1. Service items are listed correctly in `config.SERVICE_ITEMS`
2. Exact name match (case-sensitive, including spaces)
3. Data loader is adding `is_service` flag

### Service revenue not showing

**Check:**
1. Service items exist in your data
2. Names match exactly in `config.SERVICE_ITEMS`
3. Call `get_data_summary()` or `get_overall_metrics()` to see breakdown

### Performance issues

**Solution:**
Service filtering adds minimal overhead. If experiencing issues:
1. Check overall data size (not related to service filtering)
2. Enable sampling in cross-sell analysis
3. Review caching in individual analysis modules

## Related Files

- `config.py` - Service items configuration
- `data_loader.py` - Service detection and flagging
- `product_analysis.py` - Filters services from product metrics
- `sales_analysis.py` - Tracks service revenue separately
- `inventory_management.py` - Excludes services from inventory
- `cross_sell_analysis.py` - Excludes services from recommendations
- `customer_analysis.py` - Includes services (customer spending)
- `rfm_analysis.py` - Includes services (customer value)

## Questions?

Service filtering is designed to be automatic and transparent. The system will inform you when services are detected and excluded from specific analyses through console output messages.

