"""Data loading and preprocessing module."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple
import config


class DataLoader:
    """Handles data loading and preprocessing for pharmacy sales data."""
    
    def __init__(self, file_path: str):
        """
        Initialize the data loader.
        
        Args:
            file_path: Path to the sales data file (CSV or Excel)
        """
        self.file_path = file_path
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self) -> pd.DataFrame:
        """Load data from file."""
        try:
            if self.file_path.endswith('.csv'):
                self.raw_data = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xlsx', '.xls')):
                self.raw_data = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel.")
            
            print(f"Loaded {len(self.raw_data)} records from {self.file_path}")
            return self.raw_data
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Preprocess the raw data.
        
        Handles:
        - Column name standardization
        - Date/time parsing
        - Order ID computation
        - Data type conversion
        - Missing value handling
        """
        if self.raw_data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        df = self.raw_data.copy()
        
        # Standardize column names
        df = self._standardize_columns(df)
        
        # Parse dates and times
        df = self._parse_datetime(df)
        
        # Handle units and pieces
        df = self._process_quantities(df)
        
        # Handle customer names (make optional)
        df = self._process_customer_names(df)
        
        # Use receipt column as order_id or compute if not present
        df = self._process_order_ids(df)
        
        # Clean and validate data
        df = self._clean_data(df)
        
        self.processed_data = df
        print(f"Preprocessed {len(df)} records with {df['order_id'].nunique()} unique orders")
        
        return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names."""
        # Try to map columns
        column_map = {}
        df_columns = df.columns.tolist()
        
        for original_col, standard_col in config.COLUMN_MAPPING.items():
            if original_col in df_columns:
                column_map[original_col] = standard_col
            # Try case-insensitive matching
            else:
                for col in df_columns:
                    if col.lower().strip() == original_col.lower().strip():
                        column_map[col] = standard_col
                        break
        
        df = df.rename(columns=column_map)
        
        # Verify required columns exist (customer_name is now optional)
        required_cols = ['item_code', 'item_name', 'date', 'total']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    def _parse_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse date and time columns."""
        # Parse date column (may already contain datetime with time component)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Check if date column already has time information (not just 00:00:00)
        has_time_in_date = False
        if df['date'].notna().any():
            # Check if any non-zero times exist
            has_time_in_date = (df['date'].dt.hour != 0).any() or (df['date'].dt.minute != 0).any() or (df['date'].dt.second != 0).any()
        
        # Parse separate time column if available and has data
        if 'time' in df.columns and df['time'].notna().any():
            # Store original time strings before conversion
            time_strings = df['time'].astype(str).copy()
            
            # Try to parse time
            try:
                # If time is already a time object, keep it
                if not pd.api.types.is_datetime64_any_dtype(df['time']):
                    df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.time
                else:
                    df['time'] = df['time'].dt.time
            except:
                df['time'] = pd.to_datetime(df['time'], errors='coerce').dt.time
            
            # Create datetime column by combining date and time
            # Use the original time strings for better compatibility
            try:
                df['datetime'] = pd.to_datetime(
                    df['date'].dt.date.astype(str) + ' ' + time_strings,
                    errors='coerce'
                )
            except:
                # Fallback method using time objects
                df['datetime'] = pd.to_datetime(
                    df['date'].dt.date.astype(str) + ' ' + df['time'].astype(str),
                    errors='coerce'
                )
        elif has_time_in_date:
            # Date column already has time info - preserve it
            df['datetime'] = df['date']
            df['time'] = df['date'].dt.time
        else:
            # No time info available, use date only
            df['datetime'] = df['date']
            df['time'] = df['date'].dt.time
        
        return df
    
    def _process_quantities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process units, pieces, and quantity columns.
        
        Understanding Units, Pieces, and Quantity:
        ==========================================
        - **Units**: Full units/boxes (integer) - informational
        - **Pieces**: Loose pieces (integer) - informational  
        - **Quantity**: Total effective quantity (can be fractional) - AUTHORITATIVE ⭐
        
        Real-World Examples:
        -------------------
        1. Units=1, Pieces=1, Quantity=1.50
           → Sold 1 full unit + 1 loose piece = 1.50 units total
        
        2. Units=0, Pieces=1, Quantity=0.50
           → Sold only 1 loose piece = 0.50 units total
        
        3. Units=2, Pieces=0, Quantity=2.00
           → Sold 2 full units = 2.00 units total
        
        Processing Logic:
        ----------------
        - If 'quantity' column exists → Use it as authoritative (can be fractional)
        - If 'quantity' missing → Calculate from units and pieces (legacy):
          * If pieces > 0, use pieces as quantity
          * Otherwise, use units as quantity
        
        All calculations in the system use **Quantity** as the measure of items sold.
        """
        # Ensure numeric types for units (always integer)
        if 'units' in df.columns:
            df['units'] = pd.to_numeric(df['units'], errors='coerce').fillna(0).astype(int)
        else:
            df['units'] = 1
        
        # Ensure numeric types for pieces (always integer)
        if 'pieces' in df.columns:
            df['pieces'] = pd.to_numeric(df['pieces'], errors='coerce').fillna(0).astype(int)
        else:
            df['pieces'] = 0
        
        # Handle quantity column (can be fractional)
        if 'quantity' in df.columns:
            # Quantity column exists in the raw data - use it directly
            # Keep as float to preserve fractional values (0.50, 0.80, etc.)
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
            print("Using 'Quantity' column from data (supports fractional values)")
        else:
            # Calculate quantity from units and pieces
            # If pieces > 0, use pieces, otherwise use units
            df['quantity'] = df.apply(
                lambda row: row['pieces'] if row['pieces'] > 0 else row['units'],
                axis=1
            )
            print("Calculated 'quantity' from 'units' and 'pieces' columns")
        
        return df
    
    def _process_customer_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process customer names, handling empty/null values.
        
        Empty customer names will be replaced with 'Unknown Customer'.
        """
        # Ensure customer_name column exists
        if 'customer_name' not in df.columns:
            df['customer_name'] = 'Unknown Customer'
        else:
            # Replace empty, null, or whitespace-only values with 'Unknown Customer'
            df['customer_name'] = df['customer_name'].fillna('Unknown Customer')
            df['customer_name'] = df['customer_name'].astype(str).str.strip()
            df.loc[df['customer_name'] == '', 'customer_name'] = 'Unknown Customer'
            df.loc[df['customer_name'].str.lower() == 'nan', 'customer_name'] = 'Unknown Customer'
        
        return df
    
    def _process_order_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process order IDs from receipt column or compute if not present.
        
        If 'receipt' column exists, use it as order_id.
        Otherwise, compute order IDs based on customer and datetime.
        """
        # Check if receipt column exists and has valid data
        if 'receipt' in df.columns and df['receipt'].notna().any():
            # Use receipt as order_id
            df['order_id'] = df['receipt'].fillna(-1)  # Fill missing receipts with -1
            
            # Convert to appropriate type (try int, fallback to string)
            try:
                df['order_id'] = df['order_id'].astype(int)
            except (ValueError, TypeError):
                # If conversion fails, keep as string
                df['order_id'] = df['order_id'].astype(str)
            
            print(f"Using receipt column as order_id: {df['order_id'].nunique()} unique orders")
        else:
            # Compute order IDs using the old logic
            df = self._compute_order_ids(df)
            print(f"Computed order_id from datetime: {df['order_id'].nunique()} unique orders")
        
        return df
    
    def _compute_order_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute order IDs based on customer and purchase datetime.
        
        Orders are grouped by:
        - Same customer
        - Same date
        - Within a time window (e.g., 30 minutes)
        
        OPTIMIZED: Uses vectorized operations instead of nested loops.
        """
        # Sort by customer and datetime
        df = df.sort_values(['customer_name', 'datetime']).reset_index(drop=True)
        
        # Calculate time difference from previous row (in minutes)
        df['time_diff'] = df['datetime'].diff().dt.total_seconds() / 60
        
        # Check if customer changed from previous row
        df['customer_changed'] = df['customer_name'] != df['customer_name'].shift(1)
        
        # New order if: customer changed OR time gap > 30 minutes OR time is NaN
        df['new_order'] = (
            df['customer_changed'] | 
            (df['time_diff'] > 30) | 
            (df['time_diff'].isna())
        )
        
        # Assign order IDs using cumulative sum
        df['order_id'] = df['new_order'].cumsum() - 1
        
        # Clean up temporary columns
        df = df.drop(columns=['time_diff', 'customer_changed', 'new_order'])
        
        df['order_id'] = df['order_id'].astype(int)
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data."""
        # Remove rows with missing critical data (customer_name is now optional)
        df = df.dropna(subset=['date', 'total'])
        
        # Ensure numeric columns
        numeric_cols = ['selling_price', 'total', 'quantity', 'units', 'pieces']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Fill missing categorical columns and ensure they're strings
        categorical_cols = ['sale_type', 'category', 'item_code', 'item_name', 'customer_name']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna('Unknown')
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Add derived columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.isocalendar().week
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_name'] = df['date'].dt.day_name()
        
        # REFUND HANDLING: Identify refund transactions
        # A refund is indicated by a negative total value
        df['is_refund'] = df['total'] < 0
        
        # Count refunds for reporting
        num_refunds = df['is_refund'].sum()
        if num_refunds > 0:
            refund_value = df[df['is_refund']]['total'].sum()
            print(f"⚠ Identified {num_refunds} refund transactions (total: ${refund_value:,.2f})")
        
        # For refunds, quantities should also be negative to maintain consistency
        # Ensure quantity matches the sign of total for refunds
        df.loc[df['is_refund'], 'quantity'] = -abs(df.loc[df['is_refund'], 'quantity'])
        
        # SERVICE ITEM HANDLING: Flag service items (non-physical products)
        # Service items contribute to revenue but are not actual products
        df['is_service'] = df['item_name'].isin(config.SERVICE_ITEMS)
        
        # Count service transactions for reporting
        num_services = df['is_service'].sum()
        if num_services > 0:
            service_revenue = df[df['is_service']]['total'].sum()
            print(f"ℹ️  Identified {num_services} service transactions (revenue: ${service_revenue:,.2f})")
            print(f"   Service items: {', '.join(config.SERVICE_ITEMS)}")
        
        return df
    
    def get_data_summary(self) -> dict:
        """Get summary statistics of the processed data."""
        if self.processed_data is None:
            raise ValueError("No processed data available.")
        
        df = self.processed_data
        
        # Separate refunds from regular sales
        sales_df = df[~df['is_refund']]
        refunds_df = df[df['is_refund']]
        
        # Separate service items from products
        service_df = df[df['is_service']]
        product_df = df[~df['is_service']]
        
        # Calculate net revenue (sales - refunds)
        gross_revenue = sales_df['total'].sum()
        refund_amount = abs(refunds_df['total'].sum())
        net_revenue = df['total'].sum()  # This already includes negative refunds
        
        # Calculate service vs product revenue
        service_revenue = service_df[~service_df['is_refund']]['total'].sum()
        product_revenue = product_df[~product_df['is_refund']]['total'].sum()
        
        return {
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'gross_revenue': gross_revenue,
            'refund_amount': refund_amount,
            'net_revenue': net_revenue,
            'total_revenue': net_revenue,  # Alias for backward compatibility
            'service_revenue': service_revenue,
            'product_revenue': product_revenue,
            'service_revenue_pct': (service_revenue / gross_revenue * 100) if gross_revenue > 0 else 0,
            'refund_rate_pct': (refund_amount / gross_revenue * 100) if gross_revenue > 0 else 0,
            'num_refunds': len(refunds_df),
            'num_sales': len(sales_df),
            'num_services': len(service_df[~service_df['is_refund']]),
            'unique_customers': df['customer_name'].nunique(),
            'unique_products': df['item_name'].nunique(),
            'unique_products_excl_services': product_df['item_name'].nunique(),
            'unique_orders': df['order_id'].nunique(),
            'avg_order_value': df.groupby('order_id')['total'].sum().mean(),
            'total_quantity_sold': sales_df['quantity'].sum(),  # Only count positive sales
            'total_quantity_refunded': abs(refunds_df['quantity'].sum())
        }


def load_sample_data() -> pd.DataFrame:
    """Generate sample data for testing purposes with receipt column and unknown customers."""
    np.random.seed(42)
    
    # Sample data generation
    n_records = 1000
    start_date = datetime(2024, 1, 1)
    
    customers = [f"Customer_{i}" for i in range(1, 51)]
    # Add some None/empty customers for testing
    customers.extend([None, '', '  '])  # These will become "Unknown Customer"
    
    items = [
        ('ITEM001', 'Paracetamol 500mg', 'Pain Relief'),
        ('ITEM002', 'Amoxicillin 250mg', 'Antibiotics'),
        ('ITEM003', 'Vitamin D3', 'Vitamins'),
        ('ITEM004', 'Omeprazole 20mg', 'Digestive'),
        ('ITEM005', 'Aspirin 100mg', 'Pain Relief'),
        ('ITEM006', 'Cetirizine 10mg', 'Allergy'),
        ('ITEM007', 'Metformin 500mg', 'Diabetes'),
        ('ITEM008', 'Atorvastatin 20mg', 'Cardiovascular'),
        ('ITEM009', 'Losartan 50mg', 'Cardiovascular'),
        ('ITEM010', 'Insulin Glargine', 'Diabetes'),
    ]
    
    sale_types = ['Cash', 'Insurance', 'Credit']
    
    records = []
    receipt_counter = 1
    
    for _ in range(n_records):
        item_code, item_name, category = items[np.random.choice(len(items))]
        date = start_date + timedelta(days=np.random.randint(0, 300))
        time = f"{np.random.randint(8, 20):02d}:{np.random.randint(0, 60):02d}:{np.random.randint(0, 60):02d}"
        selling_price = np.random.uniform(5, 200)
        
        # Generate realistic quantity data:
        # - Units: always integer (full units)
        # - Pieces: always integer (number of pieces)
        # - Quantity: can be fractional (actual quantity sold)
        
        if np.random.random() > 0.85:  # 15% chance of fractional sale
            # Fractional sale: quantity is fractional (0.25, 0.33, 0.5, 0.75, 0.80)
            units = 0
            pieces = 0
            quantity = np.random.choice([0.25, 0.33, 0.5, 0.75, 0.80])
        elif np.random.random() > 0.5:  # 50% of remaining: piece-based sale
            # Selling by pieces (units=0, but pieces>0)
            units = 0
            pieces = np.random.randint(1, 10)  # Integer pieces
            quantity = pieces  # Quantity equals pieces
        else:  # Remaining: normal unit-based sale
            # Normal sale by units
            units = np.random.randint(1, 5)
            pieces = units * np.random.choice([10, 20, 30])  # Integer pieces
            quantity = units  # Quantity equals units
        
        total = selling_price * quantity
        
        # Generate receipt ID (some items may share same receipt for multi-item orders)
        if np.random.random() > 0.3:  # 70% chance of new receipt
            receipt_counter += 1
        
        records.append({
            'Receipt': receipt_counter,
            'Item Code': item_code,
            'Item Name': item_name,
            'Units': units,
            'Pieces': pieces,
            'Quantity': quantity,
            'Selling Price': selling_price,
            'Total': total,
            'Sale Type': np.random.choice(sale_types),
            'Customer Name': np.random.choice(customers),  # May include None or empty
            'Date': date.strftime('%Y-%m-%d'),
            'Time': time,
            'Category': category
        })
    
    return pd.DataFrame(records)

