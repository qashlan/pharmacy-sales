# Environment Setup Guide

## Quick Setup

### Step 1: Create .env File

Copy the example file and rename it:

```bash
cp env.example .env
```

Or create it manually:

```bash
# Linux/Mac
cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
EOF

# Windows (Command Prompt)
echo # OpenAI API Configuration > .env
echo OPENAI_API_KEY=your-api-key-here >> .env
```

### Step 2: Add Your API Key

Edit the `.env` file and add your OpenAI API key:

```bash
# Option 1: Use nano (Linux/Mac)
nano .env

# Option 2: Use any text editor
# Open .env in your preferred editor
```

Replace `your-api-key-here` with your actual OpenAI API key:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Save and Close

Save the file. The system will automatically load it when you run the dashboard.

---

## Getting an OpenAI API Key

1. **Sign up / Log in** to OpenAI:
   - Visit: https://platform.openai.com/
   - Create an account or sign in

2. **Navigate to API Keys**:
   - Go to: https://platform.openai.com/api-keys
   - Or click your profile → "API Keys"

3. **Create New Key**:
   - Click "Create new secret key"
   - Give it a name (e.g., "Pharmacy Analytics")
   - Copy the key (starts with `sk-`)
   - ⚠️ **Important**: You can only see it once!

4. **Add to .env File**:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

---

## .env File Format

The `.env` file should look like this:

```env
# OpenAI API Configuration (Optional)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# To disable OpenAI (use pattern matching only), leave empty or set to:
# OPENAI_API_KEY=
```

### Rules:
- ✅ No spaces around `=`
- ✅ No quotes needed (unless the value contains spaces)
- ✅ Lines starting with `#` are comments
- ✅ Empty values are allowed
- ✅ File should be in project root directory

---

## Verification

### Test if .env is Loaded

Run this command:

```bash
python3 -c "import config; print('API Key loaded:', 'Yes' if config.OPENAI_API_KEY else 'No')"
```

**Expected output:**
- With key: `API Key loaded: Yes`
- Without key: `API Key loaded: No`

### Test OpenAI Integration

```bash
python3 test_openai_features.py
```

This will:
- ✅ Check if .env is loaded
- ✅ Verify API key is valid
- ✅ Test connection to OpenAI
- ✅ Run sample queries

### Run the Dashboard

```bash
streamlit run dashboard.py
```

Navigate to "🤖 AI Query Assistant" and check for:
- ✨ **GPT Enhanced** (green) = Working!
- 🔧 **Pattern Matching** (blue) = Not enabled or key missing

---

## Troubleshooting

### Issue: "API Key loaded: No"

**Possible causes:**
1. `.env` file doesn't exist
2. `.env` file is in wrong location
3. File has wrong format
4. `python-dotenv` not installed

**Solutions:**

```bash
# Check if .env exists
ls -la .env

# Check if it's in the right place
pwd  # Should show the project directory

# Verify file contents
cat .env

# Install python-dotenv if missing
pip install python-dotenv

# Try reloading
python3 -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY', 'NOT FOUND'))"
```

### Issue: "OpenAI not available"

**Check:**
1. Is API key in `.env` file?
2. Is it the correct format (`sk-...`)?
3. Is `openai` package installed?
4. Is there a network connection?

**Test manually:**

```bash
# Test API key directly
python3 << EOF
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print(f"Key loaded: {api_key[:10]}..." if api_key else "No key found")

from openai import OpenAI
client = OpenAI(api_key=api_key)
try:
    client.models.list()
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

### Issue: ".env file not found"

**Check location:**

```bash
# Should be in project root
ls -la | grep .env

# If not there, create it:
cp env.example .env
```

### Issue: "Permission denied"

```bash
# Fix permissions (Linux/Mac)
chmod 600 .env

# Verify
ls -la .env
```

---

## Security Best Practices

### ✅ DO:
- Keep `.env` in project root
- Add `.env` to `.gitignore` (already done)
- Use different keys for dev/prod
- Rotate keys periodically
- Use environment-specific .env files

### ❌ DON'T:
- Never commit `.env` to Git
- Don't share your API key
- Don't hardcode keys in source code
- Don't use production keys in development
- Don't give `.env` file to others (share `env.example` instead)

### File Permissions

Set restrictive permissions on .env file:

```bash
# Linux/Mac: Owner read/write only
chmod 600 .env

# Verify
ls -l .env
# Should show: -rw------- (600)
```

---

## Multiple Environments

### Development vs Production

Create separate .env files:

```bash
# Development
.env.development

# Production
.env.production

# Local testing
.env.local
```

Load specific file:

```python
from dotenv import load_dotenv

# Development
load_dotenv('.env.development')

# Production
load_dotenv('.env.production')
```

---

## Alternative: System Environment Variables

If you prefer not to use a `.env` file, you can set system environment variables:

### Linux/Mac (Bash):
```bash
export OPENAI_API_KEY='sk-your-key-here'

# Add to ~/.bashrc or ~/.zshrc for persistence
echo "export OPENAI_API_KEY='sk-your-key-here'" >> ~/.bashrc
source ~/.bashrc
```

### Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=sk-your-key-here

# For persistence, use System Properties → Environment Variables
setx OPENAI_API_KEY "sk-your-key-here"
```

### Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY = 'sk-your-key-here'

# For persistence
[Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
```

**Note**: The system will check `.env` file first, then fall back to system environment variables.

---

## Docker Setup

If running in Docker, pass environment variables:

```bash
# Via docker run
docker run -e OPENAI_API_KEY='sk-your-key' pharmacy-analytics

# Via docker-compose.yml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

---

## FAQ

**Q: Do I need a .env file?**  
A: No, it's optional. The system works without OpenAI.

**Q: Where should .env be located?**  
A: In the project root directory (same folder as config.py and dashboard.py).

**Q: Can I use system environment variables instead?**  
A: Yes! The system checks both. `.env` file is just more convenient.

**Q: What if I don't have an OpenAI API key?**  
A: Leave `.env` empty or don't create it. System will use pattern matching.

**Q: Is .env secure?**  
A: Yes, if you follow best practices (don't commit to Git, set file permissions, keep it private).

**Q: Can I add other config to .env?**  
A: Yes! You can add any configuration variables you need.

---

## Summary

1. **Create**: `cp env.example .env`
2. **Edit**: Add your OpenAI API key
3. **Save**: File should be in project root
4. **Test**: Run `python3 test_openai_features.py`
5. **Use**: Run `streamlit run dashboard.py`

That's it! The system will automatically load your configuration.

