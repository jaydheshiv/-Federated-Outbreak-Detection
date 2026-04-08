# 🆘 Complete Troubleshooting Guide

## ⚡ Quick Start Checklist

Before running the app, verify these:

```
☐ Python 3.9+ installed (python --version)
☐ Dependencies installed (pip install -r requirements-streamlit.txt)
☐ OpenAI API key obtained (https://platform.openai.com/api-keys)
☐ Trained models exist in models/ folder
☐ Data files exist in data/ folder
☐ .env file created with OPENAI_API_KEY (for enhanced app)
☐ Running from correct directory
```

---

## 🚀 Getting Started (Step-by-Step)

### Step 1: Install Dependencies
```powershell
cd "d:\sem-8\HCA\cat 2\federated_health_triage"
pip install -r requirements-streamlit.txt
```

**Expected output:**
```
Successfully installed numpy, pandas, scikit-learn, 
matplotlib, seaborn, openai, streamlit, plotly
```

### Step 2: Run the Standard App (Test First)
```powershell
streamlit run app.py
```

**What to see:**
- Browser opens automatically to http://localhost:8501
- Dashboard page loads within 2 seconds
- Shows 7 page tabs on left sidebar
- All visualizations render properly

### Step 3: Run the AI-Enhanced App (After Testing Standard)
```powershell
# In a new terminal:
cd "d:\sem-8\HCA\cat 2\federated_health_triage"
streamlit run app_ai_enhanced.py
```

**What to see:**
- Same interface as app.py
- Plus new "AI Assistant" page
- Dashboard has "AI System Insights" section
- ChatGPT features enabled (if API key is valid)

---

## ❌ Common Issues & Solutions

### Issue 1: `ModuleNotFoundError: No module named 'openai'`

**Symptoms:**
```
Traceback (most recent call last):
  File "app_ai_enhanced.py", line 15, in <module>
    import openai
ModuleNotFoundError: No module named 'openai'
```

**Solution:**
```powershell
# Install missing packages
pip install openai
pip install -r requirements-streamlit.txt

# Verify installation
python -c "import openai; print(openai.__version__)"
```

**If still failing:**
```powershell
# Use specific version
pip install openai==1.3.5

# Rebuild environment
pip install --upgrade --force-reinstall openai streamlit
```

---

### Issue 2: `FileNotFoundError: data/Clinic_A_data.csv`

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 
'data/Clinic_A_data.csv'
```

**Solution:**
1. **Generate data first:**
```powershell
python train.py
# This will create all data files
```

2. **Verify files exist:**
```powershell
dir data/
# Should show:
#   Clinic_A_data.csv
#   Clinic_B_data.csv
#   Clinic_C_data.csv
```

3. **If files exist, check folder permission:**
```powershell
# Verify read access
Get-Item data/Clinic_A_data.csv

# If error, grant permission
```

---

### Issue 3: `OpenAI API Key Invalid`

**Symptoms:**
```
AuthenticationError: Incorrect API key provided. 
You can find your API key at https://platform.openai.com/account/api-keys.
```

**Solution:**

**Option A: Using .env file (Recommended)**
1. Create `.env` file in project root:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

2. Restart Streamlit:
```powershell
# Kill current instance (Ctrl+C)
# Restart:
streamlit run app_ai_enhanced.py
```

**Option B: Set environment variable**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
streamlit run app_ai_enhanced.py
```

**Option C: Hardcode (NOT RECOMMENDED)**
```python
# In app_ai_enhanced.py, find:
openai.api_key = os.getenv("OPENAI_API_KEY")

# Replace with:
openai.api_key = "sk-your-key"  # ⚠️ SECURITY RISK!
```

**Verify API Key:**
```powershell
python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
try:
    openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hi'}],
        max_tokens=5
    )
    print('✅ API Key valid!')
except Exception as e:
    print(f'❌ API Key error: {e}')
"
```

---

### Issue 4: `streamlit not found` or `No module named streamlit`

**Symptoms:**
```
streamlit: The term 'streamlit' is not recognized
OR
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```powershell
# Install streamlit
pip install streamlit

# Verify installation
streamlit --version
# Should show: Streamlit, version X.XX.X

# Check Python version (must be 3.9+)
python --version
```

---

### Issue 5: `Port 8501 already in use`

**Symptoms:**
```
Error: Address already in use
ERROR in logger code: Traceback...
streamlit.errors.StreamlitAPIException: The address is in use
```

**Solution:**

**Option A: Use different port**
```powershell
streamlit run app_ai_enhanced.py --server.port 8502
```

**Option B: Kill existing process**
```powershell
# Find process using port 8501
Get-NetTCPConnection -LocalPort 8501

# Kill it
Stop-Process -Id <PID> -Force

# Then restart
streamlit run app_ai_enhanced.py
```

**Option C: Clear cache**
```powershell
# Delete Streamlit cache
rm -r ~/.streamlit
streamlit run app_ai_enhanced.py
```

---

### Issue 6: `Models folder missing`

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 
'models/Urban Center Clinic_model.pkl'
```

**Solution:**
1. **Generate all models:**
```powershell
python train.py
# Runs all 6 training steps
# Creates models/ folder with 3 pickle files
```

2. **Verify models exist:**
```powershell
dir models/
# Should show:
#   Urban Center Clinic_model.pkl
#   Rural Area Clinic_model.pkl
#   Travel Hub Clinic_model.pkl
```

---

### Issue 7: ChatGPT Features Not Working (Grayed Out)

**Symptoms:**
- Settings page has toggle but it's grayed out
- AI features don't generate text
- No error messages

**Debug Steps:**
1. **Check if API key is loaded:**
```python
import os
key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {key is not None}")
print(f"Key preview: {key[:10]}..." if key else "None")
```

2. **Check if feature is enabled in settings:**
   - Open app
   - Go to Settings page
   - Toggle "Enable ChatGPT Features" to ON
   - Refresh browser (F5)

3. **Check API account status:**
   - Visit https://platform.openai.com/account/usage
   - Verify you have API credits
   - Check for rate limits

---

### Issue 8: Slow Page Loads (with AI enabled)

**Symptoms:**
- Dashboard takes 5+ seconds to load
- Patient Assessment is slow
- Chat responses take 10+ seconds

**Solutions:**

**Quick Fixes:**
```powershell
# 1. Clear cache
rm -r ~/.streamlit

# 2. Restart Python
# Ctrl+C to stop app
# Run again: streamlit run app_ai_enhanced.py

# 3. Clear browser cache
# Ctrl+Shift+Delete in browser
```

**Configuration Optimization:**
```
In Settings page:
1. Set "AI Analysis Depth" to "Brief" (faster)
2. Enable "Cache Results" (1 hour TTL)
3. Disable AI on heavy pages (if needed)
```

**Cost/Performance Tradeoff:**
```
Brief:     1-2s per AI call, $0.001 per call
Normal:    2-4s per AI call, $0.005 per call
Detailed:  4-6s per AI call, $0.010 per call
```

---

### Issue 9: `ValueError: Unexpected value for column`

**Symptoms:**
```
ValueError: Unexpected value for column 'risk_level': 'invalid_value'
File "app_ai_enhanced.py", line 234, in page_patient_assessment()
```

**Solution:**
```powershell
# Regenerate clean data
python train.py

# OR check data integrity
python -c "
import pandas as pd
df = pd.read_csv('data/Clinic_A_data.csv')
print('Unique risk levels:', df['risk_level'].unique())
print('Data shape:', df.shape)
print('Missing values:', df.isnull().sum())
"
```

---

### Issue 10: Out of Memory Error

**Symptoms:**
```
MemoryError: Unable to allocate memory
OR
Streamlit app crashes without error
```

**Solution:**
```powershell
# For large datasets, increase memory
# Windows PowerShell:
$env:PYTHONHASHSEED='0'

# Restart with memory limits
streamlit run app_ai_enhanced.py

# Monitor memory usage
# Task Manager → Performance → Memory

# If still issues:
# - Reduce number of cached plots
# - Disable detailed analytics
# - Split into separate apps
```

---

## 🧪 Testing & Validation

### Validate Setup (Run This)

```powershell
python -c "
print('🔍 Validating Setup...\n')

# Check Python version
import sys
print(f'✓ Python {sys.version.split()[0]}')

# Check imports
try:
    import pandas as pd
    import numpy as np
    import sklearn
    import streamlit as st
    import plotly.graph_objects as go
    import openai
    print('✓ All packages installed')
except ImportError as e:
    print(f'✗ Missing: {e}')

# Check data files
import os
files_needed = [
    'data/Clinic_A_data.csv',
    'data/Clinic_B_data.csv',
    'data/Clinic_C_data.csv',
    'models/Urban Center Clinic_model.pkl',
    'models/Rural Area Clinic_model.pkl',
    'models/Travel Hub Clinic_model.pkl',
]
for f in files_needed:
    exists = os.path.exists(f)
    symbol = '✓' if exists else '✗'
    print(f'{symbol} {f}')

# Check API key
key = os.getenv('OPENAI_API_KEY')
if key:
    print(f'✓ OpenAI API key found ({key[:10]}...)')
else:
    print('⚠ OpenAI API key not found')
    
print('\n✅ Setup validation complete!')
"
```

---

## 📞 When Something Goes Wrong

### 1. **Check the Error Message**
```
Read the full error stack trace
→ Look for FileNotFoundError, ImportError, KeyError, etc.
→ Google the error message
```

### 2. **Check the Logs**
```powershell
# Streamlit shows logs in terminal
# Look for red error messages
# See line numbers where error occurred
```

### 3. **Isolate the Problem**
```powershell
# Test components individually
python -c "import openai"  # Check OpenAI
python -c "import streamlit"  # Check Streamlit
python train.py  # Check training pipeline
python -c "import pandas; print(pd.read_csv('data/Clinic_A_data.csv').shape)"
```

### 4. **Search for Solutions**
- Error message in Google
- Check requirements versions
- Look for compatibility issues

---

## 🔧 Manual Fixes

### Fix 1: Regenerate Everything
```powershell
# Nuclear option - cleans and rebuilds
rm -r data/ models/ results/ __pycache__/
pip install --upgrade --force-reinstall -r requirements-streamlit.txt
python train.py
streamlit run app_ai_enhanced.py
```

### Fix 2: Reset .streamlit Cache
```powershell
# Clear Streamlit's internal cache
rm -r ~/.streamlit/
streamlit run app_ai_enhanced.py
```

### Fix 3: Use Standard App Instead
```powershell
# If AI enhanced is broken, use standard
streamlit run app.py
# This should work (simpler, no AI calls)
```

### Fix 4: Downgrade Versions
```powershell
# If conflicts occur
pip install streamlit==1.25.0
pip install openai==1.2.0
pip install plotly==5.14.0
```

---

## ✅ Verification Checklist

Before reporting issues, verify:

```
☐ Running from correct directory
  cd "d:\sem-8\HCA\cat 2\federated_health_triage"

☐ Python 3.9+ installed
  python --version

☐ All dependencies installed
  pip list | grep streamlit

☐ Data files exist
  ls data/
  
☐ Models exist
  ls models/
  
☐ API key set (for enhanced app)
  echo $env:OPENAI_API_KEY
  
☐ Port 8501 not in use
  Get-NetTCPConnection -LocalPort 8501
  
☐ No conflicting processes
  Get-Process | grep streamlit
  
☐ Browser cache cleared
  Ctrl+Shift+Delete
```

---

## 📊 Performance Benchmarks

Expected performance on standard machine:

```
Standard App (app.py):
  Dashboard load:        0.5-1s
  Patient Assessment:    0.3-0.5s
  Clinic Analytics:      0.5-1s
  Outbreak Detection:    0.5-1s
  Average page:          0.5s

AI-Enhanced App (app_ai_enhanced.py):
  Dashboard load:        1-2s (without AI)
  With AI insights:      2-4s (ChatGPT call)
  Patient Assessment:    1-2s (without AI)
  With AI analysis:      2-3s (ChatGPT call)
  Average page:          1-2s
  Chat response:         2-4s

On slower connection:
  Add +1-2s for each AI feature
```

---

## 🎯 Success Indicators

When everything works, you should see:

```
✅ Dashboard
  - KPI cards show numbers
  - Pie charts render
  - Risk distribution shows data
  - No red error messages

✅ Patient Assessment
  - Input form accepts data
  - Risk level shows (0-3)
  - Clinic context displays
  - Recommendations appear

✅ AI Features (if enabled)
  - AI insights auto-generate
  - ChatGPT responses appear
  - No "API Error" messages
  - Responses load in 2-4 seconds

✅ Settings
  - Can toggle AI on/off
  - Can adjust analysis depth
  - Cost estimation updates
  - No errors saving settings
```

---

## 🚨 Emergency Fallback

If everything fails and you need something NOW:

```powershell
# Use the stable version (no AI)
streamlit run app.py

# This should work 100% (no external dependencies)
# None of the features require external APIs
```

---

**Still having issues?** 
1. ✅ Run the validation script above
2. ✅ Check all error messages in terminal
3. ✅ Try the regenerate everything fix
4. ✅ Fall back to app.py (standard version)

**Need help with OpenAI API specifically?**
- Visit: https://platform.openai.com/docs
- Check account on: https://platform.openai.com/account/usage
- Contact: support.openai.com

---

**Good luck! 🚀**
