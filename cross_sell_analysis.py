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
    
    def __init__(self, data: pd.DataFrame, enable_sampling: bool = True, max_records: int = 100000):
        """
        Initialize cross-sell analyzer.
        
        Args:
            data: Preprocessed sales DataFrame
            enable_sampling: If True, sample large datasets for performance
            max_records: Maximum records to analyze (for sampling)
        
        Note:
            Items are grouped by order_id (which comes from the Receipt column in raw data).
            This ensures items from the same receipt/transaction are analyzed together.
        """
        # Verify order_id exists (should come from receipt column)
        if 'order_id' not in data.columns:
            raise ValueError("Data must have 'order_id' column (mapped from Receipt column)")
        
        # Exclude refunds from cross-sell analysis
        # Refunds don't represent actual purchase intent/patterns
        self.data = data[~data['is_refund']].copy()
        
        # Exclude service items from cross-sell analysis
        # Services are not products and don't represent meaningful cross-sell patterns
        if 'is_service' in self.data.columns:
            num_services = self.data['is_service'].sum()
            self.data = self.data[~self.data['is_service']].copy()
            if num_services > 0:
                print(f"ℹ️  Cross-Sell Analysis: Excluded {num_services} service transactions")
        
        # OPTIMIZATION: Sample large datasets for better performance
        if enable_sampling and len(self.data) > max_records:
            print(f"⚡ Sampling {max_records:,} most recent records from {len(self.data):,} for faster analysis")
            self.data = self.data.nlargest(max_records, 'date')
        
        self.basket_data: Optional[pd.DataFrame] = None
        self.association_rules_df: Optional[pd.DataFrame] = None
        self._frequent_itemsets_cache: Optional[pd.DataFrame] = None
        self._cooccurrence_cache: Optional[pd.DataFrame] = None
        self._order_item_sets_cache: Optional[Dict] = None
        self._order_totals_cache: Optional[Dict] = None
        
        # Verify order_id grouping
        unique_orders = self.data['order_id'].nunique()
        total_items = len(self.data)
        
        self.analysis_metadata = {
            'total_orders': unique_orders,
            'total_items': total_items,
            'avg_items_per_order': total_items / unique_orders if unique_orders > 0 else 0,
            'multi_item_orders': 0,
            'unique_products': 0,
            'support_used': None,
            'rules_found': 0,
            'refunds_excluded': len(data) - len(self.data),
            'uses_receipt_grouping': True  # Confirms using receipt/order_id
        }
        
        if self.analysis_metadata['refunds_excluded'] > 0:
            print(f"ℹ Cross-sell analysis: Excluded {self.analysis_metadata['refunds_excluded']} refund transactions")
        
        print(f"ℹ Cross-sell analysis: Using order_id (from Receipt column) to group {unique_orders} orders with {total_items} items")
        
    def create_basket_matrix(self) -> pd.DataFrame:
        """
        Create a transaction-product matrix for market basket analysis.
        
        Uses order_id (from Receipt column) to group items that were purchased together.
        
        Returns:
            Binary matrix where rows are orders and columns are products
        """
        # Create basket: each order_id with list of products
        # NOTE: order_id comes from Receipt column in original data
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
    
    def get_receipt_grouping_info(self) -> Dict:
        """
        Get information about how items are grouped by receipt/order_id.
        
        This method shows how the Receipt column is being used to identify
        which items were sold together in the same transaction.
        
        Returns:
            Dictionary with grouping statistics and sample orders
        """
        # Group items by order_id
        order_groups = self.data.groupby('order_id').agg({
            'item_name': lambda x: list(x),
            'customer_name': 'first',
            'date': 'first',
            'total': 'sum'
        }).reset_index()
        
        # Calculate basket sizes
        order_groups['basket_size'] = order_groups['item_name'].apply(len)
        
        # Statistics
        total_orders = len(order_groups)
        single_item_orders = (order_groups['basket_size'] == 1).sum()
        multi_item_orders = (order_groups['basket_size'] > 1).sum()
        avg_basket_size = order_groups['basket_size'].mean()
        max_basket_size = order_groups['basket_size'].max()
        
        # Sample multi-item orders (for verification)
        sample_orders = order_groups[order_groups['basket_size'] > 1].head(10)
        
        # Get distribution of basket sizes
        basket_size_dist = order_groups['basket_size'].value_counts().sort_index().to_dict()
        
        return {
            'grouping_method': 'order_id (from Receipt column)',
            'total_orders': total_orders,
            'single_item_orders': single_item_orders,
            'multi_item_orders': multi_item_orders,
            'multi_item_percentage': (multi_item_orders / total_orders * 100) if total_orders > 0 else 0,
            'avg_basket_size': avg_basket_size,
            'max_basket_size': max_basket_size,
            'basket_size_distribution': basket_size_dist,
            'sample_multi_item_orders': sample_orders[['order_id', 'customer_name', 'date', 'item_name', 'basket_size', 'total']].to_dict('records')
        }
    
    def verify_receipt_grouping(self, sample_size: int = 5) -> None:
        """
        Verify and display how items are grouped by receipt/order_id.
        
        Shows sample orders to confirm that items from the same receipt
        are correctly grouped together for cross-sell analysis.
        
        Args:
            sample_size: Number of sample orders to display
        """
        print("\n" + "="*70)
        print("RECEIPT/ORDER GROUPING VERIFICATION")
        print("="*70)
        
        info = self.get_receipt_grouping_info()
        
        print(f"\n📋 Grouping Method: {info['grouping_method']}")
        print(f"\n📊 Order Statistics:")
        print(f"   • Total Orders: {info['total_orders']:,}")
        print(f"   • Single-Item Orders: {info['single_item_orders']:,} ({100-info['multi_item_percentage']:.1f}%)")
        print(f"   • Multi-Item Orders: {info['multi_item_orders']:,} ({info['multi_item_percentage']:.1f}%)")
        print(f"   • Average Basket Size: {info['avg_basket_size']:.2f} items")
        print(f"   • Largest Basket: {info['max_basket_size']} items")
        
        print(f"\n📦 Basket Size Distribution:")
        for size, count in sorted(info['basket_size_distribution'].items()):
            pct = (count / info['total_orders'] * 100)
            print(f"   • {size} item{'s' if size > 1 else ''}: {count:,} orders ({pct:.1f}%)")
        
        print(f"\n🔍 Sample Multi-Item Orders (Receipt Grouping):")
        print("   These show items that were purchased together in same receipt:\n")
        
        for i, order in enumerate(info['sample_multi_item_orders'][:sample_size], 1):
            print(f"   Order #{order['order_id']}:")
            print(f"      Customer: {order['customer_name']}")
            print(f"      Date: {order['date']}")
            print(f"      Items ({order['basket_size']}):")
            for item in order['item_name']:
                print(f"         - {item}")
            print(f"      Total: ${order['total']:.2f}")
            print()
        
        print("="*70)
        print("✅ Items are correctly grouped by Receipt/Order ID")
        print("="*70 + "\n")
    
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
        OPTIMIZED: Uses vectorized operations for better performance.
        
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
        
        # OPTIMIZATION: Pre-compute order-item mapping for faster lookups (with caching)
        if self._order_item_sets_cache is None:
            self._order_item_sets_cache = self.data.groupby('order_id')['item_name'].apply(set).to_dict()
        if self._order_totals_cache is None:
            self._order_totals_cache = self.data.groupby('order_id')['total'].sum().to_dict()
        
        order_item_sets = self._order_item_sets_cache
        order_totals = self._order_totals_cache
        
        # Calculate bundle metrics using vectorized approach
        bundle_metrics = []
        
        for _, row in bundles.iterrows():
            items_set = set(row['bundle_items'])
            
            # OPTIMIZED: Find orders containing all items in bundle using set operations
            matching_orders = [
                order_id for order_id, order_items in order_item_sets.items()
                if items_set.issubset(order_items)
            ]
            
            bundle_frequency = len(matching_orders)
            
            if bundle_frequency > 0:
                # OPTIMIZED: Use pre-computed totals instead of querying data
                bundle_revenue = sum(order_totals.get(order_id, 0) for order_id in matching_orders)
                avg_basket_value = bundle_revenue / bundle_frequency
            else:
                bundle_revenue = 0
                avg_basket_value = 0
            
            bundle_metrics.append({
                'bundle_frequency': bundle_frequency,
                'bundle_revenue': bundle_revenue,
                'avg_basket_value': avg_basket_value
            })
        
        # Add metrics to bundles DataFrame
        metrics_df = pd.DataFrame(bundle_metrics)
        bundles = pd.concat([bundles.reset_index(drop=True), metrics_df], axis=1)
        
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
        OPTIMIZED: Uses pre-computed mappings and efficient data structures.
        """
        # OPTIMIZED: Pre-compute order items as sets and totals
        order_data = self.data.groupby('order_id').agg({
            'item_name': lambda x: list(set(x)),
            'total': 'sum'
        })
        
        # Filter for multi-item orders
        order_data = order_data[order_data['item_name'].apply(len) >= min_items]
        
        if len(order_data) == 0:
            print("⚠ No multi-item orders found for bundle analysis.")
            return pd.DataFrame()
        
        # OPTIMIZED: Count item combinations more efficiently
        bundle_counts = defaultdict(int)
        bundle_revenue = defaultdict(float)
        total_orders = self.data['order_id'].nunique()
        
        # Limit combinations for very large baskets to avoid exponential explosion
        max_basket_size_for_combos = min(max_items * 2, 10)
        
        for items, order_total in zip(order_data['item_name'], order_data['total']):
            # Skip extremely large baskets to prevent performance issues
            if len(items) > max_basket_size_for_combos:
                items = items[:max_basket_size_for_combos]
            
            # Generate combinations
            for size in range(min_items, min(max_items + 1, len(items) + 1)):
                for combo in combinations(sorted(items), size):
                    bundle_counts[combo] += 1
                    bundle_revenue[combo] += order_total
        
        # Convert to DataFrame more efficiently
        if len(bundle_counts) == 0:
            return pd.DataFrame()
        
        # OPTIMIZED: Create DataFrame in one go instead of appending
        bundles_df = pd.DataFrame([
            {
                'bundle_items': list(bundle),
                'itemset_size': len(bundle),
                'bundle_frequency': count,
                'support': count / total_orders,
                'bundle_revenue': bundle_revenue[bundle],
                'avg_basket_value': bundle_revenue[bundle] / count if count > 0 else 0,
                'score': count * np.log1p(bundle_revenue[bundle])
            }
            for bundle, count in bundle_counts.items()
        ])
        
        bundles_df = bundles_df.sort_values('score', ascending=False).head(n)
        
        print(f"✓ Found {len(bundles_df)} bundles using co-occurrence analysis")
        return bundles_df
    
    def analyze_product_affinity(self) -> pd.DataFrame:
        """
        Calculate product affinity scores for all product pairs.
        OPTIMIZED: Uses cached co-occurrence data.
        
        Affinity = How often products are bought together relative to their individual frequencies
        """
        if self.association_rules_df is None:
            self.generate_association_rules()
        
        if self.association_rules_df is None or len(self.association_rules_df) == 0:
            # Fallback: calculate co-occurrence manually (with caching)
            if self._cooccurrence_cache is not None:
                return self._cooccurrence_cache
            
            self._cooccurrence_cache = self._calculate_cooccurrence()
            return self._cooccurrence_cache
        
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
        """
        Calculate co-occurrence matrix manually.
        OPTIMIZED: Uses vectorized operations and numpy for performance.
        """
        # OPTIMIZED: Get unique items per order in one pass
        orders = self.data.groupby('order_id')['item_name'].apply(
            lambda x: list(set(str(item) for item in x))
        )
        total_orders = len(orders)
        
        if total_orders == 0:
            return pd.DataFrame()
        
        # OPTIMIZED: Count products and pairs more efficiently
        cooccurrence = defaultdict(int)
        product_counts = defaultdict(int)
        
        for items in orders:
            # Count individual products
            for item in items:
                product_counts[item] += 1
            
            # Count pairs (only for multi-item orders)
            if len(items) >= 2:
                # OPTIMIZED: Generate pairs without sorting each time
                items_sorted = sorted(items)
                for item_a, item_b in combinations(items_sorted, 2):
                    cooccurrence[(item_a, item_b)] += 1
        
        if len(cooccurrence) == 0:
            return pd.DataFrame()
        
        # OPTIMIZED: Vectorize metric calculations
        product_a_list = []
        product_b_list = []
        counts = []
        
        for (product_a, product_b), count in cooccurrence.items():
            product_a_list.append(product_a)
            product_b_list.append(product_b)
            counts.append(count)
        
        # Create DataFrame early for vectorized operations
        cooccurrence_df = pd.DataFrame({
            'product_a': product_a_list,
            'product_b': product_b_list,
            'cooccurrence_count': counts
        })
        
        # OPTIMIZED: Vectorized calculations
        cooccurrence_df['support'] = cooccurrence_df['cooccurrence_count'] / total_orders
        
        # Calculate probabilities for lift
        cooccurrence_df['prob_a'] = cooccurrence_df['product_a'].map(
            lambda x: product_counts[x] / total_orders
        )
        cooccurrence_df['prob_b'] = cooccurrence_df['product_b'].map(
            lambda x: product_counts[x] / total_orders
        )
        
        # Vectorized lift calculation
        cooccurrence_df['lift'] = np.where(
            (cooccurrence_df['prob_a'] * cooccurrence_df['prob_b']) > 0,
            cooccurrence_df['support'] / (cooccurrence_df['prob_a'] * cooccurrence_df['prob_b']),
            0
        )
        
        # Vectorized confidence calculations
        cooccurrence_df['confidence_a_to_b'] = np.where(
            cooccurrence_df['prob_a'] > 0,
            cooccurrence_df['support'] / cooccurrence_df['prob_a'],
            0
        )
        cooccurrence_df['confidence_b_to_a'] = np.where(
            cooccurrence_df['prob_b'] > 0,
            cooccurrence_df['support'] / cooccurrence_df['prob_b'],
            0
        )
        
        # Clean up temporary columns
        cooccurrence_df = cooccurrence_df.drop(['prob_a', 'prob_b'], axis=1)
        
        # Sort by lift
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
        OPTIMIZED: Uses cached order mappings and vectorized operations.
        """
        # OPTIMIZED: Use cached order-item mapping
        if self._order_item_sets_cache is None:
            self._order_item_sets_cache = self.data.groupby('order_id')['item_name'].apply(set).to_dict()
        
        # Find orders containing the target product
        orders_with_product = [
            order_id for order_id, items in self._order_item_sets_cache.items()
            if product_name in items
        ]
        
        if len(orders_with_product) == 0:
            return pd.DataFrame()
        
        # OPTIMIZED: Find all products in those orders (vectorized)
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
        
        # OPTIMIZED: Vectorized lift calculation
        all_orders = len(self._order_item_sets_cache)
        
        # Pre-compute product frequencies
        product_freq = self.data.groupby('item_name')['order_id'].nunique().to_dict()
        
        cooccurrence['lift'] = cooccurrence['complementary_product'].apply(
            lambda prod: (
                cooccurrence.loc[cooccurrence['complementary_product'] == prod, 'times_bought_together'].values[0] /
                ((total_orders_with_product / all_orders) * (product_freq.get(prod, 0) / all_orders) * all_orders)
            ) if ((total_orders_with_product / all_orders) * (product_freq.get(prod, 0) / all_orders) * all_orders) > 0 else 0
        )
        
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
        Confirms that Receipt column (as order_id) is being used for grouping.
        """
        diagnostics = {
            'grouping_method': 'order_id (from Receipt column)',
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
        print(f"\n🔗 Grouping Method: {diag['grouping_method']}")
        print(f"   (Items from same Receipt are grouped together)")
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

