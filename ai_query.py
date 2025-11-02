"""AI-powered natural language query system for sales data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import re
from datetime import datetime, timedelta

from sales_analysis import SalesAnalyzer
from customer_analysis import CustomerAnalyzer
from product_analysis import ProductAnalyzer
from rfm_analysis import RFMAnalyzer
from refill_prediction import RefillPredictor
from cross_sell_analysis import CrossSellAnalyzer

# Import OpenAI integration (optional)
try:
    from openai_integration import OpenAIAssistant
    OPENAI_ENABLED = True
except ImportError:
    OPENAI_ENABLED = False


class AIQueryEngine:
    """
    Natural language query engine for pharmacy sales data.
    
    Supports queries like:
    - "What are the top 10 products by revenue?"
    - "Show me customers at risk of churning"
    - "Which products are frequently bought together?"
    - "What is the average order value?"
    """
    
    def __init__(self, data: pd.DataFrame, use_openai: bool = True):
        """
        Initialize AI query engine.
        
        Args:
            data: Preprocessed sales DataFrame
            use_openai: Whether to use OpenAI for enhanced query interpretation
        """
        self.data = data
        self.sales_analyzer = SalesAnalyzer(data)
        self.customer_analyzer = CustomerAnalyzer(data)
        self.product_analyzer = ProductAnalyzer(data)
        self.rfm_analyzer = RFMAnalyzer(data)
        self.refill_predictor = RefillPredictor(data)
        self.cross_sell_analyzer = CrossSellAnalyzer(data)
        
        # Initialize OpenAI assistant if available and enabled
        self.openai_assistant = None
        self.openai_enabled = False
        if use_openai and OPENAI_ENABLED:
            try:
                self.openai_assistant = OpenAIAssistant(data)
                self.openai_enabled = self.openai_assistant.is_available
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI assistant: {e}")
        
        # Query patterns and their handlers (fallback system)
        self.query_patterns = self._initialize_query_patterns()
    
    def _initialize_query_patterns(self) -> List[Dict]:
        """Initialize regex patterns for different query types."""
        return [
            # Sales queries
            {
                'patterns': [
                    r'total\s+revenue',
                    r'how\s+much\s+(revenue|sales|money)',
                    r'sum\s+of\s+sales'
                ],
                'handler': self._handle_total_revenue,
                'type': 'sales'
            },
            {
                'patterns': [
                    r'top\s+(\d+)?\s*products',
                    r'best\s+selling\s+products',
                    r'most\s+popular\s+products'
                ],
                'handler': self._handle_top_products,
                'type': 'sales'
            },
            {
                'patterns': [
                    r'average\s+order\s+value',
                    r'avg\s+order',
                    r'mean\s+order\s+value'
                ],
                'handler': self._handle_avg_order_value,
                'type': 'sales'
            },
            {
                'patterns': [
                    r'sales\s+trend',
                    r'revenue\s+trend',
                    r'daily\s+sales',
                    r'monthly\s+sales'
                ],
                'handler': self._handle_sales_trends,
                'type': 'sales'
            },
            
            # Customer queries
            {
                'patterns': [
                    r'(best|top|high.?value)\s+customers?',
                    r'customers?\s+(by|with)\s+(highest|most)\s+(revenue|spend)',
                ],
                'handler': self._handle_top_customers,
                'type': 'customer'
            },
            {
                'patterns': [
                    r'churn(ing)?\s+customers?',
                    r'customers?\s+at\s+risk',
                    r'lost\s+customers?',
                    r'inactive\s+customers?'
                ],
                'handler': self._handle_churn_risk,
                'type': 'customer'
            },
            {
                'patterns': [
                    r'new\s+customers?',
                    r'recent\s+customers?',
                    r'customer\s+acquisition'
                ],
                'handler': self._handle_new_customers,
                'type': 'customer'
            },
            {
                'patterns': [
                    r'repeat\s+(rate|customers?)',
                    r'customer\s+retention',
                    r'loyal\s+customers?'
                ],
                'handler': self._handle_repeat_rate,
                'type': 'customer'
            },
            
            # Product queries
            {
                'patterns': [
                    r'fast\s+moving\s+products?',
                    r'products?\s+selling\s+quickly',
                    r'high\s+velocity\s+products?'
                ],
                'handler': self._handle_fast_movers,
                'type': 'product'
            },
            {
                'patterns': [
                    r'slow\s+moving\s+products?',
                    r'products?\s+not\s+selling',
                    r'low\s+velocity\s+products?'
                ],
                'handler': self._handle_slow_movers,
                'type': 'product'
            },
            {
                'patterns': [
                    r'inventory\s+(signals?|recommendations?)',
                    r'(what|which)\s+products?\s+to\s+(reorder|stock)',
                    r'stock\s+planning'
                ],
                'handler': self._handle_inventory_signals,
                'type': 'product'
            },
            
            # RFM queries
            {
                'patterns': [
                    r'rfm\s+(segmentation|analysis|segments?)',
                    r'customer\s+segments?',
                    r'segment\s+customers?'
                ],
                'handler': self._handle_rfm_segments,
                'type': 'rfm'
            },
            {
                'patterns': [
                    r'vip\s+customers?',
                    r'champions?',
                    r'most\s+valuable\s+customers?'
                ],
                'handler': self._handle_vip_customers,
                'type': 'rfm'
            },
            
            # Refill queries
            {
                'patterns': [
                    r'overdue\s+refills?',
                    r'customers?\s+need(ing)?\s+refills?',
                    r'late\s+refills?'
                ],
                'handler': self._handle_overdue_refills,
                'type': 'refill'
            },
            {
                'patterns': [
                    r'upcoming\s+refills?',
                    r'future\s+refills?',
                    r'refills?\s+due\s+soon'
                ],
                'handler': self._handle_upcoming_refills,
                'type': 'refill'
            },
            
            # Cross-sell queries
            {
                'patterns': [
                    r'(products?|items?)\s+(bought|purchased)\s+together',
                    r'product\s+(associations?|bundles?)',
                    r'cross.?sell',
                    r'complementary\s+products?'
                ],
                'handler': self._handle_cross_sell,
                'type': 'cross_sell'
            }
        ]
    
    def query(self, question: str, use_gpt_insights: bool = True) -> Dict[str, Any]:
        """
        Process a natural language query and return results.
        
        Uses OpenAI for query interpretation and insights if available,
        falls back to pattern matching otherwise.
        
        Args:
            question: Natural language question
            use_gpt_insights: Whether to use GPT for generating insights
            
        Returns:
            Dictionary containing answer, data, and visualization info
        """
        question_lower = question.lower().strip()
        
        # Try OpenAI interpretation first if available
        if self.openai_enabled:
            try:
                interpretation = self.openai_assistant.interpret_query(question)
                
                if interpretation.get('success'):
                    # Map OpenAI interpretation to our handlers
                    result = self._execute_interpreted_query(interpretation)
                    
                    if result.get('success') and use_gpt_insights:
                        # Enhance result with GPT-generated insights
                        gpt_insights = self.openai_assistant.generate_insight(
                            result, 
                            query_context=question
                        )
                        result['gpt_insights'] = gpt_insights
                        result['ai_powered'] = True
                        
                        # Get follow-up question suggestions
                        suggestions = self.openai_assistant.suggest_next_questions(
                            question, 
                            result
                        )
                        if suggestions:
                            result['suggestions'] = suggestions
                    
                    result['original_question'] = question
                    return result
            except Exception as e:
                print(f"OpenAI query processing failed, falling back to pattern matching: {e}")
        
        # Fallback to pattern matching
        for pattern_group in self.query_patterns:
            for pattern in pattern_group['patterns']:
                if re.search(pattern, question_lower):
                    try:
                        result = pattern_group['handler'](question_lower)
                        result['query_type'] = pattern_group['type']
                        result['original_question'] = question
                        result['ai_powered'] = False
                        return result
                    except Exception as e:
                        return {
                            'success': False,
                            'answer': f"Error processing query: {str(e)}",
                            'error': str(e),
                            'ai_powered': False
                        }
        
        # If no pattern matched, return helpful message
        return {
            'success': False,
            'answer': "I couldn't understand your question. Try asking about:\n" +
                     "- Sales metrics (e.g., 'total revenue', 'top products')\n" +
                     "- Customer insights (e.g., 'churning customers', 'top customers')\n" +
                     "- Product performance (e.g., 'fast moving products', 'inventory signals')\n" +
                     "- Refill predictions (e.g., 'overdue refills', 'upcoming refills')\n" +
                     "- Cross-sell opportunities (e.g., 'products bought together')",
            'suggestions': [
                "What is the total revenue?",
                "Show me the top 10 products",
                "Which customers are at risk of churning?",
                "What are the fast moving products?",
                "Show me overdue refills"
            ],
            'ai_powered': False
        }
    
    def _execute_interpreted_query(self, interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a query based on OpenAI interpretation.
        
        Args:
            interpretation: Query interpretation from OpenAI
            
        Returns:
            Query results
        """
        intent = interpretation.get('intent', '')
        action = interpretation.get('action', '')
        params = interpretation.get('parameters', {})
        
        # Map OpenAI intents to handler methods (comprehensive mapping)
        handler_map = {
            # Sales analysis
            'total_revenue': self._handle_total_revenue,
            'top_products': self._handle_top_products,
            'avg_order_value': self._handle_avg_order_value,
            'sales_trend': self._handle_sales_trends,
            'sales_trends': self._handle_sales_trends,
            'revenue_trend': self._handle_sales_trends,
            'daily_sales': self._handle_sales_trends,
            'monthly_sales': self._handle_sales_trends,
            'average_sales_per_day': self._handle_total_revenue,  # Uses daily avg
            
            # Customer analysis
            'top_customers': self._handle_top_customers,
            'best_customers': self._handle_top_customers,
            'high_value_customers': self._handle_top_customers,
            'churn_risk': self._handle_churn_risk,
            'churning_customers': self._handle_churn_risk,
            'at_risk_customers': self._handle_churn_risk,
            'repeat_rate': self._handle_repeat_rate,
            'frequent_buyers': self._handle_top_customers,  # Similar to top customers
            'search_customer': self._handle_customer_search,  # New handler
            'customer_details': self._handle_customer_search,
            
            # Product analysis
            'fast_moving_products': lambda q: self._handle_fast_moving_products(q),
            'fast_moving': lambda q: self._handle_fast_moving_products(q),
            'slow_moving_products': lambda q: self._handle_slow_moving_products(q),
            'slow_moving': lambda q: self._handle_slow_moving_products(q),
            'product_performance': self._handle_top_products,
            'best_selling': self._handle_top_products,
            
            # RFM analysis
            'rfm_segments': self._handle_rfm_segments,
            'customer_segments': self._handle_rfm_segments,
            'segmentation': self._handle_rfm_segments,
            'vip_customers': self._handle_vip_customers,
            'champions': self._handle_vip_customers,
            'loyal_customers': self._handle_vip_customers,
            
            # Refill prediction
            'overdue_refills': self._handle_overdue_refills,
            'upcoming_refills': self._handle_upcoming_refills,
            'refill_predictions': self._handle_overdue_refills,
            
            # Cross-sell
            'cross_sell': self._handle_cross_sell,
            'product_associations': self._handle_cross_sell,
            'products_bought_together': self._handle_cross_sell,
            'bundle_opportunities': self._handle_cross_sell,
        }
        
        # Try to find and execute the appropriate handler
        handler = handler_map.get(action)
        if handler:
            try:
                return handler("")  # Handlers don't actually use the question string
            except Exception as e:
                return {
                    'success': False,
                    'answer': f"Error executing query: {str(e)}",
                    'error': str(e)
                }
        
        # If no direct handler, try to infer from intent
        if intent and not handler:
            # Try using intent as the action
            handler = handler_map.get(intent)
            if handler:
                try:
                    return handler("")
                except Exception as e:
                    return {
                        'success': False,
                        'answer': f"Error executing query: {str(e)}",
                        'error': str(e)
                    }
        
        # No handler found - use GPT to generate a general response
        if self.openai_enabled and self.openai_assistant:
            try:
                # Generate a response using the interpretation
                response_text = f"Based on your question about {intent} - {action}:\n\n"
                
                # Try to provide some relevant general information
                if 'sales' in intent or 'revenue' in intent:
                    metrics = self.sales_analyzer.get_overall_metrics()
                    response_text += f"Total revenue: ${metrics['total_revenue']:,.2f}\n"
                    response_text += f"Average daily revenue: ${metrics['daily_avg_revenue']:,.2f}\n"
                elif 'customer' in intent:
                    top_customers = self.customer_analyzer.get_high_value_customers(10)
                    response_text += f"We have {len(self.data['customer_name'].unique())} unique customers.\n"
                    response_text += f"Top customers by spend:\n"
                    for _, row in top_customers.head(5).iterrows():
                        response_text += f"- {row['customer_name']}: ${row['total_spent']:,.2f}\n"
                elif 'product' in intent:
                    top_products = self.sales_analyzer.get_top_products(10, 'revenue')
                    response_text += f"Top selling products:\n"
                    for _, row in top_products.head(5).iterrows():
                        response_text += f"- {row['item_name']}: ${row['revenue']:,.2f}\n"
                
                return {
                    'success': True,
                    'answer': response_text,
                    'interpretation': interpretation,
                    'note': 'Generated general response based on query intent'
                }
            except:
                pass
        
        # Final fallback
        return {
            'success': False,
            'answer': f"I understood your intent ({intent}: {action}), but I don't have a specific handler for that yet. Try rephrasing your question or use the chat interface for more flexibility.",
            'interpretation': interpretation,
            'suggestions': [
                "What is the total revenue?",
                "Show me the top 10 products",
                "Which customers are at risk of churning?",
                "What are the fast moving products?"
            ]
        }
    
    # Sales handlers
    def _handle_total_revenue(self, question: str) -> Dict:
        """Handle total revenue queries."""
        metrics = self.sales_analyzer.get_overall_metrics()
        
        return {
            'success': True,
            'answer': (f"The total revenue is ${metrics['total_revenue']:,.2f} from "
                      f"{metrics['total_orders']:,} orders over {metrics['date_range_days']} days."),
            'data': metrics,
            'viz_type': 'metric',
            'recommendations': [
                f"Average daily revenue: ${metrics['daily_avg_revenue']:,.2f}",
                f"Average order value: ${metrics['avg_order_value']:,.2f}"
            ]
        }
    
    def _handle_top_products(self, question: str) -> Dict:
        """Handle top products queries."""
        # Extract number from question
        match = re.search(r'top\s+(\d+)', question)
        n = int(match.group(1)) if match else 10
        
        top_products = self.sales_analyzer.get_top_products(n, 'revenue')
        
        answer_text = f"Here are the top {len(top_products)} products by revenue:\n"
        for idx, row in top_products.head(5).iterrows():
            answer_text += f"- {row['item_name']}: ${row['revenue']:,.2f}\n"
        
        return {
            'success': True,
            'answer': answer_text,
            'data': top_products.to_dict('records'),
            'viz_type': 'bar_chart',
            'viz_config': {
                'x': 'item_name',
                'y': 'revenue',
                'title': f'Top {n} Products by Revenue'
            }
        }
    
    def _handle_avg_order_value(self, question: str) -> Dict:
        """Handle average order value queries."""
        metrics = self.sales_analyzer.get_overall_metrics()
        
        return {
            'success': True,
            'answer': (f"The average order value is ${metrics['avg_order_value']:,.2f}. "
                      f"Customers typically buy {metrics['avg_items_per_order']:.1f} items per order."),
            'data': {
                'avg_order_value': metrics['avg_order_value'],
                'avg_items_per_order': metrics['avg_items_per_order']
            },
            'viz_type': 'metric'
        }
    
    def _handle_sales_trends(self, question: str) -> Dict:
        """Handle sales trend queries."""
        # Determine period from question
        if 'daily' in question or 'day' in question:
            trends = self.sales_analyzer.get_daily_trends()
            period = 'daily'
        elif 'weekly' in question or 'week' in question:
            trends = self.sales_analyzer.get_weekly_trends()
            period = 'weekly'
        else:
            trends = self.sales_analyzer.get_monthly_trends()
            period = 'monthly'
        
        # Calculate trend direction
        recent_avg = trends.tail(5)['revenue'].mean()
        earlier_avg = trends.head(5)['revenue'].mean()
        trend_direction = "increasing" if recent_avg > earlier_avg else "decreasing"
        change_pct = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
        
        return {
            'success': True,
            'answer': (f"The {period} revenue trend is {trend_direction} "
                      f"({abs(change_pct):.1f}% {'increase' if change_pct > 0 else 'decrease'} recently)."),
            'data': trends.to_dict('records'),
            'viz_type': 'line_chart',
            'viz_config': {
                'x': list(trends.columns)[0],  # Date column
                'y': 'revenue',
                'title': f'{period.capitalize()} Revenue Trend'
            }
        }
    
    # Customer handlers
    def _handle_top_customers(self, question: str) -> Dict:
        """Handle top customers queries."""
        match = re.search(r'(\d+)', question)
        n = int(match.group(1)) if match else 20
        
        top_customers = self.customer_analyzer.get_high_value_customers(n)
        
        answer_text = f"Here are the top {len(top_customers)} customers by spending:\n"
        for idx, row in top_customers.head(5).iterrows():
            answer_text += (f"- {row['customer_name']}: ${row['total_spent']:,.2f} "
                           f"({row['total_orders']} orders)\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': top_customers.to_dict('records'),
            'viz_type': 'table'
        }
    
    def _handle_churn_risk(self, question: str) -> Dict:
        """Handle churn risk queries."""
        churn_customers = self.customer_analyzer.get_churn_risk_customers(90)
        
        if len(churn_customers) == 0:
            return {
                'success': True,
                'answer': "Great news! No customers are currently at risk of churning.",
                'data': [],
                'viz_type': 'metric'
            }
        
        # Calculate total value at risk
        total_value = churn_customers['total_spent'].sum()
        
        answer_text = (f"Warning: {len(churn_customers)} customers are at risk of churning, "
                      f"representing ${total_value:,.2f} in customer value.\n\n"
                      f"Top at-risk customers:\n")
        
        for idx, row in churn_customers.head(5).iterrows():
            answer_text += (f"- {row['customer_name']}: ${row['total_spent']:,.2f} "
                           f"(inactive for {row['days_since_last_purchase']} days)\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': churn_customers.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Reach out to these customers with personalized offers",
                "Send re-engagement campaigns",
                "Offer loyalty rewards or discounts"
            ]
        }
    
    def _handle_new_customers(self, question: str) -> Dict:
        """Handle new customers queries."""
        match = re.search(r'(\d+)\s+days?', question)
        days = int(match.group(1)) if match else 30
        
        new_customers = self.customer_analyzer.get_new_customers(days)
        
        answer_text = f"You acquired {len(new_customers)} new customers in the last {days} days."
        
        if len(new_customers) > 0:
            avg_spend = new_customers['total_spent'].mean()
            answer_text += f"\n\nAverage spending by new customers: ${avg_spend:,.2f}"
        
        return {
            'success': True,
            'answer': answer_text,
            'data': new_customers.to_dict('records'),
            'viz_type': 'table'
        }
    
    def _handle_repeat_rate(self, question: str) -> Dict:
        """Handle repeat rate queries."""
        metrics = self.customer_analyzer.get_repeat_purchase_rate()
        
        answer_text = (f"Customer retention metrics:\n"
                      f"- Repeat purchase rate: {metrics['repeat_rate_pct']:.1f}%\n"
                      f"- Repeat customers: {metrics['repeat_customers']:,}\n"
                      f"- One-time customers: {metrics['one_time_customers']:,}\n"
                      f"- Average orders per customer: {metrics['avg_orders_per_customer']:.2f}")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': metrics,
            'viz_type': 'metric'
        }
    
    # Product handlers
    def _handle_fast_movers(self, question: str) -> Dict:
        """Handle fast-moving products queries."""
        fast_movers = self.product_analyzer.get_fast_moving_products(15)
        
        answer_text = f"Top {len(fast_movers)} fast-moving products:\n"
        for idx, row in fast_movers.head(5).iterrows():
            answer_text += f"- {row['item_name']}: {row['sales_velocity']:.2f} units/day\n"
        
        return {
            'success': True,
            'answer': answer_text,
            'data': fast_movers.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Ensure adequate stock levels for these items",
                "Consider increasing inventory for fast movers",
                "Monitor for potential stockouts"
            ]
        }
    
    def _handle_slow_movers(self, question: str) -> Dict:
        """Handle slow-moving products queries."""
        slow_movers = self.product_analyzer.get_slow_moving_products(15)
        
        answer_text = f"Top {len(slow_movers)} slow-moving products:\n"
        for idx, row in slow_movers.head(5).iterrows():
            answer_text += (f"- {row['item_name']}: {row['sales_velocity']:.2f} units/day "
                           f"({row['days_since_last_sale']} days since last sale)\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': slow_movers.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Consider discounts or promotions for slow movers",
                "Review if these products should be discontinued",
                "Reduce order quantities for these items"
            ]
        }
    
    def _handle_inventory_signals(self, question: str) -> Dict:
        """Handle inventory planning queries."""
        signals = self.product_analyzer.get_inventory_planning_signals()
        
        # Count by signal type
        signal_counts = signals['inventory_signal'].value_counts().to_dict()
        
        answer_text = "Inventory planning signals:\n"
        for signal, count in signal_counts.items():
            answer_text += f"- {signal}: {count} products\n"
        
        # Highlight urgent items
        urgent = signals[signals['inventory_signal'].str.contains('Reorder - High')]
        if len(urgent) > 0:
            answer_text += f"\n⚠️ Urgent: {len(urgent)} products need immediate reordering!"
        
        return {
            'success': True,
            'answer': answer_text,
            'data': signals.to_dict('records'),
            'viz_type': 'table'
        }
    
    # RFM handlers
    def _handle_rfm_segments(self, question: str) -> Dict:
        """Handle RFM segmentation queries."""
        self.rfm_analyzer.segment_customers()
        segment_summary = self.rfm_analyzer.get_segment_summary()
        
        answer_text = "Customer segment distribution:\n"
        for _, row in segment_summary.iterrows():
            answer_text += (f"- {row['segment']}: {row['customer_count']} customers "
                           f"({row['revenue_pct']:.1f}% of revenue)\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': segment_summary.to_dict('records'),
            'viz_type': 'table'
        }
    
    def _handle_vip_customers(self, question: str) -> Dict:
        """Handle VIP customers queries."""
        self.rfm_analyzer.segment_customers()
        vip_customers = self.rfm_analyzer.get_vip_customers(20)
        
        answer_text = f"You have {len(vip_customers)} VIP customers:\n"
        for idx, row in vip_customers.head(5).iterrows():
            answer_text += (f"- {row['customer_name']} ({row['segment']}): "
                           f"${row['monetary']:,.2f}, {row['frequency']} orders\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': vip_customers.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Provide VIP treatment and exclusive offers",
                "Request testimonials and referrals",
                "Maintain regular communication"
            ]
        }
    
    # Refill handlers
    def _handle_customer_search(self, question: str) -> Dict:
        """Handle customer search/lookup queries."""
        # Try to find customer name in the question
        import re
        matches = re.findall(r'\b([A-Z][A-Z]+)\b', question)
        
        if not matches:
            # Return top customers if no specific name found
            return self._handle_top_customers(question)
        
        customer_name = matches[0]
        customer_data = self.data[self.data['customer_name'].str.contains(customer_name, case=False, na=False)]
        
        if len(customer_data) == 0:
            return {
                'success': False,
                'answer': f"No data found for customer '{customer_name}'. Try checking the spelling or use 'top customers' to see all customers."
            }
        
        # Calculate customer metrics
        total_spent = customer_data['total'].sum()
        total_orders = customer_data['order_id'].nunique()
        total_items = len(customer_data)
        first_purchase = customer_data['date'].min()
        last_purchase = customer_data['date'].max()
        
        # Get top items
        top_items = customer_data.groupby('item_name')['total'].sum().sort_values(ascending=False).head(5)
        
        answer_text = f"**Customer: {customer_name}**\n\n"
        answer_text += f"Total Spent: ${total_spent:,.2f}\n"
        answer_text += f"Total Orders: {total_orders}\n"
        answer_text += f"Total Items: {total_items}\n"
        answer_text += f"First Purchase: {first_purchase.strftime('%Y-%m-%d')}\n"
        answer_text += f"Last Purchase: {last_purchase.strftime('%Y-%m-%d')}\n\n"
        answer_text += "**Top 5 Products:**\n"
        for item, amount in top_items.items():
            answer_text += f"- {item}: ${amount:,.2f}\n"
        
        return {
            'success': True,
            'answer': answer_text,
            'data': customer_data.to_dict('records'),
            'viz_type': 'customer_profile'
        }
    
    def _handle_upcoming_refills(self, question: str) -> Dict:
        """Handle upcoming refills queries."""
        self.refill_predictor.calculate_purchase_intervals()
        upcoming = self.refill_predictor.get_upcoming_refills(30)
        
        if len(upcoming) == 0:
            return {
                'success': True,
                'answer': "No refills expected in the next 30 days.",
                'data': [],
                'viz_type': 'metric'
            }
        
        answer_text = f"📅 {len(upcoming)} upcoming refills in the next 30 days:\n"
        for idx, row in upcoming.head(5).iterrows():
            answer_text += (f"- {row['customer_name']} - {row['item_name']}: "
                           f"expected in {row['days_until_predicted']} days\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': upcoming.to_dict('records'),
            'viz_type': 'table'
        }
    
    def _handle_overdue_refills(self, question: str) -> Dict:
        """Handle overdue refills queries."""
        self.refill_predictor.calculate_purchase_intervals()
        overdue = self.refill_predictor.get_overdue_refills(7)
        
        if len(overdue) == 0:
            return {
                'success': True,
                'answer': "No overdue refills detected!",
                'data': [],
                'viz_type': 'metric'
            }
        
        answer_text = f"⚠️ {len(overdue)} overdue refills detected:\n"
        for idx, row in overdue.head(5).iterrows():
            answer_text += (f"- {row['customer_name']} - {row['item_name']}: "
                           f"{row['days_overdue']} days overdue\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': overdue.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Contact these customers for refill reminders",
                "Offer convenient ordering options",
                "Check if customers switched to competitors"
            ]
        }
    
    def _handle_upcoming_refills(self, question: str) -> Dict:
        """Handle upcoming refills queries."""
        match = re.search(r'(\d+)\s+days?', question)
        days = int(match.group(1)) if match else 30
        
        self.refill_predictor.calculate_purchase_intervals()
        upcoming = self.refill_predictor.get_upcoming_refills(days)
        
        answer_text = f"{len(upcoming)} refills expected in the next {days} days"
        
        if len(upcoming) > 0:
            # Group by week
            upcoming_copy = upcoming.copy()
            upcoming_copy['week'] = pd.to_datetime(upcoming_copy['predicted_next_purchase']).dt.isocalendar().week
            weekly_counts = upcoming_copy['week'].value_counts().sort_index()
            answer_text += f"\n\nWeekly breakdown available in data."
        
        return {
            'success': True,
            'answer': answer_text,
            'data': upcoming.to_dict('records'),
            'viz_type': 'table'
        }
    
    # Cross-sell handlers
    def _handle_cross_sell(self, question: str) -> Dict:
        """Handle cross-sell queries."""
        affinity = self.cross_sell_analyzer.analyze_product_affinity()
        
        if len(affinity) == 0:
            return {
                'success': True,
                'answer': "Not enough data to identify cross-sell patterns yet.",
                'data': [],
                'viz_type': 'metric'
            }
        
        answer_text = f"Top product associations (frequently bought together):\n"
        for idx, row in affinity.head(5).iterrows():
            answer_text += (f"- {row['product_a']} + {row['product_b']}: "
                           f"{row['lift']:.2f}x more likely together\n")
        
        return {
            'success': True,
            'answer': answer_text,
            'data': affinity.to_dict('records'),
            'viz_type': 'table',
            'recommendations': [
                "Create product bundles based on these associations",
                "Place associated products near each other",
                "Offer cross-sell recommendations at checkout"
            ]
        }
    
    def get_insights(self) -> List[str]:
        """Generate automatic insights from the data."""
        insights = []
        
        try:
            # Sales insights
            metrics = self.sales_analyzer.get_overall_metrics()
            growth = self.sales_analyzer.get_growth_analysis()
            
            if growth['revenue_growth_pct'] > 10:
                insights.append(f"📈 Revenue is growing strongly ({growth['revenue_growth_pct']:.1f}% increase)")
            elif growth['revenue_growth_pct'] < -10:
                insights.append(f"📉 Revenue is declining ({abs(growth['revenue_growth_pct']):.1f}% decrease)")
            
            # Customer insights
            churn_risk = self.customer_analyzer.get_churn_risk_customers(90)
            if len(churn_risk) > 0:
                insights.append(f"⚠️ {len(churn_risk)} customers at risk of churning")
            
            # Product insights
            slow_movers = self.product_analyzer.get_slow_moving_products(10)
            if len(slow_movers) > 0:
                insights.append(f"🐌 {len(slow_movers)} slow-moving products need attention")
            
            # Refill insights
            self.refill_predictor.calculate_purchase_intervals()
            overdue = self.refill_predictor.get_overdue_refills(7)
            if len(overdue) > 0:
                insights.append(f"💊 {len(overdue)} customers have overdue refills")
            
        except Exception as e:
            insights.append(f"Error generating insights: {str(e)}")
        
        return insights


def create_query_examples() -> List[str]:
    """Get example queries that users can try."""
    return [
        "What is the total revenue?",
        "Show me the top 10 products",
        "Which customers are at risk of churning?",
        "What are the fast moving products?",
        "Show me overdue refills",
        "What is the average order value?",
        "Show me new customers from the last 30 days",
        "Which products are bought together?",
        "What are the VIP customers?",
        "Show me inventory signals",
        "What is the repeat purchase rate?",
        "Show me sales trends",
        "Which products are slow moving?",
        "Show me RFM segments",
        "What are the upcoming refills?"
    ]

