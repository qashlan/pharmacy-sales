# Dynamic AI Query System

## Overview

The AI Query system now supports **dynamic queries** - you can ask ANY question about your data, even without predefined handlers. The system uses GPT to understand your question, generates pandas code dynamically, executes it, and returns the results.

## How It Works

1. **You ask a question** in natural language
2. **GPT interprets** your question and generates pandas code
3. **The code is executed** safely on your data
4. **Results are displayed** with explanations

## Example "Aggressive" Queries

### Complex Aggregations

```
"What is the average revenue per customer by month?"
"Show me the median order value for each product category"
"Which day of the week has the highest sales?"
"What's the revenue breakdown by sale type (Cash vs Insurance vs Credit)?"
```

### Time-Based Analysis

```
"Compare sales from weekdays vs weekends"
"Show me the growth rate month over month"
"Which hour of the day has peak sales?"
"What's the revenue trend by quarter?"
```

### Customer Behavior

```
"Find customers who spent more than $1000 in the last 3 months"
"Which customers bought more than 5 different products?"
"Show me customers who haven't purchased in 60 days"
"What's the average time between purchases for each customer?"
```

### Product Analysis

```
"Find products that are sold together more than 3 times"
"Which products have the highest profit margin?"
"Show me products that are purchased only by specific customers"
"What's the price variation for each product over time?"
```

### Statistical Queries

```
"Show me the standard deviation of daily sales"
"What's the correlation between units sold and revenue?"
"Find outliers in product prices"
"Calculate the 90th percentile of order values"
```

### Comparative Analysis

```
"Compare this month's sales to last month"
"Show me the top 10 growing products by revenue increase"
"Which customers increased their spending the most?"
"Compare category performance year over year"
```

### Custom Filters

```
"Show me all transactions above $500"
"Find products sold only on weekends"
"Which customers made purchases on more than 10 different days?"
"Show me items that were never refunded"
```

### Complex Joins and Grouping

```
"For each customer, show their favorite product and total spent"
"Group products by price range and show average sales"
"Show me customers who bought product X but not product Y"
"Find customers whose average order value exceeds the overall average"
```

## Features

### Automatic Refund Handling
By default, refunds are filtered out unless you specifically ask about them:
```
"Show me all refunds in the last month"
"What's the refund rate by product?"
```

### Code Transparency
You can view the exact pandas code that was executed:
- Click on "View Executed Code" in the results
- See exactly how your question was translated to code

### Data Download
- All results can be downloaded as CSV
- Perfect for further analysis in Excel or other tools

### Safety
- Code execution is sandboxed
- No file system access
- No network operations
- Pure pandas data operations only

## Tips for Best Results

1. **Be Specific**: "Show me the top 10 products by revenue in 2024" is better than "top products"

2. **Use Natural Language**: Don't worry about technical terms - ask naturally
   - ✅ "Which customers spent the most?"
   - ✅ "What are my best-selling items?"

3. **Include Context**: Mention time periods, thresholds, or specific criteria
   - "Find customers who spent more than $1000 this year"
   - "Show me products with less than 5 sales last month"

4. **Ask Follow-up Questions**: Use the chat feature for conversational analysis
   - "Now show me only the top 5"
   - "What about last month?"

5. **Complex is OK**: Don't hesitate to ask complex multi-part questions
   - "For each product category, show me the top customer and their total spend"

## Limitations

- Results are limited to 20 rows by default (for performance)
- Very complex queries might take a few seconds
- Requires OpenAI API key to be configured

## When to Use Dynamic Queries vs Predefined Handlers

**Use Predefined Handlers** (faster, no API cost):
- Common questions like "total revenue", "top products"
- Standard RFM segmentation
- Refill predictions

**Use Dynamic Queries** (flexible, requires API):
- Complex custom analysis
- Uncommon aggregations
- Specific filters and conditions
- Exploratory data analysis

## Troubleshooting

If a query fails:
1. Try rephrasing your question
2. Break complex queries into smaller parts
3. Use the chat feature for clarification
4. Check that your OpenAI API key is valid

## Examples by Difficulty

### Easy (Predefined Handlers Available)
```
"What is the total revenue?"
"Show me the top 10 products"
"Which customers are churning?"
```

### Medium (Dynamic Queries Recommended)
```
"What's the average order value on Mondays?"
"Show me customers who bought more than 3 times in January"
"Which products are never bought on weekends?"
```

### Hard (Full Dynamic Query Power)
```
"For each customer segment, calculate the average time between purchases and compare it to the previous quarter"
"Show me the top 3 products by revenue for each category, excluding refunds, grouped by month"
"Find customers whose purchase frequency increased by more than 50% compared to 6 months ago"
```

## API Usage Note

Dynamic queries use OpenAI API calls (approximately 1 call per query). Keep this in mind for API cost management. The system uses `gpt-4o-mini` model which is cost-effective.

## Getting Started

1. **Set your OpenAI API key** in `config.py` or environment variable
2. **Go to AI Query page** in the dashboard
3. **Type your question** naturally
4. **Click Ask** and get results!

Happy analyzing! 🚀

