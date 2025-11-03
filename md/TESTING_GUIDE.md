# Testing Guide for Advanced Refill Predictions

## Quick Start Testing

### 1. Start the Dashboard
```bash
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales
source venv/bin/activate
streamlit run dashboard.py
```

### 2. Navigate to Refill Prediction
- Open the dashboard in your browser
- Click on "💊 Refill Prediction" in the sidebar menu

### 3. Verify New Features

#### Check Description
- At the top of the page, you should see the enhanced description mentioning:
  - "Advanced 7-factor confidence scoring"
  - "Customer relationship age tracking"

#### Test Overdue Refills Tab
1. Click the "⚠️ Overdue Refills" tab
2. Verify the dataframe includes these new columns:
   - `first_order_date`
   - `days_since_first_order`
3. Check that dates are properly formatted
4. Verify confidence scores are between 0-100

#### Test Upcoming Refills Tab
1. Click the "📅 Upcoming Refills" tab
2. Hover over points in the scatter plot
3. Verify hover data shows:
   - `avg_interval_days`
   - `first_order_date`
   - `days_since_first_order`
4. Check the dataframe has the new columns

#### Test Customer Schedule Tab
1. Click the "👤 Customer Schedule" tab
2. Select a customer from the dropdown
3. Verify the schedule shows:
   - `first_order_date`
   - `days_since_first_order`

#### Test Price Predictions Tab
1. Click the "💰 Price Predictions" tab
2. Scroll to "Top 20 Predicted Order Values"
3. Verify the table includes:
   - `first_order_date`
   - `days_since_first_order`

## Confidence Score Testing

### Expected Behavior:
- **New customers** (< 30 days): Lower confidence (relationship age factor pulls score down)
- **Established customers** (90+ days): Higher confidence if patterns are stable
- **Irregular patterns**: Lower confidence (trend stability and gap analysis reduce score)
- **Regular patterns**: Higher confidence (all factors contribute positively)

### Test Cases:

1. **Perfect Customer**
   - Long relationship (365+ days)
   - Consistent intervals
   - Stable quantities
   - Regular purchases
   - Expected: 85-95 confidence score

2. **New Customer**
   - First order < 30 days ago
   - Only 2-3 purchases
   - Expected: 40-60 confidence score

3. **Irregular Customer**
   - Long gaps between purchases
   - Varying quantities
   - Recent anomalies
   - Expected: 30-50 confidence score

4. **Seasonal Customer**
   - Purchases in same months annually
   - Consistent seasonal pattern
   - Expected: Moderate-high confidence (60-80)

## Data Validation

### Check First Order Dates
```python
# In Python console or notebook
from data_loader import load_data
from refill_prediction import RefillPredictor

data = load_data('pharmacy_sales.xlsx')
predictor = RefillPredictor(data)
intervals = predictor.calculate_purchase_intervals()

# Verify first_order_date is always <= last_purchase_date
assert all(intervals['first_order_date'] <= intervals['last_purchase_date'])

# Verify days_since_first_order is calculated correctly
test_row = intervals.iloc[0]
expected_days = (predictor.current_date - test_row['first_order_date']).days
assert test_row['days_since_first_order'] == expected_days

print("✓ Data validation passed!")
```

### Check Confidence Scores
```python
# Confidence scores should be 0-100
assert all(intervals['confidence_score'] >= 0)
assert all(intervals['confidence_score'] <= 100)

# Check distribution
print(f"Min confidence: {intervals['confidence_score'].min():.1f}")
print(f"Max confidence: {intervals['confidence_score'].max():.1f}")
print(f"Mean confidence: {intervals['confidence_score'].mean():.1f}")
print(f"Median confidence: {intervals['confidence_score'].median():.1f}")

# High confidence predictions (should have multiple)
high_conf = intervals[intervals['confidence_score'] >= 70]
print(f"High confidence predictions: {len(high_conf)}")
```

## Language Testing

### English Interface
1. Set language to English in sidebar
2. Verify all new fields display in English:
   - "First Order Date"
   - "Days Since First Order"
   - "Customer Relationship Age"

### Arabic Interface (RTL)
1. Set language to Arabic (العربية) in sidebar
2. Verify RTL layout works correctly
3. Check translations appear:
   - "تاريخ الطلب الأول"
   - "أيام منذ الطلب الأول"
   - "عمر علاقة العميل"

## Performance Testing

### Large Dataset Test
```python
import time

# Time the calculation
start = time.time()
predictor = RefillPredictor(data)
intervals = predictor.calculate_purchase_intervals()
elapsed = time.time() - start

print(f"Calculation time: {elapsed:.2f} seconds")
print(f"Rows processed: {len(intervals)}")
print(f"Time per row: {elapsed/len(intervals)*1000:.2f} ms")

# Should complete in reasonable time (< 5 seconds for 1000 rows)
```

### Caching Test
```python
# First call (calculates)
start = time.time()
intervals1 = predictor.calculate_purchase_intervals()
time1 = time.time() - start

# Second call (cached)
start = time.time()
intervals2 = predictor.calculate_purchase_intervals()
time2 = time.time() - start

print(f"First call: {time1:.3f}s")
print(f"Second call: {time2:.3f}s (cached)")
print(f"Speedup: {time1/time2:.1f}x")

# Cached call should be much faster
assert time2 < time1 / 10  # At least 10x faster
```

## Common Issues & Solutions

### Issue: Confidence scores all very low
**Solution**: Check data quality - may need more purchases per customer-product pair

### Issue: First order date showing as NaT
**Solution**: Verify date column is properly formatted in source data

### Issue: Scatter plot not showing hover data
**Solution**: Check that columns exist in dataframe before plotting

### Issue: Arabic text not displaying correctly
**Solution**: Verify browser and system support Arabic fonts

## Sign-off Checklist

- [ ] Dashboard loads without errors
- [ ] All 4 tabs in refill prediction work
- [ ] New columns visible in all dataframes
- [ ] Confidence scores in valid range (0-100)
- [ ] First order dates <= last purchase dates
- [ ] days_since_first_order calculated correctly
- [ ] Hover data shows in scatter plot
- [ ] English translations present
- [ ] Arabic translations present
- [ ] Performance acceptable (< 5s for typical dataset)
- [ ] No linting errors (except environment warnings)

## Success Criteria

✅ **Implementation Successful If:**
1. All new columns display correctly
2. Confidence scores show meaningful variation
3. First order tracking provides valuable insights
4. Dashboard performance remains good
5. Both languages work properly
6. Data validation passes all checks

## Next Steps After Testing

1. Monitor confidence score distribution over time
2. Collect feedback on prediction accuracy
3. A/B test confidence thresholds for campaigns
4. Consider adding confidence score explanation tooltips
5. Document any edge cases discovered during testing

