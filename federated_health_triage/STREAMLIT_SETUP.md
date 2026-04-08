# 🚀 Streamlit Application Setup Guide

## Quick Start

### 1. Install Streamlit Dependencies
```powershell
pip install -r requirements-streamlit.txt
```

Or install individually:
```powershell
pip install streamlit plotly pandas numpy scikit-learn openai
```

### 2. Run the Streamlit App
```powershell
streamlit run app.py
```

The app will open in your browser at: `http://localhost:8501`

---

## 📱 Features

### 🏠 Dashboard
- **Real-time System Overview**
  - Total patients across all clinics
  - High-risk cases count
  - Outbreak clusters detected
  - System health metrics

- **Clinic Status**
  - Individual clinic information
  - Patient statistics
  - High-risk cases breakdown
  - Outbreak cluster detection

- **Risk Distribution**
  - Pie chart of risk levels
  - System-wide metrics
  - API response times

### 🔍 Patient Assessment
- **Individual Risk Evaluation**
  - Demographics input (age, gender)
  - Medical history (comorbidities, vaccination status)
  - Exposure history (travel, contact with confirmed cases)
  - Symptom tracking
  
- **Real-time Results**
  - Risk level with confidence score
  - Identified risk factors
  - Clinical recommendations
  - ChatGPT clinical analysis (if API available)

- **Assessment History**
  - View past assessments
  - Track patient outcomes
  - Trending analysis

### 📊 Clinic Analytics
- **Clinic-Specific Performance**
  - Select any of 3 clinics
  - View key metrics
  - Model accuracy tracking
  
- **Performance Trends**
  - 30-day accuracy trend
  - Risk classification distribution
  - Feature importance visualization

- **Advanced Analytics**
  - Comparative analysis
  - Temporal patterns
  - Predictive insights

### 🚨 Outbreak Detection
- **Population-Level Monitoring**
  - Configurable detection thresholds
  - Real-time clinic status
  - Active alerts dashboard
  
- **Outbreak Timeline**
  - 7-day high-risk trend
  - Alert trigger visualization
  - Historical outbreak data

- **Automated Alerts**
  - Cluster detection
  - Surge notifications
  - Public health notifications

### 📈 Model Performance
- **Individual Clinic Metrics**
  - Accuracy, Precision, Recall, F1-Score
  - Performance comparison charts
  - Radar chart visualization

- **Federated Ensemble**
  - Combined model performance
  - Sensitivity & Specificity
  - Confusion matrix

- **Performance Trends**
  - Historical accuracy tracking
  - Model improvement metrics

### ⚙️ Settings
- **Model Configuration**
  - Select learning algorithm
  - Aggregation method
  - Data split parameters

- **ChatGPT Integration**
  - Enable/disable AI advisor
  - Model selection
  - Cost tracking

- **Notifications**
  - Outbreak alerts
  - Customizable thresholds
  - System monitoring

---

## 🎯 Usage Examples

### Example 1: Daily Risk Assessment
1. Go to "🔍 Patient Assessment"
2. Enter patient information
3. Click "🔍 Assess Risk"
4. View recommendations and explanations

### Example 2: Monitor Clinic Performance
1. Go to "📊 Clinic Analytics"
2. Select clinic from dropdown
3. View performance trends
4. Identify high-risk patients

### Example 3: Detect Outbreaks
1. Go to "🚨 Outbreak Detection"
2. Set detection thresholds
3. View current clinic status
4. Review active alerts

---

## 🔧 Troubleshooting

### Port Already in Use
If port 8501 is already in use:
```powershell
streamlit run app.py --server.port 8502
```

### Module Not Found
Install missing dependencies:
```powershell
pip install -r requirements-streamlit.txt --upgrade
```

### ChatGPT Integration Issues
- Ensure `.env` file has `OPENAI_API_KEY` set
- Check API quota at https://platform.openai.com/account/usage
- ChatGPT features work but show graceful fallback if unavailable

---

## 📊 Data Flow

```
Patient Input
    ↓
Risk Assessment Engine
    ↓
Clinic Models (Federated)
    ↓
Ensemble Consolidation
    ↓
ChatGPT Analysis (Optional)
    ↓
Clinical Recommendations
    ↓
Real-time Dashboard Display
```

---

## 🚀 Deployment

### Local Development
```powershell
streamlit run app.py
```

### With Custom Config
```powershell
streamlit run app.py --config.toml
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Authorize and select repository
4. Deploy with one click

---

## 📈 Performance Tips

1. **Caching**
   - Models are cached with `@st.cache_resource`
   - Inputs cached with appropriate TTL

2. **Optimization**
   - Use `use_container_width=True` for responsive layouts
   - Lazy load heavy computations
   - Batch API calls where possible

3. **Monitoring**
   - Check settings page for system health
   - Monitor API response times
   - Track model accuracy trends

---

## 🆘 Support

For issues:
1. Check error messages in console
2. Review logs in `.streamlit/` directory
3. Ensure all dependencies installed
4. Verify data files exist in `data/` directory

---

## 📚 Documentation

- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

---

**Happy Monitoring! 🏥**
