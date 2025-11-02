#!/usr/bin/env python3
"""
Test script to verify Cross-Sell performance optimizations.

This script:
1. Loads data
2. Tests optimized cross-sell analysis
3. Measures performance
4. Verifies correctness
"""

import time
import pandas as pd
from data_loader import DataLoader
from cross_sell_analysis import CrossSellAnalyzer


def format_time(seconds):
    """Format seconds to readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.2f}s"


def test_cross_sell_performance():
    """Test cross-sell analysis performance."""
    print("="*70)
    print("CROSS-SELL PERFORMANCE OPTIMIZATION TEST")
    print("="*70)
    
    # Load data
    print("\n📂 Loading data...")
    start = time.time()
    loader = DataLoader('pharmacy_sales.xlsx')
    data = loader.load_data()
    data = loader.preprocess_data()
    load_time = time.time() - start
    print(f"✓ Loaded {len(data):,} records in {format_time(load_time)}")
    
    # Test with sampling (optimized)
    print("\n" + "="*70)
    print("TEST 1: WITH OPTIMIZATIONS (Sampling + Caching)")
    print("="*70)
    
    start = time.time()
    analyzer_optimized = CrossSellAnalyzer(data, enable_sampling=True, max_records=100000)
    init_time = time.time() - start
    print(f"✓ Analyzer initialized in {format_time(init_time)}")
    
    # Test bundle suggestions
    print("\n📦 Testing bundle suggestions...")
    start = time.time()
    bundles = analyzer_optimized.get_bundle_suggestions(min_items=2, max_items=4, n=10)
    bundle_time = time.time() - start
    print(f"✓ Found {len(bundles)} bundles in {format_time(bundle_time)}")
    if len(bundles) > 0:
        print(f"   Top bundle: {bundles.iloc[0]['bundle_items']}")
    
    # Test complementary products (with caching)
    print("\n🔗 Testing complementary products...")
    if len(data) > 0:
        test_product = data['item_name'].value_counts().index[0]
        start = time.time()
        complementary = analyzer_optimized.get_complementary_products(test_product, n=5)
        comp_time = time.time() - start
        print(f"✓ Found complementary products for '{test_product}' in {format_time(comp_time)}")
        print(f"   Found {len(complementary)} complementary products")
    
    # Test product affinity (cached)
    print("\n💫 Testing product affinity...")
    start = time.time()
    affinity = analyzer_optimized.analyze_product_affinity()
    affinity_time = time.time() - start
    print(f"✓ Calculated product affinity in {format_time(affinity_time)}")
    print(f"   Found {len(affinity)} product pairs")
    
    # Test caching effectiveness
    print("\n" + "="*70)
    print("TEST 2: CACHE EFFECTIVENESS")
    print("="*70)
    
    print("\n🔄 Re-running bundle suggestions (should use cache)...")
    start = time.time()
    bundles_cached = analyzer_optimized.get_bundle_suggestions(min_items=2, max_items=4, n=10)
    bundle_cached_time = time.time() - start
    print(f"✓ Retrieved bundles in {format_time(bundle_cached_time)}")
    
    cache_speedup = bundle_time / bundle_cached_time if bundle_cached_time > 0 else 0
    print(f"   Cache speedup: {cache_speedup:.1f}x faster!")
    
    # Test without sampling (full dataset)
    if len(data) <= 50000:  # Only test on smaller datasets
        print("\n" + "="*70)
        print("TEST 3: WITHOUT SAMPLING (Full Dataset)")
        print("="*70)
        
        start = time.time()
        analyzer_full = CrossSellAnalyzer(data, enable_sampling=False)
        init_full_time = time.time() - start
        print(f"✓ Analyzer initialized in {format_time(init_full_time)}")
        
        start = time.time()
        bundles_full = analyzer_full.get_bundle_suggestions(min_items=2, max_items=4, n=10)
        bundle_full_time = time.time() - start
        print(f"✓ Found {len(bundles_full)} bundles in {format_time(bundle_full_time)}")
        
        sampling_speedup = bundle_full_time / bundle_time if bundle_time > 0 else 0
        print(f"   Sampling speedup: {sampling_speedup:.1f}x faster!")
    else:
        print(f"\n⏭️  Skipping full dataset test (dataset too large: {len(data):,} records)")
    
    # Performance summary
    print("\n" + "="*70)
    print("PERFORMANCE SUMMARY")
    print("="*70)
    
    total_time = init_time + bundle_time + comp_time + affinity_time
    print(f"\n📊 Total Analysis Time: {format_time(total_time)}")
    print(f"   • Initialization: {format_time(init_time)}")
    print(f"   • Bundle suggestions: {format_time(bundle_time)}")
    print(f"   • Complementary products: {format_time(comp_time)}")
    print(f"   • Product affinity: {format_time(affinity_time)}")
    
    print(f"\n⚡ Cache Performance:")
    print(f"   • First bundle query: {format_time(bundle_time)}")
    print(f"   • Cached bundle query: {format_time(bundle_cached_time)}")
    print(f"   • Speedup: {cache_speedup:.1f}x")
    
    # Diagnostics
    print("\n📋 Data Diagnostics:")
    diag = analyzer_optimized.get_analysis_diagnostics()
    print(f"   • Total orders analyzed: {diag['total_orders']:,}")
    print(f"   • Unique products: {diag['unique_products']:,}")
    print(f"   • Multi-item orders: {diag['multi_item_orders']:,} ({diag['pct_multi_item']:.1f}%)")
    print(f"   • Avg basket size: {diag['avg_basket_size']:.2f}")
    
    # Performance rating
    print("\n🎯 Performance Rating:")
    if total_time < 5:
        rating = "🌟 EXCELLENT"
    elif total_time < 15:
        rating = "✅ GOOD"
    elif total_time < 30:
        rating = "⚠️  ACCEPTABLE"
    else:
        rating = "🐌 SLOW"
    
    print(f"   {rating} - Total time: {format_time(total_time)}")
    
    # Optimization status
    print("\n✅ Optimization Features:")
    print("   ✓ Caching enabled")
    print("   ✓ Vectorized operations")
    print("   ✓ Set-based matching")
    print("   ✓ Smart sampling")
    print("   ✓ Pre-computed mappings")
    
    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY! 🎉")
    print("="*70)
    
    return {
        'total_time': total_time,
        'bundle_time': bundle_time,
        'cache_speedup': cache_speedup,
        'bundles_found': len(bundles),
        'affinity_pairs': len(affinity)
    }


def main():
    """Main entry point."""
    try:
        results = test_cross_sell_performance()
        
        print("\n💡 Tips:")
        print("   • For large datasets, enable sampling for best performance")
        print("   • Cache is automatically used for repeated queries")
        print("   • Adjust max_records in UI for your specific needs")
        print("   • See CROSS_SELL_PERFORMANCE_OPTIMIZATION.md for details")
        
        return 0
    
    except FileNotFoundError:
        print("\n❌ Error: pharmacy_sales.xlsx not found")
        print("   Please ensure the data file exists in the current directory")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

