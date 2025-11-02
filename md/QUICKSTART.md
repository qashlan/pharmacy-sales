# 🚀 Quick Start Guide

Get started with Pharmacy Sales Analytics in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Step 3: Load Your Data

### Option A: Use Sample Data (for testing)
The system will automatically load sample data if no file is uploaded.

### Option B: Upload Your Sales Data
1. Click "Upload Sales Data" in the sidebar
2. Select your CSV or Excel file
3. Your data should have these columns:
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

## Step 4: Explore the Analytics

Navigate through different sections:

### 📊 Sales Analysis
- View total revenue and trends
- Identify top products and categories
- Analyze time-based patterns
- Detect sales anomalies

### 👥 Customer Insights
- Find your most valuable customers
- Identify customers at risk of churning
- Analyze customer segments
- Track new customer acquisition

### 📦 Product Performance
- See fast-moving vs slow-moving products
- ABC classification for inventory
- Product lifecycle analysis
- Get inventory planning signals

### 🎯 RFM Segmentation
- Segment customers by Recency, Frequency, Monetary
- Get actionable recommendations for each segment
- Identify VIP customers and at-risk customers

### 💊 Refill Prediction
- Find overdue refills
- Predict upcoming refills
- View customer refill schedules
- Track refill compliance

### 🔗 Cross-Sell Analysis
- Discover product bundles
- Find products bought together
- Get cross-sell recommendations
- Analyze market basket patterns

## Step 5: Ask Questions in Natural Language

Try asking questions like:
- "What is the total revenue?"
- "Show me the top 10 products"
- "Which customers are at risk of churning?"
- "What products should I reorder?"
- "Show me overdue refills"

## Step 6: Export Reports

1. Go to "📥 Export & Reports"
2. Select report type
3. Click "Generate Report"
4. Download as CSV

## 💡 Tips for Best Results

1. **Use at least 3-6 months of historical data**
2. **Ensure customer names and product codes are consistent**
3. **Update data regularly (daily or weekly)**
4. **Act on the automated recommendations**
5. **Monitor key metrics weekly**

## 📝 Example Data Format

Create a CSV file with these columns:

```csv
Item Code,Item Name,Units,Pieces,Selling Price,Total,Sale Type,Customer Name,Date,Time,Category
ITEM001,Paracetamol 500mg,2,20,12.50,25.00,Cash,Customer_001,2024-01-15,14:30:00,Pain Relief
ITEM002,Amoxicillin 250mg,1,10,45.00,45.00,Insurance,Customer_002,2024-01-15,14:35:00,Antibiotics
ITEM003,Vitamin D3,3,30,8.00,24.00,Cash,Customer_001,2024-01-15,14:32:00,Vitamins
```

## 🎯 Key Metrics to Monitor

- **Total Revenue**: Track overall sales performance
- **Average Order Value**: Measure transaction size
- **Repeat Purchase Rate**: Customer loyalty indicator
- **Churn Risk**: Customers needing attention
- **Fast Movers**: Products selling quickly
- **Overdue Refills**: Revenue opportunity

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Make sure Streamlit is installed
pip install streamlit

# Try running with full path
python -m streamlit run dashboard.py
```

### Data upload issues
- Check that your CSV has all required columns
- Ensure dates are in YYYY-MM-DD format
- Verify no special characters in customer names

### Analysis showing "Not enough data"
- You need at least 30 days of transaction history
- Ensure multiple customers and products in dataset
- Check that dates are parsed correctly

## 📚 Next Steps

1. **Review the Full README** - Detailed documentation of all features
2. **Check example_usage.py** - Code examples for programmatic access
3. **Customize config.py** - Adjust thresholds and parameters
4. **Schedule Regular Updates** - Set up automated data imports

## 🆘 Need Help?

Common questions:

**Q: How much data do I need?**
A: At least 30 days of transaction history with multiple customers and products.

**Q: Can I use Excel files?**
A: Yes! Both .xlsx and .csv formats are supported.

**Q: How do I interpret RFM scores?**
A: Higher scores (4-5) are better. See the dashboard for segment explanations.

**Q: What if I don't have "Pieces" column?**
A: The system will use "Units" instead. Both are handled automatically.

**Q: Can I run this on a server?**
A: Yes! Use `streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0`

## 🎉 You're Ready!

Start exploring your pharmacy sales data and making data-driven decisions!

For detailed documentation, see README.md

