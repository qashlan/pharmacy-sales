# Pharmaceutical Analysis Queries Guide

## Advanced Analytical Questions for Pharmacy Data

This guide shows you how to ask sophisticated pharmaceutical business intelligence questions using the AI Query system.

---

## 🔬 Seasonal & Trend Analysis

### Peak Sales Identification

**Question:**
> "Are there specific times of year when Atrovent sales peak, and what might contribute to those trends?"

**What the system will do:**
1. Filter for Atrovent product
2. Group sales by month/season
3. Identify peak periods
4. Calculate growth rates

**Similar questions you can ask:**
```
"When do Paracetamol sales peak during the year?"
"Show me monthly sales trends for antibiotics"
"Which months have the highest Vitamin D3 sales?"
"Is there a seasonal pattern in allergy medication sales?"
"Compare winter vs summer sales for respiratory medications"
```

**Expected Result Format:**
```
Month    Revenue    Quantity    YoY_Growth
Jan      $2,450     245         +15%
Feb      $2,890     289         +22%
Mar      $3,200     320         +18%
...
```

### Seasonal Pattern Analysis

**Questions:**
```
"Do respiratory medication sales increase in winter months?"
"Show me the quarterly trend for pain relief medications"
"Which seasons have the highest antibiotic sales?"
"Are there monthly patterns in insulin sales?"
"Compare allergy medication sales across all months"
```

---

## 🔗 Correlation Analysis

### Product-Condition Correlations

**Question:**
> "How do prescription rates for Atrovent correlate with the prevalence of respiratory conditions in our customer base?"

**What the system will do:**
1. Identify customers who bought Atrovent
2. Analyze their purchase patterns for other respiratory medications
3. Calculate correlation metrics
4. Identify related product patterns

**Similar questions:**
```
"Which customers buy multiple diabetes medications together?"
"Is there a correlation between antibiotic and vitamin sales?"
"Show me customers who buy both pain relief and anti-inflammatory medications"
"Which products are commonly purchased with cardiovascular medications?"
"Do customers who buy insulin also purchase related diabetes care products?"
```

**Advanced Correlation Queries:**
```
"Find customers who transitioned from one medication to another"
"Which products have the strongest purchase correlation?"
"Show me medication combinations that indicate chronic conditions"
"Identify customer clusters based on medication purchase patterns"
```

---

## 📊 Customer Health Profile Analysis

### Chronic Condition Indicators

**Questions:**
```
"Which customers show purchase patterns indicating chronic respiratory conditions?"
"Identify customers with consistent diabetes medication purchases"
"Show me customers who regularly buy cardiovascular medications"
"Find customers with multiple medication categories (polypharmacy)"
"Which customers show long-term pain management medication patterns?"
```

### Purchase Frequency & Adherence

**Questions:**
```
"How often do customers refill their Atrovent prescriptions?"
"Are there gaps in medication purchase patterns that suggest non-adherence?"
"Show me customers with irregular refill patterns for chronic medications"
"Calculate the average time between refills for insulin"
"Which customers have stopped refilling their regular medications?"
```

---

## 🎯 Product-Specific Deep Dives

### Single Product Analysis

**For Atrovent (or any specific product):**
```
"What is the average purchase quantity for Atrovent?"
"Show me the top 10 customers by Atrovent spending"
"How has Atrovent revenue changed month-over-month?"
"What percentage of our customers have purchased Atrovent?"
"Compare Atrovent sales to other respiratory medications"
```

### Category-Level Analysis

**Questions:**
```
"Which respiratory medications are most popular?"
"Show me market share by product within the diabetes category"
"How do sales of different pain relief medications compare?"
"What's the revenue breakdown for cardiovascular medications?"
"Rank antibiotic products by sales volume"
```

---

## 📈 Growth & Trend Analysis

### Year-over-Year Comparisons

**Questions:**
```
"Compare Atrovent sales this year vs last year"
"Which products show the highest growth rate?"
"Are respiratory medication sales increasing or decreasing over time?"
"Show me the 3-month moving average for insulin sales"
"What's the compound growth rate for pain relief medications?"
```

### Market Dynamics

**Questions:**
```
"Which therapeutic categories are growing fastest?"
"Are we losing customers in any medication categories?"
"Show me new customer acquisition trends for chronic medications"
"Which products are declining in popularity?"
"Identify emerging product trends in our sales data"
```

---

## 🏥 Clinical Insights

### Co-Morbidity Analysis

**Questions:**
```
"Which customers buy medications for multiple chronic conditions?"
"Show me common medication combinations that indicate co-morbidities"
"Find customers taking both diabetes and cardiovascular medications"
"What percentage of respiratory medication buyers also purchase allergy medications?"
"Identify customers with complex medication regimens"
```

### Treatment Patterns

**Questions:**
```
"Do customers switch between different pain medications?"
"Show me customers who started new chronic medications in the last 6 months"
"Which customers have escalating medication needs (increasing quantities)?"
"Find customers who discontinued chronic medications"
"Analyze treatment adherence by medication category"
```

---

## 💊 Medication Management

### Inventory & Demand Planning

**Questions:**
```
"Which months require higher stock of respiratory medications?"
"Predict Atrovent demand for the next quarter based on historical patterns"
"What's the average monthly consumption of diabetes medications?"
"Show me fast-moving vs slow-moving medications"
"Which products have unpredictable demand patterns?"
```

### Refill Patterns

**Questions:**
```
"What's the typical refill cycle for Atrovent customers?"
"Are customers refilling too early or too late?"
"Show me medications with the most consistent refill patterns"
"Which customers might need refill reminders?"
"Calculate the average days supply based on refill frequency"
```

---

## 🔍 Complex Multi-Factor Analysis

### Advanced Analytical Questions

**Combining Multiple Factors:**
```
"For customers taking respiratory medications, what's their average spending on related products?"

"Show me seasonal trends in allergy medication sales correlated with respiratory medication purchases"

"Which customer segments (by medication type) have the highest lifetime value?"

"Analyze the relationship between medication adherence and customer retention"

"Do customers who buy generic medications have different purchase patterns than brand-name buyers?"

"What's the correlation between number of medications purchased and total customer spending?"

"Identify customers whose medication purchases suggest they should be in disease management programs"
```

---

## 📊 Statistical Analysis

### Quantitative Metrics

**Questions:**
```
"What's the standard deviation in Atrovent purchase quantities?"
"Calculate the coefficient of variation for respiratory medication sales"
"Show me outliers in medication purchase patterns"
"What's the 75th percentile of spending on diabetes medications?"
"Calculate the Gini coefficient for medication category distribution"
```

### Predictive Indicators

**Questions:**
```
"Based on historical patterns, when should we expect the next peak in respiratory medication sales?"

"Which customers show declining purchase frequency that might indicate switching to competitors?"

"Predict which customers are likely to start chronic medication therapy"

"Identify leading indicators for seasonal medication demand"
```

---

## 🎯 Real-World Use Cases

### Case 1: Respiratory Medication Strategy
```
1. "Are there specific times of year when respiratory medication sales peak?"
2. "Which customers buy multiple respiratory medications?"
3. "What's the average treatment duration for respiratory medications?"
4. "Show me customers who might benefit from bulk purchasing respiratory medications"
5. "Compare our respiratory medication sales to overall market trends"
```

### Case 2: Diabetes Care Program
```
1. "Identify all customers purchasing diabetes medications"
2. "Calculate average monthly spending per diabetes patient"
3. "Find gaps in diabetes medication refills"
4. "Which diabetes patients also buy related monitoring supplies?"
5. "Show me new diabetes medication starts in the last quarter"
```

### Case 3: Chronic Pain Management
```
1. "Which customers show long-term pain medication patterns?"
2. "Are pain medication customers also buying anti-inflammatory drugs?"
3. "Show me escalation patterns in pain medication purchases"
4. "Identify customers who might benefit from pain management consultation"
5. "What's the customer retention rate for chronic pain patients?"
```

---

## 💡 Tips for Pharmaceutical Queries

### Be Specific About:
1. **Product Names** - Use exact names or categories
   - ✅ "Show Atrovent sales trends"
   - ✅ "Analyze respiratory medication patterns"

2. **Time Periods** - Specify the timeframe
   - ✅ "Last 12 months"
   - ✅ "Compare Q1 2024 to Q1 2023"

3. **Metrics** - Clarify what you want to measure
   - ✅ "Revenue trends"
   - ✅ "Quantity sold"
   - ✅ "Number of customers"

4. **Conditions** - Add relevant filters
   - ✅ "Customers who bought more than 3 times"
   - ✅ "Sales above $500"

### Understanding the Context:

The AI system will:
- Recognize medication names (case-insensitive)
- Understand therapeutic categories
- Handle seasonal patterns
- Calculate correlations
- Identify purchase patterns
- Perform time-series analysis

---

## 🚀 Getting Started

### Example Workflow:

**Step 1: Start Broad**
```
"Show me all respiratory medication sales by month"
```

**Step 2: Narrow Down**
```
"For respiratory medications, which specific products have the highest sales?"
```

**Step 3: Deep Dive**
```
"Analyze Atrovent specifically - when do sales peak and who are the top customers?"
```

**Step 4: Correlations**
```
"Do customers who buy Atrovent also purchase other specific medications?"
```

**Step 5: Insights**
```
"Based on Atrovent purchase patterns, what seasonal stocking strategy should we use?"
```

---

## 📈 Expected Response Format

When you ask a pharmaceutical query, you'll get:

1. **Answer Summary** - High-level insights
2. **Detailed Data** - Table with results (downloadable)
3. **Executed Code** - The pandas code that ran (click to expand)
4. **Explanation** - What the analysis shows

**Example Response:**

**Query:** "Are there specific times of year when Atrovent sales peak?"

**Answer:**
```
Seasonal Analysis: Atrovent

Peak Sales Periods:
- Highest: March-April (Spring allergy season)
- Secondary Peak: October-November (Fall season)
- Lowest: June-August (Summer months)

Contributing Factors:
- Spring allergy season drives 40% annual sales
- Fall respiratory season accounts for 30%
- Winter shows moderate but steady demand
```

**Data:**
```csv
Month,Revenue,Quantity,Customers,Avg_per_Customer
Jan,$2,450,245,42,$58.33
Feb,$2,890,289,48,$60.21
Mar,$3,850,385,65,$59.23
...
```

---

## 🎓 Learning Path

### Beginner Queries
```
"Show me total sales for [Product Name]"
"Which customers buy [Product Name]?"
"What are the top 10 medications by revenue?"
```

### Intermediate Queries
```
"Show me monthly trends for [Product Name]"
"Compare [Product A] vs [Product B] sales"
"Which customers buy multiple diabetes medications?"
```

### Advanced Queries
```
"Analyze seasonal patterns in respiratory medication sales and identify peak periods"
"Show me customers with purchase patterns indicating multiple chronic conditions"
"Calculate the correlation between [Product A] and [Product B] purchases"
```

### Expert Queries
```
"For customers purchasing respiratory medications, analyze the relationship between seasonal demand, customer retention, and average purchase value, broken down by specific product categories"
```

---

## 🔐 Privacy & Ethics

**Important Notes:**
- All analysis is based on aggregated sales data
- Individual customer privacy is maintained
- Medical conditions are inferred from purchase patterns, not diagnoses
- Use insights responsibly for better patient care
- Comply with HIPAA and local privacy regulations

---

## ✅ Quick Reference

### Common Query Templates

**Seasonal Analysis:**
```
"When do [product/category] sales peak during the year?"
```

**Customer Patterns:**
```
"Which customers buy multiple [category] medications?"
```

**Correlations:**
```
"What products are commonly purchased together with [product]?"
```

**Trends:**
```
"Show me the [period] trend for [product/category]"
```

**Comparisons:**
```
"Compare [product A] sales to [product B] in [time period]"
```

---

## 📞 Need Help?

If your query doesn't work as expected:
1. **Simplify** - Break complex questions into parts
2. **Be Specific** - Use exact product names
3. **Check Spelling** - Verify product names are correct
4. **Try Variations** - Rephrase the question
5. **Use Chat** - Ask follow-up questions for clarification

---

**Ready to analyze? Start with the examples above and explore your pharmaceutical data!** 🚀

*For general query help, see `DYNAMIC_AI_QUERIES.md`*
*For quick start, see `AI_QUERY_QUICKSTART.md`*

