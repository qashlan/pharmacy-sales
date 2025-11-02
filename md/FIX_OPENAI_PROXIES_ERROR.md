# Fix: OpenAI 'proxies' Error

## Error Message
```
⚠️ OpenAI initialization failed: Client.__init__() got an unexpected keyword argument 'proxies'
```

## Root Cause

This error occurs when there's a version mismatch or corrupted OpenAI installation. The `proxies` parameter exists in some versions but not in OpenAI v1.x that we need for compatibility with `langchain-openai`.

---

## 🔧 Quick Fix

### Step 1: Completely Remove OpenAI

```bash
pip uninstall openai -y
```

### Step 2: Clean pip cache

```bash
pip cache purge
```

### Step 3: Reinstall Correct Version

```bash
pip install 'openai>=1.6.1,<2.0.0'
```

### Step 4: Verify Installation

```bash
python3 -c "import openai; print('OpenAI version:', openai.__version__)"
```

**Expected output:** `OpenAI version: 1.54.4` (or any 1.x.x version)

### Step 5: Test Integration

```bash
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales
python3 test_openai_features.py
```

---

## 🐛 If That Doesn't Work

### Complete Clean Reinstall

```bash
# 1. Uninstall ALL OpenAI-related packages
pip uninstall openai openai-whisper langchain-openai -y

# 2. Clear pip cache
pip cache purge

# 3. Update pip itself
pip install --upgrade pip

# 4. Install from requirements.txt
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales
pip install -r requirements.txt

# 5. Verify
pip show openai
```

---

## 🔄 Alternative: Use Virtual Environment (Recommended)

This will ensure a clean installation without conflicts:

```bash
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales

# Remove old venv if exists
rm -rf venv

# Create fresh virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test
python3 test_openai_features.py

# Run dashboard
streamlit run dashboard.py
```

---

## 📋 Verification Checklist

After fixing, verify everything works:

### 1. Check OpenAI Version
```bash
pip show openai
```
**Should show:** Version: 1.x.x (NOT 2.x.x)

### 2. Test Import
```bash
python3 -c "from openai import OpenAI; print('✅ Import successful')"
```

### 3. Test Client Creation
```bash
python3 << 'EOF'
from openai import OpenAI
client = OpenAI(api_key='test')
print('✅ Client creation successful')
EOF
```

### 4. Test Full Integration
```bash
python3 test_openai_features.py
```

### 5. Run Dashboard
```bash
streamlit run dashboard.py
```

Navigate to "🤖 AI Query Assistant" - should show "✨ GPT Enhanced" or "🔧 Pattern Matching"

---

## 🔍 Debugging

### Check What's Installed

```bash
pip list | grep -i openai
```

**Expected output:**
```
openai              1.54.4
python-dotenv       1.0.0
```

**Should NOT show:**
- openai 2.x.x (wrong version)
- Multiple openai packages

### Check Installation Location

```bash
python3 -c "import openai; print(openai.__file__)"
```

This shows where the package is installed. If you see multiple paths or system paths, you might have conflicting installations.

### Check for Conflicting Packages

```bash
pip list | grep -i langchain
```

If you see `langchain-openai`, verify its version requirements:
```bash
pip show langchain-openai
```

---

## 💡 Why This Happens

1. **Version Mismatch**: OpenAI v2.x has different initialization parameters than v1.x
2. **Cached Installation**: pip cache might have corrupted files
3. **Multiple Installations**: System-wide and user-specific packages conflict
4. **Dependency Conflicts**: Other packages (like langchain-openai) require specific versions

---

## ✅ Prevention

### Use Virtual Environments

Always use virtual environments for Python projects:

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Benefits:
- ✅ Isolated from system packages
- ✅ No version conflicts
- ✅ Easy to recreate
- ✅ Multiple projects can have different versions

### Pin Exact Versions

For production, consider pinning exact versions:

```bash
# Generate exact versions
pip freeze > requirements-lock.txt

# Install exact versions
pip install -r requirements-lock.txt
```

---

## 🆘 Still Not Working?

### Last Resort: System-wide Reset

**⚠️ Warning**: This affects all Python packages

```bash
# List all packages
pip list

# Uninstall all (careful!)
pip freeze | xargs pip uninstall -y

# Reinstall fresh
cd /media/ahmed.qashlan@ad.cyshield/Cy1/Apps/pharmacy_sales
pip install -r requirements.txt
```

### Use Docker (Advanced)

For complete isolation, consider Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["streamlit", "run", "dashboard.py"]
```

---

## 📝 Summary

The `proxies` error indicates version incompatibility. Follow these steps:

1. ✅ Uninstall openai completely
2. ✅ Clear pip cache
3. ✅ Install correct version (1.6.1 to 1.x)
4. ✅ Test with test_openai_features.py
5. ✅ Use virtual environment for future projects

**Most likely fix:**
```bash
pip uninstall openai -y
pip cache purge
pip install 'openai>=1.6.1,<2.0.0'
```

Then test with:
```bash
python3 test_openai_features.py
```

Good luck! 🚀

