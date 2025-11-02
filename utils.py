"""Utility functions for the pharmacy sales analytics system."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


def format_currency(value: float, symbol: str = "$") -> str:
    """Format currency values."""
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage values."""
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 0) -> str:
    """Format numbers with thousand separators."""
    if decimals == 0:
        return f"{int(value):,}"
    return f"{value:,.{decimals}f}"


def calculate_growth_rate(old_value: float, new_value: float) -> float:
    """Calculate growth rate between two values."""
    if old_value == 0:
        return 0 if new_value == 0 else 100
    return ((new_value - old_value) / old_value) * 100


def get_date_range_description(start_date: datetime, end_date: datetime) -> str:
    """Get human-readable date range description."""
    days = (end_date - start_date).days
    
    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    elif days <= 7:
        return f"Last {days} days"
    elif days <= 30:
        return f"Last {days // 7} weeks"
    elif days <= 90:
        return f"Last {days // 30} months"
    else:
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"


def categorize_value(value: float, thresholds: Dict[str, float]) -> str:
    """
    Categorize a value based on thresholds.
    
    Args:
        value: Value to categorize
        thresholds: Dict like {'low': 10, 'medium': 50, 'high': 100}
    """
    sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1])
    
    for category, threshold in sorted_thresholds:
        if value <= threshold:
            return category
    
    return sorted_thresholds[-1][0]


def calculate_cohort_retention(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cohort retention rates.
    
    Args:
        data: DataFrame with customer_name, date columns
    """
    # Get first purchase date for each customer
    first_purchase = data.groupby('customer_name')['date'].min().reset_index()
    first_purchase.columns = ['customer_name', 'cohort_date']
    first_purchase['cohort'] = first_purchase['cohort_date'].dt.to_period('M')
    
    # Merge with main data
    data = data.merge(first_purchase[['customer_name', 'cohort']], on='customer_name')
    data['order_period'] = data['date'].dt.to_period('M')
    
    # Calculate periods since first purchase
    data['period_number'] = (
        (data['order_period'] - data['cohort']).apply(lambda x: x.n)
    )
    
    # Create cohort matrix
    cohort_data = data.groupby(['cohort', 'period_number'])['customer_name'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort', columns='period_number', values='customer_name')
    
    # Calculate retention rates
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    return retention


def detect_outliers_iqr(data: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """
    Detect outliers using IQR method.
    
    Args:
        data: Series of numeric values
        multiplier: IQR multiplier (1.5 for mild, 3 for extreme outliers)
    
    Returns:
        Boolean series indicating outliers
    """
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (data < lower_bound) | (data > upper_bound)


def calculate_moving_average(data: pd.Series, window: int = 7) -> pd.Series:
    """Calculate moving average."""
    return data.rolling(window=window, min_periods=1).mean()


def calculate_exponential_moving_average(data: pd.Series, span: int = 7) -> pd.Series:
    """Calculate exponential moving average."""
    return data.ewm(span=span, adjust=False).mean()


def get_trend_direction(values: List[float]) -> str:
    """
    Determine trend direction from a series of values.
    
    Returns: 'increasing', 'decreasing', or 'stable'
    """
    if len(values) < 2:
        return 'stable'
    
    # Compare first half to second half
    mid = len(values) // 2
    first_half = np.mean(values[:mid])
    second_half = np.mean(values[mid:])
    
    if first_half == 0:
        return 'stable'
    
    change_pct = ((second_half - first_half) / first_half) * 100
    
    if change_pct > 5:
        return 'increasing'
    elif change_pct < -5:
        return 'decreasing'
    else:
        return 'stable'


def create_time_bins(df: pd.DataFrame, date_column: str = 'date', bin_type: str = 'month') -> pd.DataFrame:
    """
    Create time bins for aggregation.
    
    Args:
        df: DataFrame with date column
        date_column: Name of date column
        bin_type: 'day', 'week', 'month', 'quarter', or 'year'
    """
    df = df.copy()
    
    if bin_type == 'day':
        df['time_bin'] = df[date_column].dt.date
    elif bin_type == 'week':
        df['time_bin'] = df[date_column].dt.to_period('W').astype(str)
    elif bin_type == 'month':
        df['time_bin'] = df[date_column].dt.to_period('M').astype(str)
    elif bin_type == 'quarter':
        df['time_bin'] = df[date_column].dt.to_period('Q').astype(str)
    elif bin_type == 'year':
        df['time_bin'] = df[date_column].dt.year
    else:
        raise ValueError(f"Invalid bin_type: {bin_type}")
    
    return df


def calculate_concentration_ratio(values: pd.Series, top_n: int = 5) -> float:
    """
    Calculate concentration ratio (e.g., CR5 = top 5 items' share of total).
    
    Returns percentage of total represented by top N items
    """
    total = values.sum()
    if total == 0:
        return 0
    
    top_sum = values.nlargest(top_n).sum()
    return (top_sum / total) * 100


def create_summary_report(data: Dict[str, Any], title: str = "Analysis Report") -> str:
    """Create a formatted summary report from analysis results."""
    report = f"\n{'='*60}\n"
    report += f"{title:^60}\n"
    report += f"{'='*60}\n\n"
    
    for key, value in data.items():
        key_formatted = key.replace('_', ' ').title()
        
        if isinstance(value, float):
            if 'pct' in key.lower() or 'percent' in key.lower():
                report += f"{key_formatted:.<40} {value:.1f}%\n"
            elif 'revenue' in key.lower() or 'value' in key.lower() or 'spend' in key.lower():
                report += f"{key_formatted:.<40} ${value:,.2f}\n"
            else:
                report += f"{key_formatted:.<40} {value:,.2f}\n"
        elif isinstance(value, int):
            report += f"{key_formatted:.<40} {value:,}\n"
        else:
            report += f"{key_formatted:.<40} {value}\n"
    
    report += f"\n{'='*60}\n"
    return report


def export_to_json(data: Any, filepath: str):
    """Export data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def export_to_csv(df: pd.DataFrame, filepath: str):
    """Export DataFrame to CSV."""
    df.to_csv(filepath, index=False, encoding='utf-8-sig')


def get_business_recommendations(metrics: Dict[str, float]) -> List[str]:
    """Generate business recommendations based on metrics."""
    recommendations = []
    
    # Revenue recommendations
    if 'revenue_growth_pct' in metrics:
        growth = metrics['revenue_growth_pct']
        if growth < -10:
            recommendations.append("⚠️ Revenue is declining. Review pricing strategy and customer retention.")
        elif growth > 20:
            recommendations.append("✅ Strong revenue growth. Consider scaling operations.")
    
    # Customer recommendations
    if 'repeat_rate_pct' in metrics:
        repeat_rate = metrics['repeat_rate_pct']
        if repeat_rate < 30:
            recommendations.append("💡 Low repeat purchase rate. Implement loyalty program.")
        elif repeat_rate > 60:
            recommendations.append("✅ Excellent customer retention. Maintain quality service.")
    
    # Inventory recommendations
    if 'num_slow_movers' in metrics:
        slow_movers = metrics['num_slow_movers']
        if slow_movers > 20:
            recommendations.append("📦 Many slow-moving products. Consider promotions or discontinuation.")
    
    # Churn recommendations
    if 'churn_risk_count' in metrics:
        at_risk = metrics['churn_risk_count']
        if at_risk > 10:
            recommendations.append("⚠️ Multiple customers at churn risk. Launch win-back campaign.")
    
    return recommendations


def calculate_pareto_threshold(values: pd.Series, percentage: float = 80) -> Tuple[float, int]:
    """
    Calculate the Pareto threshold (e.g., items contributing to 80% of total).
    
    Returns:
        Tuple of (threshold_value, number_of_items)
    """
    sorted_values = values.sort_values(ascending=False)
    cumsum = sorted_values.cumsum()
    total = sorted_values.sum()
    
    threshold_index = (cumsum >= total * percentage / 100).idxmax()
    threshold_position = sorted_values.index.get_loc(threshold_index)
    
    return sorted_values.iloc[threshold_position], threshold_position + 1


def generate_color_palette(n_colors: int, palette: str = 'blues') -> List[str]:
    """Generate a color palette for visualizations."""
    palettes = {
        'blues': ['#08519c', '#3182bd', '#6baed6', '#9ecae1', '#c6dbef'],
        'greens': ['#006d2c', '#31a354', '#74c476', '#a1d99b', '#c7e9c0'],
        'reds': ['#a50f15', '#de2d26', '#fb6a4a', '#fc9272', '#fcbba1'],
        'oranges': ['#a63603', '#e6550d', '#fd8d3c', '#fdae6b', '#fdd0a2']
    }
    
    base_colors = palettes.get(palette, palettes['blues'])
    
    if n_colors <= len(base_colors):
        return base_colors[:n_colors]
    else:
        # Repeat colors if needed
        return (base_colors * (n_colors // len(base_colors) + 1))[:n_colors]


class PerformanceTimer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"{self.name} took {elapsed:.2f} seconds")


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that DataFrame has required columns.
    
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names (lowercase, replace spaces with underscores)."""
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    return df


def aggregate_by_period(
    df: pd.DataFrame,
    date_column: str,
    value_column: str,
    agg_func: str = 'sum',
    period: str = 'D'
) -> pd.DataFrame:
    """
    Aggregate data by time period.
    
    Args:
        df: DataFrame with date and value columns
        date_column: Name of date column
        value_column: Name of value column to aggregate
        agg_func: Aggregation function ('sum', 'mean', 'count', etc.)
        period: Pandas period alias ('D', 'W', 'M', 'Q', 'Y')
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    df.set_index(date_column, inplace=True)
    
    result = df[value_column].resample(period).agg(agg_func).reset_index()
    return result

