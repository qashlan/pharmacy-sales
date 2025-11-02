"""Cross-sell pattern analysis using market basket analysis."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set, Optional
from itertools import combinations
from collections import defaultdict
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import config
import warnings
warnings.filterwarnings('ignore')


class CrossSellAnalyzer:
    """Analyzes product associations and cross-sell opportunities."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize cross-sell analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        self.basket_data: Optional[pd.DataFrame] = None
        self.association_rules_df: Optional[pd.DataFrame] = None
        self._frequent_itemsets_cache: Optional[pd.DataFrame] = None
        self.analysis_metadata = {
            'total_orders': 0,
            'multi_item_orders': 0,
            'unique_products': 0,
            'support_used': None,
            'rules_found': 0
        }
        
    def create_basket_matrix(self) -> pd.DataFrame:
        """
        Create a transaction-product matrix for market basket analysis.
        
        Returns:
            Binary matrix where rows are orders and columns are products
        """
        # Create basket: each order_id with list of products
        # Convert all item names to strings to handle mixed types
        baskets = self.data.groupby('order_id')['item_name'].apply(
            lambda x: [str(item) for item in x]
        ).reset_index()
        
        # Use TransactionEncoder to create binary matrix
        te = TransactionEncoder()
        te_array = te.fit(baskets['item_name']).transform(baskets['item_name'])
        basket_df = pd.DataFrame(te_array, columns=te.columns_)
        
        self.basket_data = basket_df
        return basket_df
    
    def find_frequent_itemsets(self, min_support: float = None, auto_adjust: bool = True) -> pd.DataFrame:
        """
        Find frequent itemsets using Apriori algorithm with dynamic support adjustment. (CACHED)
        
        Args:
            min_support: Minimum support threshold (default from config)
            auto_adjust: Automatically reduce support if no itemsets found
        """
        # Return cached result if available
        if self._frequent_itemsets_cache is not None:
            return self._frequent_itemsets_cache
        
        if self.basket_data is None:
            self.create_basket_matrix()
        
        if min_support is None:
            min_support = config.MIN_SUPPORT
        
        # Calculate statistics
        total_orders = len(self.basket_data)
        self.analysis_metadata['total_orders'] = total_orders
        self.analysis_metadata['unique_products'] = self.basket_data.shape[1]
        
        # Try to find frequent itemsets with decreasing support thresholds
        support_thresholds = [min_support]
        
        if auto_adjust:
            # Generate adaptive thresholds based on data size
            if total_orders < 100:
                support_thresholds = [0.05, 0.02, 0.01, 0.005]
            elif total_orders < 500:
                support_thresholds = [0.02, 0.01, 0.005, 0.002]
            elif total_orders < 1000:
                support_thresholds = [min_support, min_support/2, min_support/5, 0.001]
            else:
                support_thresholds = [min_support, min_support/2, min_support/5, min_support/10]
        
        frequent_itemsets = pd.DataFrame()
        support_used = min_support
        
        for threshold in support_thresholds:
            try:
                frequent_itemsets = apriori(
                    self.basket_data,
                    min_support=threshold,
                    use_colnames=True,
                    low_memory=True
                )
                
                if len(frequent_itemsets) > 0:
                    support_used = threshold
                    self.analysis_metadata['support_used'] = support_used
                    print(f"✓ Found {len(frequent_itemsets)} frequent itemsets with support={threshold:.4f}")
                    break
                else:
                    print(f"✗ No itemsets found with support={threshold:.4f}, trying lower threshold...")
            except Exception as e:
                print(f"Error with support={threshold}: {str(e)}")
                continue
        
        if len(frequent_itemsets) == 0:
            print("⚠ No frequent itemsets found even with lowest threshold. Using alternative analysis...")
            return pd.DataFrame()
        
        # Sort by support
        frequent_itemsets = frequent_itemsets.sort_values('support', ascending=False)
        
        # Add itemset size
        frequent_itemsets['itemset_size'] = frequent_itemsets['itemsets'].apply(len)
        
        # Add count for better understanding
        frequent_itemsets['count'] = (frequent_itemsets['support'] * total_orders).astype(int)
        
        # Cache the result
        self._frequent_itemsets_cache = frequent_itemsets
        
        return frequent_itemsets
    
    def generate_association_rules(
        self,
        min_support: float = None,
        min_confidence: float = None,
        min_lift: float = None,
        auto_adjust: bool = True
    ) -> pd.DataFrame:
        """
        Generate association rules for product recommendations with adaptive thresholds.
        
        Args:
            min_support: Minimum support threshold
            min_confidence: Minimum confidence threshold
            min_lift: Minimum lift threshold
            auto_adjust: Automatically adjust thresholds if no rules found
        """
        if min_support is None:
            min_support = config.MIN_SUPPORT
        if min_confidence is None:
            min_confidence = config.MIN_CONFIDENCE
        if min_lift is None:
            min_lift = config.MIN_LIFT
        
        # Get frequent itemsets with auto-adjustment
        frequent_itemsets = self.find_frequent_itemsets(min_support, auto_adjust=auto_adjust)
        
        if len(frequent_itemsets) == 0:
            print("⚠ No frequent itemsets found. Cannot generate association rules.")
            self.association_rules_df = pd.DataFrame()
            self.analysis_metadata['rules_found'] = 0
            return pd.DataFrame()
        
        # Filter to only itemsets with 2+ items (needed for rules)
        frequent_itemsets_filtered = frequent_itemsets[frequent_itemsets['itemset_size'] >= 2]
        
        if len(frequent_itemsets_filtered) == 0:
            print("⚠ No multi-item frequent itemsets found. Cannot generate association rules.")
            self.association_rules_df = pd.DataFrame()
            self.analysis_metadata['rules_found'] = 0
            return pd.DataFrame()
        
        # Try different confidence thresholds
        confidence_thresholds = [min_confidence]
        if auto_adjust:
            confidence_thresholds = [min_confidence, min_confidence/2, 0.1, 0.05]
        
        rules = pd.DataFrame()
        for conf_threshold in confidence_thresholds:
            try:
                rules = association_rules(
                    frequent_itemsets,
                    metric="confidence",
                    min_threshold=conf_threshold
                )
                
                if len(rules) > 0:
                    print(f"✓ Generated {len(rules)} association rules with confidence={conf_threshold:.2f}")
                    break
                else:
                    print(f"✗ No rules with confidence={conf_threshold:.2f}, trying lower...")
            except Exception as e:
                print(f"Error generating rules with confidence={conf_threshold}: {str(e)}")
                continue
        
        if len(rules) == 0:
            print("⚠ No association rules found even with lowest threshold.")
            self.association_rules_df = pd.DataFrame()
            self.analysis_metadata['rules_found'] = 0
            return pd.DataFrame()
        
        # Filter by lift (be more lenient if auto_adjust is on)
        lift_threshold = min_lift if not auto_adjust else max(min_lift/2, 0.8)
        rules = rules[rules['lift'] >= lift_threshold]
        
        if len(rules) == 0:
            print(f"⚠ No rules with lift >= {lift_threshold:.2f}")
            self.association_rules_df = pd.DataFrame()
            self.analysis_metadata['rules_found'] = 0
            return pd.DataFrame()
        
        # Convert frozensets to lists for readability
        rules['antecedents_list'] = rules['antecedents'].apply(lambda x: list(x))
        rules['consequents_list'] = rules['consequents'].apply(lambda x: list(x))
        
        # Add rule strength score
        rules['rule_strength'] = rules['confidence'] * rules['lift']
        
        # Sort by rule strength (combination of confidence and lift)
        rules = rules.sort_values('rule_strength', ascending=False)
        
        self.association_rules_df = rules
        self.analysis_metadata['rules_found'] = len(rules)
        
        print(f"✓ Successfully generated {len(rules)} high-quality association rules")
        return rules
    
    def get_product_recommendations(
        self,
        product_name: str,
        n: int = 5
    ) -> pd.DataFrame:
        """
        Get top product recommendations for a given product.
        
        Args:
            product_name: Product to get recommendations for
            n: Number of recommendations
        """
        if self.association_rules_df is None:
            self.generate_association_rules()
        
        if self.association_rules_df is None or len(self.association_rules_df) == 0:
            return pd.DataFrame()
        
        # Find rules where the product is in antecedents
        recommendations = self.association_rules_df[
            self.association_rules_df['antecedents_list'].apply(
                lambda x: product_name in x
            )
        ].copy()
        
        if len(recommendations) == 0:
            return pd.DataFrame()
        
        # Select top recommendations
        recommendations = recommendations.head(n)
        
        return recommendations[
            ['antecedents_list', 'consequents_list', 'support', 
             'confidence', 'lift', 'leverage']
        ]
    
    def get_bundle_suggestions(
        self,
        min_items: int = 2,
        max_items: int = 4,
        n: int = 10,
        auto_adjust: bool = True
    ) -> pd.DataFrame:
        """
        Suggest product bundles based on frequent itemsets with enhanced analytics.
        
        Args:
            min_items: Minimum items in bundle
            max_items: Maximum items in bundle
            n: Number of bundles to return
            auto_adjust: Use adaptive thresholds
        """
        frequent_itemsets = self.find_frequent_itemsets(auto_adjust=auto_adjust)
        
        if len(frequent_itemsets) == 0:
            print("⚠ No frequent itemsets found. Trying alternative bundle detection...")
            return self._get_bundles_by_cooccurrence(min_items, max_items, n)
        
        # Filter by itemset size
        bundles = frequent_itemsets[
            (frequent_itemsets['itemset_size'] >= min_items) &
            (frequent_itemsets['itemset_size'] <= max_items)
        ].copy()
        
        if len(bundles) == 0:
            print(f"⚠ No bundles with {min_items}-{max_items} items. Trying alternative method...")
            return self._get_bundles_by_cooccurrence(min_items, max_items, n)
        
        # Convert itemsets to lists
        bundles['bundle_items'] = bundles['itemsets'].apply(lambda x: list(x))
        
        # Calculate bundle metrics
        bundle_values = []
        bundle_frequencies = []
        avg_basket_values = []
        
        for _, row in bundles.iterrows():
            items = row['bundle_items']
            
            # Find orders with all items in bundle
            orders_with_bundle = set(self.data[self.data['item_name'] == items[0]]['order_id'])
            for item in items[1:]:
                orders_with_bundle &= set(self.data[self.data['item_name'] == item]['order_id'])
            
            bundle_frequency = len(orders_with_bundle)
            bundle_frequencies.append(bundle_frequency)
            
            # Get revenue from these complete bundle orders
            if bundle_frequency > 0:
                bundle_revenue = self.data[
                    self.data['order_id'].isin(orders_with_bundle)
                ].groupby('order_id')['total'].sum().sum()
                avg_basket_value = bundle_revenue / bundle_frequency
            else:
                bundle_revenue = 0
                avg_basket_value = 0
            
            bundle_values.append(bundle_revenue)
            avg_basket_values.append(avg_basket_value)
        
        bundles['bundle_frequency'] = bundle_frequencies
        bundles['bundle_revenue'] = bundle_values
        bundles['avg_basket_value'] = avg_basket_values
        
        # Calculate comprehensive score
        bundles['score'] = (
            bundles['support'] * 100 +  # Frequency weight
            np.log1p(bundles['bundle_revenue']) * 10 +  # Revenue weight
            bundles['itemset_size'] * 5  # Size bonus
        )
        
        bundles = bundles.sort_values('score', ascending=False).head(n)
        
        return bundles[
            ['bundle_items', 'itemset_size', 'support', 'bundle_frequency', 
             'bundle_revenue', 'avg_basket_value', 'score']
        ]
    
    def _get_bundles_by_cooccurrence(self, min_items: int = 2, max_items: int = 4, n: int = 10) -> pd.DataFrame:
        """
        Alternative bundle detection using simple co-occurrence analysis.
        """
        # Find multi-item orders
        order_items = self.data.groupby('order_id')['item_name'].apply(list).reset_index()
        order_items = order_items[order_items['item_name'].apply(len) >= min_items]
        
        if len(order_items) == 0:
            print("⚠ No multi-item orders found for bundle analysis.")
            return pd.DataFrame()
        
        # Count item combinations
        bundle_counts = defaultdict(int)
        bundle_revenue = defaultdict(float)
        
        for _, row in order_items.iterrows():
            items = list(set(row['item_name']))  # Unique items
            order_id = row['order_id']
            order_total = self.data[self.data['order_id'] == order_id]['total'].sum()
            
            # Generate combinations
            for size in range(min_items, min(max_items + 1, len(items) + 1)):
                for combo in combinations(sorted(items), size):
                    bundle_counts[combo] += 1
                    bundle_revenue[combo] += order_total
        
        # Convert to DataFrame
        if len(bundle_counts) == 0:
            return pd.DataFrame()
        
        bundles_list = []
        total_orders = self.data['order_id'].nunique()
        
        for bundle, count in bundle_counts.items():
            bundles_list.append({
                'bundle_items': list(bundle),
                'itemset_size': len(bundle),
                'bundle_frequency': count,
                'support': count / total_orders,
                'bundle_revenue': bundle_revenue[bundle],
                'avg_basket_value': bundle_revenue[bundle] / count if count > 0 else 0,
                'score': count * np.log1p(bundle_revenue[bundle])
            })
        
        bundles_df = pd.DataFrame(bundles_list)
        bundles_df = bundles_df.sort_values('score', ascending=False).head(n)
        
        print(f"✓ Found {len(bundles_df)} bundles using co-occurrence analysis")
        return bundles_df
    
    def analyze_product_affinity(self) -> pd.DataFrame:
        """
        Calculate product affinity scores for all product pairs.
        
        Affinity = How often products are bought together relative to their individual frequencies
        """
        if self.association_rules_df is None:
            self.generate_association_rules()
        
        if self.association_rules_df is None or len(self.association_rules_df) == 0:
            # Fallback: calculate co-occurrence manually
            return self._calculate_cooccurrence()
        
        # Extract product pairs and their metrics
        affinity_data = []
        
        for _, rule in self.association_rules_df.iterrows():
            antecedents = list(rule['antecedents'])
            consequents = list(rule['consequents'])
            
            # For simple pairs only
            if len(antecedents) == 1 and len(consequents) == 1:
                affinity_data.append({
                    'product_a': antecedents[0],
                    'product_b': consequents[0],
                    'support': rule['support'],
                    'confidence': rule['confidence'],
                    'lift': rule['lift'],
                    'leverage': rule['leverage'],
                    'conviction': rule['conviction'] if 'conviction' in rule else 0
                })
        
        if len(affinity_data) == 0:
            return pd.DataFrame()
        
        affinity_df = pd.DataFrame(affinity_data)
        affinity_df = affinity_df.sort_values('lift', ascending=False)
        
        return affinity_df
    
    def _calculate_cooccurrence(self) -> pd.DataFrame:
        """Calculate co-occurrence matrix manually."""
        # Get all product pairs in each order
        cooccurrence = defaultdict(int)
        product_counts = defaultdict(int)
        
        # Convert all item names to strings and group by order
        orders = self.data.groupby('order_id')['item_name'].apply(
            lambda x: [str(item) for item in x]
        )
        total_orders = len(orders)
        
        if total_orders == 0:
            return pd.DataFrame()
        
        for items in orders:
            unique_items = list(set(items))
            
            # Count individual products
            for item in unique_items:
                product_counts[item] += 1
            
            # Count pairs
            if len(unique_items) >= 2:
                for item_a, item_b in combinations(sorted(unique_items), 2):
                    cooccurrence[(item_a, item_b)] += 1
        
        # Calculate metrics
        cooccurrence_data = []
        for (product_a, product_b), count in cooccurrence.items():
            support = count / total_orders
            
            # Calculate lift
            prob_a = product_counts[product_a] / total_orders
            prob_b = product_counts[product_b] / total_orders
            prob_ab = support
            
            lift = prob_ab / (prob_a * prob_b) if (prob_a * prob_b) > 0 else 0
            confidence_a_to_b = prob_ab / prob_a if prob_a > 0 else 0
            confidence_b_to_a = prob_ab / prob_b if prob_b > 0 else 0
            
            cooccurrence_data.append({
                'product_a': product_a,
                'product_b': product_b,
                'cooccurrence_count': count,
                'support': support,
                'lift': lift,
                'confidence_a_to_b': confidence_a_to_b,
                'confidence_b_to_a': confidence_b_to_a
            })
        
        if len(cooccurrence_data) == 0:
            return pd.DataFrame()
        
        cooccurrence_df = pd.DataFrame(cooccurrence_data)
        cooccurrence_df = cooccurrence_df.sort_values('lift', ascending=False)
        
        return cooccurrence_df
    
    def get_complementary_products(self, product_name: str, n: int = 5) -> pd.DataFrame:
        """
        Find complementary products for a given product using multiple methods.
        
        Complementary = Products frequently bought together
        """
        # Method 1: Try affinity analysis
        affinity = self.analyze_product_affinity()
        
        if len(affinity) > 0:
            # Find products associated with the given product
            complementary = affinity[
                (affinity['product_a'] == product_name) |
                (affinity['product_b'] == product_name)
            ].copy()
            
            if len(complementary) > 0:
                # Extract the complementary product name
                complementary['complementary_product'] = complementary.apply(
                    lambda row: row['product_b'] if row['product_a'] == product_name else row['product_a'],
                    axis=1
                )
                
                complementary = complementary.sort_values('lift', ascending=False).head(n)
                
                # Ensure we have the 'confidence' column
                if 'confidence_a_to_b' in complementary.columns:
                    complementary['confidence'] = complementary.apply(
                        lambda row: row['confidence_a_to_b'] if row['product_a'] == product_name else row['confidence_b_to_a'],
                        axis=1
                    )
                
                return complementary[
                    ['complementary_product', 'support', 'lift', 'confidence']
                ]
        
        # Method 2: Fallback - Use simple co-occurrence
        print(f"Using fallback co-occurrence method for {product_name}")
        return self._get_complementary_by_cooccurrence(product_name, n)
    
    def _get_complementary_by_cooccurrence(self, product_name: str, n: int = 5) -> pd.DataFrame:
        """
        Fallback method: Find products bought together based on simple co-occurrence.
        """
        # Find orders containing the target product
        orders_with_product = self.data[self.data['item_name'] == product_name]['order_id'].unique()
        
        if len(orders_with_product) == 0:
            return pd.DataFrame()
        
        # Find all products in those orders
        related_items = self.data[
            (self.data['order_id'].isin(orders_with_product)) &
            (self.data['item_name'] != product_name)
        ]
        
        if len(related_items) == 0:
            return pd.DataFrame()
        
        # Count co-occurrences
        cooccurrence = related_items.groupby('item_name').agg({
            'order_id': 'nunique',
            'total': 'sum'
        }).reset_index()
        
        cooccurrence.columns = ['complementary_product', 'times_bought_together', 'total_revenue']
        
        # Calculate support
        total_orders_with_product = len(orders_with_product)
        cooccurrence['support'] = cooccurrence['times_bought_together'] / total_orders_with_product
        
        # Calculate a simple lift approximation
        all_orders = self.data['order_id'].nunique()
        for idx, row in cooccurrence.iterrows():
            product_orders = self.data[self.data['item_name'] == row['complementary_product']]['order_id'].nunique()
            expected = (total_orders_with_product / all_orders) * (product_orders / all_orders) * all_orders
            cooccurrence.loc[idx, 'lift'] = row['times_bought_together'] / expected if expected > 0 else 0
        
        cooccurrence['confidence'] = cooccurrence['support']
        
        # Sort by times bought together and support
        cooccurrence = cooccurrence.sort_values(['times_bought_together', 'support'], ascending=False).head(n)
        
        return cooccurrence[['complementary_product', 'support', 'lift', 'confidence', 'times_bought_together']]
    
    def get_category_associations(self) -> pd.DataFrame:
        """Analyze associations at the category level."""
        # Create category-level transactions
        # Convert all categories to strings to handle mixed types
        category_orders = self.data.groupby('order_id')['category'].apply(
            lambda x: [str(item) for item in set(x)]
        ).reset_index()
        
        # Create binary matrix
        te = TransactionEncoder()
        te_array = te.fit(category_orders['category']).transform(category_orders['category'])
        category_basket = pd.DataFrame(te_array, columns=te.columns_)
        
        # Find frequent category combinations
        frequent_categories = apriori(
            category_basket,
            min_support=config.MIN_SUPPORT,
            use_colnames=True
        )
        
        if len(frequent_categories) == 0:
            return pd.DataFrame()
        
        # Generate rules
        category_rules = association_rules(
            frequent_categories,
            metric="confidence",
            min_threshold=config.MIN_CONFIDENCE
        )
        
        if len(category_rules) == 0:
            return pd.DataFrame()
        
        category_rules['antecedents_list'] = category_rules['antecedents'].apply(list)
        category_rules['consequents_list'] = category_rules['consequents'].apply(list)
        
        return category_rules.sort_values('lift', ascending=False)[
            ['antecedents_list', 'consequents_list', 'support', 'confidence', 'lift']
        ]
    
    def get_customer_basket_insights(self) -> Dict:
        """Get insights about customer shopping baskets."""
        # Calculate basket statistics
        basket_stats = self.data.groupby('order_id').agg({
            'item_name': 'nunique',
            'total': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        basket_stats.columns = ['order_id', 'unique_items', 'basket_value', 'total_quantity']
        
        return {
            'avg_items_per_basket': basket_stats['unique_items'].mean(),
            'median_items_per_basket': basket_stats['unique_items'].median(),
            'avg_basket_value': basket_stats['basket_value'].mean(),
            'median_basket_value': basket_stats['basket_value'].median(),
            'max_items_in_basket': basket_stats['unique_items'].max(),
            'pct_single_item_baskets': (
                len(basket_stats[basket_stats['unique_items'] == 1]) / len(basket_stats) * 100
            ),
            'pct_multi_item_baskets': (
                len(basket_stats[basket_stats['unique_items'] > 1]) / len(basket_stats) * 100
            )
        }
    
    def get_analysis_diagnostics(self) -> Dict:
        """
        Get diagnostic information about the cross-sell analysis.
        
        Returns insights into why analysis may or may not be producing results.
        """
        diagnostics = {
            'total_records': len(self.data),
            'unique_customers': self.data['customer_name'].nunique(),
            'unique_products': self.data['item_name'].nunique(),
            'total_orders': self.data['order_id'].nunique(),
            'date_range': (self.data['date'].min(), self.data['date'].max()),
        }
        
        # Basket analysis
        basket_sizes = self.data.groupby('order_id')['item_name'].nunique()
        diagnostics['avg_basket_size'] = basket_sizes.mean()
        diagnostics['median_basket_size'] = basket_sizes.median()
        diagnostics['single_item_orders'] = (basket_sizes == 1).sum()
        diagnostics['multi_item_orders'] = (basket_sizes > 1).sum()
        diagnostics['pct_multi_item'] = (diagnostics['multi_item_orders'] / diagnostics['total_orders'] * 100)
        
        # Product frequency analysis
        product_freq = self.data.groupby('item_name')['order_id'].nunique()
        diagnostics['products_in_1_order'] = (product_freq == 1).sum()
        diagnostics['products_in_5plus_orders'] = (product_freq >= 5).sum()
        diagnostics['products_in_10plus_orders'] = (product_freq >= 10).sum()
        
        # Analysis metadata
        diagnostics.update(self.analysis_metadata)
        
        # Recommendations
        recommendations = []
        if diagnostics['pct_multi_item'] < 10:
            recommendations.append(
                "⚠ Only {:.1f}% of orders have multiple items. ".format(diagnostics['pct_multi_item']) +
                "Cross-sell analysis works best with more multi-item transactions."
            )
        
        if diagnostics['products_in_10plus_orders'] < 5:
            recommendations.append(
                "⚠ Very few products appear in 10+ orders. More transaction history needed for reliable patterns."
            )
        
        if diagnostics['total_orders'] < 100:
            recommendations.append(
                "⚠ Only {} orders in dataset. Recommend 500+ orders for robust cross-sell analysis.".format(
                    diagnostics['total_orders']
                )
            )
        
        diagnostics['recommendations'] = recommendations
        
        return diagnostics
    
    def print_diagnostics(self):
        """Print human-readable diagnostic information."""
        diag = self.get_analysis_diagnostics()
        
        print("\n" + "="*60)
        print("CROSS-SELL ANALYSIS DIAGNOSTICS")
        print("="*60)
        print(f"\n📊 Dataset Overview:")
        print(f"   • Total Records: {diag['total_records']:,}")
        print(f"   • Unique Customers: {diag['unique_customers']:,}")
        print(f"   • Unique Products: {diag['unique_products']:,}")
        print(f"   • Total Orders: {diag['total_orders']:,}")
        print(f"   • Date Range: {diag['date_range'][0].date()} to {diag['date_range'][1].date()}")
        
        print(f"\n🛒 Basket Analysis:")
        print(f"   • Average Basket Size: {diag['avg_basket_size']:.2f} items")
        print(f"   • Single-Item Orders: {diag['single_item_orders']:,} ({100-diag['pct_multi_item']:.1f}%)")
        print(f"   • Multi-Item Orders: {diag['multi_item_orders']:,} ({diag['pct_multi_item']:.1f}%)")
        
        print(f"\n📦 Product Frequency:")
        print(f"   • Products in 1 order: {diag['products_in_1_order']:,}")
        print(f"   • Products in 5+ orders: {diag['products_in_5plus_orders']:,}")
        print(f"   • Products in 10+ orders: {diag['products_in_10plus_orders']:,}")
        
        if diag.get('support_used'):
            print(f"\n🔍 Analysis Results:")
            print(f"   • Support Threshold Used: {diag['support_used']:.4f}")
            print(f"   • Association Rules Found: {diag['rules_found']:,}")
        
        if diag['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in diag['recommendations']:
                print(f"   {rec}")
        
        print("\n" + "="*60 + "\n")
    
    def suggest_upsell_opportunities(self, min_value_increase: float = 1.2) -> pd.DataFrame:
        """
        Identify upsell opportunities where adding a product significantly increases order value.
        
        Args:
            min_value_increase: Minimum multiplicative increase in order value
        """
        if self.association_rules_df is None:
            self.generate_association_rules()
        
        if self.association_rules_df is None or len(self.association_rules_df) == 0:
            return pd.DataFrame()
        
        upsell_data = []
        
        for _, rule in self.association_rules_df.iterrows():
            antecedents = list(rule['antecedents'])
            consequents = list(rule['consequents'])
            
            if len(antecedents) == 1 and len(consequents) == 1:
                base_product = antecedents[0]
                upsell_product = consequents[0]
                
                # Calculate average order values
                base_orders = self.data[
                    self.data['item_name'] == base_product
                ].groupby('order_id')['total'].sum()
                
                combined_orders = self.data[
                    self.data['item_name'].isin([base_product, upsell_product])
                ].groupby('order_id').agg({
                    'item_name': lambda x: set(x),
                    'total': 'sum'
                })
                
                combined_orders = combined_orders[
                    combined_orders['item_name'].apply(
                        lambda x: base_product in x and upsell_product in x
                    )
                ]
                
                if len(base_orders) > 0 and len(combined_orders) > 0:
                    avg_base_value = base_orders.mean()
                    avg_combined_value = combined_orders['total'].mean()
                    
                    value_increase = avg_combined_value / avg_base_value if avg_base_value > 0 else 0
                    
                    if value_increase >= min_value_increase:
                        upsell_data.append({
                            'base_product': base_product,
                            'upsell_product': upsell_product,
                            'avg_base_value': avg_base_value,
                            'avg_combined_value': avg_combined_value,
                            'value_increase_pct': (value_increase - 1) * 100,
                            'confidence': rule['confidence'],
                            'lift': rule['lift']
                        })
        
        if len(upsell_data) == 0:
            return pd.DataFrame()
        
        upsell_df = pd.DataFrame(upsell_data)
        upsell_df = upsell_df.sort_values('value_increase_pct', ascending=False)
        
        return upsell_df

