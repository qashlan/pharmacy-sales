"""RFM (Recency, Frequency, Monetary) customer segmentation module."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import config


class RFMAnalyzer:
    """Performs RFM analysis and customer segmentation."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize RFM analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        self.current_date = data['date'].max()
        self.rfm_data = None
        self.phone_mapping = None
        
    def calculate_rfm(self) -> pd.DataFrame:
        """
        Calculate RFM metrics for each customer with refund handling.
        
        Returns:
            DataFrame with Recency, Frequency, and Monetary values
        """
        # Use only sales data for frequency calculation (exclude refunds)
        sales_data = self.data[~self.data['is_refund']]
        
        # Calculate Recency and Frequency from sales
        rfm = sales_data.groupby('customer_name').agg({
            'date': lambda x: (self.current_date - x.max()).days,  # Recency
            'order_id': 'nunique'  # Frequency (only sales orders)
        }).reset_index()
        
        rfm.columns = ['customer_name', 'recency', 'frequency']
        
        # Calculate Monetary value separately to handle refunds
        # Monetary = Total Sales - Total Refunds (net spending)
        customer_sales = sales_data.groupby('customer_name')['total'].sum().reset_index()
        customer_sales.columns = ['customer_name', 'gross_spending']
        
        refunds_data = self.data[self.data['is_refund']]
        customer_refunds = refunds_data.groupby('customer_name')['total'].sum().reset_index()
        customer_refunds.columns = ['customer_name', 'refund_amount']
        customer_refunds['refund_amount'] = abs(customer_refunds['refund_amount'])
        
        # Merge monetary data
        rfm = rfm.merge(customer_sales, on='customer_name', how='left')
        rfm = rfm.merge(customer_refunds, on='customer_name', how='left')
        rfm['refund_amount'] = rfm['refund_amount'].fillna(0)
        
        # Calculate net monetary value
        rfm['monetary'] = rfm['gross_spending'] - rfm['refund_amount']
        
        # Calculate RFM scores (1-5, where 5 is best)
        # Use try-except to handle cases with duplicate values
        try:
            rfm['r_score'] = pd.qcut(rfm['recency'], q=config.RFM_BINS, labels=[5, 4, 3, 2, 1], duplicates='drop')
        except ValueError:
            # Fall back to percentile-based scoring if qcut fails
            rfm['r_score'] = pd.cut(rfm['recency'], 
                                    bins=config.RFM_BINS, 
                                    labels=[5, 4, 3, 2, 1], 
                                    duplicates='drop',
                                    include_lowest=True)
        
        try:
            rfm['f_score'] = pd.qcut(rfm['frequency'], q=config.RFM_BINS, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError:
            rfm['f_score'] = pd.cut(rfm['frequency'], 
                                    bins=config.RFM_BINS, 
                                    labels=[1, 2, 3, 4, 5], 
                                    duplicates='drop',
                                    include_lowest=True)
        
        try:
            rfm['m_score'] = pd.qcut(rfm['monetary'], q=config.RFM_BINS, labels=[1, 2, 3, 4, 5], duplicates='drop')
        except ValueError:
            rfm['m_score'] = pd.cut(rfm['monetary'], 
                                    bins=config.RFM_BINS, 
                                    labels=[1, 2, 3, 4, 5], 
                                    duplicates='drop',
                                    include_lowest=True)
        
        # Convert to integer (handle NaN from dropped duplicates)
        rfm['r_score'] = rfm['r_score'].fillna(3).astype(int)  # Default to middle score
        rfm['f_score'] = rfm['f_score'].fillna(3).astype(int)
        rfm['m_score'] = rfm['m_score'].fillna(3).astype(int)
        
        # Calculate combined RFM score
        rfm['rfm_score'] = (
            rfm['r_score'] * config.RECENCY_WEIGHT +
            rfm['f_score'] * config.FREQUENCY_WEIGHT +
            rfm['m_score'] * config.MONETARY_WEIGHT
        )
        
        # Create RFM segment string
        rfm['rfm_segment'] = (
            rfm['r_score'].astype(str) +
            rfm['f_score'].astype(str) +
            rfm['m_score'].astype(str)
        )
        
        self.rfm_data = rfm
        return rfm
    
    def segment_customers(self) -> pd.DataFrame:
        """
        Segment customers into meaningful groups based on purchase behavior.
        
        Simple, business-friendly segmentation:
        - New Customers: Only 1 purchase, recent
        - Potential Customers: 2-5 purchases
        - Champions: 6+ purchases, recent activity
        - Loyal Customers: 6+ purchases, moderate recency
        - At Risk: 6+ purchases, but inactive (30-90 days)
        - Lost Customers: Inactive for 90+ days
        - Churned: Previously good customers, now inactive
        """
        if self.rfm_data is None:
            self.calculate_rfm()
        
        rfm = self.rfm_data.copy()
        
        def assign_segment(row):
            frequency = row['frequency']
            recency = row['recency']
            monetary = row['monetary']
            
            # New Customers: Only purchased once
            if frequency == 1:
                if recency <= 30:
                    return 'New Customers'
                elif recency <= 90:
                    return 'New (At Risk)'
                else:
                    return 'Lost (New)'
            
            # Potential Customers: 2-5 purchases
            elif 2 <= frequency <= 5:
                if recency <= 30:
                    return 'Potential Customers'
                elif recency <= 90:
                    return 'Potential (Need Attention)'
                else:
                    return 'Churned (Potential)'
            
            # High frequency customers (6+ purchases)
            else:  # frequency >= 6
                if recency <= 30:
                    return 'Champions'
                elif recency <= 60:
                    return 'Loyal Customers'
                elif recency <= 90:
                    return 'At Risk'
                else:
                    return 'Lost Customers'
        
        rfm['segment'] = rfm.apply(assign_segment, axis=1)
        
        self.rfm_data = rfm
        return rfm
    
    def get_segment_summary(self) -> pd.DataFrame:
        """Get summary statistics for each customer segment."""
        if self.rfm_data is None or 'segment' not in self.rfm_data.columns:
            self.segment_customers()
        
        segment_summary = self.rfm_data.groupby('segment').agg({
            'customer_name': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean',
            'rfm_score': 'mean'
        }).reset_index()
        
        segment_summary.columns = [
            'segment', 'customer_count', 'avg_recency', 'avg_frequency',
            'avg_monetary', 'avg_rfm_score'
        ]
        
        # Calculate percentage of total customers
        total_customers = segment_summary['customer_count'].sum()
        segment_summary['customer_pct'] = (
            segment_summary['customer_count'] / total_customers * 100
        ).round(2)
        
        # Calculate revenue contribution
        segment_revenue = self.rfm_data.groupby('segment')['monetary'].sum().reset_index()
        segment_revenue.columns = ['segment', 'total_revenue']
        segment_summary = segment_summary.merge(segment_revenue, on='segment')
        
        total_revenue = segment_summary['total_revenue'].sum()
        segment_summary['revenue_pct'] = (
            segment_summary['total_revenue'] / total_revenue * 100
        ).round(2)
        
        # Sort by revenue contribution
        segment_summary = segment_summary.sort_values('total_revenue', ascending=False)
        
        return segment_summary
    
    def get_customers_by_segment(self, segment: str) -> pd.DataFrame:
        """Get list of customers in a specific segment."""
        if self.rfm_data is None or 'segment' not in self.rfm_data.columns:
            self.segment_customers()
        
        customers = self.rfm_data[self.rfm_data['segment'] == segment].copy()
        customers = customers.sort_values('monetary', ascending=False)
        
        return customers[
            ['customer_name', 'recency', 'frequency', 'monetary', 
             'r_score', 'f_score', 'm_score', 'rfm_score']
        ]
    
    def get_vip_customers(self, n: int = 20) -> pd.DataFrame:
        """Identify VIP customers (Champions and Cannot Lose Them)."""
        if self.rfm_data is None or 'segment' not in self.rfm_data.columns:
            self.segment_customers()
        
        vip_segments = ['Champions', 'Cannot Lose Them', 'Loyal Customers']
        vip = self.rfm_data[self.rfm_data['segment'].isin(vip_segments)].copy()
        vip = vip.sort_values('monetary', ascending=False).head(n)
        
        return vip[
            ['customer_name', 'segment', 'recency', 'frequency', 'monetary', 'rfm_score']
        ]
    
    def get_at_risk_customers(self) -> pd.DataFrame:
        """Identify at-risk customers who need immediate attention."""
        if self.rfm_data is None or 'segment' not in self.rfm_data.columns:
            self.segment_customers()
        
        at_risk_segments = ['At Risk', 'Cannot Lose Them', 'About to Sleep']
        at_risk = self.rfm_data[self.rfm_data['segment'].isin(at_risk_segments)].copy()
        at_risk = at_risk.sort_values('monetary', ascending=False)
        
        return at_risk[
            ['customer_name', 'segment', 'recency', 'frequency', 'monetary', 'rfm_score']
        ]
    
    def cluster_customers_kmeans(self, n_clusters: int = 4) -> pd.DataFrame:
        """
        Perform K-means clustering on RFM data.
        
        Args:
            n_clusters: Number of clusters to create
        """
        if self.rfm_data is None:
            self.calculate_rfm()
        
        # Prepare features for clustering
        features = self.rfm_data[['recency', 'frequency', 'monetary']].values
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.rfm_data['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Calculate cluster centers in original scale
        cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        cluster_info = []
        for i in range(n_clusters):
            cluster_data = self.rfm_data[self.rfm_data['cluster'] == i]
            cluster_info.append({
                'cluster': i,
                'size': len(cluster_data),
                'avg_recency': cluster_centers[i][0],
                'avg_frequency': cluster_centers[i][1],
                'avg_monetary': cluster_centers[i][2],
                'total_revenue': cluster_data['monetary'].sum()
            })
        
        cluster_summary = pd.DataFrame(cluster_info)
        
        return self.rfm_data, cluster_summary
    
    def get_transition_matrix(self, previous_rfm: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate customer segment transition matrix.
        
        Args:
            previous_rfm: RFM data from previous period with segments
        """
        if self.rfm_data is None or 'segment' not in self.rfm_data.columns:
            self.segment_customers()
        
        # Merge current and previous segments
        transition = previous_rfm[['customer_name', 'segment']].merge(
            self.rfm_data[['customer_name', 'segment']],
            on='customer_name',
            suffixes=('_previous', '_current')
        )
        
        # Create transition matrix
        transition_matrix = pd.crosstab(
            transition['segment_previous'],
            transition['segment_current'],
            normalize='index'
        ) * 100
        
        return transition_matrix.round(2)
    
    def recommend_actions(self, segment: str) -> Dict:
        """
        Recommend marketing actions for each customer segment.
        
        Args:
            segment: Customer segment name
        """
        recommendations = {
            'New Customers': {
                'priority': 'Medium',
                'actions': [
                    'Welcome email with discount for 2nd purchase',
                    'Introduce them to product categories',
                    'Ask for feedback on first experience',
                    'Offer personalized product recommendations'
                ],
                'goal': 'Convert to repeat customers'
            },
            'New (At Risk)': {
                'priority': 'Medium-High',
                'actions': [
                    'Send reminder about their first purchase',
                    'Offer special discount to encourage 2nd purchase',
                    'Highlight products they might need',
                    'Ask if they need any assistance'
                ],
                'goal': 'Re-engage before they become lost'
            },
            'Lost (New)': {
                'priority': 'Low',
                'actions': [
                    'One-time win-back offer',
                    'Survey to understand why they didn\'t return',
                    'Learn and improve from feedback'
                ],
                'goal': 'Understand barriers and improve'
            },
            'Potential Customers': {
                'priority': 'High',
                'actions': [
                    'Nurture with personalized offers',
                    'Recommend complementary products',
                    'Offer loyalty incentives',
                    'Provide excellent customer service',
                    'Encourage more frequent purchases'
                ],
                'goal': 'Grow into Champions'
            },
            'Potential (Need Attention)': {
                'priority': 'High',
                'actions': [
                    'Re-engagement campaign with special offers',
                    'Remind them of products they liked',
                    'Ask for feedback',
                    'Time-sensitive promotions'
                ],
                'goal': 'Prevent from churning'
            },
            'Churned (Potential)': {
                'priority': 'Medium',
                'actions': [
                    'Win-back campaign with significant incentives',
                    'Survey to understand why they left',
                    'Show what\'s new since they left',
                    'Personalized outreach'
                ],
                'goal': 'Reactivate and rebuild relationship'
            },
            'Champions': {
                'priority': 'Very High',
                'actions': [
                    'VIP treatment and exclusive benefits',
                    'Request reviews and referrals',
                    'Early access to new products',
                    'Personalized thank you messages',
                    'Special rewards and recognition'
                ],
                'goal': 'Maintain loyalty and advocacy'
            },
            'Loyal Customers': {
                'priority': 'High',
                'actions': [
                    'Regular engagement and appreciation',
                    'Loyalty rewards program',
                    'Cross-sell and upsell opportunities',
                    'Ask for product feedback',
                    'Keep them engaged'
                ],
                'goal': 'Maintain engagement and prevent decline'
            },
            'At Risk': {
                'priority': 'Urgent',
                'actions': [
                    'IMMEDIATE personalized outreach',
                    'Generous win-back offers',
                    'Call or personal message from staff',
                    'Understand if there are any issues',
                    'Show them they are valued'
                ],
                'goal': 'Prevent loss of valuable customers'
            },
            'Lost Customers': {
                'priority': 'Medium',
                'actions': [
                    'Major win-back campaign',
                    'Survey to understand reasons',
                    'Significant incentive to return',
                    'Show improvements made',
                    'Limited-time offer'
                ],
                'goal': 'Reactivate if cost-effective'
            }
        }
        
        return recommendations.get(segment, {
            'priority': 'Medium',
            'actions': ['Analyze customer behavior', 'Provide personalized service'],
            'goal': 'Understand and serve customer needs'
        })
    
    def calculate_rfm_by_category(self) -> pd.DataFrame:
        """
        Calculate RFM metrics for each customer within each category.
        
        This shows customer behavior specific to each product category,
        revealing which customers are Champions/Loyal/At Risk in different categories.
        
        Returns:
            DataFrame with columns:
            - customer_name
            - category
            - recency (days since last purchase in this category)
            - frequency (number of purchases in this category)
            - monetary (total spent in this category)
            - segment (RFM segment for this category)
        """
        # Use only sales data (exclude refunds)
        sales_data = self.data[~self.data['is_refund']].copy()
        
        # Calculate RFM for each customer-category combination
        rfm_by_category = sales_data.groupby(['customer_name', 'category']).agg({
            'date': lambda x: (self.current_date - x.max()).days,  # Recency
            'order_id': 'nunique',  # Frequency
            'total': 'sum'  # Monetary
        }).reset_index()
        
        rfm_by_category.columns = ['customer_name', 'category', 'recency', 'frequency', 'monetary']
        
        # Assign segments based on category-specific behavior
        def assign_category_segment(row):
            frequency = row['frequency']
            recency = row['recency']
            monetary = row['monetary']
            
            # Simplified segmentation for category-specific behavior
            if frequency == 1:
                if recency <= 30:
                    return '🆕 New Customers'
                elif recency <= 90:
                    return '⚠️ New (At Risk)'
                else:
                    return '😢 Lost (New)'
            elif 2 <= frequency <= 5:
                if recency <= 30:
                    return '🌱 Potential Customers'
                elif recency <= 90:
                    return '👀 Potential (Need Attention)'
                else:
                    return '💔 Churned (Potential)'
            else:  # frequency >= 6
                if recency <= 30:
                    return '🏆 Champions'
                elif recency <= 60:
                    return '💎 Loyal Customers'
                elif recency <= 90:
                    return '⚠️ At Risk'
                else:
                    return '😞 Lost Customers'
        
        rfm_by_category['segment'] = rfm_by_category.apply(assign_category_segment, axis=1)
        
        # Sort by category and monetary value
        rfm_by_category = rfm_by_category.sort_values(['category', 'monetary'], ascending=[True, False])
        
        return rfm_by_category
    
    def get_category_segment_summary(self) -> pd.DataFrame:
        """
        Get summary of customer segments by category.
        
        Returns:
            DataFrame showing how many customers are in each segment for each category
        """
        rfm_by_category = self.calculate_rfm_by_category()
        
        # Count customers by category and segment
        summary = rfm_by_category.groupby(['category', 'segment']).agg({
            'customer_name': 'count',
            'monetary': 'sum',
            'recency': 'mean',
            'frequency': 'mean'
        }).reset_index()
        
        summary.columns = ['category', 'segment', 'customer_count', 'total_revenue', 
                          'avg_recency', 'avg_frequency']
        
        # Calculate percentages within each category
        category_totals = summary.groupby('category')['customer_count'].sum().reset_index()
        category_totals.columns = ['category', 'category_total']
        
        summary = summary.merge(category_totals, on='category')
        summary['pct_of_category'] = (summary['customer_count'] / summary['category_total'] * 100).round(2)
        
        # Sort by category and revenue
        summary = summary.sort_values(['category', 'total_revenue'], ascending=[True, False])
        
        return summary
    
    def get_customers_by_category_segment(self, category: str, segment: str = None) -> pd.DataFrame:
        """
        Get customers in a specific category, optionally filtered by segment.
        
        Args:
            category: Product category to filter by
            segment: Optional RFM segment to filter by (e.g., 'Champions', 'At Risk')
        
        Returns:
            DataFrame with customer details for the specified category/segment
        """
        rfm_by_category = self.calculate_rfm_by_category()
        
        # Filter by category
        result = rfm_by_category[rfm_by_category['category'] == category].copy()
        
        # Filter by segment if specified
        if segment:
            # Remove emoji from segment for matching
            segment_clean = segment.split(' ', 1)[-1] if ' ' in segment else segment
            result = result[result['segment'].str.contains(segment_clean, case=False, na=False)]
        
        # Sort by monetary value
        result = result.sort_values('monetary', ascending=False)
        
        return result[['customer_name', 'segment', 'recency', 'frequency', 'monetary']]
    
    def get_top_customers_per_category(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N customers for each category by monetary value.
        
        Args:
            n: Number of top customers to return per category
        
        Returns:
            DataFrame with top customers for each category
        """
        rfm_by_category = self.calculate_rfm_by_category()
        
        # Get top N customers per category
        top_customers = (rfm_by_category
                        .groupby('category')
                        .apply(lambda x: x.nlargest(n, 'monetary'))
                        .reset_index(drop=True))
        
        return top_customers[['category', 'customer_name', 'segment', 'recency', 
                             'frequency', 'monetary']]
    
    def load_phone_mapping(self, phone_df: pd.DataFrame) -> bool:
        """
        Load phone number mapping from DataFrame.
        
        Args:
            phone_df: DataFrame with columns 'اسم العميل' (customer name) and 'التليفونات' (phone)
                     or 'customer_name' and 'phone'
        
        Returns:
            Boolean indicating success
        """
        try:
            # Check for Arabic column names first, then English
            if 'اسم العميل' in phone_df.columns and 'التليفونات' in phone_df.columns:
                phone_df = phone_df.rename(columns={
                    'اسم العميل': 'customer_name',
                    'التليفونات': 'phone'
                })
            elif 'customer_name' not in phone_df.columns or 'phone' not in phone_df.columns:
                # Try to find similar column names
                customer_cols = [col for col in phone_df.columns if 'customer' in col.lower() or 'عميل' in col]
                phone_cols = [col for col in phone_df.columns if 'phone' in col.lower() or 'تليفون' in col or 'هاتف' in col]
                
                if customer_cols and phone_cols:
                    phone_df = phone_df.rename(columns={
                        customer_cols[0]: 'customer_name',
                        phone_cols[0]: 'phone'
                    })
                else:
                    return False
            
            # Keep only customer_name and phone columns
            self.phone_mapping = phone_df[['customer_name', 'phone']].copy()
            
            # Clean customer names (strip whitespace)
            self.phone_mapping['customer_name'] = self.phone_mapping['customer_name'].astype(str).str.strip()
            
            # Remove duplicates, keep first occurrence
            self.phone_mapping = self.phone_mapping.drop_duplicates(subset='customer_name', keep='first')
            
            return True
        except Exception as e:
            print(f"Error loading phone mapping: {str(e)}")
            return False
    
    def merge_phone_numbers(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge phone numbers into RFM DataFrame.
        
        Args:
            rfm_df: RFM DataFrame with customer_name column
        
        Returns:
            RFM DataFrame with phone column added
        """
        # Create a copy to avoid modifying the original
        result = rfm_df.copy()
        
        if self.phone_mapping is None or len(self.phone_mapping) == 0:
            # No phone mapping available, add empty phone column
            result['phone'] = ''
            return result
        
        # Merge phone numbers
        result = result.merge(
            self.phone_mapping,
            on='customer_name',
            how='left'
        )
        
        # Ensure phone column exists and fill missing values
        if 'phone' in result.columns:
            result['phone'] = result['phone'].fillna('')
        else:
            result['phone'] = ''
        
        return result

