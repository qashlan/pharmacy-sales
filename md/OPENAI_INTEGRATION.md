# OpenAI Integration Guide

## Overview

The pharmacy sales analytics system now features **GPT-powered intelligence** through OpenAI integration. This enhancement provides:

- 🧠 **Intelligent Query Interpretation**: Understands complex natural language questions
- 💡 **AI-Generated Insights**: Automatically generates business insights from data analysis
- 💬 **Interactive Chat**: Have conversations about your sales data
- 🎯 **Smart Recommendations**: Get AI-suggested follow-up questions and actions

## Features

### 1. Enhanced Query Processing

The system now uses GPT to interpret queries that don't match predefined patterns:

**Before (Pattern Matching Only)**:
- Only understood specific keyword patterns
- Failed on variations or complex questions
- No context understanding

**After (GPT-Enhanced)**:
- Understands intent even with different phrasing
- Handles complex multi-part questions
- Provides context-aware responses

### 2. Automatic Insight Generation

When you ask a question, GPT analyzes the results and generates:
- Key findings and trends
- Business recommendations
- Actionable next steps
- Contextual explanations

### 3. AI Chat Interface

Have natural conversations with an AI assistant that:
- Remembers conversation context
- Answers follow-up questions
- Explains metrics in plain language
- Provides strategic guidance

### 4. Smart Follow-up Suggestions

After answering your question, the AI suggests relevant next questions to explore deeper insights.

## Setup

### Step 1: Install OpenAI Library

The library is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Step 2: Get an OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (it starts with `sk-...`)

### Step 3: Set the API Key

**Option A: .env File (✨ Recommended)**

1. Create a `.env` file in the project root:
```bash
cp env.example .env
```

2. Edit `.env` and add your key:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

3. Save the file. The system will automatically load it!

📖 **See [SETUP_ENV.md](SETUP_ENV.md) for detailed instructions**

**Option B: System Environment Variable**

Linux/Mac:
```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY='sk-your-api-key-here'
```

**Option C: Edit config.py (Not Recommended)**

Add your key to `config.py`:
```python
OPENAI_API_KEY = 'sk-your-api-key-here'
```

⚠️ **Security Warning**: Never commit API keys to version control! Use `.env` file (already in .gitignore)

### Step 4: Verify Setup

Run the dashboard:
```bash
streamlit run dashboard.py
```

Navigate to the "🤖 AI Query Assistant" page. You should see:
- ✨ **GPT Enhanced** status (green) if the integration is working
- 🔧 **Pattern Matching** status (blue) if the API key is not set

## Usage Examples

### Basic Queries (Work with or without OpenAI)

```
- What is the total revenue?
- Show me the top 10 products
- Which customers are at risk of churning?
```

### Advanced Queries (Enhanced by GPT)

```
- Compare this month's performance to last month and explain the difference
- What patterns do you see in customer purchasing behavior?
- Suggest strategies to increase revenue from at-risk customers
- Which product categories have seasonal trends?
- Explain the relationship between customer segments and refill patterns
```

### Chat Interface

After asking a question, you can have a conversation:

**You**: *"What is the total revenue?"*  
**AI**: *"The total revenue is $1,250,000 from 5,432 orders..."*

**You**: *"How does that compare to last quarter?"*  
**AI**: *"Based on the trend analysis, this represents a 15% increase..."*

**You**: *"What should I focus on to maintain this growth?"*  
**AI**: *"Here are three strategic recommendations..."*

## Cost Considerations

### Pricing

OpenAI charges based on token usage:
- **GPT-4o-mini** (default): ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- A typical query costs: $0.001 - $0.01 (less than a penny)
- Chat messages: $0.001 - $0.005 per message

### Cost Control

The system is designed to be cost-effective:

1. **Automatic Fallback**: If OpenAI fails or is unavailable, falls back to pattern matching
2. **Selective Use**: GPT is only used when needed (query interpretation and insights)
3. **Efficient Model**: Uses GPT-4o-mini (cost-effective) by default
4. **Optional Features**: You can disable GPT insights by setting `use_gpt_insights=False`

### Monthly Cost Estimate

Typical usage:
- **Light**: 50 queries/day = $1.50/month
- **Medium**: 200 queries/day = $6/month
- **Heavy**: 500 queries/day = $15/month

## Technical Architecture

### Components

1. **`openai_integration.py`**: Core OpenAI integration module
   - `OpenAIAssistant` class: Manages GPT interactions
   - Query interpretation
   - Insight generation
   - Chat functionality

2. **`ai_query.py`**: Enhanced query engine
   - Tries OpenAI interpretation first
   - Falls back to pattern matching
   - Combines GPT insights with data analysis

3. **`dashboard.py`**: Updated UI
   - Shows OpenAI status
   - Displays GPT insights
   - Chat interface
   - Follow-up suggestions

### Data Flow

```
User Query
    ↓
[OpenAI Enabled?]
    ↓ Yes                  ↓ No
GPT Interpretation    Pattern Matching
    ↓                      ↓
Execute Analysis      Execute Analysis
    ↓                      ↓
Get Results           Get Results
    ↓ (if OpenAI)
Generate GPT Insights
    ↓
Display to User
```

## Troubleshooting

### Issue: "OpenAI not available"

**Possible causes**:
1. API key not set
2. OpenAI library not installed
3. Invalid API key
4. Network connectivity issues

**Solutions**:
```bash
# Check if library is installed
pip show openai

# Reinstall if needed
pip install openai>=1.0.0

# Verify API key is set
python3 -c "import os; print(os.getenv('OPENAI_API_KEY', 'NOT SET'))"

# Test API connection
python3 -c "from openai import OpenAI; OpenAI(api_key='YOUR_KEY').models.list()"
```

### Issue: API Errors

**Rate Limit Exceeded**:
- You've exceeded your OpenAI usage quota
- Wait a few minutes or upgrade your plan

**Authentication Failed**:
- Check that your API key is correct
- Ensure no extra spaces in the key

**Connection Timeout**:
- Check your internet connection
- Verify firewall settings

### Issue: Fallback Mode

If you see "🔧 Pattern Matching" instead of "✨ GPT Enhanced":
1. The system is working, just without GPT
2. Check the console/terminal for error messages
3. Verify your API key setup
4. System will continue to work with pattern matching

## Disabling OpenAI

If you want to disable OpenAI integration:

**Option 1**: Don't set the API key  
**Option 2**: Initialize without OpenAI:
```python
engine = AIQueryEngine(data, use_openai=False)
```

## Privacy & Security

### Data Handling

- **Query text** is sent to OpenAI for interpretation
- **Analysis results** are sent to OpenAI for insight generation
- **No raw customer data** is sent (only aggregated results)
- **Conversation history** is stored locally in session state

### Best Practices

1. ✅ Use environment variables for API keys
2. ✅ Never commit API keys to Git
3. ✅ Review OpenAI's data usage policy
4. ✅ Consider data privacy regulations in your region
5. ✅ Use a separate API key per environment (dev/prod)

### OpenAI Data Policy

As of 2024:
- API calls are NOT used to train models by default
- Data is retained for 30 days for abuse monitoring
- You can request zero data retention (see OpenAI Enterprise)

## Advanced Configuration

### Change GPT Model

Edit `openai_integration.py`:
```python
self.model = "gpt-4o"  # More capable but more expensive
# or
self.model = "gpt-4o-mini"  # Cost-effective (default)
```

### Adjust Temperature

Control creativity vs consistency:
```python
temperature=0.3  # More consistent/conservative
temperature=0.7  # More creative/varied
```

### Customize System Prompts

Modify prompts in `openai_integration.py` to:
- Change AI personality
- Add domain-specific knowledge
- Adjust output format
- Include company-specific context

## FAQ

**Q: Do I need OpenAI for the system to work?**  
A: No. The system works perfectly fine without OpenAI using pattern matching. OpenAI just makes it more intelligent.

**Q: Is my data secure?**  
A: Query text and aggregated results are sent to OpenAI. No raw customer data is transmitted. Review OpenAI's privacy policy for details.

**Q: How much will this cost me?**  
A: For typical usage, expect $1-15/month. Each query costs about a penny or less.

**Q: Can I use other AI models?**  
A: Currently designed for OpenAI. Could be adapted for other providers (Anthropic Claude, Google Gemini, etc.) with code modifications.

**Q: What happens if OpenAI is down?**  
A: The system automatically falls back to pattern matching. You'll see a status indicator change, but functionality continues.

**Q: Can I customize the AI's responses?**  
A: Yes! Edit the system prompts in `openai_integration.py` to adjust personality, tone, and output format.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review OpenAI's documentation: https://platform.openai.com/docs
3. Check system logs for error messages
4. Test with simple queries first

## Future Enhancements

Potential additions:
- 📊 GPT-generated visualizations
- 🎨 Custom dashboard creation via natural language
- 📈 Predictive analytics with GPT-4
- 🗣️ Voice interface
- 📱 Mobile app with AI chat
- 🔄 Automated report generation
- 🎯 AI-powered A/B testing suggestions

---

**Last Updated**: November 1, 2025  
**Version**: 1.0  
**OpenAI API Version**: v1+

