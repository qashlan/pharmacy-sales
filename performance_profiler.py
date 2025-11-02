#!/usr/bin/env python3
"""Performance profiling tool to identify bottlenecks in the pharmacy sales analytics system."""

import time
import tracemalloc
import pandas as pd
import sys
from functools import wraps
from typing import Callable, Any
import psutil
import os

# Import all modules to profile
from data_loader import DataLoader, load_sample_data
from sales_analysis import SalesAnalyzer
from customer_analysis import CustomerAnalyzer
from product_analysis import ProductAnalyzer
from rfm_analysis import RFMAnalyzer
from refill_prediction import RefillPredictor
from cross_sell_analysis import CrossSellAnalyzer


class PerformanceProfiler:
    """Profile performance of different operations."""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process(os.getpid())
        
    def profile_function(self, func: Callable, name: str, *args, **kwargs) -> Any:
        """Profile a single function execution."""
        # Memory before
        mem_before = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Start time
        start_time = time.time()
        
        # Start memory tracking
        tracemalloc.start()
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        # End time
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Memory tracking
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory after
        mem_after = self.process.memory_info().rss / 1024 / 1024  # MB
        mem_delta = mem_after - mem_before
        
        # Store results
        self.results.append({
            'operation': name,
            'time_seconds': elapsed,
            'memory_mb': mem_delta,
            'peak_memory_mb': peak / 1024 / 1024,
            'success': success,
            'error': error
        })
        
        return result
    
    def print_results(self):
        """Print profiling results in a nice format."""
        print("\n" + "=" * 100)
        print("PERFORMANCE PROFILING RESULTS")
        print("=" * 100)
        
        df = pd.DataFrame(self.results)
        
        # Sort by time
        df = df.sort_values('time_seconds', ascending=False)
        
        print("\n📊 SLOWEST OPERATIONS (sorted by time):")
        print("-" * 100)
        print(f"{'Operation':<40} {'Time (s)':<12} {'Memory (MB)':<15} {'Peak Mem (MB)':<15} {'Status'}")
        print("-" * 100)
        
        for _, row in df.iterrows():
            status = "✓" if row['success'] else f"✗ {row['error'][:30]}"
            print(f"{row['operation']:<40} {row['time_seconds']:>10.3f}   {row['memory_mb']:>12.2f}   "
                  f"{row['peak_memory_mb']:>13.2f}   {status}")
        
        print("-" * 100)
        
        # Summary statistics
        total_time = df['time_seconds'].sum()
        total_memory = df['memory_mb'].sum()
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Total Memory Delta: {total_memory:.2f} MB")
        print(f"  Operations: {len(df)}")
        print(f"  Failed: {(~df['success']).sum()}")
        
        # Identify bottlenecks
        print(f"\n⚠️  BOTTLENECKS (>1 second):")
        slow_ops = df[df['time_seconds'] > 1.0]
        if len(slow_ops) > 0:
            for _, row in slow_ops.iterrows():
                print(f"  - {row['operation']}: {row['time_seconds']:.2f}s")
        else:
            print("  ✓ No major bottlenecks detected!")
        
        # Memory hogs
        print(f"\n💾 MEMORY INTENSIVE (>50 MB):")
        memory_hogs = df[df['memory_mb'] > 50]
        if len(memory_hogs) > 0:
            for _, row in memory_hogs.iterrows():
                print(f"  - {row['operation']}: {row['memory_mb']:.2f} MB")
        else:
            print("  ✓ No major memory issues detected!")
        
        return df


def profile_data_loading(profiler: PerformanceProfiler, data_size: int = 1000):
    """Profile data loading operations."""
    print(f"\n{'='*100}")
    print(f"PROFILING DATA LOADING ({data_size} records)")
    print(f"{'='*100}")
    
    # Generate sample data
    sample_df = profiler.profile_function(
        load_sample_data,
        f"1. Generate Sample Data ({data_size} records)"
    )
    
    if sample_df is None:
        print("Failed to generate sample data!")
        return None
    
    # Save to temp file
    temp_file = f'/tmp/profile_data_{data_size}.csv'
    sample_df.to_csv(temp_file, index=False)
    
    # Load data
    loader = DataLoader(temp_file)
    profiler.profile_function(
        loader.load_data,
        "2. Load Data from CSV"
    )
    
    # Preprocess data
    data = profiler.profile_function(
        loader.preprocess_data,
        "3. Preprocess Data (TOTAL)"
    )
    
    return data


def profile_analyzer_creation(profiler: PerformanceProfiler, data):
    """Profile creation of analyzer instances."""
    print(f"\n{'='*100}")
    print(f"PROFILING ANALYZER INSTANTIATION")
    print(f"{'='*100}")
    
    analyzers = {}
    
    analyzers['sales'] = profiler.profile_function(
        SalesAnalyzer,
        "4. Create SalesAnalyzer",
        data
    )
    
    analyzers['customer'] = profiler.profile_function(
        CustomerAnalyzer,
        "5. Create CustomerAnalyzer",
        data
    )
    
    analyzers['product'] = profiler.profile_function(
        ProductAnalyzer,
        "6. Create ProductAnalyzer",
        data
    )
    
    analyzers['rfm'] = profiler.profile_function(
        RFMAnalyzer,
        "7. Create RFMAnalyzer",
        data
    )
    
    analyzers['refill'] = profiler.profile_function(
        RefillPredictor,
        "8. Create RefillPredictor",
        data
    )
    
    analyzers['cross_sell'] = profiler.profile_function(
        CrossSellAnalyzer,
        "9. Create CrossSellAnalyzer",
        data
    )
    
    return analyzers


def profile_analyzer_operations(profiler: PerformanceProfiler, analyzers: dict):
    """Profile common analyzer operations."""
    print(f"\n{'='*100}")
    print(f"PROFILING ANALYZER OPERATIONS")
    print(f"{'='*100}")
    
    # Sales Analysis
    if analyzers.get('sales'):
        sales = analyzers['sales']
        profiler.profile_function(
            sales.get_overall_metrics,
            "10. Sales: Get Overall Metrics"
        )
        profiler.profile_function(
            sales.get_daily_trends,
            "11. Sales: Get Daily Trends"
        )
        profiler.profile_function(
            sales.get_top_products,
            "12. Sales: Get Top Products",
            n=20
        )
    
    # Customer Analysis
    if analyzers.get('customer'):
        customer = analyzers['customer']
        profiler.profile_function(
            customer.get_customer_summary,
            "13. Customer: Get Summary (CACHED)"
        )
        profiler.profile_function(
            customer.get_high_value_customers,
            "14. Customer: Get High Value",
            n=20
        )
        profiler.profile_function(
            customer.get_churn_risk_customers,
            "15. Customer: Get Churn Risk"
        )
    
    # Product Analysis
    if analyzers.get('product'):
        product = analyzers['product']
        profiler.profile_function(
            product.get_product_summary,
            "16. Product: Get Summary (CACHED)"
        )
        profiler.profile_function(
            product.get_abc_classification,
            "17. Product: ABC Classification"
        )
    
    # RFM Analysis
    if analyzers.get('rfm'):
        rfm = analyzers['rfm']
        profiler.profile_function(
            rfm.calculate_rfm_simple,
            "18. RFM: Calculate Simple Segments"
        )
    
    # Refill Prediction (EXPENSIVE)
    if analyzers.get('refill'):
        refill = analyzers['refill']
        profiler.profile_function(
            refill.calculate_purchase_intervals,
            "19. Refill: Calculate Purchase Intervals (EXPENSIVE)"
        )
        
        # Test cache effectiveness
        profiler.profile_function(
            refill.calculate_purchase_intervals,
            "20. Refill: Get Intervals (CACHED - should be instant)"
        )
    
    # Cross-Sell Analysis (EXPENSIVE)
    if analyzers.get('cross_sell'):
        cross_sell = analyzers['cross_sell']
        profiler.profile_function(
            cross_sell.get_order_basket_summary,
            "21. Cross-Sell: Get Basket Summary"
        )
        profiler.profile_function(
            cross_sell.find_frequent_itemsets,
            "22. Cross-Sell: Find Frequent Itemsets (EXPENSIVE)",
            min_support=0.01
        )
        
        # Test cache effectiveness
        profiler.profile_function(
            cross_sell.find_frequent_itemsets,
            "23. Cross-Sell: Get Itemsets (CACHED - should be instant)",
            min_support=0.01
        )


def profile_with_different_sizes():
    """Profile with different dataset sizes."""
    print("\n" + "=" * 100)
    print("MULTI-SIZE PERFORMANCE TESTING")
    print("=" * 100)
    
    sizes = [100, 1000, 5000]
    results = []
    
    for size in sizes:
        print(f"\n\n{'#'*100}")
        print(f"# TESTING WITH {size} RECORDS")
        print(f"{'#'*100}")
        
        profiler = PerformanceProfiler()
        
        # Profile everything
        data = profile_data_loading(profiler, data_size=size)
        if data is not None:
            analyzers = profile_analyzer_creation(profiler, data)
            profile_analyzer_operations(profiler, analyzers)
        
        # Get results
        df = profiler.print_results()
        
        # Store summary
        results.append({
            'records': size,
            'total_time': df['time_seconds'].sum(),
            'slowest_op': df.loc[df['time_seconds'].idxmax(), 'operation'],
            'slowest_time': df['time_seconds'].max()
        })
    
    # Compare across sizes
    print("\n" + "=" * 100)
    print("SCALABILITY ANALYSIS")
    print("=" * 100)
    
    results_df = pd.DataFrame(results)
    print("\n", results_df.to_string(index=False))
    
    # Calculate time per record
    results_df['time_per_record_ms'] = (results_df['total_time'] / results_df['records']) * 1000
    
    print(f"\n📈 Time per Record:")
    for _, row in results_df.iterrows():
        print(f"  {row['records']:>5} records: {row['time_per_record_ms']:.2f} ms/record")
    
    # Identify scaling issues
    if len(results_df) > 1:
        time_ratio = results_df.iloc[-1]['total_time'] / results_df.iloc[0]['total_time']
        record_ratio = results_df.iloc[-1]['records'] / results_df.iloc[0]['records']
        
        print(f"\n🎯 Scaling Factor:")
        print(f"  Records increased: {record_ratio:.1f}x")
        print(f"  Time increased: {time_ratio:.1f}x")
        
        if time_ratio > record_ratio * 1.5:
            print(f"  ⚠️  WARNING: Non-linear scaling detected! (O(n²) or worse)")
            print(f"     Time grew {time_ratio/record_ratio:.1f}x faster than expected")
        elif time_ratio > record_ratio:
            print(f"  ⚠️  Slightly worse than linear scaling")
        else:
            print(f"  ✓ Good scaling performance!")


def main():
    """Run comprehensive performance profiling."""
    print("\n" + "🔍" * 50)
    print("PHARMACY SALES ANALYTICS - PERFORMANCE PROFILER")
    print("🔍" * 50)
    
    print("\nThis tool will:")
    print("  1. Profile data loading and preprocessing")
    print("  2. Profile analyzer instantiation")
    print("  3. Profile common operations")
    print("  4. Test with different dataset sizes")
    print("  5. Identify bottlenecks and scaling issues")
    
    print("\n⏱️  This may take 1-2 minutes...")
    
    # Run profiling with different sizes
    profile_with_different_sizes()
    
    print("\n" + "=" * 100)
    print("✅ PROFILING COMPLETE!")
    print("=" * 100)
    
    print("\n📝 RECOMMENDATIONS:")
    print("\nBased on the results above, focus optimization efforts on:")
    print("  1. Operations taking >1 second")
    print("  2. Operations with non-linear scaling")
    print("  3. Memory-intensive operations (>50 MB)")
    print("\nFor specific optimization strategies, see:")
    print("  - PERFORMANCE_OPTIMIZATIONS.md")
    print("  - PERFORMANCE_ENHANCEMENTS.md (this file)")


if __name__ == '__main__':
    main()

