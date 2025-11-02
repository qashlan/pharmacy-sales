#!/usr/bin/env python3
"""
Test pharmaceutical analytical queries.

Demonstrates the system's ability to handle sophisticated
pharmaceutical business intelligence questions.
"""

from data_loader import DataLoader, load_sample_data
from ai_query import AIQueryEngine
import config

def test_pharmaceutical_queries():
    """Test pharmaceutical-specific analytical queries."""
    
    print("=" * 80)
    print("PHARMACEUTICAL ANALYSIS QUERIES - DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Load sample data
    print("Loading sample data...")
    sample_df = load_sample_data()
    loader = DataLoader(None)
    loader.raw_data = sample_df
    data = loader.preprocess_data()
    print(f"✓ Loaded {len(data)} records")
    print(f"✓ Products in dataset: {data['item_name'].nunique()}")
    print(f"✓ Date range: {data['date'].min().date()} to {data['date'].max().date()}")
    print()
    
    # Initialize AI query engine
    print("Initializing AI Query Engine...")
    engine = AIQueryEngine(data, use_openai=True)
    
    if not engine.openai_enabled:
        print("⚠️  OpenAI is not enabled.")
        print("   These pharmaceutical queries require OpenAI API key.")
        print("   Please set OPENAI_API_KEY in config.py or environment variables.")
        print()
        print("   However, you can still use these queries in the dashboard once configured!")
        return
    
    print(f"✓ AI Query Engine initialized (OpenAI: Enabled)")
    print()
    
    # Pharmaceutical analytical queries
    pharma_queries = [
        {
            "query": "Are there specific times of year when Amoxicillin sales peak?",
            "category": "Seasonal Trend Analysis",
            "description": "Identifies peak sales periods for antibiotic"
        },
        {
            "query": "Which customers buy multiple pain relief medications together?",
            "category": "Product Correlation",
            "description": "Finds customers purchasing related medications"
        },
        {
            "query": "Show me monthly sales trends for all antibiotics",
            "category": "Category Trend Analysis",
            "description": "Analyzes antibiotic category over time"
        },
        {
            "query": "Compare diabetes medication sales in different seasons",
            "category": "Seasonal Comparison",
            "description": "Compares seasonal patterns for chronic medications"
        },
        {
            "query": "Which customers show regular monthly purchase patterns for cardiovascular medications?",
            "category": "Adherence Analysis",
            "description": "Identifies consistent medication users"
        },
        {
            "query": "Do customers who buy Metformin also purchase other diabetes-related products?",
            "category": "Co-Purchase Analysis",
            "description": "Analyzes medication combinations"
        },
        {
            "query": "What's the average time between purchases for customers buying insulin?",
            "category": "Refill Pattern Analysis",
            "description": "Calculates refill frequency"
        },
        {
            "query": "Show me the top 5 products by revenue in each therapeutic category",
            "category": "Category Performance",
            "description": "Ranks products within categories"
        },
    ]
    
    print("-" * 80)
    print("TESTING PHARMACEUTICAL ANALYTICAL QUERIES")
    print("-" * 80)
    print()
    print("These are the types of sophisticated questions you can ask:")
    print()
    
    # Display queries without actually running them (to avoid API costs during demo)
    for i, query_info in enumerate(pharma_queries, 1):
        print(f"{i}. {query_info['category']}")
        print(f"   Query: \"{query_info['query']}\"")
        print(f"   Purpose: {query_info['description']}")
        print()
    
    print("-" * 80)
    print()
    
    # Ask user if they want to run actual tests
    print("Would you like to run these queries? (This will use OpenAI API)")
    print()
    response = input("Run tests? (y/n): ").lower().strip()
    
    if response != 'y':
        print()
        print("Skipping actual execution.")
        print("To run these queries, use the dashboard AI Query interface!")
        print()
        demo_mode()
        return
    
    print()
    print("=" * 80)
    print("RUNNING QUERIES")
    print("=" * 80)
    print()
    
    # Run selected queries
    selected_queries = pharma_queries[:3]  # Run first 3 to save API costs
    
    for i, query_info in enumerate(selected_queries, 1):
        print("-" * 80)
        print(f"TEST {i}/{len(selected_queries)}: {query_info['category']}")
        print(f"Query: \"{query_info['query']}\"")
        print()
        
        try:
            result = engine.query(query_info['query'], use_gpt_insights=False)
            
            if result['success']:
                print("✓ SUCCESS")
                print()
                
                # Show answer
                answer_lines = result['answer'].split('\n')[:5]  # First 5 lines
                print("Answer Preview:")
                for line in answer_lines:
                    print(f"  {line}")
                if len(result['answer'].split('\n')) > 5:
                    print("  ...")
                print()
                
                # Show code if available
                if result.get('code_executed'):
                    print("Generated Code:")
                    print(f"  {result['code_executed'][:150]}...")
                    print()
                
                # Show data summary
                if result.get('data'):
                    if isinstance(result['data'], list) and len(result['data']) > 0:
                        print(f"Data returned: {len(result['data'])} records")
                    elif isinstance(result['data'], dict):
                        print(f"Data returned: {len(result['data'])} fields")
                print()
            else:
                print("✗ FAILED")
                print(f"Error: {result.get('answer', 'Unknown error')[:200]}")
                print()
        
        except Exception as e:
            print(f"✗ EXCEPTION: {str(e)}")
            print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("These queries showcase the system's pharmaceutical analysis capabilities.")
    print("You can ask similar questions in the dashboard AI Query interface!")
    print()


def demo_mode():
    """Demonstrate what the queries would produce."""
    print("=" * 80)
    print("DEMO MODE - Example Results")
    print("=" * 80)
    print()
    
    print("📊 Example 1: Seasonal Peak Analysis")
    print("-" * 80)
    print('Query: "Are there specific times of year when Amoxicillin sales peak?"')
    print()
    print("Expected Result:")
    print("""
    Month    Revenue    Quantity    Peak_Indicator
    Jan      $2,450     245         Medium
    Feb      $3,890     389         High ← Winter Peak
    Mar      $3,200     320         High
    Apr      $2,100     210         Low
    ...
    Oct      $3,500     350         High ← Fall Peak
    Nov      $3,800     380         High
    Dec      $2,900     290         Medium
    
    Analysis: Amoxicillin sales peak during winter months (Feb-Mar) and 
    fall season (Oct-Nov), correlating with cold and flu season.
    """)
    print()
    
    print("📊 Example 2: Customer Correlation Analysis")
    print("-" * 80)
    print('Query: "Which customers buy multiple pain relief medications together?"')
    print()
    print("Expected Result:")
    print("""
    Customer          Products_Bought              Total_Spent
    Customer_15       Paracetamol, Aspirin         $245.50
    Customer_23       Aspirin, Ibuprofen           $198.30
    Customer_42       Paracetamol, Aspirin, Other  $312.80
    ...
    
    Analysis: 15% of customers purchase multiple pain relief products,
    indicating either preference comparison or different use cases.
    """)
    print()
    
    print("📊 Example 3: Therapeutic Category Trends")
    print("-" * 80)
    print('Query: "Show me monthly sales trends for all antibiotics"')
    print()
    print("Expected Result:")
    print("""
    Month    Amoxicillin    Azithromycin    Total_Category    Growth_Rate
    Jan      $2,450         $1,200          $3,650           +5%
    Feb      $3,890         $1,800          $5,690           +56%
    Mar      $3,200         $1,600          $4,800           -16%
    ...
    
    Analysis: Antibiotic sales show clear seasonal pattern with peaks
    during winter and fall months, typical of respiratory infection seasons.
    """)
    print()
    
    print("=" * 80)
    print()
    print("💡 These are just examples! The actual system will:")
    print("   1. Analyze YOUR real data")
    print("   2. Generate appropriate pandas code")
    print("   3. Execute it safely")
    print("   4. Return actual results")
    print()
    print("🚀 Try it yourself in the dashboard!")
    print()


def show_examples():
    """Show example queries users can try."""
    print("=" * 80)
    print("EXAMPLE PHARMACEUTICAL QUERIES TO TRY")
    print("=" * 80)
    print()
    
    examples = {
        "Seasonal Analysis": [
            "When do respiratory medication sales peak during the year?",
            "Show me quarterly trends for pain relief medications",
            "Are there monthly patterns in vitamin sales?",
            "Compare antibiotic sales across all seasons",
        ],
        "Customer Insights": [
            "Which customers buy multiple diabetes medications?",
            "Show me customers with regular cardiovascular medication purchases",
            "Find customers who buy both pain relief and anti-inflammatory drugs",
            "Which customers show chronic medication purchase patterns?",
        ],
        "Product Correlations": [
            "What products are commonly purchased together with insulin?",
            "Do customers who buy Metformin also purchase other diabetes products?",
            "Show me medication combinations that appear frequently",
            "Which products have the strongest purchase correlation?",
        ],
        "Trend Analysis": [
            "What's the growth rate for antibiotic sales over the last 6 months?",
            "Show me the month-over-month change in pain medication sales",
            "Are cardiovascular medication sales increasing or decreasing?",
            "Compare this year's allergy medication sales to last year",
        ],
        "Advanced Analytics": [
            "Calculate the average refill frequency for chronic medications",
            "Show me the standard deviation in purchase quantities by product category",
            "Which customers have irregular refill patterns?",
            "Identify customers whose medication needs are escalating",
        ]
    }
    
    for category, queries in examples.items():
        print(f"📌 {category}")
        print("-" * 80)
        for query in queries:
            print(f"   • {query}")
        print()
    
    print("=" * 80)
    print()
    print("💡 Copy any of these questions and paste them into the")
    print("   AI Query interface in the dashboard!")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_examples()
    else:
        test_pharmaceutical_queries()

