# Lost Customer Detection & Business Logic

## Business Rule Implemented

**Key Insight:** Customers who are overdue by 6+ months are **highly unlikely** to return without intervention.

## Overview

Based on your business knowledge, we've implemented a sophisticated customer status classification system that automatically identifies and prioritizes customers at risk of being lost forever.

## Customer Status Classification

### 4-Tier Status System

| Status | Overdue Period | Color | Confidence Adjustment | Action Priority |
|--------|---------------|-------|----------------------|-----------------|
| **🔴 Likely Lost** | 6+ months (180+ days) | Red | Max 20% confidence | **URGENT - Win-back campaign** |
| **🟠 At High Risk** | 3-6 months (90-179 days) | Orange | 40% of original | **HIGH - Immediate outreach** |
| **🟡 At Risk** | 1-3 months (30-89 days) | Yellow | 60-80% of original | **MEDIUM - Proactive contact** |
| **🟢 Action Needed** | <1 month (<30 days) | Green | 90% of original | **LOW - Standard reminder** |

## How It Works

### 1. Automatic Status Assignment

When a customer is overdue for a refill, the system automatically:

1. **Calculates days overdue** = Current date - Predicted purchase date
2. **Assigns status** based on the table above
3. **Adjusts confidence score** downward (older = less likely to return)
4. **Calculates churn probability** = 100 - Adjusted Confidence

### 2. Confidence Score Adjustment Logic

```python
Original Confidence → Adjusted Based on Overdue Duration

Example:
- Customer had 85% confidence for next purchase
- Now 7 months overdue (210 days)
- Status: "Likely Lost"  
- Adjusted Confidence: 85% × 0.2 = 17% (max 20%)
- Churn Probability: 100 - 17 = 83%
```

### 3. Priority Ranking

Customers are automatically sorted by:
1. **Status** (Likely Lost first)
2. **Lifetime Value** (high-value customers prioritized within each status)
3. **Days Overdue** (most overdue first)

## New Features in Dashboard

### Enhanced Overdue Tab

#### 1. Status Breakdown Metrics
```
🔴 Likely Lost (6+ mo)     | 15 customers
🟠 At High Risk (3-6 mo)   | 8 customers  
🟡 At Risk (1-3 mo)        | 12 customers
🟢 Action Needed (<1 mo)   | 23 customers
```

#### 2. Likely Lost Customer Section
- Dedicated section for 6+ month overdue customers
- Sorted by lifetime value (prioritize high-value recoveries)
- Recommended action items
- Business insights

#### 3. Color-Coded Visualization
- Bar chart colored by customer status
- Easy visual identification of critical cases
- Hover data shows all details

#### 4. New Data Columns
- `customer_status` - Classification (Likely Lost, At High Risk, etc.)
- `adjusted_confidence` - Confidence adjusted for overdue period
- `churn_probability` - Likelihood customer won't return (%)

## Business Impact

### Before This Update:
❌ All overdue customers treated equally
❌ No distinction between 1 month vs 6 months overdue
❌ Same confidence score regardless of how late
❌ No prioritization guidance

### After This Update:
✅ 4-tier classification system
✅ Clear identification of lost customers
✅ Confidence scores reflect reality
✅ Automatic prioritization by status and value
✅ Actionable recommendations for each tier

## Recommended Actions by Status

### 🔴 Likely Lost (6+ Months)
**Probability of Return: Very Low (< 20%)**

**Actions:**
1. **📞 Personal Call** - Direct phone contact from manager
2. **💌 Win-Back Campaign** - Special offer email series
3. **🎁 Significant Incentive** - 20-30% discount or free shipping
4. **❓ Exit Survey** - Understand why they left
5. **🔍 Competitive Analysis** - Check if they went to competitors

**Expected ROI:** Low success rate, but high-value customers worth the effort

---

### 🟠 At High Risk (3-6 Months)
**Probability of Return: Low (30-40%)**

**Actions:**
1. **📧 Urgent Email** - "We miss you" message
2. **🎯 Targeted Offer** - 15-20% discount
3. **📱 SMS Reminder** - Quick text message
4. **🆕 Product Updates** - Show new items they might like
5. **⭐ Loyalty Reminder** - Point balance or rewards available

**Expected ROI:** Medium success rate with proper incentives

---

### 🟡 At Risk (1-3 Months)
**Probability of Return: Moderate (40-60%)**

**Actions:**
1. **📧 Reminder Email** - Gentle nudge
2. **🎁 Small Incentive** - 10% discount or free sample
3. **💊 Health Reminder** - Importance of continuity
4. **📦 Easy Reorder** - One-click purchase link
5. **⏰ Automated Follow-up** - Series of reminders

**Expected ROI:** Good success rate with light touch

---

### 🟢 Action Needed (<1 Month)
**Probability of Return: Good (60-90%)**

**Actions:**
1. **📧 Standard Reminder** - "Time to reorder"
2. **📱 SMS Notification** - Brief reminder
3. **🔔 App Push Notification** - If applicable
4. **📦 Cart Pre-fill** - Make reordering easy
5. **✅ Confirmation** - Once they place order

**Expected ROI:** High success rate with minimal effort

## New Method Available

### `get_likely_lost_customers(min_overdue_days=180)`

Returns customers who are very overdue and likely lost.

**Usage:**
```python
predictor = RefillPredictor(data)
lost = predictor.get_likely_lost_customers()

# Shows:
# - Customer name and product
# - First order date (relationship history)
# - Last purchase date
# - Days since last purchase
# - Days overdue
# - Average interval
# - Number of purchases
# - Total lifetime value
# - Potential recovery value
```

**Parameters:**
- `min_overdue_days`: Threshold for "lost" (default: 180 = 6 months)

**Returns:**
- Sorted by lifetime value (high-value customers first)
- Ready for targeted win-back campaigns

## Use Cases

### 1. Weekly Priority List
```python
# Get most urgent cases for weekly review
overdue = predictor.get_overdue_refills(tolerance=7)
likely_lost = overdue[overdue['customer_status'] == 'Likely Lost']
top_10 = likely_lost.nlargest(10, 'total_lifetime_value')

# Call these 10 customers personally
```

### 2. Automated Campaigns
```python
# Segment by status for different campaign triggers
action_needed = overdue[overdue['customer_status'] == 'Action Needed']
at_risk = overdue[overdue['customer_status'] == 'At Risk']  
high_risk = overdue[overdue['customer_status'] == 'At High Risk']
likely_lost = overdue[overdue['customer_status'] == 'Likely Lost']

# Each segment gets appropriate campaign
```

### 3. Monthly Lost Customer Report
```python
# Generate recovery opportunities report
lost = predictor.get_likely_lost_customers()
total_value_at_risk = lost['total_lifetime_value'].sum()
high_value_recoveries = lost[lost['total_lifetime_value'] > 10000]

# Focus on high-value recovery opportunities
```

## Key Metrics to Track

### 1. Recovery Rate by Status
- % of "At Risk" customers who return
- % of "High Risk" customers who return  
- % of "Likely Lost" customers who return

### 2. Revenue Impact
- Total lifetime value at risk (sum of all lost customers)
- Recovered revenue (customers who returned after intervention)
- ROI of win-back campaigns

### 3. Prevention Metrics
- Average time to churn
- Early warning indicators
- Success rate of proactive outreach

## Technical Details

### Confidence Adjustment Formula

```python
if days_overdue >= 180:  # 6+ months
    adjusted = original_confidence * 0.2
    adjusted = min(adjusted, 20)  # Cap at 20%
    
elif days_overdue >= 90:  # 3-6 months
    adjusted = original_confidence * 0.4
    
elif days_overdue >= 60:  # 2-3 months
    adjusted = original_confidence * 0.6
    
elif days_overdue >= 30:  # 1-2 months
    adjusted = original_confidence * 0.8
    
else:  # <1 month
    adjusted = original_confidence * 0.9
```

### Churn Probability

```python
churn_probability = 100 - adjusted_confidence

# Example:
# Adjusted confidence = 18%
# Churn probability = 82%
# Interpretation: 82% chance they won't return
```

## Files Modified

1. **refill_prediction.py** (~60 lines added)
   - `get_overdue_refills()` - Added status classification and confidence adjustment
   - `get_likely_lost_customers()` - New method for lost customer analysis
   
2. **dashboard.py** (~90 lines modified)
   - Enhanced overdue tab with status breakdown
   - Color-coded visualizations
   - Likely lost customer section
   - Recommended actions

3. **config.py** (~20 lines added)
   - English translations for new statuses
   - Arabic translations for new statuses

## Validation & Testing

### Expected Results After Implementation:

1. **Overdue Tab Shows:**
   - ✅ 4 status metrics at the top
   - ✅ Dedicated "Likely Lost" section with recommendations
   - ✅ Color-coded bar chart
   - ✅ New columns: customer_status, adjusted_confidence, churn_probability

2. **Data Validation:**
   - ✅ All overdue customers have a status
   - ✅ Adjusted confidence ≤ original confidence
   - ✅ Churn probability = 100 - adjusted confidence
   - ✅ 6+ months overdue → adjusted confidence ≤ 20%

3. **Business Logic:**
   - ✅ Clear prioritization
   - ✅ Actionable insights
   - ✅ Value-based sorting

## Next Steps After Restart

1. **Review Likely Lost Customers**
   - Check who's been lost for 6+ months
   - Identify high-value recovery opportunities
   - Plan win-back campaign

2. **Set Up Automated Alerts**
   - Weekly email with "Likely Lost" customers
   - Daily summary of "Action Needed" customers
   - Monthly recovery opportunity report

3. **Track Results**
   - Recovery rate by status
   - ROI of interventions
   - Average time to churn

4. **Refine Thresholds**
   - Adjust 6-month threshold if needed
   - Customize by product category
   - Fine-tune confidence adjustments

## Summary

✅ **Business Rule Applied:** 6+ months overdue = likely lost
✅ **Automatic Classification:** 4-tier status system
✅ **Smart Prioritization:** By status and lifetime value
✅ **Confidence Adjustment:** Reflects reality of return likelihood
✅ **Actionable Insights:** Clear recommendations for each tier
✅ **Visual Clarity:** Color-coded, easy-to-understand dashboard

**Impact:** Transform raw overdue data into actionable customer recovery strategy! 🎯

