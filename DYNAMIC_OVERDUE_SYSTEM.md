# Dynamic Overdue Refill System

## What Changed

The overdue refill system is now **fully adjustable and dynamic**! Both the time period and customer status classifications automatically adjust based on your selections.

## Two Adjustable Sliders

### 1. Grace Period (0-14 days)
**What it does:** Days of tolerance before considering a refill "overdue"
- Default: 7 days
- Example: If set to 7, predictions that are 7+ days late are considered overdue

### 2. Show Overdue Up To (30-365 days)
**What it does:** Maximum days since last purchase to display
- Default: 90 days (3 months)
- Range: 30 to 365 days (in 30-day increments)
- Example: If set to 90, only shows customers whose last purchase was within 90 days

## Dynamic Status Classification

The customer status tiers automatically scale based on your "Show overdue up to" setting:

### Formula:
```
Period is divided into 4 equal tiers (25% each):

🔴 Likely Lost    = Top 25% (75-100% of max days)
🟠 At High Risk   = Second tier (50-75% of max days)
🟡 At Risk        = Third tier (25-50% of max days)
🟢 Action Needed  = Bottom 25% (0-25% of max days)
```

## Examples

### Example 1: 90 Days Setting (Default)

**Slider:** Show overdue up to = 90 days

**Status Breakdown:**
- 🔴 **Likely Lost**: 68+ days overdue (75% of 90)
- 🟠 **At High Risk**: 45-67 days overdue (50-75%)
- 🟡 **At Risk**: 23-44 days overdue (25-50%)
- 🟢 **Action Needed**: <23 days overdue (0-25%)

### Example 2: 180 Days Setting

**Slider:** Show overdue up to = 180 days

**Status Breakdown:**
- 🔴 **Likely Lost**: 135+ days overdue (75% of 180)
- 🟠 **At High Risk**: 90-134 days overdue
- 🟡 **At Risk**: 45-89 days overdue
- 🟢 **Action Needed**: <45 days overdue

### Example 3: 60 Days Setting (Short Term)

**Slider:** Show overdue up to = 60 days

**Status Breakdown:**
- 🔴 **Likely Lost**: 45+ days overdue (75% of 60)
- 🟠 **At High Risk**: 30-44 days overdue
- 🟡 **At Risk**: 15-29 days overdue
- 🟢 **Action Needed**: <15 days overdue

### Example 4: 360 Days Setting (Long Term)

**Slider:** Show overdue up to = 360 days

**Status Breakdown:**
- 🔴 **Likely Lost**: 270+ days overdue (75% of 360)
- 🟠 **At High Risk**: 180-269 days overdue
- 🟡 **At Risk**: 90-179 days overdue
- 🟢 **Action Needed**: <90 days overdue

## How It Works in the Dashboard

### Step 1: Adjust Sliders
```
Grace period (days): ●━━━━━━━━━━ 7

Show overdue up to (days): ━━━━━●━━━━━ 120
```

### Step 2: Status Tiers Calculate Automatically
```
Based on 120 days:
- Likely Lost: 90+ days
- At High Risk: 60-89 days
- At Risk: 30-59 days
- Action Needed: <30 days
```

### Step 3: Metrics Update Dynamically
```
┌────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│ 🔴 Likely Lost     │ 🟠 At High Risk    │ 🟡 At Risk         │ 🟢 Action Needed   │
│ (90+ days)         │ (60-89 days)       │ (30-59 days)       │ (<30 days)         │
├────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│ 25 customers       │ 48 customers       │ 82 customers       │ 120 customers      │
└────────────────────┴────────────────────┴────────────────────┴────────────────────┘
```

### Step 4: Charts Re-color
Bar chart colors update based on the dynamic status:
- Red bars = Top 25% (Likely Lost)
- Orange bars = 50-75% (At High Risk)
- Yellow bars = 25-50% (At Risk)
- Green bars = 0-25% (Action Needed)

## Use Cases

### Focus on Short-Term (30-60 days)
**When to use:** You want to focus only on very recent customers
- Set slider to 30 or 60 days
- Status tiers compress to shorter periods
- Good for: Active customer retention, urgent follow-ups

**Example:**
- 60 days → Likely Lost at 45+ days
- Perfect for high-touch pharmacy with frequent customers

### Standard View (90 days - Default)
**When to use:** Balance between recent and longer-term customers
- Set slider to 90 days (default)
- Status tiers: 68, 45, 23 days
- Good for: General overdue management

**Example:**
- 90 days → Likely Lost at 68+ days
- Standard approach for most pharmacies

### Long-Term View (180-360 days)
**When to use:** Want to see all customers, including very old ones
- Set slider to 180+ days
- Status tiers expand to longer periods
- Good for: Complete customer base review, recovery campaigns

**Example:**
- 360 days → Likely Lost at 270+ days
- See everyone who ordered in the past year

## Benefits

### 1. Flexibility
✅ Adjust to your business needs
✅ Switch between short-term and long-term views
✅ Different strategies for different time periods

### 2. Consistent Logic
✅ Always 4 tiers (quartiles)
✅ Proportional scaling
✅ Fair distribution across time period

### 3. Clear Communication
✅ Status labels show exact day ranges
✅ No confusion about thresholds
✅ Dynamic messaging matches your selection

### 4. Better Decision Making
✅ Focus on actionable timeframes
✅ Exclude irrelevant old data
✅ Tailor view to your recovery strategy

## Filter Information Display

The system shows you exactly what's being displayed:

### When Showing Filtered Data:
```
📅 Showing overdue refills from past 90 days 
   (224 shown, 2492 older excluded)
```

### When All Are Old:
```
📅 No overdue refills in the past 90 days. 
   (2716 customers haven't ordered in 90+ days - likely lost)
```

### When None Overdue:
```
✅ No overdue refills!
```

## Recommendations by Business Type

### High-Volume Pharmacy (Frequent Orders)
**Recommended:** 30-60 days
- Customers order frequently
- Focus on immediate action
- Shorter "likely lost" threshold

### Standard Pharmacy
**Recommended:** 90-120 days (Default)
- Balanced approach
- Mix of frequent and occasional customers
- Standard recovery timeline

### Specialty Pharmacy (Long-Term Medications)
**Recommended:** 180-360 days
- Customers order less frequently
- Longer natural intervals
- Extended recovery window

## Advanced Usage

### Quarterly Reviews
```
Q1: Set to 90 days, review standard overdue
Q2: Set to 180 days, check longer-term trends
Q3: Set to 60 days, focus on recent activity
Q4: Set to 360 days, annual customer review
```

### Campaign Planning
```
Week 1: 30 days - Urgent follow-ups
Week 2: 60 days - At-risk outreach
Week 3: 90 days - Standard recovery
Week 4: 180 days - Long-term win-back
```

### Segmented Approach
```
Product A (fast-moving): 30-60 days
Product B (standard): 90 days
Product C (chronic): 180-360 days
```

## Technical Details

### Calculation Formula
```python
tier_size = max_overdue_days / 4

likely_lost_threshold = max_overdue_days * 0.75  # Top 25%
high_risk_threshold = max_overdue_days * 0.50    # 50-75%
at_risk_threshold = max_overdue_days * 0.25      # 25-50%
action_needed = 0 to at_risk_threshold           # 0-25%
```

### Status Assignment
```python
if days_overdue >= likely_lost_threshold:
    status = 'Likely Lost'
elif days_overdue >= high_risk_threshold:
    status = 'At High Risk'
elif days_overdue >= at_risk_threshold:
    status = 'At Risk'
else:
    status = 'Action Needed'
```

## What Happens After Restart

1. **Open Overdue Refills Tab**
2. **See Two Sliders:**
   - Grace period (0-14 days) - left slider
   - Show overdue up to (30-365 days) - right slider
3. **Adjust Sliders:**
   - Move the "Show overdue up to" slider
   - Watch status labels update instantly
   - See customer counts redistribute
4. **Status Metrics Show Dynamic Ranges:**
   - "🔴 Likely Lost (68+ days)" changes with slider
   - All 4 metrics update their day ranges
   - Chart colors reclassify automatically

## Quick Reference Table

| Max Days | Likely Lost | At High Risk | At Risk | Action Needed |
|----------|-------------|--------------|---------|---------------|
| 30 | 23+ | 15-22 | 8-14 | <8 |
| 60 | 45+ | 30-44 | 15-29 | <15 |
| 90 | 68+ | 45-67 | 23-44 | <23 |
| 120 | 90+ | 60-89 | 30-59 | <30 |
| 180 | 135+ | 90-134 | 45-89 | <45 |
| 240 | 180+ | 120-179 | 60-119 | <60 |
| 360 | 270+ | 180-269 | 90-179 | <90 |

## Summary

### What You Control:
✅ Time period to analyze (30-365 days)
✅ Grace period before overdue (0-14 days)

### What Adjusts Automatically:
✅ Customer status classifications
✅ Status threshold day ranges
✅ Metric labels
✅ Chart colors
✅ "Likely Lost" section header
✅ Filter information messages

### Result:
🎯 **Completely flexible overdue management system that adapts to your business needs!**

No more fixed "6 months" or "3 months" - you decide what makes sense for your pharmacy, and everything else adjusts automatically!

