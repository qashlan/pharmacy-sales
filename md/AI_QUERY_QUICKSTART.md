# AI Query System - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Configure OpenAI API Key

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Update config.py**
```python
OPENAI_API_KEY = "sk-your-api-key-here"
```

### Step 2: Start the Dashboard
```bash
streamlit run dashboard.py
```

### Step 3: Ask Questions!
1. Navigate to **"🤖 AI Query"** page
2. Type your question
3. Click **"🔍 Ask"**

---

## 💡 Example Questions to Try

### Start Simple
```
"What is the total revenue?"
"Show me the top 10 products"
"Which customers are at risk of churning?"
```

### Get More Specific
```
"What's the average order value on Mondays?"
"Show me customers who spent more than $500"
"Which products were sold only on weekends?"
```

### Go Aggressive! 🔥
```
"Find customers who bought more than 5 different products"
"Compare sales from weekdays vs weekends"
"What's the median order value for each product category?"
"Show me the top 3 customers for each category"
```

---

## 🎯 What's New?

### Before: Limited to Predefined Questions
- Only specific patterns worked
- Couldn't ask custom questions
- Limited flexibility

### Now: Ask ANYTHING! 🎉
- Any question about your data
- Complex aggregations
- Custom filters
- Statistical analysis
- Comparative queries
- Time-based analysis

---

## 🔍 See How It Works

When you ask a question, you can:
1. **View the executed code** - Click "View Executed Code"
2. **Download results** - Export to CSV
3. **Ask follow-ups** - Use the chat feature

### Example:

**You Ask:**
> "Which customers spent more than $500 on weekends?"

**System Shows:**
```python
# Generated Code:
weekend_sales = df[df['day_of_week'] >= 5]
result = weekend_sales.groupby('customer_name')['total'].sum()
result = result[result > 500].sort_values(ascending=False).head(20)
```

**You Get:**
```
Customer_15: $1,245.30
Customer_8:  $892.50
Customer_23: $654.20
...
```

---

## 🎓 Learn by Example

### Query Types You Can Try:

#### Aggregations
```
"What's the average/median/sum of X by Y?"
"Show me the total sales per category"
"Count how many customers bought each product"
```

#### Filters
```
"Find all transactions above $X"
"Show me customers who..."
"Which products that..."
```

#### Comparisons
```
"Compare X vs Y"
"Show me the difference between..."
"Which is higher/lower/better..."
```

#### Time-Based
```
"What happened on [day/month/date]?"
"Compare this month to last month"
"Show me trends over time"
```

#### Rankings
```
"Top X by Y"
"Bottom X by Y"
"Rank customers/products by..."
```

---

## ⚡ Pro Tips

1. **Be Specific** - Include numbers, dates, conditions
   - ✅ "Top 10 customers who spent more than $500 in 2024"
   - ❌ "Show customers"

2. **Use Natural Language** - Talk normally
   - ✅ "Which customers haven't purchased in 60 days?"
   - ✅ "Find customers who stopped buying"

3. **Ask Follow-ups** - Use the chat for conversations
   - "Now show only the top 5"
   - "What about last month?"

4. **Check the Code** - Learn from what gets generated
   - Click "View Executed Code"
   - See how questions become pandas operations

5. **Download Results** - Export for Excel/further analysis
   - Click "Download Results as CSV"

---

## 🎪 Try These Right Now!

Copy and paste into the AI Query interface:

### Easy (1 minute each)
```
What is the total revenue?
Show me the top 5 products by sales
Which customers spent the most?
```

### Medium (2 minutes each)
```
What's the average order value for each day of the week?
Find customers who made more than 3 purchases
Show me products that sell best on weekends
```

### Advanced (3 minutes each)
```
For each product category, show me the top 3 customers by spending
Compare revenue between weekdays and weekends, broken down by hour
Find customers whose purchase frequency doubled compared to last month
```

---

## 🔥 Power User Features

### Complex Multi-Part Questions
```
"For each customer segment, calculate average revenue per transaction and compare to overall average"
```

### Statistical Analysis
```
"Show me the standard deviation of order values by product category"
"Calculate the 75th percentile of customer spending"
```

### Conditional Logic
```
"Find products that are bought by more than 10 customers but have sales below $100"
```

---

## 🐛 Troubleshooting

### "OpenAI not available"
→ Check your API key is set correctly

### "Code execution error"
→ Try rephrasing your question
→ Break complex queries into parts

### No results returned
→ Check if your filters are too restrictive
→ Verify data exists for your query

### Slow response
→ Normal for complex queries (2-3 seconds)
→ Consider simplifying the question

---

## 📚 More Resources

- **Full Documentation**: `DYNAMIC_AI_QUERIES.md`
- **Technical Details**: `AI_QUERY_FIXES_AND_ENHANCEMENTS.md`
- **Test Suite**: Run `python test_dynamic_queries.py`

---

## ✅ Verification Checklist

Before diving in, ensure:
- [ ] OpenAI API key is configured
- [ ] Dashboard is running (`streamlit run dashboard.py`)
- [ ] You're on the "🤖 AI Query" page
- [ ] You see "GPT Enhanced" badge (green)

---

## 🎉 You're Ready!

The system can now answer **virtually any question** about your pharmacy sales data. 

Start with simple questions and work your way up to complex analyses. Every query is a learning opportunity!

**Have fun exploring your data! 🚀**

---

*Quick Start Guide v1.0*
*For more examples, see DYNAMIC_AI_QUERIES.md*

