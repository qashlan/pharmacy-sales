# Pharmacy Sales Analytics - User Guide

## 🚀 Quick Start (For End Users)

### First Time Setup

1. **Extract the ZIP file** to a location on your computer
   - Example: `C:\PharmacySalesAnalytics\`

2. **Open the folder** and find `PharmacySalesAnalytics.exe`

3. **Double-click** the executable
   - Windows might ask "Do you want to allow this app?" → Click **Yes**
   - A console window will appear - don't close it!

4. **Wait a few seconds** - your default browser will open automatically with the dashboard

5. **Start analyzing!** The application is now ready to use

### Every Time You Use It

1. Double-click `PharmacySalesAnalytics.exe`
2. Wait for browser to open automatically
3. When done, close the console window to stop the application

## 📊 Using the Dashboard

### Loading Your Data

The application needs pharmacy sales data in Excel format:

#### Required Columns:
- **Item Code**: Product identifier
- **Item Name**: Product name
- **Date**: Sale date (YYYY-MM-DD)
- **Selling Price**: Price per unit
- **Units/Pieces/Quantity**: Amount sold
- **Customer Name**: Customer identifier (optional)
- **Category**: Product category (optional)

#### How to Upload:

1. In the sidebar, click **"Upload Sales Data"**
2. Click **"Browse files"**
3. Select your Excel file (.xlsx)
4. Wait for it to load
5. Start exploring!

### Features Overview

#### 📈 Sales Analysis
- View overall performance metrics
- Analyze revenue trends (daily, weekly, monthly)
- Identify top-performing products
- Detect sales anomalies
- Track refunds and returns

#### 👥 Customer Insights
- Analyze customer behavior
- Identify high-value customers
- Detect churn risk
- Track repeat customers
- Find new customer trends

#### 📦 Product Performance
- Fast vs slow-moving products
- ABC classification analysis
- Product lifecycle stages
- Inventory planning signals

#### 🏬 Inventory Management
- Monitor stock levels
- Get reorder recommendations
- Predict stockout risks
- Identify overstocked items
- Category-wise analysis

#### 🎯 RFM Segmentation
- Segment customers by behavior
- Identify champions and loyal customers
- Find at-risk customers
- Get recommended actions for each segment

#### 🔄 Refill Prediction
- Predict when customers will reorder
- Identify overdue refills
- Forecast upcoming refills
- Estimate order values

#### 🛒 Cross-Sell Analysis
- Find product bundles
- Get product recommendations
- Analyze market basket patterns
- Identify complementary products

#### 🤖 AI Query Assistant
- Ask questions in plain English
- Get AI-powered insights
- Have conversations about your data
- (Requires OpenAI API key for full features)

#### 📑 Export & Reports
- Generate comprehensive reports
- Export data to CSV
- Download charts and analyses

## 🌐 Language Support

Switch between English and Arabic:
- Click the **Language** dropdown in the sidebar
- Select your preferred language
- The entire interface updates instantly

## ⚙️ Configuration

### Setting Up AI Features (Optional)

To use AI-powered insights:

1. Get an OpenAI API key from https://platform.openai.com/
2. Create a file named `.env` in the application folder
3. Add this line: `OPENAI_API_KEY=your_key_here`
4. Restart the application

### Changing Settings

Edit `config.py` to customize:
- Analysis parameters
- RFM scoring
- Inventory thresholds
- Lead times
- Date formats

## 💡 Tips & Best Practices

### Data Preparation

✅ **DO**:
- Use consistent date formats
- Include product categories
- Keep customer names standardized
- Remove duplicate entries
- Use positive numbers for sales, negative for refunds

❌ **DON'T**:
- Mix different date formats
- Leave many blank fields
- Use special characters in names
- Have inconsistent product codes

### Performance Tips

- **Large datasets** (>100,000 rows): May take 30-60 seconds to load
- **Cross-sell analysis**: Works best with 1000+ multi-item orders
- **Refill predictions**: Needs at least 3 months of data
- **AI features**: Require internet connection

### Common Use Cases

1. **Weekly Sales Review**
   - Upload latest data
   - Check Sales Analysis → Overall Performance
   - Review top products and trends

2. **Inventory Management**
   - Upload inventory file
   - Check Inventory Management tab
   - Review reorder alerts
   - Export reorder list

3. **Customer Retention**
   - Go to RFM Segmentation
   - Identify "At Risk" customers
   - Export list for marketing campaigns

4. **Product Bundling**
   - Check Cross-Sell Analysis
   - Review product bundles
   - Get recommendations for displays

## 🐛 Troubleshooting

### Application Won't Start

**Problem**: Double-clicking does nothing

**Solutions**:
1. Right-click → Run as Administrator
2. Check if another instance is running (check Task Manager)
3. Restart your computer
4. Check antivirus isn't blocking it

### Browser Doesn't Open

**Problem**: Application starts but no browser window

**Solution**:
1. Look at the console window for the URL (usually `http://localhost:8501`)
2. Manually copy and paste the URL into your browser

### "Port Already in Use" Error

**Problem**: Error message about port being used

**Solution**:
1. Close any other running instances
2. Restart the application
3. If persists, restart your computer

### Upload Fails

**Problem**: File won't upload or loads incorrectly

**Solutions**:
1. Check file format (must be .xlsx or .csv)
2. Ensure required columns exist
3. Check for special characters in column names
4. Try with sample data first
5. Verify file isn't corrupted

### Charts Don't Display

**Problem**: Blank spaces where charts should be

**Solutions**:
1. Wait a few seconds (large datasets take time)
2. Try a different browser
3. Clear browser cache
4. Check if data has enough records

### Slow Performance

**Problem**: Application is slow or unresponsive

**Solutions**:
1. Close unnecessary browser tabs
2. Filter data to smaller date ranges
3. Close other applications
4. Check if your computer meets minimum requirements:
   - 4GB RAM (8GB recommended)
   - Modern processor (Intel i3 or equivalent)
   - Windows 10/11

## 📞 Getting Help

### Error Messages

If you see an error:
1. Take a screenshot of the console window
2. Note what you were doing when it occurred
3. Try restarting the application
4. Check the console for detailed error messages

### Data Issues

If results don't look right:
1. Verify your data format matches requirements
2. Check for duplicate records
3. Ensure dates are valid
4. Try with sample data to confirm app works

## 🔒 Privacy & Security

- **All data stays on your computer** - nothing is uploaded to cloud
- **No telemetry** - we don't track usage
- **OpenAI integration** (if enabled) only sends anonymized queries
- **Data files** are stored in the application folder
- **Exported reports** go to the `output/` folder

## 📁 File Locations

The application creates these folders:

```
PharmacySalesAnalytics\
├── data\              ← Your uploaded data
├── output\
│   ├── charts\       ← Generated charts
│   ├── reports\      ← Exported reports
│   └── inventory\    ← Inventory analysis files
```

You can access these folders directly to:
- View exported files
- Backup your data
- Share reports with colleagues

## 🎓 Learning Resources

### Sample Data

The application includes sample data for testing:
- Click **"Use Sample Data"** in the sidebar
- Explore all features without uploading your own data
- Good for training and learning

### Tutorial Workflow

1. **Start with Sales Analysis** - understand your overall performance
2. **Move to Customer Insights** - know your customers
3. **Check Product Performance** - optimize inventory
4. **Use RFM Segmentation** - target marketing campaigns
5. **Try Cross-Sell Analysis** - increase average order value
6. **Explore AI Query** - ask specific questions

## 📊 Exporting & Sharing

### Export Options

- **CSV files**: Open in Excel, Google Sheets
- **Charts**: Downloadable as PNG images
- **Reports**: Comprehensive Excel reports

### Sharing Results

1. Generate reports from Export & Reports tab
2. Find files in `output/reports/` folder
3. Share via email or shared drive
4. Include charts from `output/charts/`

## ⚡ Keyboard Shortcuts

- **Ctrl + C** (in console): Stop the application
- **F5** (in browser): Refresh the dashboard
- **Ctrl + F** (in browser): Search on page

## 🔄 Updates

When a new version is released:
1. Close the current application
2. Delete the old folder (after backing up your data)
3. Extract the new version
4. Copy your data files to the new `data/` folder
5. Restart the application

---

## ✨ Quick Tips

💡 **Tip 1**: Keep your data file updated weekly for best insights

💡 **Tip 2**: Use filters to focus on specific products or periods

💡 **Tip 3**: Export reports before closing to save your analysis

💡 **Tip 4**: The AI Query Assistant can answer custom questions about your data

💡 **Tip 5**: RFM Segmentation is great for customer retention campaigns

---

**Need Help?** Check the console window for detailed error messages or contact your IT support.

**Enjoying the app?** Share it with colleagues to help them analyze their pharmacy data too!



