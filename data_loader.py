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
        
        # Compute order IDs
        df = self._compute_order_ids(df)
        
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
        
        # Verify required columns exist
        required_cols = ['item_code', 'item_name', 'customer_name', 'date', 'total']
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
        """Process units and pieces columns."""
        # Ensure numeric types
        if 'units' in df.columns:
            df['units'] = pd.to_numeric(df['units'], errors='coerce').fillna(0)
        else:
            df['units'] = 1
        
        if 'pieces' in df.columns:
            df['pieces'] = pd.to_numeric(df['pieces'], errors='coerce').fillna(0)
        else:
            df['pieces'] = 0
        
        # Calculate total quantity
        # If pieces > 0, use pieces, otherwise use units
        df['quantity'] = df.apply(
            lambda row: row['pieces'] if row['pieces'] > 0 else row['units'],
            axis=1
        )
        
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
        # Remove rows with missing critical data
        df = df.dropna(subset=['customer_name', 'date', 'total'])
        
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
        
        return df
    
    def get_data_summary(self) -> dict:
        """Get summary statistics of the processed data."""
        if self.processed_data is None:
            raise ValueError("No processed data available.")
        
        df = self.processed_data
        
        return {
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'total_revenue': df['total'].sum(),
            'unique_customers': df['customer_name'].nunique(),
            'unique_products': df['item_name'].nunique(),
            'unique_orders': df['order_id'].nunique(),
            'avg_order_value': df.groupby('order_id')['total'].sum().mean(),
            'total_quantity_sold': df['quantity'].sum()
        }


def load_sample_data() -> pd.DataFrame:
    """Generate sample data for testing purposes."""
    np.random.seed(42)
    
    # Sample data generation
    n_records = 1000
    start_date = datetime(2024, 1, 1)
    
    customers = [f"Customer_{i}" for i in range(1, 51)]
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
    for _ in range(n_records):
        item_code, item_name, category = items[np.random.choice(len(items))]
        date = start_date + timedelta(days=np.random.randint(0, 300))
        time = f"{np.random.randint(8, 20):02d}:{np.random.randint(0, 60):02d}:{np.random.randint(0, 60):02d}"
        units = np.random.randint(1, 5)
        pieces = units * np.random.choice([1, 10, 20, 30])
        selling_price = np.random.uniform(5, 200)
        total = selling_price * units
        
        records.append({
            'Item Code': item_code,
            'Item Name': item_name,
            'Units': units,
            'Pieces': pieces,
            'Selling Price': selling_price,
            'Total': total,
            'Sale Type': np.random.choice(sale_types),
            'Customer Name': np.random.choice(customers),
            'Date': date.strftime('%Y-%m-%d'),
            'Time': time,
            'Category': category
        })
    
    return pd.DataFrame(records)

