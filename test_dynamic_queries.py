#!/usr/bin/env python3
"""
Test script for Dynamic AI Query system.

This script demonstrates the new dynamic query capabilities that allow
aggressive/complex queries without predefined handlers.
"""

from data_loader import DataLoader, load_sample_data
from ai_query import AIQueryEngine
import config

def test_dynamic_queries():
    """Test various aggressive queries using the dynamic query system."""
    
    print("=" * 80)
    print("DYNAMIC AI QUERY SYSTEM - TEST SCRIPT")
    print("=" * 80)
    print()
    
    # Load sample data
    print("Loading sample data...")
    sample_df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = sample_df
    data = loader.preprocess_data()
    print(f"✓ Loaded {len(data)} records")
    print()
    
    # Initialize AI query engine
    print("Initializing AI Query Engine...")
    engine = AIQueryEngine(data, use_openai=True)
    
    if not engine.openai_enabled:
        print("⚠️  OpenAI is not enabled. Dynamic queries require OpenAI API key.")
        print("   Please set OPENAI_API_KEY in config.py or environment variables.")
        return
    
    print(f"✓ AI Query Engine initialized (OpenAI: {'Enabled' if engine.openai_enabled else 'Disabled'})")
    print()
    
    # Test queries - from simple to aggressive
    test_queries = [
        # Predefined handler queries (should work without dynamic query)
        {
            "query": "What is the total revenue?",
            "category": "Basic (Predefined Handler)",
            "expected": "Should use predefined handler"
        },
        {
            "query": "Show me the top 5 products",
            "category": "Basic (Predefined Handler)",
            "expected": "Should use predefined handler"
        },
        
        # Medium complexity - might trigger dynamic queries
        {
            "query": "What's the average revenue per customer?",
            "category": "Medium (Dynamic Query)",
            "expected": "Calculate mean revenue per customer"
        },
        {
            "query": "Which day of the week has the highest sales?",
            "category": "Medium (Dynamic Query)",
            "expected": "Group by day name and sum revenue"
        },
        {
            "query": "Show me customers who spent more than $500",
            "category": "Medium (Dynamic Query)",
            "expected": "Filter customers by total spend"
        },
        
        # Aggressive/Complex queries - should definitely use dynamic queries
        {
            "query": "What's the median order value for each product category?",
            "category": "Aggressive (Dynamic Query)",
            "expected": "Group by category, calculate median"
        },
        {
            "query": "Find customers who bought more than 3 different products",
            "category": "Aggressive (Dynamic Query)",
            "expected": "Count distinct products per customer"
        },
        {
            "query": "Compare sales from weekdays vs weekends",
            "category": "Aggressive (Dynamic Query)",
            "expected": "Split by weekday/weekend and compare"
        },
        {
            "query": "Show me the top 3 customers for each product category",
            "category": "Very Aggressive (Dynamic Query)",
            "expected": "Group by category, rank customers, take top 3"
        },
    ]
    
    # Run tests
    results = []
    for i, test_case in enumerate(test_queries, 1):
        print("-" * 80)
        print(f"TEST {i}/{len(test_queries)}: {test_case['category']}")
        print(f"Query: \"{test_case['query']}\"")
        print(f"Expected: {test_case['expected']}")
        print()
        
        try:
            result = engine.query(test_case['query'], use_gpt_insights=False)
            
            if result['success']:
                print(f"✓ SUCCESS")
                print(f"   Dynamic Query: {result.get('dynamic_query', False)}")
                print(f"   AI Powered: {result.get('ai_powered', False)}")
                
                # Show answer preview
                answer_preview = result['answer'][:200]
                if len(result['answer']) > 200:
                    answer_preview += "..."
                print(f"   Answer: {answer_preview}")
                
                # Show executed code if available
                if result.get('code_executed'):
                    print(f"   Executed Code: {result['code_executed'][:100]}...")
                
                # Count data records returned
                if result.get('data'):
                    if isinstance(result['data'], list):
                        print(f"   Data Records: {len(result['data'])}")
                    elif isinstance(result['data'], dict):
                        print(f"   Data Fields: {len(result['data'])}")
                
                results.append({
                    'query': test_case['query'],
                    'status': 'SUCCESS',
                    'dynamic': result.get('dynamic_query', False)
                })
            else:
                print(f"✗ FAILED")
                print(f"   Error: {result.get('answer', 'Unknown error')}")
                results.append({
                    'query': test_case['query'],
                    'status': 'FAILED',
                    'dynamic': False
                })
        
        except Exception as e:
            print(f"✗ EXCEPTION: {str(e)}")
            results.append({
                'query': test_case['query'],
                'status': 'EXCEPTION',
                'dynamic': False
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    total_tests = len(results)
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    exceptions = sum(1 for r in results if r['status'] == 'EXCEPTION')
    dynamic_queries = sum(1 for r in results if r['dynamic'])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful} ({successful/total_tests*100:.1f}%)")
    print(f"Failed: {failed}")
    print(f"Exceptions: {exceptions}")
    print(f"Dynamic Queries Used: {dynamic_queries}")
    print()
    
    if successful == total_tests:
        print("🎉 ALL TESTS PASSED!")
    elif successful >= total_tests * 0.8:
        print("✓ Most tests passed - system is working well")
    else:
        print("⚠️  Several tests failed - check configuration")
    
    print()
    print("=" * 80)
    print("Note: Dynamic queries require OpenAI API key.")
    print("See DYNAMIC_AI_QUERIES.md for usage guide and examples.")
    print("=" * 80)


if __name__ == "__main__":
    test_dynamic_queries()

