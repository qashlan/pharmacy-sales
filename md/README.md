# 💊 Pharmacy Sales Analytics System

A comprehensive AI-powered analytics platform for pharmacy sales data that transforms raw sales information into actionable business intelligence.

## 🌟 Features

### 1. Sales Analysis
- **Revenue tracking** with daily, weekly, and monthly trends
- **Top products** and categories analysis
- **Time-based patterns** (hourly, daily, weekly)
- **Anomaly detection** to identify unusual sales patterns
- **Growth analysis** and velocity metrics

### 2. Customer Behavior Insights
- **Customer segmentation** by value (high, medium, low)
- **Frequent buyers** identification
- **Churn risk detection** for at-risk customers
- **New customer acquisition** tracking
- **Repeat purchase rate** and customer lifetime value
- **Customer cohort analysis** and retention rates

### 3. Product Performance
- **Fast-moving vs slow-moving** products
- **ABC classification** for inventory prioritization
- **Product lifecycle** stage identification
- **Inventory planning signals** (reorder, overstock, optimal)
- **Category performance** analysis
- **Price sensitivity** insights

### 4. RFM Customer Segmentation
Segments customers based on:
- **Recency** — when was the last purchase
- **Frequency** — how often they buy
- **Monetary** — how much they spend

Identifies:
- Champions
- Loyal Customers
- Potential Loyalists
- New Customers
- Promising
- Need Attention
- About to Sleep
- At Risk
- Cannot Lose Them
- Hibernating
- Lost

Includes **actionable recommendations** for each segment.

### 5. Refill Prediction
- **Purchase interval analysis** for customer-product pairs
- **Overdue refill detection** for proactive customer outreach
- **Upcoming refills forecast** (7, 14, 30 days ahead)
- **Customer refill schedules** and compliance tracking
- **Irregular pattern detection** to identify issues

### 6. Cross-Sell & Bundle Analysis
- **Market basket analysis** using association rules
- **Product affinity** calculations (which products sell together)
- **Bundle suggestions** based on purchase patterns
- **Complementary products** recommendations
- **Upsell opportunities** identification
- **Category associations** analysis

### 7. AI Natural Language Query System
Ask questions in plain English (or Arabic):
- "What is the total revenue?"
- "Show me customers at risk of churning"
- "Which products are frequently bought together?"
- "What are the fast moving products?"
- "Show me overdue refills"

**✨ NEW: GPT-Powered Enhancement (Optional)**
- 🧠 **Intelligent Query Interpretation**: Understands complex questions using OpenAI GPT
- 💡 **AI-Generated Insights**: Automatic business insights and recommendations
- 💬 **Interactive Chat**: Have conversations about your sales data
- 🎯 **Smart Suggestions**: AI-suggested follow-up questions

Works with or without OpenAI API key. See [OPENAI_INTEGRATION.md](OPENAI_INTEGRATION.md) for setup.

### 8. Interactive Dashboard
- Beautiful, modern Streamlit interface
- Real-time visualizations with Plotly
- Export capabilities (CSV reports)
- Bilingual support (English & Arabic)

## 📋 Requirements

```
pandas==2.1.4
numpy==1.26.2
plotly==5.18.0
streamlit==1.29.0
scikit-learn==1.3.2
matplotlib==3.8.2
seaborn==0.13.0
scipy==1.11.4
openpyxl==3.1.2
xlsxwriter==3.1.9
python-dateutil==2.8.2
mlxtend==0.23.1
statsmodels==0.14.1
setuptools>=65.5.0
openai>=1.0.0  # Optional: For GPT-powered features
```

## 🚀 Installation

1. **Clone or download** this repository

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Prepare your data:**
   - Your sales data should have these columns:
     - Item Code
     - Item Name
     - Units
     - Pieces
     - Selling Price
     - Total
     - Sale Type
     - Customer Name
     - Date
     - Time
     - Category

4. **Run the dashboard:**
```bash
streamlit run dashboard.py
```

5. **Access the dashboard:**
   - Open your browser to `http://localhost:8501`

## 📊 Data Format

### Required Columns

| Column Name | Description | Type | Example |
|------------|-------------|------|---------|
| Item Code | Unique product identifier | String | "ITEM001" |
| Item Name | Product name | String | "Paracetamol 500mg" |
| Units | Number of units sold | Integer | 2 |
| Pieces | Total pieces (units × pack size) | Integer | 20 |
| Selling Price | Unit selling price | Float | 12.50 |
| Total | Total transaction amount | Float | 25.00 |
| Sale Type | Type of sale | String | "Cash", "Insurance" |
| Customer Name | Customer identifier | String | "Customer_123" |
| Date | Transaction date | Date | "2024-01-15" |
| Time | Transaction time | Time | "14:30:00" |
| Category | Product category | String | "Pain Relief" |

### Edge Cases Handled

- **Units vs Pieces:** System handles cases where one unit contains multiple pieces
- **Order IDs:** Automatically computed from customer + purchase date/time (30-minute window)
- **Missing data:** Intelligent handling of missing values
- **Date formats:** Flexible date/time parsing

## 📱 Usage

### Starting the Dashboard

```bash
streamlit run dashboard.py
```

### Using Sample Data

If you don't have data ready, the system will automatically generate sample data for demonstration.

### Uploading Your Data

1. Click "Upload Sales Data" in the sidebar
2. Select your CSV or Excel file
3. The system will automatically process and analyze it

### Navigating the Dashboard

**Sales Analysis** — Revenue trends, top products, time patterns, anomalies

**Customer Insights** — Top customers, churn risk, segments, new customers

**Product Performance** — Fast/slow movers, ABC classification, lifecycle, inventory signals

**RFM Segmentation** — Customer segments with actionable recommendations

**Refill Prediction** — Overdue refills, upcoming refills, customer schedules

**Cross-Sell Analysis** — Product bundles, associations, market basket insights

**Export & Reports** — Download CSV reports for any analysis

### Using AI Queries

Navigate to any section and use natural language to ask questions:

```
"What is the total revenue?"
"Show me the top 10 products by sales"
"Which customers haven't purchased in 90 days?"
"What products should I reorder?"
"Which items are frequently bought together?"
```

## 🎯 Use Cases

### 1. Inventory Management
- Identify which products need reordering
- Detect slow-moving items for promotions
- Optimize stock levels based on sales velocity

### 2. Customer Retention
- Find at-risk customers before they churn
- Segment customers for targeted marketing
- Track customer lifetime value

### 3. Revenue Optimization
- Identify best-selling products and categories
- Detect sales anomalies and trends
- Analyze pricing impact on sales

### 4. Marketing Strategy
- Create effective customer segments
- Plan refill reminder campaigns
- Design product bundles based on purchase patterns

### 5. Strategic Planning
- Forecast demand based on historical patterns
- Plan seasonal inventory
- Optimize product mix

## 📈 Example Insights

The system automatically generates insights like:

- "📈 Revenue is growing strongly (25.3% increase)"
- "⚠️ 15 customers at risk of churning"
- "🐌 8 slow-moving products need attention"
- "💊 23 customers have overdue refills"
- "🎯 VIP customers contribute 45% of revenue"

## 🔧 Configuration

Edit `config.py` to customize:

```python
# RFM weights
RECENCY_WEIGHT = 1.0
FREQUENCY_WEIGHT = 1.0
MONETARY_WEIGHT = 1.0

# Churn threshold
CHURN_THRESHOLD_DAYS = 90

# Association rules
MIN_SUPPORT = 0.01
MIN_CONFIDENCE = 0.3
MIN_LIFT = 1.0
```

## 📊 Analysis Modules

### Standalone Usage

You can also use the analysis modules independently:

```python
from data_loader import DataLoader
from sales_analysis import SalesAnalyzer

# Load and process data
loader = DataLoader("sales_data.csv")
loader.load_data()
data = loader.preprocess_data()

# Analyze sales
analyzer = SalesAnalyzer(data)
metrics = analyzer.get_overall_metrics()
trends = analyzer.get_daily_trends()
top_products = analyzer.get_top_products(10)

print(f"Total Revenue: ${metrics['total_revenue']:,.2f}")
```

### Available Modules

- `data_loader.py` — Data loading and preprocessing
- `sales_analysis.py` — Sales metrics and trends
- `customer_analysis.py` — Customer behavior analysis
- `product_analysis.py` — Product performance metrics
- `rfm_analysis.py` — RFM segmentation
- `refill_prediction.py` — Refill forecasting
- `cross_sell_analysis.py` — Market basket analysis
- `ai_query.py` — Natural language query engine

## 🌐 Language Support

The system supports both English and Arabic:
- Switch language in the sidebar
- All metrics and labels are translated
- Reports can be generated in either language

## 📥 Export Options

Export any analysis as CSV:
- Sales reports (daily/weekly/monthly)
- Customer lists (by segment, value, risk)
- Product performance reports
- RFM segmentation results
- Refill predictions
- Cross-sell recommendations

## 🛠️ Troubleshooting

### Data Loading Issues

**Problem:** "Missing required columns"
**Solution:** Ensure your CSV has all required columns with correct names

**Problem:** "Date parsing error"
**Solution:** Check date format is YYYY-MM-DD or common format

### Performance Issues

**Problem:** Dashboard is slow with large datasets
**Solution:** The system is optimized for datasets up to 100K records. For larger datasets, consider pre-filtering by date range.

### No Results in Analysis

**Problem:** "Not enough data for analysis"
**Solution:** Ensure you have at least 30 days of transaction history and multiple customers

## 🎓 Best Practices

1. **Regular Updates:** Update your data daily for best insights
2. **Date Range:** Include at least 3-6 months of historical data
3. **Data Quality:** Ensure customer names and product codes are consistent
4. **Action on Insights:** Use the automated recommendations to guide business decisions
5. **Monitor Trends:** Check weekly/monthly trends regularly

## 🤝 Support & Contribution

For questions, issues, or feature requests:
- Review the documentation
- Check the example queries
- Test with sample data first

## 📄 License

This project is provided as-is for pharmacy sales analytics purposes.

## 🎉 Acknowledgments

Built with:
- Streamlit for the dashboard
- Plotly for interactive visualizations
- Scikit-learn for ML algorithms
- MLxtend for market basket analysis
- Pandas for data manipulation

---

**Made with ❤️ for pharmacies to make data-driven decisions**

