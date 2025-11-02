"""OpenAI GPT integration for intelligent query interpretation and insights generation."""

import os
import json
import re
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import config

# Try to import OpenAI, but make it optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class OpenAIAssistant:
    """
    OpenAI-powered assistant for pharmacy sales analytics.
    
    Features:
    - Interprets natural language queries
    - Generates insights from data analysis results
    - Provides recommendations in natural language
    - Supports conversation context
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize OpenAI assistant.
        
        Args:
            data: Preprocessed sales DataFrame
        """
        self.data = data
        self.client = None
        self.is_available = False
        self.model = "gpt-4o-mini"  # Cost-effective model for most tasks
        
        # Initialize OpenAI client if API key is available
        self._initialize_client()
        
        # Conversation history
        self.conversation_history = []
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key."""
        api_key = config.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
        
        if not OPENAI_AVAILABLE:
            print("⚠️  OpenAI library not installed. Install with: pip install openai")
            return
        
        if not api_key:
            print("⚠️  OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            return
        
        try:
            # Initialize OpenAI client - compatible with v1.x
            # Only pass api_key parameter (v1.x doesn't support proxies in __init__)
            self.client = OpenAI(api_key=api_key)
            
            # Test the connection with a simple call
            try:
                self.client.models.list()
            except AttributeError:
                # Fallback for older OpenAI v1.x versions
                pass
            
            self.is_available = True
            print("✅ OpenAI integration enabled")
        except TypeError as e:
            if 'proxies' in str(e):
                print(f"⚠️  OpenAI version incompatibility detected. Please reinstall:")
                print(f"    pip uninstall openai")
                print(f"    pip install 'openai>=1.6.1,<2.0.0'")
            else:
                print(f"⚠️  OpenAI initialization failed: {str(e)}")
            self.is_available = False
        except Exception as e:
            print(f"⚠️  OpenAI initialization failed: {str(e)}")
            self.is_available = False
    
    def get_data_context(self) -> str:
        """Generate a summary of the dataset for GPT context."""
        try:
            total_records = len(self.data)
            date_range = (self.data['date'].min(), self.data['date'].max())
            unique_customers = self.data['customer_name'].nunique()
            unique_products = self.data['item_name'].nunique()
            total_revenue = self.data['total'].sum()
            unique_orders = self.data['order_id'].nunique()
            
            context = f"""
Dataset Summary:
- Total Records: {total_records:,}
- Date Range: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}
- Unique Customers: {unique_customers:,}
- Unique Products: {unique_products:,}
- Total Revenue: ${total_revenue:,.2f}
- Total Orders: {unique_orders:,}

Available Columns: {', '.join(self.data.columns.tolist())}

Top 5 Products by Revenue:
{self.data.groupby('item_name')['total'].sum().sort_values(ascending=False).head().to_string()}

Top 5 Customers by Spend:
{self.data.groupby('customer_name')['total'].sum().sort_values(ascending=False).head().to_string()}
"""
            return context
        except Exception as e:
            return f"Error generating context: {str(e)}"
    
    def interpret_query(self, user_query: str) -> Dict[str, Any]:
        """
        Use GPT to interpret a natural language query and determine the intent.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary with query interpretation including intent, parameters, and suggested action
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'OpenAI not available',
                'fallback': True
            }
        
        system_prompt = f"""You are an AI assistant for a pharmacy sales analytics system.

Your role is to interpret user queries about sales data and determine what analysis should be performed.

{self.get_data_context()}

For each query, respond with a JSON object containing:
- "intent": The type of analysis (e.g., "sales_analysis", "customer_analysis", "product_analysis", "rfm_segmentation", "refill_prediction", "cross_sell_analysis")
- "action": Specific action to take (e.g., "top_products", "churn_risk", "revenue_trend")
- "parameters": Any parameters for the analysis (e.g., limit, threshold, date_range)
- "confidence": How confident you are in this interpretation (0-1)
- "clarification": If the query is unclear, suggest clarification questions

Available analysis types:
1. Sales Analysis: revenue trends, anomaly detection, top products, sales by category
2. Customer Analysis: churn risk, high-value customers, frequent buyers, new customers
3. Product Analysis: fast/slow-moving products, ABC classification, lifecycle stages
4. RFM Segmentation: customer segments (Champions, Loyal, At-Risk, etc.)
5. Refill Prediction: overdue refills, upcoming refills, refill patterns
6. Cross-Sell Analysis: product associations, recommendations, bundles

Respond ONLY with valid JSON, no additional text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            interpretation = json.loads(response.choices[0].message.content)
            interpretation['success'] = True
            interpretation['raw_query'] = user_query
            
            return interpretation
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback': True,
                'raw_query': user_query
            }
    
    def generate_insight(self, analysis_result: Dict[str, Any], query_context: str = "") -> str:
        """
        Generate natural language insights from analysis results using GPT.
        
        Args:
            analysis_result: Results from data analysis
            query_context: Original query context
            
        Returns:
            Natural language explanation of the insights
        """
        if not self.is_available:
            return "OpenAI not available for insight generation."
        
        # Prepare result summary for GPT
        result_summary = self._prepare_result_summary(analysis_result)
        
        system_prompt = """You are an expert pharmacy business analyst.

Generate clear, actionable insights from the analysis results.

Guidelines:
- Be concise but informative
- Highlight key findings and trends
- Provide specific recommendations when relevant
- Use business-friendly language
- Include numbers and percentages to support insights
- Structure insights with bullet points or short paragraphs
- Focus on actionable information

Format your response as:
**Key Insights:**
- [Insight 1]
- [Insight 2]
...

**Recommendations:**
- [Recommendation 1]
- [Recommendation 2]
..."""

        user_message = f"""Query: {query_context}

Analysis Results:
{result_summary}

Provide insights and recommendations based on these results."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def _prepare_result_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Convert analysis results to a text summary for GPT."""
        summary_parts = []
        
        for key, value in analysis_result.items():
            if isinstance(value, pd.DataFrame):
                # Summarize dataframe
                summary_parts.append(f"\n{key}:")
                summary_parts.append(value.head(10).to_string())
            elif isinstance(value, (list, dict)):
                summary_parts.append(f"\n{key}: {json.dumps(value, default=str, indent=2)}")
            else:
                summary_parts.append(f"{key}: {value}")
        
        return "\n".join(summary_parts)
    
    def _query_customer_data(self, customer_name: str) -> str:
        """Query specific customer data from the dataset."""
        try:
            # Case-insensitive search
            customer_data = self.data[self.data['customer_name'].str.contains(customer_name, case=False, na=False)]
            
            if len(customer_data) == 0:
                return f"No data found for customer '{customer_name}'."
            
            # Get customer summary
            total_spent = customer_data['total'].sum()
            total_orders = customer_data['order_id'].nunique()
            items_purchased = customer_data.groupby('item_name')['quantity'].sum().sort_values(ascending=False)
            
            summary = f"\n**Customer: {customer_name}**\n"
            summary += f"- Total Spent: ${total_spent:,.2f}\n"
            summary += f"- Total Orders: {total_orders}\n"
            summary += f"- Total Items: {len(customer_data)}\n\n"
            summary += "**Items Purchased:**\n"
            
            for item, qty in items_purchased.head(20).items():
                item_data = customer_data[customer_data['item_name'] == item]
                total_price = item_data['total'].sum()
                summary += f"- {item}: {int(qty)} units (${total_price:.2f})\n"
            
            if len(items_purchased) > 20:
                summary += f"\n... and {len(items_purchased) - 20} more items"
            
            return summary
        except Exception as e:
            return f"Error querying customer data: {str(e)}"
    
    def _query_product_data(self, product_name: str) -> str:
        """Query specific product data from the dataset."""
        try:
            # Case-insensitive search
            product_data = self.data[self.data['item_name'].str.contains(product_name, case=False, na=False)]
            
            if len(product_data) == 0:
                return f"No data found for product '{product_name}'."
            
            # Get product summary
            total_revenue = product_data['total'].sum()
            total_quantity = product_data['quantity'].sum()
            total_customers = product_data['customer_name'].nunique()
            avg_price = product_data['selling_price'].mean()
            
            summary = f"\n**Product: {product_name}**\n"
            summary += f"- Total Revenue: ${total_revenue:,.2f}\n"
            summary += f"- Total Quantity Sold: {int(total_quantity)}\n"
            summary += f"- Unique Customers: {total_customers}\n"
            summary += f"- Average Price: ${avg_price:.2f}\n\n"
            summary += "**Top Customers:**\n"
            
            top_customers = product_data.groupby('customer_name')['total'].sum().sort_values(ascending=False).head(10)
            for customer, spent in top_customers.items():
                summary += f"- {customer}: ${spent:.2f}\n"
            
            return summary
        except Exception as e:
            return f"Error querying product data: {str(e)}"
    
    def chat(self, user_message: str, include_context: bool = True) -> str:
        """
        Have a conversation with GPT about the sales data.
        
        Args:
            user_message: User's message
            include_context: Whether to include data context
            
        Returns:
            GPT's response
        """
        if not self.is_available:
            return "OpenAI chat is not available. Please check your API key."
        
        # Check if user is asking about specific customer or product
        additional_data = ""
        user_lower = user_message.lower()
        
        # Extract customer name if asking about specific customer
        if any(word in user_lower for word in ['customer', 'purchased', 'bought', 'buy']):
            # Try to extract customer name (common pattern: asking about "CUSTOMER_NAME")
            # Look for capitalized words or quoted names
            matches = re.findall(r'\b([A-Z][A-Z]+)\b', user_message)
            if matches:
                customer_name = matches[0]
                additional_data += self._query_customer_data(customer_name)
        
        # Extract product name if asking about specific product
        if any(word in user_lower for word in ['product', 'item', 'medicine', 'drug']):
            # Try to extract product name
            matches = re.findall(r'(?:product|item|medicine)\s+["\']?([^"\'?\n]+)["\']?', user_message, re.IGNORECASE)
            if matches:
                product_name = matches[0].strip()
                additional_data += self._query_product_data(product_name)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful pharmacy sales analytics assistant with access to real sales data.

You help users understand their sales data and make data-driven decisions.

{self.get_data_context() if include_context else ''}

When users ask about specific customers or products, I will provide you with the actual data from the database.

Be friendly, professional, and provide specific insights based on the actual data provided."""
            }
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history[-6:])  # Keep last 3 exchanges
        
        # Add current message with any queried data
        user_content = user_message
        if additional_data:
            user_content += f"\n\n**Queried Data:**\n{additional_data}"
        
        messages.append({"role": "user", "content": user_content})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1200
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def suggest_next_questions(self, current_query: str, results: Optional[Dict] = None) -> List[str]:
        """
        Suggest relevant follow-up questions based on current query and results.
        
        Args:
            current_query: The current query
            results: Optional results from the current query
            
        Returns:
            List of suggested follow-up questions
        """
        if not self.is_available:
            return []
        
        prompt = f"""Based on this query: "{current_query}"

Suggest 3-5 relevant follow-up questions a user might want to ask about their pharmacy sales data.

Make questions specific, actionable, and progressively deeper.

Respond with a JSON array of questions only."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You suggest insightful follow-up questions for data analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('questions', [])
            
        except Exception as e:
            print(f"Error suggesting questions: {str(e)}")
            return []
    
    def explain_metric(self, metric_name: str, value: Any, context: Dict = None) -> str:
        """
        Generate a plain-language explanation of a metric.
        
        Args:
            metric_name: Name of the metric
            value: The metric value
            context: Additional context about the metric
            
        Returns:
            Plain language explanation
        """
        if not self.is_available:
            return f"{metric_name}: {value}"
        
        prompt = f"""Explain this pharmacy sales metric in simple terms:

Metric: {metric_name}
Value: {value}
Context: {json.dumps(context, default=str) if context else 'N/A'}

Provide:
1. What this metric means
2. Why it matters for a pharmacy business
3. Whether this value is good/bad/neutral (if possible to assess)
4. Actionable suggestion if relevant

Keep it concise (2-3 sentences)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You explain business metrics in simple, actionable terms."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"{metric_name}: {value} (explanation unavailable)"
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


def check_openai_status() -> Tuple[bool, str]:
    """
    Check if OpenAI integration is available and working.
    
    Returns:
        Tuple of (is_available, status_message)
    """
    if not OPENAI_AVAILABLE:
        return False, "OpenAI library not installed"
    
    api_key = config.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return False, "API key not configured"
    
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return True, "OpenAI integration active"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

