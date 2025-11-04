# RFM Phone Number Mapping Feature

## Overview
This feature allows you to upload an optional Excel file to map customer names to phone numbers in the RFM segmentation analysis. Phone numbers will be displayed in customer tables and included in exported CSV files.

## How to Use

### 1. Prepare Your Phone Mapping File

Create an Excel file (.xlsx, .xls) or CSV file with the following columns:

| اسم العميل | التليفونات |
|------------|------------|
| أحمد محمد | 0123456789 |
| سارة علي | 0198765432 |
| محمد خالد | 0111222333 |

**Column Names:**
- **اسم العميل** - Customer name (must match exactly with customer names in your sales data)
- **التليفونات** - Phone number

**Alternative English Column Names:**
The system also accepts:
- `customer_name` instead of `اسم العميل`
- `phone` instead of `التليفونات`

### 2. Upload the Phone Mapping File

1. Navigate to the **RFM Analysis** page in the dashboard
2. Find the "📱 Optional: Upload Phone Numbers" section
3. Click on "Upload phone mapping file (optional)"
4. Select your Excel or CSV file
5. If successful, you'll see a confirmation message showing how many phone numbers were loaded

### 3. View Phone Numbers in RFM Analysis

Phone numbers will now appear in:

#### Tab 1: Overall Segmentation
- Customer details table for each segment
- Includes columns: Customer Name, Phone, Recency, Frequency, Monetary, RFM Scores

#### Tab 2: RFM by Category
- Customer details filtered by category and segment
- Includes columns: Customer Name, Phone, Segment, Recency, Frequency, Monetary

### 4. Export Segment Data with Phone Numbers

Each segment view now has export buttons that provide:

**📥 Download Customer Data (CSV)**
- All customers in the selected segment
- Complete RFM metrics
- Phone numbers (if mapping file was uploaded)

**📱 Copy Phone Numbers**
- Extracts all phone numbers from the displayed customers
- Automatically filters out empty phone numbers
- Formats as comma-separated list: `0123456789, 0198765432, 0111222333`
- Shows count of phone numbers available
- Provides two ways to access:
  1. Download as `.txt` file
  2. Expand "📋 View Phone Numbers" to copy directly (Ctrl+A, Ctrl+C)

**Export Options:**
- **Tab 1 (Overall Segmentation):** "📥 Download All [Segment Name] Customers (CSV)" + "📱 Copy Phone Numbers"
- **Tab 2 (RFM by Category):** "📥 Download Filtered Customer Data (CSV)" + "📱 Copy Phone Numbers"

The exported data can be used for:
- **SMS marketing campaigns** - Paste phone list directly into SMS service
- **WhatsApp bulk messaging** - Copy-paste into WhatsApp Business
- **Direct customer outreach** - Quick access to contact numbers
- **Call center operations** - Import phone list into dialer

## Features

### Automatic Column Detection
The system automatically detects various column name formats:
- Arabic: `اسم العميل`, `التليفونات`
- English: `customer_name`, `phone`
- Variations: Any column containing "customer", "عميل", "phone", "تليفون", "هاتف"

### Data Cleaning
- Automatically strips whitespace from customer names
- Removes duplicate customer entries (keeps first occurrence)
- Handles missing phone numbers gracefully (shows empty string)

### Smart Matching
- Customer names are matched exactly (case-sensitive)
- Only customers with matching names will show phone numbers
- Customers without phone mapping will show empty phone field

## File Format Example

You can click the **"📋 Show Format Example"** button in the dashboard to see a sample format.

### Excel Format (.xlsx)
```
Column A: اسم العميل
Column B: التليفونات

Row 1: أحمد محمد | 0123456789
Row 2: سارة علي | 0198765432
Row 3: محمد خالد | 0111222333
```

### CSV Format (.csv)
```csv
اسم العميل,التليفونات
أحمد محمد,0123456789
سارة علي,0198765432
محمد خالد,0111222333
```

## Use Cases

### 1. WhatsApp Bulk Messaging
1. Filter to "Champions" segment
2. Click "📱 Copy Phone Numbers"
3. Expand "📋 View Phone Numbers"
4. Select all (Ctrl+A) and copy (Ctrl+C)
5. Paste into WhatsApp Business for loyalty campaign

### 2. SMS Marketing Campaigns
1. Select "Potential Customers" segment
2. Click "📱 Copy Phone Numbers" to download `.txt` file
3. Import into your SMS service
4. Send targeted promotions

### 3. Re-engagement Campaigns
1. Filter "At Risk" customers by category
2. Copy phone numbers
3. Paste into messaging platform for personalized outreach

### 4. Win-back Campaigns
1. Export "Lost Customers" phone numbers
2. Use for special offer calls or SMS

### 5. Customer Service Outreach
1. Filter by specific segment
2. Copy phone numbers for proactive service calls

### 6. Quick Copy for Immediate Use
- Click expander to view all numbers
- Copy-paste directly into any application
- No need to download and open files

## Translations

The "Phone" column header automatically translates based on language setting:
- **English:** "Phone"
- **Arabic:** "التليفونات"

## Technical Details

### Supported File Formats
- Excel: `.xlsx`, `.xls`
- CSV: `.csv`

### Data Privacy
- Phone numbers are only stored in memory during the session
- No phone data is permanently saved by the system
- Exported CSV files are generated on-demand

### Performance
- Phone mapping is fast and efficient
- Works with thousands of customer records
- No performance impact if no phone file is uploaded

## Troubleshooting

### "Could not load phone mapping" Error
**Solution:** Ensure your file has the correct column names:
- `اسم العميل` and `التليفونات` (Arabic)
- or `customer_name` and `phone` (English)

### No Phone Numbers Showing
**Possible causes:**
1. Customer names don't match exactly between files
2. Extra spaces in customer names
3. Different spelling/formatting

**Solution:** Ensure customer names match exactly (including spaces and Arabic characters)

### Some Customers Missing Phone Numbers
This is normal - only customers in your phone mapping file will show phone numbers. Others will show an empty phone field.

## Summary

This feature seamlessly integrates phone number data into your RFM analysis workflow, enabling:
- ✅ Easy phone number mapping via Excel/CSV upload
- ✅ Phone numbers displayed in all RFM customer tables
- ✅ Phone numbers included in all CSV exports
- ✅ Multi-language support (English/Arabic)
- ✅ Smart column detection
- ✅ Ready for marketing campaigns and customer outreach

---

**Need Help?** The dashboard provides a format example button and helpful error messages to guide you through the process.

