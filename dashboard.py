"""Interactive Streamlit dashboard for pharmacy sales analytics."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Import analysis modules
from data_loader import DataLoader, load_sample_data
from sales_analysis import SalesAnalyzer
from customer_analysis import CustomerAnalyzer
from product_analysis import ProductAnalyzer
from inventory_management import InventoryManager, load_inventory_from_file, create_sample_inventory
from rfm_analysis import RFMAnalyzer
from refill_prediction import RefillPredictor
from cross_sell_analysis import CrossSellAnalyzer
from ai_query import AIQueryEngine, create_query_examples
import config

# Configure pandas to display datetime with time component
pd.set_option('display.max_colwidth', None)
pd.options.display.date_dayfirst = False
pd.options.display.date_yearfirst = True

# Configure Plotly for Streamlit dark theme
import plotly.io as pio
pio.templates.default = "plotly_dark"

# Page configuration
st.set_page_config(
    page_title="Pharmacy Sales Analytics",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language before any UI rendering
if 'language' not in st.session_state:
    st.session_state.language = config.DEFAULT_LANGUAGE

# Get current language
CURRENT_LANG = st.session_state.language

# Translation helper function (global)
def t(key, **kwargs):
    """Get translation for key with optional formatting."""
    translations = config.TRANSLATIONS.get(CURRENT_LANG, config.TRANSLATIONS['en'])
    text = translations.get(key, key)
    # Format with any provided kwargs (e.g., {n}, {days}, {product})
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # If formatting fails, return unformatted text
    return text

def tc(column_name):
    """Translate column name based on current language."""
    col_translations = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
    return col_translations.get(column_name, column_name)

def translate_columns(df, column_mapping=None):
    """
    Translate dataframe column names to current language.
    
    Args:
        df: DataFrame to translate
        column_mapping: Optional dict of column renames to apply before translation
                       (maps raw column name to standard name)
    
    Returns:
        DataFrame with translated column names
    """
    df = df.copy()
    
    # Apply custom mapping first if provided
    if column_mapping:
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Then translate to current language
    col_translations = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
    df = df.rename(columns={k: col_translations.get(k, k) for k in df.columns})
    
    return df

# Custom CSS with RTL support
def get_custom_css(is_rtl=False):
    """Generate custom CSS based on language direction."""
    direction = "rtl" if is_rtl else "ltr"
    text_align = "right" if is_rtl else "left"
    slider_transform = "scaleX(-1)" if is_rtl else "scaleX(1)"
    
    return f"""
    <style>
    /* Base layout */
    .main {{
        padding: 0rem 1rem;
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for sidebar */
    [data-testid="stSidebar"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for metrics */
    .stMetric {{
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    h1 {{
        color: #1f77b4;
    }}
    
    h2 {{
        color: #2ca02c;
    }}
    
    /* Tabs */
    .stTabs {{
        direction: {direction};
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        direction: {direction};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    .stTabs [data-baseweb="tab-panel"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Buttons */
    .stButton > button {{
        direction: {direction};
    }}
    
    /* Text inputs and selectboxes */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Enhanced RTL support for selectbox */
    .stSelectbox {{
        direction: {direction};
    }}
    
    .stSelectbox [data-baseweb="select"] {{
        direction: {direction};
    }}
    
    .stSelectbox [data-baseweb="select"] > div {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL dropdown menu */
    .stSelectbox [role="listbox"],
    .stSelectbox [data-baseweb="popover"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    .stSelectbox [role="option"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Enhanced RTL support for multiselect */
    .stMultiSelect {{
        direction: {direction};
    }}
    
    .stMultiSelect [data-baseweb="select"] {{
        direction: {direction};
    }}
    
    .stMultiSelect [data-baseweb="select"] > div {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL for multiselect tags/chips */
    .stMultiSelect [data-baseweb="tag"] {{
        direction: {direction};
    }}
    
    /* RTL dropdown menu for multiselect */
    .stMultiSelect [role="listbox"],
    .stMultiSelect [data-baseweb="popover"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    .stMultiSelect [role="option"] {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for date input */
    .stDateInput {{
        direction: {direction};
    }}
    
    .stDateInput > div > div > input {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for radio buttons */
    .stRadio {{
        direction: {direction};
    }}
    
    .stRadio > div {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    .stRadio [role="radiogroup"] {{
        direction: {direction};
    }}
    
    .stRadio label {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for checkbox */
    .stCheckbox {{
        direction: {direction};
    }}
    
    .stCheckbox > label {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL support for slider */
    .stSlider {{
        direction: ltr;
    }}
    
    /* Flip slider track and thumb in RTL mode */
    .stSlider [data-baseweb="slider"] {{
        transform: {slider_transform};
    }}
    
    /* Keep labels readable - no transform */
    .stSlider label,
    .stSlider > label {{
        direction: ltr;
        text-align: {text_align};
    }}
    
    .stSlider [data-testid="stMarkdownContainer"] {{
        direction: ltr;
    }}
    
    /* RTL support for number input */
    .stNumberInput {{
        direction: {direction};
    }}
    
    .stNumberInput > div > div > input {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Dataframes */
    .stDataFrame {{
        direction: {direction};
    }}
    
    /* RTL support for table structure */
    .stDataFrame table {{
        direction: {direction};
    }}
    
    .stDataFrame thead th,
    .stDataFrame tbody td {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL for all table elements */
    div[data-testid="stDataFrame"] table,
    div[data-testid="stDataFrame"] thead,
    div[data-testid="stDataFrame"] tbody,
    div[data-testid="stDataFrame"] tr,
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* RTL for styled dataframes */
    .dataframe {{
        direction: {direction};
    }}
    
    .dataframe thead th,
    .dataframe tbody td {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Row hover highlighting for dataframes */
    div[data-testid="stDataFrame"] tbody tr:hover {{
        background-color: #e3f2fd !important;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }}
    
    /* Alternative selector for styled dataframes */
    .dataframe tbody tr:hover {{
        background-color: #e3f2fd !important;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }}
    
    /* Row hover for Streamlit's internal table structure */
    [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"] tbody tr:hover td {{
        background-color: #e3f2fd !important;
    }}
    
    /* Chat messages */
    .stChatMessage {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Info boxes, warnings, errors, success messages */
    .stAlert {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        direction: {direction};
        text-align: {text_align};
    }}
    
    /* Markdown content */
    .stMarkdown {{
        direction: {direction};
        text-align: {text_align};
    }}
    </style>
    """

# Apply CSS based on current language
st.markdown(get_custom_css(is_rtl=(CURRENT_LANG == 'ar')), unsafe_allow_html=True)


def format_datetime_columns(df):
    """Format datetime columns to show both date and time."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            # Format datetime columns to show both date and time
            df[col] = df[col].dt.strftime(config.DATETIME_FORMAT)
    return df


@st.cache_data
def load_and_process_data(file_path=None):
    """Load and process the sales data."""
    try:
        if file_path:
            loader = DataLoader(file_path)
            loader.load_data()
        else:
            # Load sample data
            st.info(t('loading'))
            sample_df = load_sample_data()
            loader = DataLoader(None)
            loader.raw_data = sample_df
        
        processed_data = loader.preprocess_data()
        return processed_data, loader.get_data_summary()
    except Exception as e:
        st.error(t('error_loading', error=str(e)))
        return None, None


@st.cache_resource
def get_sales_analyzer(data):
    """Create and cache SalesAnalyzer instance."""
    return SalesAnalyzer(data)


@st.cache_resource
def get_customer_analyzer(data):
    """Create and cache CustomerAnalyzer instance."""
    return CustomerAnalyzer(data)


@st.cache_resource
def get_product_analyzer(data):
    """Create and cache ProductAnalyzer instance."""
    return ProductAnalyzer(data)


@st.cache_resource
def get_rfm_analyzer(data):
    """Create and cache RFMAnalyzer instance."""
    return RFMAnalyzer(data)


@st.cache_resource
def get_refill_predictor(data):
    """Create and cache RefillPredictor instance."""
    return RefillPredictor(data)


@st.cache_resource
def get_cross_sell_analyzer(data, _enable_sampling=True, _max_records=100000):
    """
    Create and cache CrossSellAnalyzer instance.
    
    Args:
        data: Sales data
        _enable_sampling: Enable sampling for large datasets (for performance)
        _max_records: Maximum records to analyze
    """
    return CrossSellAnalyzer(data, enable_sampling=_enable_sampling, max_records=_max_records)


def get_ai_query_engine(data):
    """Create and cache AIQueryEngine instance in session state."""
    # Use a hash of the data shape to detect data changes
    data_hash = f"{len(data)}_{data.columns.tolist()}"
    
    # Initialize or retrieve from session state
    if 'ai_query_engine' not in st.session_state:
        st.session_state.ai_query_engine = None
        st.session_state.ai_query_engine_data_hash = None
    
    # Create new engine if data has changed or engine doesn't exist
    if (st.session_state.ai_query_engine is None or 
        st.session_state.ai_query_engine_data_hash != data_hash):
        st.session_state.ai_query_engine = AIQueryEngine(data)
        st.session_state.ai_query_engine_data_hash = data_hash
    
    return st.session_state.ai_query_engine


def display_metrics(metrics):
    """Display key metrics in columns."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            t('total_revenue'),
            f"${metrics.get('total_revenue', 0):,.2f}",
            help=t('help_total_revenue')
        )
    
    with col2:
        st.metric(
            t('total_orders'),
            f"{metrics.get('unique_orders', 0):,}",
            help=t('help_unique_orders')
        )
    
    with col3:
        st.metric(
            t('unique_customers'),
            f"{metrics.get('unique_customers', 0):,}",
            help=t('help_unique_customers')
        )
    
    with col4:
        st.metric(
            t('avg_order_value'),
            f"${metrics.get('avg_order_value', 0):,.2f}",
            help=t('help_avg_order')
        )


def sales_analysis_page(data):
    """Sales analysis section."""
    st.header(f"📊 {t('sales_analysis')}")
    
    analyzer = get_sales_analyzer(data)
    
    # Overall metrics (always show all-time data)
    st.subheader(t('overall_performance'))
    metrics = analyzer.get_overall_metrics()
    display_metrics(metrics)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"📈 {t('trends')}", f"🏆 {t('top_products')}", f"⏰ {t('time_patterns')}", f"🚨 {t('anomalies')}", f"↩️ {t('refunds')}"
    ])
    
    with tab1:
        st.subheader(t('revenue_trends'))
        
        # Time period selection
        period = st.selectbox(t('select_period'), [t('daily'), t('weekly'), t('monthly')], key='sales_trends_period')
        
        if period == t('daily'):
            trends = analyzer.get_daily_trends()
            x_col = 'date'
        elif period == t('weekly'):
            trends = analyzer.get_weekly_trends()
            x_col = 'week_start'
        else:
            trends = analyzer.get_monthly_trends()
            x_col = 'month_start'
        
        # Revenue trend chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=trends[x_col], y=trends['revenue'],
            name='Revenue',
            marker=dict(color='#1f77b4')
        ))
        
        if 'revenue_ma7' in trends.columns:
            fig.add_trace(go.Scatter(
                x=trends[x_col], y=trends['revenue_ma7'],
                mode='lines',
                name='7-Day MA',
                line=dict(color='#ff7f0e', width=3, dash='dash')
            ))
        
        period_key = 'daily' if period == t('daily') else ('weekly' if period == t('weekly') else 'monthly')
        fig.update_layout(
            title=f"{period} {t('revenue')} {t('trend')}",
            xaxis_title=t('date'),
            yaxis_title=f"{t('revenue')} ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch')
        
        # Orders and customers
        col1, col2 = st.columns(2)
        
        with col1:
            fig_orders = px.bar(
                trends, x=x_col, y='orders',
                title=f"{period} Orders",
                color='orders',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_orders, width='stretch')
        
        with col2:
            fig_customers = px.bar(
                trends, x=x_col, y='customers',
                title=f"{period} Unique Customers",
                color='customers',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_customers, width='stretch')
    
    with tab2:
        st.subheader(t('top_performing_products'))
        
        # Month filter selector (inside Top Products tab only)
        # Get available months
        available_months = analyzer.get_available_months()
        
        # Create month options: "All Time" + individual months
        month_options = ["All Time"] + [
            f"{month} ({pd.to_datetime(month).strftime('%B %Y')})"
            for month in available_months
        ]
        
        # Filter controls in a clean layout
        filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
        
        with filter_col1:
            selected_option = st.selectbox(
                "📅 Time Period",
                options=month_options,
                index=0,
                key='top_products_month_filter',
                help="Select a specific month or view all-time data"
            )
        
        # Extract actual month value (YYYY-MM format or None for "All Time")
        if selected_option == "All Time":
            selected_month = None
            period_label = "All Time"
            period_count = f"({len(available_months)} months)"
        else:
            # Extract YYYY-MM from "YYYY-MM (Month YYYY)" format
            selected_month = selected_option.split(" ")[0]
            period_label = pd.to_datetime(selected_month).strftime('%B %Y')
            period_count = ""
        
        with filter_col2:
            metric_choice = st.selectbox(
                "📊 Sort By",
                options=[t('revenue'), t('quantity'), t('orders')],
                index=0,
                key='sales_top_products_metric',
                help="Choose metric to sort products by"
            )
        
        with filter_col3:
            n_products = st.slider(
                "🔢 Number of Products",
                min_value=5,
                max_value=100,
                value=10,
                step=5,
                key='sales_top_products_slider',
                help="Adjust number of products to display"
            )
        
        # Display period summary
        if selected_month:
            st.info(f"📊 Showing top {n_products} products for **{period_label}** sorted by **{metric_choice}**")
        else:
            st.info(f"📊 Showing top {n_products} products for **All Time** {period_count} sorted by **{metric_choice}**")
        
        st.markdown("")  # Add spacing
        
        # Get top products based on selected filters
        if metric_choice == t('revenue'):
            top_products = analyzer.get_top_products(n_products, 'revenue', month=selected_month)
            chart_metric = 'revenue'
            chart_metric_label = 'Revenue ($)'
        elif metric_choice == t('quantity'):
            top_products = analyzer.get_top_products(n_products, 'quantity', month=selected_month)
            chart_metric = 'quantity'
            chart_metric_label = 'Quantity Sold'
        else:
            top_products = analyzer.get_top_products(n_products, 'orders', month=selected_month)
            chart_metric = 'orders'
            chart_metric_label = 'Number of Orders'
        
        # Data table section
        st.markdown(f"### 📋 Detailed Product Data")
        
        # Data table with renamed columns
        top_products_display = top_products.copy()
        
        # Format currency columns before translation
        if 'revenue' in top_products_display.columns:
            top_products_display['revenue'] = top_products_display['revenue'].apply(lambda x: f"${x:,.2f}")
        if 'price_per_unit' in top_products_display.columns:
            top_products_display['price_per_unit'] = top_products_display['price_per_unit'].apply(lambda x: f"${x:,.2f}")
        
        # Add special marker to quantity column
        if 'quantity' in top_products_display.columns:
            top_products_display = top_products_display.rename(columns={'quantity': 'quantity ⭐'})
        
        # Translate all column names
        top_products_display = translate_columns(top_products_display)
        
        st.dataframe(
            format_datetime_columns(top_products_display),
            use_container_width=True,
            hide_index=True,
            height=400
        )
        st.caption("⭐ Quantity is the total sold (Units and Pieces are informational)")
        
        # Divider
        st.markdown("---")
        
        # Bar chart with dynamic title
        chart_title = f"Top {n_products} Products by {metric_choice.title()}"
        if selected_month:
            chart_title += f" - {period_label}"
        else:
            chart_title += " - All Time"
        
        fig = px.bar(
            top_products,
            x='item_name',
            y=chart_metric if chart_metric in top_products.columns else 'revenue',
            title=chart_title,
            color=chart_metric if chart_metric in top_products.columns else 'revenue',
            color_continuous_scale='Blues',
            labels={'item_name': 'Product', chart_metric: chart_metric_label}
        )
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, width='stretch')
    
    with tab3:
        st.subheader(t('time_based_patterns'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Day of week patterns
            dow_patterns = analyzer.get_day_of_week_patterns()
            fig_dow = px.bar(
                dow_patterns,
                x='day',
                y='revenue',
                title='Revenue by Day of Week',
                color='revenue',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_dow, width='stretch')
        
        with col2:
            # Hourly patterns
            hourly_patterns = analyzer.get_hourly_patterns()
            fig_hourly = px.bar(
                hourly_patterns,
                x='hour',
                y='revenue',
                title='Revenue by Hour of Day',
                color='revenue',
                color_continuous_scale='Blues',
                labels={'hour': 'Hour of Day', 'revenue': 'Revenue ($)'}
            )
            # Ensure x-axis shows all hours
            fig_hourly.update_xaxes(
                tickmode='linear',
                tick0=0,
                dtick=1,
                range=[-0.5, 23.5]
            )
            st.plotly_chart(fig_hourly, width='stretch')
    
    with tab4:
        st.subheader(t('anomaly_detection'))
        
        contamination = st.slider(
            t('anomaly_sensitivity'),
            1, 10, 5,
            key='sales_anomaly_sensitivity'
        ) / 100
        
        anomalies = analyzer.detect_anomalies(contamination)
        
        # Plot with anomalies highlighted
        fig = go.Figure()
        
        # Normal days
        normal_days = anomalies[~anomalies['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=normal_days['date'],
            y=normal_days['total'],
            mode='markers',
            name='Normal Days',
            marker=dict(color='blue', size=6)
        ))
        
        # Anomalous days
        anomaly_days = anomalies[anomalies['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=anomaly_days['date'],
            y=anomaly_days['total'],
            mode='markers',
            name='Anomalies',
            marker=dict(color='red', size=10, symbol='star')
        ))
        
        fig.update_layout(
            title='Sales Anomaly Detection',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            hovermode='closest'
        )
        st.plotly_chart(fig, width='stretch')
        
        # Show anomalous days
        if len(anomaly_days) > 0:
            st.subheader(t('detected_anomalies_explanation'))
            
            # Add summary of normal baseline
            if len(normal_days) > 0:
                st.info(f"📊 **Normal Day Baseline:** "
                       f"Revenue: ${normal_days['total'].mean():,.0f} | "
                       f"Orders: {normal_days['num_orders'].mean():.0f} | "
                       f"Quantity: {normal_days['quantity'].mean():,.0f}")
            
            # Prepare display dataframe with reasons
            anomaly_display = anomaly_days[[
                'date', 'total', 'num_orders', 'quantity',
                'revenue_diff_pct', 'orders_diff_pct', 'quantity_diff_pct',
                'anomaly_reason', 'anomaly_score'
            ]].sort_values('date', ascending=False).copy()
            
            # Rename columns to match translation keys
            anomaly_display = anomaly_display.rename(columns={
                'total': 'revenue',
                'num_orders': 'orders',
                'revenue_diff_pct': 'revenue_change_pct',
                'orders_diff_pct': 'orders_change_pct',
                'quantity_diff_pct': 'quantity_change_pct'
            })
            
            # Translate column names
            anomaly_display = translate_columns(anomaly_display)
            
            # Format the dataframe
            st.dataframe(
                format_datetime_columns(anomaly_display),
                use_container_width=True,
                hide_index=True
            )
            
            # Add detailed view with expandable sections
            st.markdown(f"### 🔍 {t('detailed_anomaly_breakdown')}")
            for idx, row in anomaly_days.sort_values('date', ascending=False).iterrows():
                with st.expander(f"📅 {row['date'].strftime('%Y-%m-%d (%A)')} - {row['anomaly_reason']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Revenue", 
                                 f"${row['total']:,.2f}",
                                 delta=f"{row['revenue_diff_pct']:+.1f}%",
                                 delta_color="off")
                        st.caption(f"Normal avg: ${row['avg_revenue']:,.0f}")
                    
                    with col2:
                        st.metric("Orders", 
                                 f"{int(row['num_orders'])}",
                                 delta=f"{row['orders_diff_pct']:+.1f}%",
                                 delta_color="off")
                        st.caption(f"Normal avg: {row['avg_orders']:.0f}")
                    
                    with col3:
                        st.metric("Quantity Sold", 
                                 f"{int(row['quantity'])}",
                                 delta=f"{row['quantity_diff_pct']:+.1f}%",
                                 delta_color="off")
                        st.caption(f"Normal avg: {row['avg_quantity']:.0f}")
                    
                    # Show z-scores
                    st.markdown("**Statistical Scores:**")
                    st.write(f"- Revenue Z-Score: {row['revenue_zscore']:.2f} "
                            f"({'⚠️ Significant' if abs(row['revenue_zscore']) > 2 else '✓ Normal'})")
                    st.write(f"- Orders Z-Score: {row['orders_zscore']:.2f} "
                            f"({'⚠️ Significant' if abs(row['orders_zscore']) > 2 else '✓ Normal'})")
                    st.write(f"- Quantity Z-Score: {row['quantity_zscore']:.2f} "
                            f"({'⚠️ Significant' if abs(row['quantity_zscore']) > 2 else '✓ Normal'})")
                    st.write(f"- Anomaly Score: {row['anomaly_score']:.3f} (more negative = more anomalous)")
        else:
            st.info(t('no_anomalies_detected'))
    
    with tab5:
        st.subheader(t('refund_analysis'))
        
        # Get refund analysis
        refund_analysis = analyzer.get_refund_analysis()
        
        if not refund_analysis.get('has_refunds', False):
            st.info(t('no_refunds_found'))
        else:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    t('total_refunds'),
                    f"${refund_analysis['total_refund_amount']:,.2f}",
                    delta=f"-{refund_analysis['refund_rate_pct']:.1f}%"
                )
            with col2:
                st.metric(
                    t('refund_transactions'),
                    f"{refund_analysis['total_refund_transactions']:,}"
                )
            with col3:
                st.metric(
                    t('refund_rate'),
                    f"{refund_analysis['refund_rate_pct']:.2f}%"
                )
            with col4:
                st.metric(
                    t('avg_refund_value'),
                    f"${refund_analysis['avg_refund_value']:,.2f}"
                )
            
            # Controls for refunded products and customers (outside tabs to prevent reset)
            st.markdown(f"### 🎛️ {t('display_controls')}")
            col_ctrl1, col_ctrl2 = st.columns(2)
            with col_ctrl1:
                n_refunded = st.slider(
                    "📦 Number of Refunded Products",
                    min_value=5,
                    max_value=100,
                    value=10,
                    step=5,
                    help="Adjust how many refunded products to display",
                    key="refund_products_slider"
                )
            with col_ctrl2:
                n_refund_customers = st.slider(
                    "👤 Number of Refund Customers",
                    min_value=5,
                    max_value=100,
                    value=10,
                    step=5,
                    help="Adjust how many refund customers to display",
                    key="refund_customers_slider_new"
                )
            
            st.markdown("---")
            
            # Tabs within refunds
            refund_tab1, refund_tab2, refund_tab3, refund_tab4 = st.tabs([
                f"📦 {t('refunded_products')}", 
                f"👤 {t('refund_customers')}", 
                f"📅 {t('refund_trends')}",
                f"📋 {t('refund_details')}"
            ])
            
            with refund_tab1:
                st.subheader(t('top_refunded_products'))
                
                top_refunded = refund_analysis['top_refunded_products']
                
                if len(top_refunded) > 0:
                    # Bar chart
                    fig = px.bar(
                        top_refunded.head(n_refunded),
                        x='item_name',
                        y='refund_amount',
                        title=f"{t('products_by_refund_amount')} - Top {n_refunded}",
                        color='refund_amount',
                        color_continuous_scale='Reds',
                        labels={'refund_amount': t('refund_amount'), 'item_name': t('product')}
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, width='stretch')
                    
                    # Detailed table - shows same number as slider
                    refund_products_display = top_refunded.head(n_refunded).copy()
                    refund_products_display = translate_columns(refund_products_display)
                    st.dataframe(
                        refund_products_display,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(t('no_data_available'))
            
            with refund_tab2:
                st.subheader(t('customers_with_most_refunds'))
                
                top_refund_customers = refund_analysis['top_refund_customers']
                
                if len(top_refund_customers) > 0:
                    # Bar chart
                    fig = px.bar(
                        top_refund_customers.head(n_refund_customers),
                        x='customer_name',
                        y='refund_amount',
                        title=f"{t('customers_by_refund_amount')} - Top {n_refund_customers}",
                        color='refund_amount',
                        color_continuous_scale='Oranges',
                        labels={'refund_amount': t('refund_amount'), 'customer_name': t('customer')}
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, width='stretch')
                    
                    # Detailed table - shows same number as slider
                    refund_customers_display = top_refund_customers.head(n_refund_customers).copy()
                    refund_customers_display = translate_columns(refund_customers_display)
                    st.dataframe(
                        refund_customers_display,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(t('no_data_available'))
            
            with refund_tab3:
                st.subheader(t('refund_trends_over_time'))
                
                # Monthly refunds
                refunds_by_month = refund_analysis['refunds_by_month']
                
                if len(refunds_by_month) > 0:
                    # Convert period to string for plotting
                    refunds_by_month['month_str'] = refunds_by_month['month'].astype(str)
                    
                    # Bar chart
                    fig = px.bar(
                        refunds_by_month,
                        x='month_str',
                        y='refund_amount',
                        title=t('monthly_refund_trend'),
                        labels={'refund_amount': t('refund_amount'), 'month_str': t('month')},
                        color='refund_amount',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(
                        xaxis_title=t('month'),
                        yaxis_title=t('refund_amount') + ' ($)',
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, width='stretch')
                    
                    # Orders trend
                    fig2 = px.bar(
                        refunds_by_month,
                        x='month_str',
                        y='refund_orders',
                        title=t('monthly_refund_orders'),
                        labels={'refund_orders': t('refund_orders'), 'month_str': t('month')},
                        color='refund_orders',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig2, width='stretch')
                else:
                    st.info(t('no_data_available'))
            
            with refund_tab4:
                st.subheader(t('refund_transaction_details'))
                
                # Get actual refund transactions from data
                refund_data = data[data['is_refund']]
                
                if len(refund_data) > 0:
                    # Add filter options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Date filter
                        date_range = st.date_input(
                            t('date_range'),
                            value=(refund_data['date'].min().date(), refund_data['date'].max().date()),
                            key='refund_date_range'
                        )
                    
                    with col2:
                        # Product filter
                        all_products = [t('all_products')] + sorted(refund_data['item_name'].unique().tolist())
                        selected_product = st.selectbox(
                            t('filter_by_product'),
                            all_products,
                            key='refund_details_product_filter'
                        )
                    
                    # Apply filters
                    filtered_refunds = refund_data.copy()
                    
                    if len(date_range) == 2:
                        filtered_refunds = filtered_refunds[
                            (filtered_refunds['date'].dt.date >= date_range[0]) &
                            (filtered_refunds['date'].dt.date <= date_range[1])
                        ]
                    
                    if selected_product != t('all_products'):
                        filtered_refunds = filtered_refunds[filtered_refunds['item_name'] == selected_product]
                    
                    # Display summary
                    st.metric(
                        t('filtered_refunds'),
                        f"{len(filtered_refunds):,}",
                        f"${abs(filtered_refunds['total'].sum()):,.2f}"
                    )
                    
                    # Display refund transactions
                    display_columns = ['date', 'order_id', 'customer_name', 'item_name', 
                                      'units', 'pieces', 'quantity', 'total']
                    # Only include columns that exist
                    display_columns = [col for col in display_columns if col in filtered_refunds.columns]
                    refund_display = filtered_refunds[display_columns].copy()
                    
                    # Convert to positive values for readability
                    if 'total' in refund_display.columns:
                        refund_display['total'] = refund_display['total'].abs()
                    if 'quantity' in refund_display.columns:
                        refund_display['quantity'] = refund_display['quantity'].abs()
                    if 'units' in refund_display.columns:
                        refund_display['units'] = refund_display['units'].abs()
                    if 'pieces' in refund_display.columns:
                        refund_display['pieces'] = refund_display['pieces'].abs()
                    
                    refund_display = refund_display.sort_values('date', ascending=False)
                    
                    # Rename 'total' to 'refund_amount' and add marker to quantity
                    if 'total' in refund_display.columns:
                        refund_display = refund_display.rename(columns={'total': 'refund_amount'})
                    if 'quantity' in refund_display.columns:
                        refund_display = refund_display.rename(columns={'quantity': 'quantity ⭐'})
                    
                    # Translate column names
                    refund_display = translate_columns(refund_display)
                    
                    st.dataframe(
                        format_datetime_columns(refund_display),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("⭐ Quantity = total units refunded (Units and Pieces show breakdown if available)")
                    
                    # Download button
                    csv = refund_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=t('download_refund_data'),
                        data=csv,
                        file_name=f"refunds_{date_range[0]}_{date_range[1]}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info(t('no_refund_transactions'))


def monthly_analysis_page(data):
    """Monthly sales and category analysis with comparison."""
    st.header(f"📅 {t('monthly_sales_category')}")
    
    analyzer = get_sales_analyzer(data)
    
    # Get available months
    available_months = analyzer.get_available_months()
    
    if len(available_months) == 0:
        st.warning(t('no_data_monthly'))
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📊 Monthly Overview",
        "📂 Category Breakdown",
        "🔄 Month Comparison"
    ])
    
    with tab1:
        st.subheader(t('monthly_sales_overview'))
        
        # Get monthly trends
        monthly_trends = analyzer.get_monthly_trends()
        
        if len(monthly_trends) > 0:
            # Show data table first with refunds
            display_monthly = monthly_trends[[
                'year_month', 'gross_revenue', 'refund_amount', 'revenue', 'refund_rate',
                'orders', 'refund_orders', 'customers', 'items_sold', 'items_refunded', 'mom_growth'
            ]].copy()
            
            # Rename columns to match translation keys
            display_monthly = display_monthly.rename(columns={
                'year_month': 'month',
                'revenue': 'net_revenue',
                'refund_rate': 'refund_rate'
            })
            
            # Translate column names
            display_monthly = translate_columns(display_monthly)
            
            # Get translated column names for formatting
            trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
            gross_col = trans_cols.get('gross_revenue', 'Gross Revenue')
            refund_col = trans_cols.get('refund_amount', 'Refunds')
            net_col = trans_cols.get('net_revenue', 'Net Revenue')
            rate_col = trans_cols.get('refund_rate', 'Refund Rate %')
            orders_col = trans_cols.get('orders', 'Orders')
            refund_orders_col = trans_cols.get('refund_orders', 'Refund Orders')
            customers_col = trans_cols.get('customers', 'Customers')
            items_sold_col = trans_cols.get('items_sold', 'Items Sold')
            items_refunded_col = trans_cols.get('items_refunded', 'Items Refunded')
            mom_col = trans_cols.get('mom_growth', 'MoM Growth %')
            
            st.dataframe(
                display_monthly.style.format({
                    gross_col: '${:,.2f}',
                    refund_col: '${:,.2f}',
                    net_col: '${:,.2f}',
                    rate_col: '{:.2f}%',
                    orders_col: '{:,.0f}',
                    refund_orders_col: '{:,.0f}',
                    customers_col: '{:,.0f}',
                    items_sold_col: '{:,.0f}',
                    items_refunded_col: '{:,.0f}',
                    mom_col: '{:+.2f}%'
                }).map(
                    lambda x: 'background-color: #ffe6e6' if 'Refund' in str(x) else '',
                    subset=[refund_col, refund_orders_col, items_refunded_col, rate_col]
                ),
                use_container_width=True,
                hide_index=True
            )
            
            # Revenue trend chart below table
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=monthly_trends['month_start'],
                y=monthly_trends['revenue'],
                name='Revenue',
                marker=dict(color='#1f77b4'),
                text=monthly_trends['revenue'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto'
            ))
            
            fig.update_layout(
                title='Monthly Revenue Trend',
                xaxis_title='Month',
                yaxis_title='Revenue ($)',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, width='stretch')
        else:
            st.info(t('no_monthly_trend'))
    
    with tab2:
        st.subheader(t('category_spending_by_month'))
        
        # Get monthly category breakdown
        monthly_category = analyzer.get_monthly_category_breakdown()
        
        if len(monthly_category) > 0:
            # Month selector for detailed view with "All Time" option
            month_options = ["All Time"] + available_months
            
            selected_option = st.selectbox(
                "Select Month for Detailed Category Breakdown",
                options=month_options,
                index=0,  # Default to "All Time"
                format_func=lambda x: x if x == "All Time" else pd.to_datetime(x).strftime('%B %Y'),
                key='monthly_category_selector'
            )
            
            # Filter for selected month or aggregate all
            if selected_option == "All Time":
                # Aggregate all months
                month_data = monthly_category.groupby('category').agg({
                    'revenue': 'sum',
                    'quantity': 'sum',
                    'orders': 'sum',
                    'refund_amount': 'sum',
                    'refund_quantity': 'sum'
                }).reset_index()
                month_data['avg_order_value'] = month_data['revenue'] / month_data['orders']
                month_data['net_revenue'] = month_data['revenue'] - month_data['refund_amount']
                month_data['refund_rate'] = (month_data['refund_amount'] / month_data['revenue'] * 100).round(2).fillna(0)
                period_label = "All Time"
            else:
                # Filter for selected month
                month_data = monthly_category[monthly_category['year_month'] == selected_option]
                period_label = pd.to_datetime(selected_option).strftime('%B %Y')
            
            if len(month_data) > 0:
                # Category summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Gross Revenue", f"${month_data['revenue'].sum():,.2f}")
                with col2:
                    st.metric("Total Refunds", f"${month_data['refund_amount'].sum():,.2f}", 
                             delta=f"-{month_data['refund_amount'].sum() / month_data['revenue'].sum() * 100:.1f}%")
                with col3:
                    st.metric("Net Revenue", f"${month_data['net_revenue'].sum():,.2f}")
                with col4:
                    st.metric("Total Categories", len(month_data))
                
                # Detailed category table with refunds
                st.markdown("#### Category Details")
                display_categories = month_data[['category', 'revenue', 'refund_amount', 'net_revenue', 
                                                  'refund_rate', 'quantity', 'refund_quantity', 
                                                  'orders', 'avg_order_value']].copy()
                display_categories['revenue_pct'] = (display_categories['revenue'] / display_categories['revenue'].sum() * 100).round(2)
                display_categories = display_categories.sort_values('revenue', ascending=False)
                
                # Rename columns to match translation keys
                display_categories = display_categories.rename(columns={
                    'revenue': 'gross_revenue',
                    'net_revenue': 'net_revenue',
                    'refund_quantity': 'refund_quantity'
                })
                
                # Translate column names
                display_categories = translate_columns(display_categories)
                
                # Get translated column names for formatting
                trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
                cat_col = trans_cols.get('category', 'Category')
                gross_col = trans_cols.get('gross_revenue', 'Gross Revenue')
                refund_col = trans_cols.get('refund_amount', 'Refunds')
                net_col = trans_cols.get('net_revenue', 'Net Revenue')
                rate_col = trans_cols.get('refund_rate', 'Refund Rate %')
                qty_col = trans_cols.get('quantity', 'Quantity')
                qty_refund_col = trans_cols.get('refund_quantity', 'Qty Refunded')
                orders_col = trans_cols.get('orders', 'Orders')
                aov_col = trans_cols.get('avg_order_value', 'Avg Order Value')
                rev_pct_col = trans_cols.get('revenue_pct', 'Revenue %')
                
                st.dataframe(
                    display_categories.style.format({
                        gross_col: '${:,.2f}',
                        refund_col: '${:,.2f}',
                        net_col: '${:,.2f}',
                        rate_col: '{:.2f}%',
                        qty_col: '{:,.0f}',
                        qty_refund_col: '{:,.0f}',
                        orders_col: '{:,.0f}',
                        aov_col: '${:,.2f}',
                        rev_pct_col: '{:.2f}%'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Pie chart of category spending (below table)
                st.markdown("---")
                fig_pie = px.pie(
                    month_data,
                    values='revenue',
                    names='category',
                    title=f'Category Distribution - {period_label}',
                    hole=0.4
                )
                st.plotly_chart(fig_pie, width='stretch')
            
            # Stacked bar chart for all months
            st.markdown("#### Category Spending Trend Across All Months")
            
            # Create pivot table for stacked bar chart
            pivot_data = monthly_category.pivot_table(
                index='year_month',
                columns='category',
                values='revenue',
                aggfunc='sum',
                fill_value=0
            )
            
            fig_stacked = go.Figure()
            
            for category in pivot_data.columns:
                fig_stacked.add_trace(go.Bar(
                    x=[pd.to_datetime(m).strftime('%b %Y') for m in pivot_data.index],
                    y=pivot_data[category],
                    name=category,
                    text=pivot_data[category].apply(lambda x: f'${x:,.0f}' if x > 0 else ''),
                    textposition='inside'
                ))
            
            fig_stacked.update_layout(
                title='Monthly Category Spending Trend',
                xaxis_title='Month',
                yaxis_title='Revenue ($)',
                barmode='stack',
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_stacked, width='stretch')
            
            # Download option
            csv_data = monthly_category.to_csv(index=False)
            st.download_button(
                label="📥 Download Monthly Category Data (CSV)",
                data=csv_data,
                file_name=f"monthly_category_breakdown_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No category breakdown data available")
    
    with tab3:
        st.subheader(t('compare_two_months'))
        
        if len(available_months) < 2:
            st.warning("Need at least 2 months of data for comparison")
        else:
            # Month selectors
            col1, col2 = st.columns(2)
            
            with col1:
                month1 = st.selectbox(
                    "First Month",
                    options=available_months,
                    index=max(0, len(available_months) - 2),
                    format_func=lambda x: pd.to_datetime(x).strftime('%B %Y'),
                    key='month1'
                )
            
            with col2:
                month2 = st.selectbox(
                    "Second Month",
                    options=available_months,
                    index=len(available_months) - 1,
                    format_func=lambda x: pd.to_datetime(x).strftime('%B %Y'),
                    key='month2'
                )
            
            if month1 and month2:
                # Get comparison data
                comparison = analyzer.get_month_comparison(month1, month2)
                
                if 'error' in comparison:
                    st.error(comparison['error'])
                else:
                    month1_name = pd.to_datetime(month1).strftime('%B %Y')
                    month2_name = pd.to_datetime(month2).strftime('%B %Y')
                    
                    # Overall metrics comparison
                    st.markdown(f"### Overall Comparison: {month1_name} vs {month2_name}")
                    
                    m1 = comparison['month1_metrics']
                    m2 = comparison['month2_metrics']
                    changes = comparison['changes']
                    
                    # Display metrics in columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Revenue",
                            f"${m2['revenue']:,.2f}",
                            f"{changes['revenue_change_pct']:+.1f}%",
                            delta_color="normal"
                        )
                        st.caption(f"{month1_name}: ${m1['revenue']:,.2f}")
                    
                    with col2:
                        st.metric(
                            "Orders",
                            f"{m2['orders']:,}",
                            f"{changes['orders_change_pct']:+.1f}%",
                            delta_color="normal"
                        )
                        st.caption(f"{month1_name}: {m1['orders']:,}")
                    
                    with col3:
                        st.metric(
                            "Customers",
                            f"{m2['customers']:,}",
                            f"{changes['customers_change_pct']:+.1f}%",
                            delta_color="normal"
                        )
                        st.caption(f"{month1_name}: {m1['customers']:,}")
                    
                    with col4:
                        aov_delta = m2['avg_order_value'] - m1['avg_order_value']
                        # Format delta with sign before dollar sign for proper color detection
                        delta_formatted = f"-${abs(aov_delta):.2f}" if aov_delta < 0 else f"+${aov_delta:.2f}"
                        st.metric(
                            "Avg Order Value",
                            f"${m2['avg_order_value']:,.2f}",
                            delta=delta_formatted,
                            delta_color="normal"
                        )
                        st.caption(f"{month1_name}: ${m1['avg_order_value']:,.2f}")
                    
                    # Category comparison
                    st.markdown("### Category Comparison")
                    
                    category_comp = comparison['category_comparison']
                    
                    if len(category_comp) > 0:
                        # Detailed comparison table
                        st.markdown("#### Detailed Category Comparison")
                        display_comp = category_comp[[
                            'category', 'revenue_m1', 'revenue_m2', 'revenue_change', 'revenue_change_pct',
                            'quantity_m1', 'quantity_m2', 'orders_m1', 'orders_m2'
                        ]].copy()
                        
                        # Use translated terms for column headers
                        trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
                        cat_label = trans_cols.get('category', 'Category')
                        rev_label = trans_cols.get('revenue', 'Revenue')
                        qty_label = trans_cols.get('quantity', 'Qty')
                        orders_label = trans_cols.get('orders', 'Orders')
                        change_label = trans_cols.get('change', 'Change')
                        change_pct_label = trans_cols.get('change_pct', 'Change %')
                        
                        display_comp.columns = [
                            cat_label,
                            f'{month1_name} {rev_label}',
                            f'{month2_name} {rev_label}',
                            f'{rev_label} {change_label}',
                            change_pct_label,
                            f'{month1_name} {qty_label}',
                            f'{month2_name} {qty_label}',
                            f'{month1_name} {orders_label}',
                            f'{month2_name} {orders_label}'
                        ]
                        
                        st.dataframe(
                            display_comp.style.format({
                                f'{month1_name} {rev_label}': '${:,.2f}',
                                f'{month2_name} {rev_label}': '${:,.2f}',
                                f'{rev_label} {change_label}': '${:,.2f}',
                                change_pct_label: '{:+.2f}%',
                                f'{month1_name} {qty_label}': '{:,.0f}',
                                f'{month2_name} {qty_label}': '{:,.0f}',
                                f'{month1_name} {orders_label}': '{:,.0f}',
                                f'{month2_name} {orders_label}': '{:,.0f}'
                            }).map(
                                lambda x: 'color: green' if isinstance(x, str) and '+' in str(x) and '%' in str(x) else 
                                         ('color: red' if isinstance(x, str) and '-' in str(x) and '%' in str(x) else ''),
                                subset=[change_pct_label]
                            ),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Side-by-side bar chart
                        fig_compare = go.Figure()
                        
                        fig_compare.add_trace(go.Bar(
                            x=category_comp['category'],
                            y=category_comp['revenue_m1'],
                            name=month1_name,
                            marker=dict(color='#1f77b4'),
                            text=category_comp['revenue_m1'].apply(lambda x: f'${x:,.0f}'),
                            textposition='auto'
                        ))
                        
                        fig_compare.add_trace(go.Bar(
                            x=category_comp['category'],
                            y=category_comp['revenue_m2'],
                            name=month2_name,
                            marker=dict(color='#ff7f0e'),
                            text=category_comp['revenue_m2'].apply(lambda x: f'${x:,.0f}'),
                            textposition='auto'
                        ))
                        
                        fig_compare.update_layout(
                            title='Category Revenue Comparison',
                            xaxis_title='Category',
                            yaxis_title='Revenue ($)',
                            barmode='group',
                            height=500,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_compare, width='stretch')
                        
                        # Download comparison
                        csv_comparison = category_comp.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download Comparison ({month1_name} vs {month2_name})",
                            data=csv_comparison,
                            file_name=f"month_comparison_{month1}_{month2}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No category data available for comparison")


def customer_analysis_page(data):
    """Customer behavior analysis section."""
    st.header(f"👥 {t('customer_insights')}")
    
    analyzer = get_customer_analyzer(data)
    
    # Customer metrics
    st.subheader(t('customer_metrics'))
    repeat_metrics = analyzer.get_repeat_purchase_rate()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t('total_customers'), f"{repeat_metrics['total_customers']:,}")
    with col2:
        st.metric(t('repeat_customers'), f"{repeat_metrics['repeat_customers']:,}")
    with col3:
        st.metric(t('repeat_rate'), f"{repeat_metrics['repeat_rate_pct']:.1f}%")
    with col4:
        st.metric(t('avg_customer_ltv'), f"${repeat_metrics['avg_customer_ltv']:,.2f}")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🌟 {t('valuable_customers')}", f"⚠️ {t('churn_risk')}", f"📊 {t('segments')}", f"🆕 {t('new_customers')}"
    ])
    
    with tab1:
        st.subheader(t('valuable_customers'))
        
        # Add controls for adjusting number of customers to display
        st.markdown(f"### 👥 {t('customer_display_settings')}")
        col_control1, col_control2 = st.columns(2)
        
        with col_control1:
            n_high_value = st.slider(
                "Number of High-Value Customers",
                min_value=5,
                max_value=100,
                value=15,
                step=5,
                help="Adjust how many high-value customers to display"
            )
        
        with col_control2:
            n_frequent = st.slider(
                "Number of Frequent Buyers",
                min_value=5,
                max_value=100,
                value=15,
                step=5,
                help="Adjust how many frequent buyers to display"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**High-Value Customers (by Spend) - Top {n_high_value}**")
            high_value = analyzer.get_high_value_customers(n_high_value)
            high_value_display = translate_columns(high_value.copy())
            st.dataframe(format_datetime_columns(high_value_display), use_container_width=True, hide_index=True)
        
        with col2:
            st.write(f"**Frequent Buyers - Top {n_frequent}**")
            frequent = analyzer.get_frequent_buyers(n_frequent)
            frequent_display = translate_columns(frequent.copy())
            st.dataframe(format_datetime_columns(frequent_display), use_container_width=True, hide_index=True)
        
        # Add customer product history section
        st.markdown("---")
        st.markdown(f"### 🛒 {t('customer_purchase_history')}")
        st.markdown("Select a customer to view all products they have purchased")
        
        # Get list of all customers
        customers = sorted([str(c) for c in data['customer_name'].unique()])
        
        col_select, col_button = st.columns([4, 1])
        with col_select:
            selected_customer = st.selectbox(
                "Select Customer",
                customers,
                key="customer_product_history"
            )
        
        with col_button:
            st.write("")  # Spacing
            st.write("")  # Spacing
            show_products = st.button("View Products", type="primary", key="view_customer_products")
        
        if show_products or 'show_customer_products' in st.session_state:
            if show_products:
                st.session_state.show_customer_products = True
            
            if selected_customer:
                with st.spinner(f"Loading purchase history for {selected_customer}..."):
                    product_history = analyzer.get_customer_product_preferences(selected_customer)
                
                if len(product_history) > 0:
                    # Display summary metrics
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    with col_m1:
                        st.metric("Total Products", len(product_history))
                    with col_m2:
                        st.metric("Total Spent", f"${product_history['total_spent'].sum():,.2f}")
                    with col_m3:
                        st.metric("Total Quantity", f"{product_history['total_quantity'].sum():,.0f}")
                    with col_m4:
                        st.metric("Avg Spent per Product", f"${product_history['total_spent'].mean():,.2f}")
                    
                    # Display product history table
                    st.markdown(f"#### Products purchased by **{selected_customer}**")
                    product_history_display = translate_columns(product_history.copy())
                    st.dataframe(
                        format_datetime_columns(product_history_display),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Add visualization of top products
                    st.markdown("---")
                    col_viz1, col_viz2 = st.columns(2)
                    
                    with col_viz1:
                        # Top products by spend
                        top_products_spend = product_history.nlargest(10, 'total_spent')
                        fig_spend = px.bar(
                            top_products_spend,
                            x='item_name',
                            y='total_spent',
                            title=f'Top 10 Products by Spend - {selected_customer}',
                            color='total_spent',
                            color_continuous_scale='Blues',
                            labels={'item_name': 'Product', 'total_spent': 'Total Spent ($)'}
                        )
                        fig_spend.update_xaxes(tickangle=-45)
                        st.plotly_chart(fig_spend, width='stretch')
                    
                    with col_viz2:
                        # Top products by purchase frequency
                        top_products_freq = product_history.nlargest(10, 'times_purchased')
                        fig_freq = px.bar(
                            top_products_freq,
                            x='item_name',
                            y='times_purchased',
                            title=f'Top 10 Products by Purchase Frequency - {selected_customer}',
                            color='times_purchased',
                            color_continuous_scale='Greens',
                            labels={'item_name': 'Product', 'times_purchased': 'Times Purchased'}
                        )
                        fig_freq.update_xaxes(tickangle=-45)
                        st.plotly_chart(fig_freq, width='stretch')
                    
                    # Category breakdown
                    if 'category' in product_history.columns:
                        st.markdown("---")
                        st.markdown("#### Category Breakdown")
                        category_summary = product_history.groupby('category').agg({
                            'total_spent': 'sum',
                            'total_quantity': 'sum',
                            'times_purchased': 'sum',
                            'item_name': 'count'
                        }).reset_index()
                        # Rename to match translation keys and translate
                        category_summary.columns = ['category', 'total_spent', 'total_quantity', 'times_purchased', 'count']
                        category_summary = category_summary.sort_values('total_spent', ascending=False)
                        category_summary = translate_columns(category_summary)
                        
                        col_cat1, col_cat2 = st.columns([2, 1])
                        
                        with col_cat1:
                            fig_cat = px.pie(
                                category_summary,
                                values='Total Spent',
                                names='Category',
                                title='Spending by Category',
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            st.plotly_chart(fig_cat, width='stretch')
                        
                        with col_cat2:
                            st.dataframe(
                                category_summary.style.format({
                                    'Total Spent': '${:,.2f}',
                                    'Total Quantity': '{:,.0f}',
                                    'Times Purchased': '{:,.0f}'
                                }),
                                use_container_width=True,
                                hide_index=True
                            )
                    
                    # Download option
                    st.markdown("---")
                    csv = product_history.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {selected_customer}'s Purchase History",
                        data=csv,
                        file_name=f"{selected_customer.replace(' ', '_')}_purchase_history_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"No purchase history found for {selected_customer}")
    
    with tab2:
        st.subheader(t('churn_risk_analysis'))
        
        threshold = st.slider("Inactivity threshold (days)", 30, 180, 90, key='customer_churn_threshold')
        churn_risk = analyzer.get_churn_risk_customers(threshold)
        
        if len(churn_risk) > 0:
            st.warning(f"Found {len(churn_risk)} customers at risk of churning")
            
            # Visualization
            fig = px.scatter(
                churn_risk.head(50),
                x='days_since_last_purchase',
                y='total_spent',
                size='total_orders',
                hover_name='customer_name',
                title='Churn Risk Customers (Size = Order Count)',
                labels={
                    'days_since_last_purchase': 'Days Since Last Purchase',
                    'total_spent': 'Total Spent ($)'
                }
            )
            st.plotly_chart(fig, width='stretch')
            
            churn_risk_display = translate_columns(churn_risk.copy())
            st.dataframe(format_datetime_columns(churn_risk_display), use_container_width=True, hide_index=True)
        else:
            st.success("No customers at risk of churning!")
    
    with tab3:
        st.subheader(t('customer_segmentation'))
        
        segments = analyzer.get_customer_segments_by_value()
        
        # Create segment comparison
        segment_data = []
        for segment_name, segment_info in segments.items():
            segment_data.append({
                'Segment': segment_name.replace('_', ' ').title(),
                'Customers': segment_info['count'],
                'Revenue': segment_info['total_revenue'],
                'Avg Spend': segment_info['avg_spent'],
                'Revenue %': segment_info['revenue_contribution_pct']
            })
        
        segment_df = pd.DataFrame(segment_data)
        
        # Translate segment dataframe columns
        segment_df_translated = segment_df.copy()
        segment_df_translated.columns = ['segment', 'customers', 'revenue', 'avg_spend', 'revenue_pct']
        segment_df_translated = translate_columns(segment_df_translated)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_count = px.pie(
                segment_df,
                values='Customers',
                names='Segment',
                title='Customer Distribution by Segment'
            )
            st.plotly_chart(fig_count, width='stretch')
        
        with col2:
            fig_revenue = px.pie(
                segment_df,
                values='Revenue',
                names='Segment',
                title='Revenue Contribution by Segment'
            )
            st.plotly_chart(fig_revenue, width='stretch')
        
        st.dataframe(format_datetime_columns(segment_df_translated), use_container_width=True, hide_index=True)
    
    with tab4:
        st.subheader(t('new_customers'))
        
        days_back = st.slider("Recent period (days)", 7, 90, 30, key='customer_new_days_back')
        new_customers = analyzer.get_new_customers(days_back)
        
        if len(new_customers) > 0:
            st.info(f"{len(new_customers)} new customers in the last {days_back} days")
            
            # Daily new customer acquisition
            daily_new = new_customers.groupby('first_purchase').size().reset_index()
            daily_new.columns = ['date', 'new_customers']
            
            fig = px.bar(
                daily_new,
                x='date',
                y='new_customers',
                title='Daily New Customer Acquisition'
            )
            st.plotly_chart(fig, width='stretch')
            
            # Translate columns in dataframe
            new_customers_display = translate_columns(new_customers.copy())
            st.dataframe(format_datetime_columns(new_customers_display), use_container_width=True, hide_index=True)
        else:
            st.info(f"No new customers in the last {days_back} days")


def product_analysis_page(data):
    """Product performance analysis section."""
    st.header(f"📦 {t('product_performance')}")
    
    analyzer = get_product_analyzer(data)
    
    # Display overall product metrics including refunds
    st.subheader(f"📊 {t('product_overview')}")
    product_summary = analyzer.get_product_summary()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Products", f"{len(product_summary):,}")
    with col2:
        total_sold = product_summary['quantity_sold'].sum()
        st.metric("Total Quantity Sold", f"{total_sold:,.0f}")
    with col3:
        total_refunded = product_summary['refund_quantity'].sum()
        st.metric("Total Refunded", f"{total_refunded:,.0f}")
    with col4:
        net_quantity = product_summary['net_quantity'].sum()
        st.metric("Net Quantity", f"{net_quantity:,.0f}")
    with col5:
        refund_rate = (total_refunded / total_sold * 100) if total_sold > 0 else 0
        st.metric("Refund Rate", f"{refund_rate:.2f}%")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([
        f"🏃 {t('fast_slow_movers')}", f"📊 {t('abc_analysis')}", f"🔄 {t('lifecycle')}"
    ])
    
    with tab1:
        # Add controls for adjusting number of products to display
        st.markdown(f"### 📊 {t('product_velocity_analysis')}")
        col_control1, col_control2 = st.columns(2)
        
        with col_control1:
            n_fast = st.slider(
                "Number of Fast-Moving Products",
                min_value=5,
                max_value=100,
                value=10,
                step=5,
                help="Adjust how many fast-moving products to display"
            )
        
        with col_control2:
            n_slow = st.slider(
                "Number of Slow-Moving Products",
                min_value=5,
                max_value=100,
                value=10,
                step=5,
                help="Adjust how many slow-moving products to display"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🏃 Fast-Moving Products (Top {n_fast})")
            fast_movers = analyzer.get_fast_moving_products(n_fast)
            
            if len(fast_movers) > 0:
                # Format the dataframe for better display
                fast_movers_display = fast_movers.copy()
                
                # Add marker to quantity column and translate
                if 'quantity_sold' in fast_movers_display.columns:
                    fast_movers_display = fast_movers_display.rename(columns={'quantity_sold': 'quantity_sold ⭐'})
                
                fast_movers_display = translate_columns(fast_movers_display)
                
                st.dataframe(format_datetime_columns(fast_movers_display), use_container_width=True, hide_index=True)
                st.caption("⭐ Quantity Sold = total units sold (Units and Pieces are breakdowns)")
                
                # Quick stats with refund info
                total_fast_revenue = fast_movers['revenue'].sum()
                total_fast_quantity = fast_movers['quantity_sold'].sum()
                total_fast_refunded = fast_movers['refund_quantity'].sum()
                total_fast_net = fast_movers['net_quantity'].sum()
                
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1:
                    st.metric("Combined Revenue", f"${total_fast_revenue:,.2f}")
                with col_s2:
                    st.metric("Total Sold", f"{total_fast_quantity:,.0f}")
                with col_s3:
                    st.metric("Total Refunded", f"{total_fast_refunded:,.0f}")
                with col_s4:
                    st.metric("Net Quantity", f"{total_fast_net:,.0f}")
            else:
                st.warning(t('no_fast_moving'))
        
        with col2:
            st.subheader(f"🐌 Slow-Moving Products (Bottom {n_slow})")
            slow_movers = analyzer.get_slow_moving_products(n_slow)
            
            if len(slow_movers) > 0:
                # Format the dataframe for better display
                slow_movers_display = slow_movers.copy()
                
                # Add marker to quantity column and translate
                if 'quantity_sold' in slow_movers_display.columns:
                    slow_movers_display = slow_movers_display.rename(columns={'quantity_sold': 'quantity_sold ⭐'})
                
                slow_movers_display = translate_columns(slow_movers_display)
                
                st.dataframe(format_datetime_columns(slow_movers_display), use_container_width=True, hide_index=True)
                st.caption("⭐ Quantity Sold = total units sold (Units and Pieces are breakdowns)")
                
                # Quick stats with refund info
                total_slow_revenue = slow_movers['revenue'].sum()
                avg_days_since_sale = slow_movers['days_since_last_sale'].mean()
                total_slow_quantity = slow_movers['quantity_sold'].sum()
                total_slow_refunded = slow_movers['refund_quantity'].sum()
                total_slow_net = slow_movers['net_quantity'].sum()
                
                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
                with col_s1:
                    st.metric("Combined Revenue", f"${total_slow_revenue:,.2f}")
                with col_s2:
                    st.metric("Total Sold", f"{total_slow_quantity:,.0f}")
                with col_s3:
                    st.metric("Total Refunded", f"{total_slow_refunded:,.0f}")
                with col_s4:
                    st.metric("Net Quantity", f"{total_slow_net:,.0f}")
                with col_s5:
                    st.metric("Avg Days Since Sale", f"{avg_days_since_sale:.0f}")
            else:
                st.info(t('no_slow_moving'))
        
        # Add velocity comparison chart
        if len(fast_movers) > 0 and len(slow_movers) > 0:
            st.markdown("---")
            st.subheader(f"📈 {t('sales_velocity_comparison')}")
            
            # Combine top 5 from each for comparison
            comparison_fast = fast_movers.head(5).copy()
            comparison_fast['category_type'] = 'Fast-Moving'
            comparison_slow = slow_movers.head(5).copy()
            comparison_slow['category_type'] = 'Slow-Moving'
            
            comparison_df = pd.concat([comparison_fast, comparison_slow])
            
            fig = px.bar(
                comparison_df,
                x='item_name',
                y='sales_velocity',
                color='category_type',
                title='Sales Velocity Comparison (Units/Day) - Top 5 Each',
                labels={'sales_velocity': 'Sales Velocity (units/day)', 'item_name': 'Product'},
                color_discrete_map={'Fast-Moving': '#2ca02c', 'Slow-Moving': '#d62728'},
                barmode='group'
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, width='stretch')
    
    with tab2:
        st.subheader(t('abc_classification'))
        st.write("**A-items:** Top 20% products generating 80% revenue")
        st.write("**B-items:** Next 30% products generating 15% revenue")
        st.write("**C-items:** Remaining 50% products generating 5% revenue")
        
        abc_data = analyzer.classify_products_abc()
        
        # Distribution
        abc_summary = abc_data.groupby('abc_class').agg({
            'item_name': 'count',
            'revenue': 'sum',
            'quantity_sold': 'sum',
            'refund_quantity': 'sum',
            'net_quantity': 'sum'
        }).reset_index()
        # Rename to match translation keys
        abc_summary.columns = ['abc_class', 'count', 'revenue', 'quantity', 'refund_quantity', 'net_quantity']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Create chart before translation
            fig = px.bar(
                abc_summary,
                x='abc_class',
                y='revenue',
                title='Revenue by ABC Class',
                color='abc_class',
                color_discrete_map={'A': 'green', 'B': 'orange', 'C': 'red'}
            )
            # Update axis labels
            fig.update_xaxes(title_text=t('abc_class') if 'abc_class' in config.TRANSLATIONS[CURRENT_LANG] else 'ABC Class')
            fig.update_yaxes(title_text=t('revenue') if 'revenue' in config.TRANSLATIONS[CURRENT_LANG] else 'Revenue')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Translate for display in table
            abc_summary_display = translate_columns(abc_summary)
            st.dataframe(format_datetime_columns(abc_summary_display), use_container_width=True, hide_index=True)
        
        # Full table
        class_filter = st.multiselect(
            "Filter by class",
            ['A', 'B', 'C'],
            default=['A'],
            key='product_abc_class_filter'
        )
        filtered_abc = abc_data[abc_data['abc_class'].isin(class_filter)].copy()
        
        # Add marker to quantity and translate columns
        if 'quantity_sold' in filtered_abc.columns:
            filtered_abc = filtered_abc.rename(columns={'quantity_sold': 'quantity_sold ⭐'})
        
        filtered_abc = translate_columns(filtered_abc)
        
        st.dataframe(format_datetime_columns(filtered_abc), use_container_width=True, hide_index=True)
        st.caption("⭐ Quantity Sold = total units sold (ABC classification based on revenue)")
    
    with tab3:
        st.subheader(t('product_lifecycle_stages'))
        
        lifecycle = analyzer.get_product_lifecycle_stage()
        
        # Distribution by stage
        stage_counts = lifecycle['lifecycle_stage'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=stage_counts.values,
                names=stage_counts.index,
                title='Products by Lifecycle Stage'
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            stage_revenue = lifecycle.groupby('lifecycle_stage')['revenue'].sum()
            fig = px.bar(
                x=stage_revenue.index,
                y=stage_revenue.values,
                title='Revenue by Lifecycle Stage',
                labels={'x': 'Stage', 'y': 'Revenue ($)'}
            )
            st.plotly_chart(fig, width='stretch')
        
        # Add marker to quantity and translate columns
        lifecycle_display = lifecycle.copy()
        if 'quantity_sold' in lifecycle_display.columns:
            lifecycle_display = lifecycle_display.rename(columns={'quantity_sold': 'quantity_sold ⭐'})
        
        lifecycle_display = translate_columns(lifecycle_display)
        
        st.dataframe(format_datetime_columns(lifecycle_display), use_container_width=True, hide_index=True)
        st.caption("⭐ Quantity Sold = total units sold (lifecycle stage based on sales trends)")


def inventory_management_page(data):
    """Inventory management and reorder signals section."""
    st.header(f"📦 {t('inventory_title')}")
    st.markdown(t('inventory_description'))
    st.markdown("---")
    
    # Initialize session state for inventory data
    if 'inventory_data' not in st.session_state:
        st.session_state.inventory_data = None
    if 'inventory_manager' not in st.session_state:
        st.session_state.inventory_manager = None
    
    # File upload section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📤 {t('upload_inventory')}")
        st.info(t('inventory_file_info'))
        uploaded_file = st.file_uploader(
            "Choose inventory file", 
            type=['csv', 'xlsx', 'xls'],
            help="Upload your inventory file with product information"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button(f"🎲 {t('use_sample_inventory')}", type="secondary"):
            with st.spinner("Generating sample inventory..."):
                st.session_state.inventory_data = create_sample_inventory(data)
                st.success("✓ Sample inventory loaded!")
    
    # Load inventory data
    if uploaded_file is not None:
        try:
            with st.spinner("Loading inventory file..."):
                if uploaded_file.name.endswith('.csv'):
                    inventory_df = pd.read_csv(uploaded_file)
                else:
                    inventory_df = pd.read_excel(uploaded_file)
                st.session_state.inventory_data = inventory_df
                st.success(f"✓ Loaded {len(inventory_df)} items from {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return
    
    # If no inventory data, show message and return
    if st.session_state.inventory_data is None:
        st.warning("Please upload an inventory file or use sample inventory to begin.")
        
        # Show example format
        with st.expander("📋 Example Inventory File Format"):
            st.info("**Important:** Quantity is the authoritative stock level. Units & Pieces are informational only.")
            example_df = pd.DataFrame({
                'Item Code': ['ITEM001', 'ITEM002', 'ITEM003'],
                'Item Name': ['Paracetamol 500mg', 'Amoxicillin 250mg', 'Vitamin D3'],
                'Selling Price': [10.50, 25.00, 15.75],
                'Units': [1, 0, 3],
                'Pieces': [1, 1, 0],
                'Quantity': [1.50, 0.50, 3.00],
                'Category': ['Pain Relief', 'Antibiotics', 'Vitamins']
            })
            st.dataframe(example_df, use_container_width=True)
            st.caption("Example: ITEM001 has 1 unit + 1 piece = Quantity 1.50 | ITEM002 has 0 units + 1 piece = Quantity 0.50")
        return
    
    # Create inventory manager
    try:
        manager = InventoryManager(st.session_state.inventory_data, data)
        st.session_state.inventory_manager = manager
    except Exception as e:
        st.error(f"Error analyzing inventory: {str(e)}")
        return
    
    # Settings in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"⚙️ {t('reorder_settings')}")
    lead_time = st.sidebar.slider(
        t('lead_time_days'),
        min_value=1, max_value=30, value=config.LEAD_TIME_DAYS,
        help="Number of days between ordering and receiving stock"
    )
    urgency_threshold = st.sidebar.slider(
        t('urgency_days'),
        min_value=1, max_value=14, value=config.URGENCY_THRESHOLD_DAYS,
        help="Days threshold for urgent reorder alerts"
    )
    
    # Get inventory summary
    summary = manager.get_inventory_summary()
    
    # Display summary metrics
    st.subheader(f"📊 {t('inventory_overview')}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t('total_items'), f"{summary['total_items']:,}")
        st.metric(t('items_in_stock'), f"{summary['total_items'] - summary['items_out_of_stock']:,}")
    with col2:
        st.metric(t('inventory_value'), f"${summary['total_inventory_value']:,.2f}")
        st.metric(t('avg_days_stock'), f"{summary['avg_days_of_stock']:.1f}")
    with col3:
        st.metric(t('out_of_stock'), f"{summary['items_out_of_stock']:,}", delta=None)
        st.metric(t('urgent_reorder'), f"{summary['items_urgent_reorder']:,}", delta=None)
    with col4:
        st.metric(t('reorder_soon'), f"{summary['items_reorder_soon']:,}")
        st.metric(t('items_ok'), f"{summary['items_ok']:,}", delta=None, delta_color="normal")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"📁 {t('category_analysis')}",
        f"⚠️ {t('reorder_alerts')}",
        f"📉 {t('stockout_risk')}",
        f"📈 {t('overstocked_items')}",
        f"📊 {t('abc_inventory_analysis')}"
    ])
    
    with tab1:
        st.subheader(f"📁 {t('inventory_by_category')}")
        
        # Get category analysis
        category_df = manager.get_category_analysis()
        
        if len(category_df) > 0:
            # Category table FIRST
            category_df_display = translate_columns(category_df.copy())
            st.dataframe(category_df_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Category charts BELOW the table
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    category_df,
                    x='category',
                    y='stock_on_hand',
                    title="Stock on Hand by Category",
                    labels={'stock_on_hand': t('stock_on_hand'), 'category': t('category')},
                    color='stock_on_hand',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                fig = px.bar(
                    category_df,
                    x='category',
                    y='inventory_turnover',
                    title="Inventory Turnover by Category",
                    labels={'inventory_turnover': t('inventory_turnover'), 'category': t('category')},
                    color='inventory_turnover',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width='stretch')
        else:
            st.info("Category information not available in inventory data")
    
    with tab2:
        st.subheader(f"⚠️ {t('reorder_recommendations')}")
        
        # Get reorder signals
        reorder_df = manager.get_reorder_signals(
            lead_time_days=lead_time,
            urgency_threshold_days=urgency_threshold
        )
        
        # Filter options
        col1, col2 = st.columns([2, 3])
        with col1:
            signal_filter = st.selectbox(
                t('filter_by_signal'),
                ['All', 'OUT_OF_STOCK', 'URGENT_REORDER', 'REORDER_SOON', 'MONITOR', 'OK'],
                key='inventory_signal_filter'
            )
        
        if signal_filter != 'All':
            filtered_df = reorder_df[reorder_df['reorder_signal'] == signal_filter].copy()
        else:
            filtered_df = reorder_df.copy()
        
        # Signal distribution chart
        col1, col2 = st.columns(2)
        with col1:
            signal_counts = reorder_df['reorder_signal'].value_counts()
            fig = px.pie(
                values=signal_counts.values,
                names=signal_counts.index,
                title="Reorder Signal Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Top items needing reorder
            urgent_items = reorder_df[
                reorder_df['reorder_signal'].isin(['OUT_OF_STOCK', 'URGENT_REORDER'])
            ].head(10)
            
            if len(urgent_items) > 0:
                fig = px.bar(
                    urgent_items,
                    x='quantity_to_order',
                    y='item_name',
                    title="Top 10 Items to Reorder (by Quantity)",
                    labels={'quantity_to_order': 'Quantity to Order', 'item_name': 'Product'},
                    orientation='h',
                    color='reorder_signal',
                    color_discrete_map={
                        'OUT_OF_STOCK': '#dc3545',
                        'URGENT_REORDER': '#fd7e14'
                    }
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, width='stretch')
        
        # Display table
        st.markdown(f"### 📋 {t('reorder_recommendations')} ({len(filtered_df)} items)")
        
        # Build display columns - include Units, Pieces, and Quantity
        display_cols = ['item_code', 'item_name', 'category', 'units', 'pieces', 'quantity', 
                       'reorder_signal', 'reorder_point', 'days_of_stock', 'daily_sales_velocity', 
                       'quantity_to_order', 'priority_score']
        
        # Select only columns that exist in the data
        display_df = filtered_df[
            [col for col in display_cols if col in filtered_df.columns]
        ].copy()
        
        # Add marker to quantity column and translate
        if 'quantity' in display_df.columns:
            display_df = display_df.rename(columns={'quantity': 'quantity ⭐'})
        
        # Translate all column names
        display_df = translate_columns(display_df)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Add explanation
        st.info("⭐ **Quantity** is the authoritative stock level used for all calculations. Units & Pieces are informational.")
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label=f"📥 {t('download_reorder_list')}",
            data=csv,
            file_name=f"reorder_list_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader(t('stockout_forecast', days=config.STOCKOUT_FORECAST_DAYS))
        
        # Get stockout risk analysis
        stockout_risk = manager.get_stockout_risk(forecast_days=config.STOCKOUT_FORECAST_DAYS)
        
        if len(stockout_risk) > 0:
            st.warning(f"⚠️ {len(stockout_risk)} items at risk of stockout in the next {config.STOCKOUT_FORECAST_DAYS} days!")
            
            # Stockout timeline
            stockout_risk['stockout_date'] = pd.to_datetime(stockout_risk['estimated_stockout_date'])
            
            fig = px.scatter(
                stockout_risk.head(20),
                x='stockout_date',
                y='item_name',
                size='daily_sales_velocity',
                color='predicted_stockout_days',
                title=f"Stockout Timeline (Next {config.STOCKOUT_FORECAST_DAYS} Days)",
                labels={
                    'stockout_date': t('estimated_date'),
                    'item_name': 'Product',
                    'predicted_stockout_days': 'Days Until Stockout',
                    'daily_sales_velocity': t('daily_velocity')
                },
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, width='stretch')
            
            # Display table
            display_cols = ['item_name', 'category', 'units', 'pieces', 'quantity', 
                          'predicted_stockout_days', 'estimated_stockout_date', 
                          'daily_sales_velocity', 'potential_lost_revenue']
            
            display_df = stockout_risk[[col for col in display_cols if col in stockout_risk.columns]].copy()
            
            # Add marker to quantity column and translate
            if 'quantity' in display_df.columns:
                display_df = display_df.rename(columns={'quantity': 'quantity ⭐'})
            
            # Translate column names
            display_df = translate_columns(display_df)
            
            # Format dates after translation
            trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
            est_date_col = trans_cols.get('estimated_date', 'Estimated Date')
            if est_date_col in display_df.columns:
                display_df[est_date_col] = pd.to_datetime(display_df[est_date_col]).dt.strftime('%Y-%m-%d')
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.caption("⭐ Quantity is the total stock used for stockout prediction")
        else:
            st.success(f"✓ No items at risk of stockout in the next {config.STOCKOUT_FORECAST_DAYS} days!")
    
    with tab4:
        st.subheader(f"📈 {t('overstock_analysis')}")
        
        # Get overstocked items
        overstocked = manager.get_overstocked_items(
            overstock_threshold_days=config.OVERSTOCK_THRESHOLD_DAYS
        )
        
        if len(overstocked) > 0:
            st.info(f"ℹ️ {len(overstocked)} items have more than {config.OVERSTOCK_THRESHOLD_DAYS} days of stock")
            
            # Overstock value chart
            if 'overstock_value' in overstocked.columns:
                top_overstock = overstocked.head(15)
                fig = px.bar(
                    top_overstock,
                    x='item_name',
                    y='overstock_value',
                    title="Top 15 Overstocked Items by Value",
                    labels={'overstock_value': t('overstock_value'), 'item_name': 'Product'},
                    color='days_of_stock',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width='stretch')
            
            # Display table
            display_cols = ['item_name', 'category', 'units', 'pieces', 'quantity', 
                          'days_of_stock', 'daily_sales_velocity', 'overstock_value']
            
            display_df = overstocked[[col for col in display_cols if col in overstocked.columns]].head(50)
            
            # Add marker to quantity column and translate
            if 'quantity' in display_df.columns:
                display_df = display_df.rename(columns={'quantity': 'quantity ⭐'})
            
            # Translate column names
            display_df = translate_columns(display_df)
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.caption("⭐ Quantity is the total stock - high Days of Stock indicates slow-moving items")
        else:
            st.success(f"✓ No overstocked items (>{config.OVERSTOCK_THRESHOLD_DAYS} days of stock)")
    
    with tab5:
        st.subheader(f"📊 {t('abc_inventory_analysis')}")
        
        # Get ABC analysis
        abc_df = manager.get_abc_analysis()
        
        # ABC distribution
        col1, col2 = st.columns(2)
        
        with col1:
            abc_counts = abc_df['abc_class'].value_counts().sort_index()
            fig = px.pie(
                values=abc_counts.values,
                names=abc_counts.index,
                title="ABC Classification Distribution",
                color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c']
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            abc_revenue = abc_df.groupby('abc_class')['total_revenue'].sum().sort_index()
            fig = px.bar(
                x=abc_revenue.index,
                y=abc_revenue.values,
                title="Revenue by ABC Class",
                labels={'x': 'ABC Class', 'y': t('revenue')},
                color=abc_revenue.index,
                color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c']
            )
            st.plotly_chart(fig, width='stretch')
        
        # ABC table
        st.markdown("### ABC Classification Details")
        display_cols = ['item_name', 'abc_class', 'units', 'pieces', 'quantity', 
                       'total_revenue', 'cumulative_revenue_pct', 'total_quantity_sold']
        
        display_df = abc_df[[col for col in display_cols if col in abc_df.columns]].head(50)
        
        # Add marker to quantity column and translate
        if 'quantity' in display_df.columns:
            display_df = display_df.rename(columns={'quantity': 'quantity ⭐'})
        
        # Translate column names
        display_df = translate_columns(display_df)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption("⭐ Quantity shows current stock | Total Sold shows historical sales | ABC Class based on revenue")


def rfm_analysis_page(data):
    """RFM segmentation section."""
    st.header(f"🎯 {t('rfm_title')}")
    
    st.markdown(f"""
{t('rfm_description')}
- {t('rfm_new')}
- {t('rfm_potential')}  
- {t('rfm_champions')}
- {t('rfm_loyal')}
- {t('rfm_at_risk')}
- {t('rfm_lost')}
    """)
    
    # Phone mapping file uploader
    st.markdown("---")
    st.subheader("📱 Optional: Upload Phone Numbers")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Upload an Excel file with customer names and phone numbers to include contact information in RFM analysis.")
        phone_file = st.file_uploader(
            "Upload phone mapping file (optional)",
            type=['xlsx', 'xls', 'csv'],
            help="File should contain columns: 'اسم العميل' (Customer Name) and 'التليفونات' (Phone)",
            key='rfm_phone_upload'
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("📋 Show Format Example", key='phone_format_example'):
            example_df = pd.DataFrame({
                'اسم العميل': ['أحمد محمد', 'سارة علي', 'محمد خالد'],
                'التليفونات': ['0123456789', '0198765432', '0111222333']
            })
            st.dataframe(example_df, hide_index=True)
    
    st.markdown("---")
    
    # Initialize RFM analyzer
    analyzer = get_rfm_analyzer(data)
    
    # Load phone mapping if file is uploaded
    if phone_file is not None:
        try:
            if phone_file.name.endswith('.csv'):
                phone_df = pd.read_csv(phone_file)
            else:
                phone_df = pd.read_excel(phone_file)
            
            if analyzer.load_phone_mapping(phone_df):
                st.success(f"✓ Loaded {len(analyzer.phone_mapping)} phone numbers from {phone_file.name}")
            else:
                st.error("❌ Could not load phone mapping. Please ensure the file has columns 'اسم العميل' and 'التليفونات'")
        except Exception as e:
            st.error(f"❌ Error loading phone file: {str(e)}")
    
    rfm_data = analyzer.segment_customers()
    
    # Merge phone numbers into RFM data
    rfm_data = analyzer.merge_phone_numbers(rfm_data)
    
    # Create tabs for different views
    tab1, tab2 = st.tabs([
        "📊 Overall Segmentation",
        "📂 RFM by Category"
    ])
    
    with tab1:
        # Segment summary
        st.subheader(t('segment_overview'))
        segment_summary = analyzer.get_segment_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                segment_summary,
                values='customer_count',
                names='segment',
                title='Customer Distribution by Segment'
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.bar(
                segment_summary,
                x='segment',
                y='total_revenue',
                title='Revenue by Segment',
                color='total_revenue',
                color_continuous_scale='Blues'
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, width='stretch')
        
        segment_summary_display = translate_columns(segment_summary.copy())
        st.dataframe(format_datetime_columns(segment_summary_display), use_container_width=True, hide_index=True)
        
        # Segment details
        st.subheader(t('segment_details'))
        
        selected_segment = st.selectbox(
            "Select segment to explore",
            segment_summary['segment'].tolist(),
            key='rfm_segment_selector'
        )
        
        segment_customers = analyzer.get_customers_by_segment(selected_segment)
        
        # Merge phone numbers
        segment_customers = analyzer.merge_phone_numbers(segment_customers)
        
        st.write(f"**{selected_segment}** - {len(segment_customers)} customers")
        
        # Select columns to display (include phone if available)
        display_cols = ['customer_name', 'phone', 'recency', 'frequency', 'monetary', 
                       'r_score', 'f_score', 'm_score', 'rfm_score']
        segment_customers_display = translate_columns(segment_customers.head(20)[display_cols].copy())
        st.dataframe(format_datetime_columns(segment_customers_display), use_container_width=True, hide_index=True)
        
        # Export buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            csv_segment = segment_customers[display_cols].to_csv(index=False)
            st.download_button(
                label=f"📥 Download All {selected_segment} Customers (CSV)",
                data=csv_segment,
                file_name=f"rfm_segment_{selected_segment}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key='download_segment_tab1'
            )
        
        with col_btn2:
            # Extract non-empty phone numbers
            phone_numbers = segment_customers['phone'].astype(str).str.strip()
            phone_numbers = phone_numbers[phone_numbers != ''].tolist()
            phone_list = ', '.join(phone_numbers)
            
            if phone_numbers:
                st.download_button(
                    label=f"📱 Copy Phone Numbers ({len(phone_numbers)})",
                    data=phone_list,
                    file_name=f"phones_{selected_segment}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key='copy_phones_tab1'
                )
                # Also display in text area for easy copying
                with st.expander("📋 View Phone Numbers"):
                    st.text_area(
                        "Phone numbers (comma-separated)",
                        value=phone_list,
                        height=100,
                        key='phones_display_tab1',
                        help="Select all (Ctrl+A) and copy (Ctrl+C)"
                    )
            else:
                st.info("📱 No phone numbers available")
    
    with tab2:
        st.subheader(f"📂 {t('rfm_by_category')}")
        st.markdown("""
        This view shows how customers behave within each product category. 
        A customer might be a **Champion** in one category but **At Risk** in another!
        """)
        
        # Get RFM by category data
        rfm_by_category = analyzer.calculate_rfm_by_category()
        
        # Merge phone numbers into category data
        rfm_by_category = analyzer.merge_phone_numbers(rfm_by_category)
        
        category_segment_summary = analyzer.get_category_segment_summary()
        
        # Get list of categories
        categories = sorted(rfm_by_category['category'].unique())
        
        # Category selector
        selected_category = st.selectbox(
            "Select Product Category",
            categories,
            key='rfm_category_select'
        )
        
        # Filter data for selected category
        category_data = rfm_by_category[rfm_by_category['category'] == selected_category]
        category_summary = category_segment_summary[category_segment_summary['category'] == selected_category]
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Customers", f"{len(category_data):,}")
        with col2:
            st.metric("Total Revenue", f"${category_data['monetary'].sum():,.2f}")
        with col3:
            st.metric("Avg Customer Value", f"${category_data['monetary'].mean():,.2f}")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Segment distribution pie chart
            fig_pie = px.pie(
                category_summary,
                values='customer_count',
                names='segment',
                title=f'Customer Segments in {selected_category}',
                hole=0.4
            )
            st.plotly_chart(fig_pie, width='stretch')
        
        with col2:
            # Revenue by segment bar chart
            fig_bar = px.bar(
                category_summary,
                x='segment',
                y='total_revenue',
                title=f'Revenue by Segment - {selected_category}',
                color='total_revenue',
                color_continuous_scale='Viridis'
            )
            fig_bar.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_bar, width='stretch')
        
        # Summary table
        st.markdown(f"#### Segment Summary for {selected_category}")
        display_summary = category_summary[[
            'segment', 'customer_count', 'total_revenue', 'pct_of_category', 
            'avg_recency', 'avg_frequency'
        ]].copy()
        
        # Rename to match translation keys
        display_summary.columns = ['segment', 'customers', 'revenue', 'revenue_pct', 'recency', 'frequency']
        display_summary = translate_columns(display_summary)
        
        # Get translated column names for formatting
        trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
        cust_col = trans_cols.get('customers', 'Customers')
        rev_col = trans_cols.get('revenue', 'Revenue')
        rev_pct_col = trans_cols.get('revenue_pct', '% of Category')
        rec_col = trans_cols.get('recency', 'Recency')
        freq_col = trans_cols.get('frequency', 'Frequency')
        
        st.dataframe(
            display_summary.style.format({
                cust_col: '{:,.0f}',
                rev_col: '${:,.2f}',
                rev_pct_col: '{:.1f}%',
                rec_col: '{:.0f}',
                freq_col: '{:.1f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Customer details by segment
        st.markdown("#### Customer Details")
        
        # Get segments available in this category
        available_segments = category_summary['segment'].tolist()
        
        selected_segment_cat = st.selectbox(
            "Filter by Segment (optional)",
            ['All Segments'] + available_segments,
            key='rfm_segment_filter'
        )
        
        # Filter customers
        if selected_segment_cat == 'All Segments':
            customers_display = category_data
        else:
            customers_display = category_data[category_data['segment'] == selected_segment_cat]
        
        # Display ALL filtered customers (not just top 50)
        st.write(f"Showing all {len(customers_display)} customers")
        
        # Select columns to display (include phone)
        display_cols = ['customer_name', 'phone', 'segment', 'recency', 'frequency', 'monetary']
        display_customers = customers_display[display_cols].copy()
        display_customers = translate_columns(display_customers)
        
        # Get translated column names for formatting
        trans_cols = config.COLUMN_TRANSLATIONS.get(CURRENT_LANG, config.COLUMN_TRANSLATIONS['en'])
        rec_col = trans_cols.get('recency', 'Recency')
        freq_col = trans_cols.get('frequency', 'Frequency')
        mon_col = trans_cols.get('monetary', 'Monetary')
        
        st.dataframe(
            display_customers.style.format({
                rec_col: '{:.0f}',
                freq_col: '{:.0f}',
                mon_col: '${:,.2f}'
            }),
            use_container_width=True,
            hide_index=True,
            height=600  # Set a fixed height with scrolling
        )
        
        # Download options for filtered data
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            csv_filtered = customers_display[display_cols].to_csv(index=False)
            st.download_button(
                label=f"📥 Download Filtered Customer Data (CSV)",
                data=csv_filtered,
                file_name=f"rfm_{selected_category}_{selected_segment_cat}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key='download_category_segment'
            )
        
        with col_btn2:
            # Extract non-empty phone numbers
            phone_numbers = customers_display['phone'].astype(str).str.strip()
            phone_numbers = phone_numbers[phone_numbers != ''].tolist()
            phone_list = ', '.join(phone_numbers)
            
            if phone_numbers:
                st.download_button(
                    label=f"📱 Copy Phone Numbers ({len(phone_numbers)})",
                    data=phone_list,
                    file_name=f"phones_{selected_category}_{selected_segment_cat}_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key='copy_phones_tab2'
                )
                # Also display in text area for easy copying
                with st.expander("📋 View Phone Numbers"):
                    st.text_area(
                        "Phone numbers (comma-separated)",
                        value=phone_list,
                        height=100,
                        key='phones_display_tab2',
                        help="Select all (Ctrl+A) and copy (Ctrl+C)"
                    )
            else:
                st.info("📱 No phone numbers available")


def refill_prediction_page(data):
    """Advanced refill prediction section with price forecasting."""
    st.header(f"💊 {t('refill_title')}")
    
    st.markdown(t('refill_description'))
    
    predictor = get_refill_predictor(data)
    intervals_df = predictor.calculate_purchase_intervals(include_price_prediction=True)
    
    # Enhanced summary metrics
    st.subheader(t('refill_dashboard'))
    summary = predictor.get_refill_summary_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(t('tracked_pairs'), f"{summary['total_refill_pairs']:,}")
    with col2:
        st.metric(t('avg_interval'), f"{summary['avg_refill_interval_days']:.1f} {t('days')}")
    with col3:
        st.metric(t('overdue'), f"{summary['num_overdue_refills']:,}", 
                 delta=f"{summary['num_overdue_refills']}")
    with col4:
        st.metric(t('upcoming_30d'), f"{summary['num_upcoming_refills_30d']:,}")
    with col5:
        high_conf = len(intervals_df[intervals_df['confidence_score'] >= 70]) if intervals_df is not None and len(intervals_df) > 0 else 0
        st.metric(t('high_confidence'), f"{high_conf:,}")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📅 {t('upcoming_refills')}", f"⚠️ {t('overdue_refills')}", f"👤 {t('customer_schedule')}", f"💰 {t('price_predictions')}"
    ])
    
    with tab1:
        st.subheader(f"📅 {t('upcoming_refills_revenue')}")
        
        days_ahead = st.slider("Look ahead (days)", 7, 60, 30, key='refill_days_ahead')
        upcoming = predictor.get_upcoming_refills(days_ahead)
        
        if len(upcoming) > 0:
            # Revenue forecast metrics
            if 'predicted_order_value' in upcoming.columns:
                total_predicted_revenue = upcoming['predicted_order_value'].sum()
                avg_order_value = upcoming['predicted_order_value'].mean()
                high_confidence_revenue = upcoming[upcoming['confidence_score'] >= 70]['predicted_order_value'].sum()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Expected Refills", f"{len(upcoming):,}")
                with col2:
                    st.metric("Total Predicted Revenue", f"${total_predicted_revenue:,.2f}")
                with col3:
                    st.metric("Avg Order Value", f"${avg_order_value:,.2f}")
                with col4:
                    st.metric("High Confidence Revenue", f"${high_confidence_revenue:,.2f}",
                             help="Revenue from predictions with 70+ confidence score")
            else:
                st.info(f"{len(upcoming)} refills expected in the next {days_ahead} days")
            
            # Timeline
            # Build hover_data dynamically based on available columns
            hover_cols = ['avg_interval_days']
            if 'first_order_date' in upcoming.columns:
                hover_cols.append('first_order_date')
            if 'days_since_first_order' in upcoming.columns:
                hover_cols.append('days_since_first_order')
            if 'predicted_order_value' in upcoming.columns:
                hover_cols.append('predicted_order_value')
            if 'predicted_quantity' in upcoming.columns:
                hover_cols.append('predicted_quantity')
            
            fig = px.scatter(
                upcoming,
                x='predicted_next_purchase',
                y='customer_name',
                color='item_name',
                size='confidence_score',
                title=f'Refill Timeline (Next {days_ahead} Days)',
                hover_data=hover_cols
            )
            st.plotly_chart(fig, width='stretch')
            
            upcoming_display = translate_columns(upcoming.copy())
            st.dataframe(format_datetime_columns(upcoming_display), use_container_width=True, hide_index=True)
        else:
            st.info(f"No refills expected in the next {days_ahead} days")
    
    with tab2:
        st.subheader(f"⚠️ {t('overdue_refills_lost')}")
        
        col1, col2 = st.columns(2)
        with col1:
            tolerance = st.slider("Grace period (days)", 0, 14, 7, 
                                 help="Days of tolerance before considering overdue",
                                 key='refill_grace_period')
        with col2:
            max_overdue_days = st.slider("Show overdue up to (days)", 30, 365, 90, step=30,
                                        help="Maximum days since last purchase to show",
                                        key='refill_max_overdue')
        
        overdue = predictor.get_overdue_refills(tolerance)
        
        # Filter based on adjustable period
        total_overdue = len(overdue)
        if len(overdue) > 0 and 'last_purchase_date' in overdue.columns:
            # Calculate days since last purchase from current date
            from datetime import datetime
            current_date = predictor.current_date
            overdue['days_since_last_purchase'] = (current_date - overdue['last_purchase_date']).dt.days
            
            # Filter to only show within selected period
            overdue = overdue[overdue['days_since_last_purchase'] <= max_overdue_days].copy()
            filtered_count = len(overdue)
            excluded_count = total_overdue - filtered_count
            
            # Dynamic status classification based on max_overdue_days
            # Divide the period into 4 tiers
            tier_size = max_overdue_days / 4
            likely_lost_threshold = max_overdue_days * 0.75  # Top 25%
            high_risk_threshold = max_overdue_days * 0.50   # 50-75%
            at_risk_threshold = max_overdue_days * 0.25     # 25-50%
            # Below 25% = Action Needed
            
            def reclassify_status(row):
                days_overdue = row['days_overdue']
                if days_overdue >= likely_lost_threshold:
                    return 'Likely Lost'
                elif days_overdue >= high_risk_threshold:
                    return 'At High Risk'
                elif days_overdue >= at_risk_threshold:
                    return 'At Risk'
                else:
                    return 'Action Needed'
            
            overdue['customer_status'] = overdue.apply(reclassify_status, axis=1)
            
            if excluded_count > 0:
                st.info(f"📅 Showing overdue refills from past {max_overdue_days} days ({filtered_count} shown, {excluded_count} older excluded)")
        
        if len(overdue) > 0:
            # Status breakdown with dynamic thresholds
            st.markdown("### 📊 Customer Status Breakdown")
            
            if 'customer_status' in overdue.columns:
                status_counts = overdue['customer_status'].value_counts()
                
                # Calculate dynamic threshold labels
                likely_lost_days = int(likely_lost_threshold)
                high_risk_days = int(high_risk_threshold)
                at_risk_days = int(at_risk_threshold)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    likely_lost = status_counts.get('Likely Lost', 0)
                    st.metric(f"🔴 Likely Lost ({likely_lost_days}+ days)", likely_lost, 
                             delta=f"{likely_lost} customers")
                
                with col2:
                    high_risk = status_counts.get('At High Risk', 0)
                    st.metric(f"🟠 At High Risk ({high_risk_days}-{likely_lost_days-1} days)", high_risk,
                             delta=f"{high_risk} customers")
                
                with col3:
                    at_risk = status_counts.get('At Risk', 0)
                    st.metric(f"🟡 At Risk ({at_risk_days}-{high_risk_days-1} days)", at_risk,
                             delta=f"{at_risk} customers")
                
                with col4:
                    action_needed = status_counts.get('Action Needed', 0)
                    st.metric(f"🟢 Action Needed (<{at_risk_days} days)", action_needed,
                             delta=f"{action_needed} customers")
                
                # All overdue visualization
                st.markdown("---")
                st.markdown("### 📈 All Overdue Refills")
            
            st.error(f"{len(overdue)} total overdue refills detected!")
            
            # Top overdue colored by status
            if 'customer_status' in overdue.columns:
                fig = px.bar(
                    overdue.head(20),
                    x='days_overdue',
                    y='customer_name',
                    color='customer_status',
                    title='Top 20 Overdue Refills by Status',
                    orientation='h',
                    color_discrete_map={
                        'Likely Lost': '#FF4B4B',
                        'At High Risk': '#FFA500', 
                        'At Risk': '#FFD700',
                        'Action Needed': '#90EE90'
                    }
                )
            else:
                fig = px.bar(
                    overdue.head(20),
                    x='days_overdue',
                    y='customer_name',
                    color='item_name',
                    title='Top 20 Overdue Refills',
                    orientation='h'
                )
            
            st.plotly_chart(fig, width='stretch')
            
            # Full data table
            st.markdown("### 📋 Complete Overdue List")
            overdue_display = translate_columns(overdue.copy())
            st.dataframe(format_datetime_columns(overdue_display), use_container_width=True, hide_index=True)
        else:
            if total_overdue > 0:
                st.info(f"📅 No overdue refills in the past {max_overdue_days} days. ({total_overdue} customers haven't ordered in {max_overdue_days}+ days - likely lost)")
            else:
                st.success("✅ No overdue refills!")
    
    with tab3:
        st.subheader(t('customer_refill_schedule'))
        
        # Customer selection
        customers = data['customer_name'].unique()
        selected_customer = st.selectbox("Select customer", sorted([str(c) for c in customers]), key='refill_customer_selector')
        
        schedule = predictor.get_customer_refill_schedule(selected_customer)
        
        if len(schedule) > 0:
            # Status summary
            status_counts = schedule['refill_status'].value_counts()
            cols = st.columns(len(status_counts))
            for idx, (status, count) in enumerate(status_counts.items()):
                with cols[idx]:
                    if status == 'Overdue':
                        st.error(f"{status}: {count}")
                    elif status == 'Due Now':
                        st.warning(f"{status}: {count}")
                    elif status == 'Due Soon':
                        st.info(f"{status}: {count}")
                    else:
                        st.success(f"{status}: {count}")
            
            schedule_display = translate_columns(schedule.copy())
            st.dataframe(format_datetime_columns(schedule_display), use_container_width=True, hide_index=True)
        else:
            st.info("No refill history for this customer")
    
    with tab4:
        st.subheader(f"💰 {t('order_value_price_predictions')}")
        
        if intervals_df is not None and len(intervals_df) > 0:
            st.markdown("""
            **Advanced Metrics:**
            - 📈 **Price Trend**: Linear regression on historical prices
            - 📊 **Quantity Trend**: Purchase quantity pattern analysis
            - 💵 **Predicted Order Value**: Forecasted price × predicted quantity
            - 🎯 **Regularity Score**: How consistent the purchase pattern is (0-100)
            """)
            
            # Top predicted order values
            top_predictions = intervals_df.nlargest(20, 'predicted_order_value')[
                ['customer_name', 'item_name', 'first_order_date', 'days_since_first_order',
                 'predicted_order_value', 'predicted_unit_price', 
                 'predicted_quantity', 'confidence_score', 'regularity_score', 
                 'price_trend', 'total_lifetime_value']
            ].copy()
            
            # Format for display
            st.write("**Top 20 Predicted Order Values**")
            top_predictions_display = translate_columns(top_predictions.copy())
            st.dataframe(format_datetime_columns(top_predictions_display), use_container_width=True, hide_index=True)
            
            # Price trend analysis
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**📈 Price Trend Distribution**")
                increasing_prices = len(intervals_df[intervals_df['price_trend'] > 0.1])
                stable_prices = len(intervals_df[abs(intervals_df['price_trend']) <= 0.1])
                decreasing_prices = len(intervals_df[intervals_df['price_trend'] < -0.1])
                
                trend_data = pd.DataFrame({
                    'Trend': ['Increasing', 'Stable', 'Decreasing'],
                    'Count': [increasing_prices, stable_prices, decreasing_prices]
                })
                
                fig = px.pie(trend_data, values='Count', names='Trend',
                           title='Price Trends Across Products',
                           color='Trend',
                           color_discrete_map={'Increasing': 'red', 'Stable': 'blue', 'Decreasing': 'green'})
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.write("**🎯 Regularity Score Distribution**")
                high_reg = len(intervals_df[intervals_df['regularity_score'] >= 70])
                med_reg = len(intervals_df[(intervals_df['regularity_score'] >= 40) & (intervals_df['regularity_score'] < 70)])
                low_reg = len(intervals_df[intervals_df['regularity_score'] < 40])
                
                reg_data = pd.DataFrame({
                    'Regularity': ['High (70+)', 'Medium (40-70)', 'Low (<40)'],
                    'Count': [high_reg, med_reg, low_reg]
                })
                
                fig = px.bar(reg_data, x='Regularity', y='Count',
                           title='Purchase Regularity Distribution',
                           color='Count', color_continuous_scale='Blues')
                st.plotly_chart(fig, width='stretch')
            
            # Summary insights
            st.markdown("---")
            st.subheader(t('key_insights'))
            
            total_predicted_revenue = intervals_df['predicted_order_value'].sum()
            avg_confidence = intervals_df['confidence_score'].mean()
            avg_regularity = intervals_df['regularity_score'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Predicted Revenue", f"${total_predicted_revenue:,.2f}",
                         help="Sum of all predicted order values")
            with col2:
                st.metric("Avg Confidence", f"{avg_confidence:.1f}%",
                         help="Average prediction confidence across all customers")
            with col3:
                st.metric("Avg Regularity", f"{avg_regularity:.1f}%",
                         help="How consistent customers are with their purchases")
            
            st.success("💡 **Tip**: Focus on high regularity score customers for targeted refill reminders - they're more predictable!")
        else:
            st.info("Not enough data for price predictions")


def cross_sell_page(data):
    """Cross-sell analysis section."""
    st.header(f"🔗 {t('cross_sell_title')}")
    
    st.markdown(f"""
{t('market_basket_description')} 
{t('market_basket_helps')}
    """)
    
    # Performance optimization option
    enable_sampling = True
    max_records = 100000
    
    # Show performance info for large datasets
    if len(data) > 50000:
        with st.expander("⚡ Performance Settings", expanded=False):
            st.info(f"📊 Dataset has {len(data):,} records. For optimal performance, sampling is recommended.")
            enable_sampling = st.checkbox("Enable sampling for faster analysis", value=True, 
                                         help="Sample most recent records for better performance",
                                         key='crosssell_enable_sampling')
            if enable_sampling:
                max_records = st.slider("Max records to analyze", 10000, 200000, 100000, 10000,
                                       help="More records = more accurate but slower",
                                       key='crosssell_max_records')
    
    analyzer = get_cross_sell_analyzer(data, _enable_sampling=enable_sampling, _max_records=max_records)
    
    # Show diagnostics in expander
    with st.expander("📊 Analysis Diagnostics & Data Quality", expanded=False):
        diag = analyzer.get_analysis_diagnostics()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", f"{diag['total_orders']:,}")
            st.metric("Unique Products", f"{diag['unique_products']:,}")
        with col2:
            st.metric("Multi-Item Orders", f"{diag['multi_item_orders']:,}")
            st.metric("Multi-Item %", f"{diag['pct_multi_item']:.1f}%")
        with col3:
            st.metric("Avg Basket Size", f"{diag['avg_basket_size']:.2f}")
            st.metric("Products in 10+ Orders", f"{diag['products_in_10plus_orders']:,}")
        
        if diag.get('recommendations'):
            st.markdown("**⚠️ Data Quality Notes:**")
            for rec in diag['recommendations']:
                st.warning(rec)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🎁 {t('product_bundles')}", f"🔄 {t('product_associations')}", f"📊 {t('market_basket')}", f"💡 {t('recommendations')}"
    ])
    
    with tab1:
        st.subheader(t('suggested_bundles'))
        
        st.markdown("Bundles are groups of products frequently purchased together in the same transaction.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            min_items = st.number_input("Min items in bundle", 2, 5, 2, key='crosssell_min_items')
        with col2:
            max_items = st.number_input("Max items in bundle", 2, 10, 4, key='crosssell_max_items')
        with col3:
            n_bundles = st.number_input("Number of bundles", 5, 20, 10, key='crosssell_n_bundles')
        
        with st.spinner("Analyzing product bundles..."):
            bundles = analyzer.get_bundle_suggestions(min_items, max_items, n_bundles, auto_adjust=True)
        
        if len(bundles) > 0:
            st.success(f"✓ Found {len(bundles)} product bundles!")
            
            # Show summary table
            bundles_display = bundles[['bundle_items', 'itemset_size', 'bundle_frequency', 'support', 'bundle_revenue', 'avg_basket_value']].copy()
            bundles_display = translate_columns(bundles_display)
            st.dataframe(
                bundles_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Detailed view
            st.markdown("---")
            st.markdown("### Bundle Details")
            
            for idx, row in bundles.iterrows():
                support_pct = row['support'] * 100
                freq = row.get('bundle_frequency', int(row['support'] * analyzer.data['order_id'].nunique()))
                
                with st.expander(
                    f"Bundle {idx + 1}: {row['itemset_size']} items | "
                    f"Appears in {freq} orders ({support_pct:.1f}%) | "
                    f"Revenue: ${row['bundle_revenue']:,.2f}"
                ):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write("**Bundle Items:**")
                        for item in row['bundle_items']:
                            st.write(f"• {item}")
                    
                    with col_b:
                        st.write("**Bundle Metrics:**")
                        st.write(f"• Frequency: {freq} times")
                        st.write(f"• Support: {support_pct:.2f}%")
                        st.write(f"• Total Revenue: ${row['bundle_revenue']:,.2f}")
                        st.write(f"• Avg Basket Value: ${row.get('avg_basket_value', 0):,.2f}")
                        st.write(f"• Bundle Score: {row['score']:.2f}")
        else:
            st.warning("⚠️ No product bundles found with current settings.")
            st.info(
                "**Tips to improve results:**\n"
                "- Lower minimum items to 2\n"
                "- Ensure you have multi-item transactions in your data\n"
                "- Check the diagnostics above for data quality insights\n"
                "- Try with more historical data (500+ transactions recommended)"
            )
    
    with tab2:
        st.subheader(t('product_affinity'))
        
        st.markdown("""
        **Product affinity** shows which products are frequently purchased together. 
        - **Lift > 1**: Products bought together more than expected by chance
        - **Confidence**: Probability of buying product B when product A is purchased
        """)
        
        with st.spinner("Calculating product associations..."):
            affinity = analyzer.analyze_product_affinity()
        
        if len(affinity) > 0:
            st.success(f"✓ Found {len(affinity)} product associations!")
            
            # Filter controls
            col1, col2 = st.columns(2)
            with col1:
                min_lift_filter = st.slider("Minimum Lift", 1.0, 5.0, 1.0, 0.1, key='crosssell_min_lift')
            with col2:
                n_show = st.slider("Number of associations to show", 10, 50, 20, key='crosssell_n_show')
            
            # Apply filters
            affinity_filtered = affinity[affinity['lift'] >= min_lift_filter].head(n_show)
            
            if len(affinity_filtered) > 0:
                # Top associations
                st.write(f"**Top {len(affinity_filtered)} Product Pairs (by Lift)**")
                affinity_display = translate_columns(affinity_filtered.copy())
                st.dataframe(format_datetime_columns(affinity_display), use_container_width=True, hide_index=True)
                
                # Heatmap of top products
                if len(affinity_filtered) >= 5:
                    st.markdown("---")
                    st.write("**Product Affinity Heatmap**")
                    
                    top_products = list(set(
                        list(affinity_filtered.head(15)['product_a']) +
                        list(affinity_filtered.head(15)['product_b'])
                    ))[:10]
                    
                    # Create co-occurrence matrix
                    matrix = np.zeros((len(top_products), len(top_products)))
                    for i, prod_a in enumerate(top_products):
                        for j, prod_b in enumerate(top_products):
                            if i != j:
                                matching = affinity[
                                    ((affinity['product_a'] == prod_a) & (affinity['product_b'] == prod_b)) |
                                    ((affinity['product_a'] == prod_b) & (affinity['product_b'] == prod_a))
                                ]
                                if len(matching) > 0:
                                    matrix[i, j] = matching.iloc[0]['lift']
                    
                    fig = px.imshow(
                        matrix,
                        x=top_products,
                        y=top_products,
                        title='Product Affinity Heatmap (Lift)',
                        color_continuous_scale='Blues',
                        aspect='auto',
                        labels=dict(color="Lift")
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, width='stretch')
            else:
                st.info(f"No associations found with lift >= {min_lift_filter}. Try lowering the minimum lift.")
        else:
            st.warning("⚠️ No product associations found.")
            st.info(
                "**Possible reasons:**\n"
                "- Not enough multi-item transactions in your data\n"
                "- Products are rarely purchased together\n"
                "- Need more transaction history\n\n"
                "**Tips:**\n"
                "- Check the diagnostics tab for data quality\n"
                "- Ensure you have at least 100+ orders with 2+ items each\n"
                "- Try importing more historical data"
            )
    
    with tab3:
        st.subheader(t('market_basket_insights'))
        
        basket_insights = analyzer.get_customer_basket_insights()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Avg Items per Basket", f"{basket_insights['avg_items_per_basket']:.2f}")
            st.metric("Avg Basket Value", f"${basket_insights['avg_basket_value']:.2f}")
            st.metric("Max Items in Basket", f"{basket_insights['max_items_in_basket']:.0f}")
        
        with col2:
            st.metric("Single-Item Baskets", f"{basket_insights['pct_single_item_baskets']:.1f}%")
            st.metric("Multi-Item Baskets", f"{basket_insights['pct_multi_item_baskets']:.1f}%")
        
        # Basket size distribution
        basket_sizes = data.groupby('order_id')['item_name'].nunique().value_counts().sort_index()
        fig = px.bar(
            x=basket_sizes.index,
            y=basket_sizes.values,
            title='Basket Size Distribution',
            labels={'x': 'Number of Items', 'y': 'Number of Orders'}
        )
        st.plotly_chart(fig, width='stretch')
    
    with tab4:
        st.subheader(t('product_recommendations'))
        
        st.markdown("""
        Get personalized product recommendations based on purchase patterns. 
        Select a product to see what customers frequently buy with it.
        """)
        
        # Product selection
        products = sorted([str(p) for p in data['item_name'].unique()])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_product = st.selectbox("Select a product", products, key="rec_product")
        with col2:
            n_recs = st.slider("Number of recommendations", 3, 15, 5, key='crosssell_n_recs')
        
        if st.button("Get Recommendations", type="primary"):
            with st.spinner(f"Finding complementary products for '{selected_product}'..."):
                recommendations = analyzer.get_complementary_products(selected_product, n_recs)
            
            if len(recommendations) > 0:
                st.success(f"✓ Found {len(recommendations)} complementary products for '{selected_product}'")
                
                # Visualization
                fig = px.bar(
                    recommendations,
                    x='complementary_product',
                    y='lift',
                    title=f'Complementary Products for {selected_product}',
                    color='lift',
                    color_continuous_scale='Greens',
                    hover_data=['support', 'confidence'],
                    labels={
                        'complementary_product': 'Product',
                        'lift': 'Lift Score',
                        'support': 'Support',
                        'confidence': 'Confidence'
                    }
                )
                fig.update_xaxes(tickangle=-45)
                st.plotly_chart(fig, width='stretch')
                
                # Detailed table
                st.markdown("### Detailed Recommendations")
                recommendations_display = translate_columns(recommendations.copy())
                st.dataframe(format_datetime_columns(recommendations_display), use_container_width=True, hide_index=True)
                
                # Explanations
                st.markdown("---")
                st.markdown("### 💡 How to Use These Recommendations")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("""
                    **For Sales:**
                    - Suggest these products to customers buying '{}'
                    - Create bundle promotions
                    - Train staff on cross-sell opportunities
                    """.format(selected_product))
                
                with col_b:
                    st.markdown("""
                    **For Merchandising:**
                    - Place these products near each other
                    - Feature in joint promotions
                    - Consider volume discounts for combinations
                    """)
                
                # Check if we have frequency data
                if 'times_bought_together' in recommendations.columns:
                    top_rec = recommendations.iloc[0]
                    st.info(
                        f"💎 **Top Recommendation:** '{top_rec['complementary_product']}' "
                        f"was bought together with '{selected_product}' "
                        f"{int(top_rec.get('times_bought_together', 0))} times!"
                    )
            else:
                st.warning(f"⚠️ No strong associations found for '{selected_product}'")
                
                # Show what products this item was purchased with at all
                orders_with_product = data[data['item_name'] == selected_product]['order_id'].unique()
                if len(orders_with_product) > 0:
                    other_items = data[
                        (data['order_id'].isin(orders_with_product)) & 
                        (data['item_name'] != selected_product)
                    ]['item_name'].value_counts().head(10)
                    
                    if len(other_items) > 0:
                        st.info(
                            f"However, '{selected_product}' was purchased in {len(orders_with_product)} orders. "
                            f"Here are the top items bought in those same orders:"
                        )
                        st.dataframe(
                            pd.DataFrame({
                                'Product': other_items.index,
                                'Times': other_items.values
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info(f"'{selected_product}' is always purchased alone.")
                else:
                    st.error(f"Product '{selected_product}' not found in any orders.")


def ai_query_page(data):
    """AI natural language query interface."""
    st.header(f"🤖 {t('ai_query_title')}")
    
    # Initialize query engine
    engine = get_ai_query_engine(data)
    
    # Display OpenAI status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(t('ai_query_description'))
    with col2:
        if engine.openai_enabled:
            st.success(t('gpt_enhanced'))
            st.caption(t('gpt_caption'))
        else:
            st.info(t('pattern_matching'))
            st.caption(t('set_api_key'))
    
    # Show example queries
    with st.expander("📝 Example Questions You Can Ask"):
        examples = create_query_examples()
        col1, col2 = st.columns(2)
        
        mid = len(examples) // 2
        with col1:
            for example in examples[:mid]:
                st.write(f"• {example}")
        with col2:
            for example in examples[mid:]:
                st.write(f"• {example}")
    
    # Query input
    st.subheader(t('ask_your_question'))
    
    # Pre-filled examples
    example_questions = [
        "Custom question...",
        "What is the total revenue?",
        "Show me the top 10 products",
        "Which customers are at risk of churning?",
        "What are the fast moving products?",
        "Show me overdue refills",
        "What is the average order value?",
        "Which products are bought together?",
        "Show me VIP customers",
        "What are the RFM segments?"
    ]
    
    selected_example = st.selectbox(
        "Choose an example or write your own:",
        example_questions,
        key='ai_query_example_selector'
    )
    
    if selected_example == "Custom question...":
        user_query = st.text_input("Your question:", placeholder="e.g., What are the top 5 products by revenue?", key='ai_query_custom')
    else:
        user_query = st.text_input("Your question:", value=selected_example, key='ai_query_selected')
    
    if st.button("🔍 Ask", type="primary"):
        if user_query and user_query != "Custom question...":
            with st.spinner("Analyzing..."):
                result = engine.query(user_query)
                
                if result['success']:
                    # Display answer
                    if result.get('ai_powered'):
                        st.success("✨ GPT-Powered Analysis Complete")
                    else:
                        st.success("✓ Analysis Complete")
                    
                    st.markdown(f"**Answer:**\n\n{result['answer']}")
                    
                    # Show executed code for dynamic queries
                    if result.get('dynamic_query') and result.get('code_executed'):
                        with st.expander("🔍 View Executed Code", expanded=False):
                            st.code(result['code_executed'], language='python')
                            st.caption("This pandas code was dynamically generated by GPT to answer your query")
                    
                    # Show note for dynamic queries
                    if result.get('note'):
                        st.info(f"ℹ️ {result['note']}")
                    
                    # Show GPT-generated insights if available
                    if 'gpt_insights' in result and result['gpt_insights']:
                        st.markdown("---")
                        st.markdown("### 🧠 AI Insights")
                        st.markdown(result['gpt_insights'])
                    
                    # Show data if available
                    if 'data' in result and result['data']:
                        st.subheader(t('detailed_data'))
                        
                        if isinstance(result['data'], list) and len(result['data']) > 0:
                            df_result = pd.DataFrame(result['data'])
                            st.dataframe(format_datetime_columns(df_result), use_container_width=True, hide_index=True)
                            
                            # Download button
                            csv = df_result.to_csv(index=False)
                            st.download_button(
                                "Download Results as CSV",
                                csv,
                                f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                "text/csv"
                            )
                        elif isinstance(result['data'], dict):
                            st.json(result['data'])
                    
                    # Show AI-suggested follow-up questions if available
                    if 'suggestions' in result and result.get('ai_powered'):
                        st.markdown("---")
                        st.markdown("### 💭 Suggested Follow-up Questions")
                        for suggestion in result['suggestions']:
                            st.write(f"• {suggestion}")
                    
                    # Show recommendations
                    if 'recommendations' in result and result['recommendations']:
                        st.markdown("---")
                        st.subheader(f"💡 {t('recommendations')}")
                        for rec in result['recommendations']:
                            st.info(rec)
                    
                    # Visualization
                    if 'viz_type' in result and 'viz_config' in result:
                        if result['viz_type'] == 'bar_chart' and isinstance(result['data'], list):
                            df_viz = pd.DataFrame(result['data'])
                            fig = px.bar(
                                df_viz,
                                x=result['viz_config']['x'],
                                y=result['viz_config']['y'],
                                title=result['viz_config']['title']
                            )
                            st.plotly_chart(fig, width='stretch')
                        elif result['viz_type'] == 'line_chart' and isinstance(result['data'], list):
                            df_viz = pd.DataFrame(result['data'])
                            fig = px.line(
                                df_viz,
                                x=result['viz_config']['x'],
                                y=result['viz_config']['y'],
                                title=result['viz_config']['title'],
                                markers=True
                            )
                            st.plotly_chart(fig, width='stretch')
                else:
                    st.error(result['answer'])
                    
                    if 'suggestions' in result:
                        st.info("**Try these questions:**")
                        for suggestion in result['suggestions']:
                            st.write(f"• {suggestion}")
        else:
            st.warning("Please enter a question")
    
    # GPT Chat Feature (if OpenAI is enabled)
    if engine.openai_enabled:
        st.markdown("---")
        st.subheader(t('ai_chat'))
        st.markdown("Have a conversation with the AI about your sales data")
        
        # Initialize chat history in session state
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Synchronize session state with OpenAI assistant's internal history
        # This ensures consistency if the engine was recreated
        if len(st.session_state.chat_messages) != len(engine.openai_assistant.conversation_history):
            engine.openai_assistant.conversation_history = st.session_state.chat_messages.copy()
        
        # Display chat history
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask follow-up questions or have a conversation..."):
            # Add user message to history
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = engine.openai_assistant.chat(prompt)
                    st.markdown(response)
            
            # Add assistant response to history
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            
            # Sync back to OpenAI assistant
            engine.openai_assistant.conversation_history = st.session_state.chat_messages.copy()
        
        # Clear chat button
        if len(st.session_state.chat_messages) > 0:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_messages = []
                engine.openai_assistant.clear_history()
                st.rerun()


def export_page(data):
    """Export and reporting section."""
    st.header(f"📥 {t('export_title')}")
    
    st.subheader(t('generate_reports'))
    
    report_type = st.selectbox(
        t('select_report_type'),
        [
            t('sales_summary'),
            t('customer_analysis'),
            t('product_performance_report'),
            t('rfm_segmentation_report'),
            t('refill_predictions_report'),
            t('cross_sell_opportunities')
        ],
        key='export_report_type'
    )
    
    if st.button(t('generate_report')):
        with st.spinner(t('generating_report')):
            if report_type == t('sales_summary'):
                analyzer = get_sales_analyzer(data)
                report_df = analyzer.get_daily_trends()
            elif report_type == t('customer_analysis'):
                analyzer = get_customer_analyzer(data)
                report_df = analyzer.get_customer_summary()
            elif report_type == t('product_performance_report'):
                analyzer = get_product_analyzer(data)
                report_df = analyzer.get_product_summary()
            elif report_type == t('rfm_segmentation_report'):
                analyzer = get_rfm_analyzer(data)
                report_df = analyzer.segment_customers()
            elif report_type == t('refill_predictions_report'):
                predictor = get_refill_predictor(data)
                predictor.calculate_purchase_intervals()
                report_df = predictor.get_upcoming_refills(30)
            else:
                analyzer = get_cross_sell_analyzer(data)
                report_df = analyzer.analyze_product_affinity()
            
            # Download button
            csv = report_df.to_csv(index=False)
            st.download_button(
                label=t('download_csv'),
                data=csv,
                file_name=f"{report_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            st.success(t('report_generated'))
            report_df_display = translate_columns(report_df.copy())
            st.dataframe(format_datetime_columns(report_df_display), use_container_width=True, hide_index=True)


def main():
    """Main dashboard application."""
    # Note: Language is already initialized at module level
    
    # Sidebar
    st.sidebar.title(f"💊 {t('dashboard_title')}")
    st.sidebar.markdown("---")
    
    # Language selection (at the top)
    language_option = st.sidebar.selectbox(
        "Language / اللغة",
        ["English", "العربية"],
        index=0 if st.session_state.language == 'en' else 1
    )
    
    # Update language in session state and rerun if changed
    new_lang = 'en' if language_option == "English" else 'ar'
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        t('upload_data'),
        type=['csv', 'xlsx', 'xls'],
        help="Upload your pharmacy sales data file"
    )
    
    # Track uploaded file changes and clear cache when new file is uploaded
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None
    
    current_file_name = uploaded_file.name if uploaded_file is not None else "default"
    
    # Clear all caches when a new file is uploaded
    if st.session_state.uploaded_file_name != current_file_name:
        st.session_state.uploaded_file_name = current_file_name
        # Clear Streamlit's cache
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success(f"🔄 Cache cleared for new data file: {current_file_name}")
    
    # Load data
    if uploaded_file is not None:
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        data, summary = load_and_process_data(file_path)
    else:
        data, summary = load_and_process_data()
    
    if data is None:
        st.error(t('failed_to_load'))
        return
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.subheader(t('navigation'))
    
    # Menu items with emojis
    menu_items = [
        f"📊 {t('sales_analysis')}",
        f"📅 Monthly Analysis",
        f"👥 {t('customer_insights')}",
        f"📦 {t('product_performance')}",
        f"📦 {t('inventory_management')}",
        f"🎯 {t('rfm_segmentation')}",
        f"💊 {t('refill_prediction')}",
        f"🔗 {t('cross_sell_analysis')}",
        f"🤖 {t('ai_query')}",
        f"📥 {t('export_reports')}"
    ]
    
    page = st.sidebar.radio(t('go_to'), menu_items)
    
    # Data info
    st.sidebar.markdown("---")
    st.sidebar.subheader(t('data_info'))
    if summary:
        st.sidebar.info(f"""
            **{t('records')}:** {summary.get('total_records', 0):,}  
            **{t('date_range')}:** {summary['date_range'][0].date()} {t('to')} {summary['date_range'][1].date()}  
            **{t('customers')}:** {summary.get('unique_customers', 0):,}  
            **{t('products')}:** {summary.get('unique_products', 0):,}  
            **{t('orders')}:** {summary.get('unique_orders', 0):,}
        """)
    
    # Main content - map menu items to page functions
    # Extract the key part without emoji for mapping
    page_functions = [
        sales_analysis_page,
        monthly_analysis_page,
        customer_analysis_page,
        product_analysis_page,
        inventory_management_page,
        rfm_analysis_page,
        refill_prediction_page,
        cross_sell_page,
        ai_query_page,
        export_page
    ]
    
    # Find which page was selected
    selected_index = menu_items.index(page)
    page_functions[selected_index](data)
    
    # Footer with special font
    st.markdown("---")
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
    .footer-text {
        color: #d63384;
        text-align: center;
        padding: 20px 0;
        font-family: 'Dancing Script', cursive;
        font-size: 24px;
        font-weight: 700;
    }
    
    .footer-text .heart {
        color: #ff1493;
        animation: heartbeat 1.5s ease-in-out infinite;
        display: inline-block;
        margin: 0 5px;
    }
    
    @keyframes heartbeat {
        0% { transform: scale(1); }
        10% { transform: scale(1.1); }
        20% { transform: scale(1); }
        30% { transform: scale(1.1); }
        40% { transform: scale(1); }
        100% { transform: scale(1); }
    }
    </style>
    <div class="footer-text">
        Made with <span class="heart">♥</span> for Dr. Yara
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

