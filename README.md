# 🔐 Cyber Phishing Detection System
**Privacy-Preserving, Explainable Machine Learning–Based Phishing Detection**

## 📌 Overview

The **Cyber Phishing Detection System** is a **research-grade and production-ready web security system** designed to detect phishing websites in real-time using:
- ✅ **Random Forest Machine Learning Model** with ~97-98% accuracy
- ✅ **Real-time URL Feature Extraction** from URLs
- ✅ **Explainable Phishing Detection** (why a URL was flagged)
- ✅ **Reputation-Based Phishing Detection**
- ✅ **Automatic Model Retraining** every 24 hours
- ✅ **Model Versioning & Rollback Support**
- ✅ **RESTful FastAPI Backend**
- ✅ **Interactive Web-Based Frontend**
- ✅ **Privacy-First Design** (URLs deleted after processing)

This system is **paper-safe, zero-day capable**, and suitable for **academic research and cybersecurity projects**.

---

## 🚀 Quick Start

### **1️⃣ Backend Setup**

Navigate to the backend folder:
```bash
cd backend
```

Install required Python dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
python -m uvicorn api:app --reload
```

**Backend runs at**: `http://127.0.0.1:8000`

### **2️⃣ Frontend Access**

- Open `frontend/index.html` in a browser
- Recommended via **Live Server** or **localhost**

### **3️⃣ Test URLs**

**Legitimate:**
- `https://google.com`
- `https://github.com`
- `https://wikipedia.org`
- `https://www.india.gov.in`

**Phishing:**
- `http://paypal-confirm.click`
- `http://amazon-verify.tk`
- `http://google-login.ml`
- `http://apple-id-verify.cf`

---

## 📊 Model Performance (Current)

| Metric | Value | Status |
|--------|-------|--------|
| **Accuracy** | ~97–98% | ✅ Excellent |
| **Precision** | ~96–98% | ✅ Minimal false positives |
| **Recall** | ~98–99% | ✅ Catches most phishing |
| **F1-Score** | ~97–98% | ✅ Strong balance |
| **Inference Time** | < 50 ms | ⚡ Real-time |
| **Model Type** | Random Forest | 🌲 Ensemble ML |

**Notes:**
- ✔ Evaluated on unseen test data
- ✔ Metrics may slightly vary after retraining

---

## 🧠 Explainable Detection

For every phishing detection, the system explains:

- **Detection Method** (Reputation / Machine Learning)
- **Confidence Score**
- **Human-Readable Reasons**
- **Top Contributing Features** with percentage impact

### **Example Reasons:**

- ⚠️ Website does not use HTTPS
- 🔍 Suspicious keywords found in URL
- 🚩 Excessive hyphens or randomness in domain

This ensures **trust, transparency, and explainability**.

---

## 🔄 System Workflow

### **User Submits a URL**

```
1. URL Input (e.g., "https://google.com")
   ↓
2. URL Canonicalization (normalize format)
   ↓
3. Cryptographic Fingerprint Generation (HMAC-SHA512)
   ↓
4. Original URL Deleted Immediately (privacy)
   ↓
5. Feature Extraction (real URL characteristics)
   ↓
6. Reputation Database Check (known phishing URLs)
   ↓
7. Machine Learning Classification (Random Forest)
   ↓
8. Explainable Result Displayed (PHISHING 🚨 or LEGITIMATE ✅)
```

---

## 🧪 Features Extracted

| Feature | Description |
|---------|-------------|
| **Domain Age (heuristic)** | Detects newly registered domains |
| **TLS / HTTPS** | Checks secure connection |
| **Redirect Count** | Multiple redirects indicator |
| **Suspicious Keywords** | login, verify, confirm, update |
| **URL Length** | Long URLs are risky |
| **Dot Count** | Excessive subdomains |
| **Hyphen Count** | Brand impersonation |
| **Digit Ratio** | Obfuscated domains |
| **@ Symbol** | URL redirection trick |
| **Entropy** | Randomness in URL |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Web Frontend (Browser)                   │
│    index.html, script.js, style.css             │
└────────────────────┬────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)             │
│  • /fingerprint (extract features)              │
│  • /detect (ML prediction)                      │
│  • /scheduler/* (retraining control)            │
│  • /models/* (version management)               │
└────────┬───────────┬──────────────┬─────────────┘
         │           │              │
         ▼           ▼              ▼
    ┌────────┐  ┌────────┐  ┌──────────────┐
    │RF Model│  │Pipeline│  │Reputation DB │
    │(pkl)   │  │Manager │  │(OpenPhish)   │
    └────────┘  └────────┘  └──────────────┘
         │           │              │
         └───────────┼──────────────┘
                     ▼
         ┌──────────────────────┐
         │  Models Directory    │
         │ (versioned, indexed) │
         └──────────────────────┘
```

The architecture is **modular, scalable, and supports real-time inference**.

---

## 📁 Project Structure

```
backend/
├── api.py                    ⭐ FastAPI server
├── add_features.py           ⭐ Feature extraction
├── train_model.py            ⭐ Model training
├── evaluate_model.py         ⭐ Testing & metrics
├── model_manager.py          ⭐ Versioning & rollback
├── pipeline.py               ⭐ Automatic retraining
├── reputation.py             ⭐ Phishing database
├── fingerprint.py            SHA-512 fingerprinting
├── canonicalize.py           URL normalization
├── sync_openphish.py         OpenPhish sync
├── rf_model.pkl              Current production model
├── dataset_phase1.csv        Original 600 URLs
├── dataset_ml.csv            Features + labels
├── requirements.txt          Python dependencies
└── models/                   Versioned models
    ├── rf_model_*.pkl
    └── models_metadata.json

frontend/
├── index.html                Web interface
├── script.js                 Detection logic
└── style.css                 Styling

datasets/
├── dataset_phase1.csv
└── dataset_ml.csv

README.md
```

---

## 🔌 API Endpoints

### **Feature Extraction**
```bash
POST /fingerprint
```
**Input:**
```json
{ "url": "https://google.com" }
```
**Output:**
```json
{
  "fingerprint": "abc123...",
  "prefix": "abc123...",
  "domain_age_days": 90,
  "tls_valid": 1,
  "redirect_count": 0,
  "suspicious_js": 0
}
```

### **Phishing Detection**
```bash
POST /detect
```
**Input:**
```json
{
  "prefix": "abc123...",
  "domain_age_days": 90,
  "tls_valid": 1,
  "redirect_count": 0,
  "suspicious_js": 0
}
```
**Output:**
```json
{
  "result": "legitimate",
  "method": "machine_learning",
  "confidence": 0.98,
  "feature_influence": [...]
}
```

### **Scheduler Control**
```bash
GET  /scheduler/status          # Check scheduler status
POST /scheduler/pause           # Pause retraining
POST /scheduler/resume          # Resume retraining
```

### **Model Management**
```bash
GET  /models/history                  # List all model versions
GET  /models/current                  # Current active model
GET  /models/metrics-comparison       # Compare all versions
POST /models/rollback/{timestamp}     # Switch to old model
DELETE /models/cleanup                # Delete old versions
```

### **API Documentation**
```
http://127.0.0.1:8000/docs     # Interactive Swagger UI
http://127.0.0.1:8000/redoc    # ReDoc documentation
```

---

## 🔄 Automatic Model Retraining

**Schedule**: Every **24 hours** automatically

### **Pipeline:**

1. ✅ Sync latest phishing URLs from OpenPhish
2. ✅ Extract features for all URLs
3. ✅ Train new Random Forest model
4. ✅ Evaluate performance metrics
5. ✅ Save versioned model with metadata
6. ✅ Reload model into API memory
7. ✅ Auto-cleanup old models (keep last 10)

### **Why This Matters:**

- 🔄 Phishing techniques evolve daily
- 📈 Model stays up-to-date automatically
- 🚀 No manual intervention required
- ⚡ Doesn't block API requests

---

## 🔐 Security & Privacy

✅ **Privacy-First Design**
- Raw URLs are **never stored**
- URLs are **deleted immediately** after processing
- Only **irreversible fingerprints** are retained
- No **browsing history tracking**

✅ **Security Features**
- HTTPS usage strongly preferred
- Known phishing URLs blocked instantly
- TLS/SSL certificate validation
- Suspicious keyword detection

✅ **Data Protection**
- HMAC-SHA512 cryptographic hashing
- No personally identifiable information (PII) stored
- GDPR-compliant architecture

---

## 🧪 Test Categories

### **Legitimate Websites** ✅
- Government portals (`https://www.india.gov.in`)
- Popular trusted domains (`https://google.com`, `https://github.com`)
- Educational and documentation sites (`https://wikipedia.org`)

### **Phishing Websites** 🚨
- Fake login pages
- Brand impersonation domains (`http://paypal-confirm.click`)
- Cheap and suspicious TLDs (`.tk`, `.ml`, `.ga`, `.cf`)

### **Suspicious Patterns** ⚠️
- URLs with keywords: `verify`, `confirm`, `urgent`, `update`
- Excessive hyphens or dots in domain
- HTTP instead of HTTPS
- New domain registrations (< 30 days)

---

## 📈 Technology Stack

### **Backend:**
- **Python 3.13**
- **FastAPI** (web framework)
- **scikit-learn** (Random Forest ML)
- **APScheduler** (background jobs)
- **Joblib** (model persistence)

### **Frontend:**
- **HTML5**
- **CSS3**
- **Vanilla JavaScript** (Fetch API)

### **Dependencies:**
```txt
pandas
scikit-learn
joblib
fastapi
uvicorn
apscheduler
requests
python-whois (optional)
```

---

## 🎓 Academic Suitability

This project is suitable for:

- ✅ **Final year engineering projects**
- ✅ **IEEE / Springer / ACM research papers**
- ✅ **Cybersecurity and ML research**
- ✅ **Explainable AI studies**

### **Key Strengths:**

- 🔒 Privacy-first design
- 🤖 Hybrid detection approach (ML + Reputation)
- 📊 Explainable machine learning
- 🌐 Real-world phishing data
- 🔄 Automatic model updates
- 📈 High accuracy and performance

---

## 🤝 Future Enhancements

- [ ] **SHAP-based** feature explainability
- [ ] **Browser extension** (Chrome/Firefox)
- [ ] **Real WHOIS integration**
- [ ] **Deep learning models** (neural networks)
- [ ] **HTML content analysis**
- [ ] **Threat intelligence feeds**
- [ ] **Mobile app** (Android/iOS)
- [ ] **Advanced content analysis**

---

## 🚀 Deployment

### **Local Development**
```bash
cd backend
python -m uvicorn api:app --reload
```

### **Production** (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api:app
```

### **Docker** (recommended)
```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
docker build -t phishing-detector .
docker run -p 8000:8000 phishing-detector
```

---

## 📖 Documentation

For detailed documentation, see:
- **API Documentation**: `http://127.0.0.1:8000/docs`
- **Architecture Details**: See Architecture section above
- **Feature Engineering**: See Features Extracted section
- **Model Training**: See Automatic Model Retraining section

---

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Deep learning models (LSTM, Transformers)
- Real-time WHOIS lookups
- Browser extension development
- Mobile application
- Advanced threat intelligence
- Content-based analysis

**Steps:**
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the **MIT License**.

```
MIT License

Copyright (c) 2026 Anirudh Kulkarni

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👤 Author

**Anirudh Kulkarni**  
GitHub: [@anirudh-3001](https://github.com/anirudh-3001)

---

## 🔗 Links

- **Repository**: [https://github.com/anirudh-3001/Cyber_phishing_detection](https://github.com/anirudh-3001/Cyber_phishing_detection)
- **API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (when running)
- **Issues**: [GitHub Issues](https://github.com/anirudh-3001/Cyber_phishing_detection/issues)

---

**Last Updated**: January 2026  
**Status**: ✅ Production Ready  
**Model Type**: Explainable Hybrid Machine Learning System  
**Model Accuracy**: ~97-98%
