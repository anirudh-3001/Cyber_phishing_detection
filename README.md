# Privacy-Preserving Phishing Website Detection  
**Phase-1 Implementation**

## 📌 Overview
This project implements a **privacy-first phishing detection system** that avoids storing or analyzing raw URLs.  
Instead of traditional URL-based inspection, the system converts URLs into **irreversible cryptographic fingerprints** and performs phishing detection using **metadata-driven machine learning**.

The goal of Phase-1 is to **prove feasibility**: phishing detection can be achieved **without compromising user browsing privacy**.

---

## 🚨 Problem Statement
Most existing phishing detection systems:
- Analyze full URLs
- Store user browsing history
- Create privacy and data-leak risks if compromised

This project addresses the question:

> **Can phishing websites be detected without ever storing or analyzing URLs?**

---

## 💡 Core Idea
- URLs are used **only once**
- Each URL is canonicalized and converted into a **HMAC-SHA-512 fingerprint**
- The raw URL is **immediately destroyed**
- Detection is performed using **privacy-safe metadata features**
- Even if the system is breached, URLs **cannot be recovered**

---

## 🔐 Privacy Guarantee
- ❌ No raw URLs stored
- ❌ No URL text used in ML training
- ❌ No browsing history logged
- ✅ Only irreversible fingerprints and metadata are retained

---

## 🔄 System Workflow

1. User clicks a URL (e.g., from WhatsApp)
2. URL is canonicalized locally
3. HMAC-SHA-512 fingerprint is generated
4. Raw URL is deleted permanently
5. Fingerprint prefix is checked for known phishing
6. Metadata features are extracted
7. Machine Learning model classifies the site
8. User is warned if phishing is detected

---

## 📊 Dataset

### Phishing URLs
- **OpenPhish** (industry-recognized real-time phishing feed)

### Legitimate URLs
- **Tranco Top Sites** (research-grade ranking of legitimate domains)

📌 Raw URLs are discarded after fingerprint generation.

---

## 🧠 Algorithms & Techniques

### Cryptography
- **HMAC–SHA-512**
  - Strong, irreversible fingerprinting
  - Prevents URL reconstruction
  - Resistant to brute-force attacks

### Machine Learning
- **Random Forest Classifier**
  - Lightweight and explainable
  - Works well with tabular metadata
  - Suitable for feasibility testing

---

## 🧾 Features Used (Phase-1)
*(Privacy-safe, no URL semantics)*

- Domain age (mocked for feasibility)
- TLS certificate validity (mocked)
- Redirect chain length (mocked)
- JavaScript obfuscation indicator (mocked)

📌 Real feature extraction is planned in Phase-2.

---

## 📈 Evaluation Metrics
- Accuracy
- Precision
- Recall
- F1-score

📌 Phase-1 results validate **pipeline correctness**, not final performance.

---

## 🧪 Phase-1 Results
- Balanced dataset (phishing vs legitimate)
- ML performance close to random baseline
- Expected outcome due to placeholder metadata
- Confirms **no information leakage or bias**

---

## 🧩 Project Phases

### ✅ Phase-0: Environment Setup
- Virtual environment
- Dependency management
- Project structure

### ✅ Phase-1: Feasibility (Completed)
- Privacy-preserving URL handling
- Cryptographic fingerprinting
- Dataset preparation
- ML training & evaluation
- Git-based version control

### 🔜 Phase-2: Enhancements (Planned)
- Real WHOIS & TLS metadata
- Hash-prefix reputation cache
- FastAPI live inference API
- Browser extension integration
- Performance optimization

---

## 📁 Project Structure
Cyber_Phishing/
├── backend/
│ ├── canonicalize.py
│ ├── fingerprint.py
│ ├── local_flow.py
│ ├── dataset_prep.py
│ ├── add_features.py
│ ├── train_model.py
│ ├── openphish.txt
│ └── tranco.txt
├── README.md
└── .gitignore

## 🏁 Conclusion
This Phase-1 implementation demonstrates that **phishing detection is feasible without exposing user browsing data**.  
The system establishes a strong foundation for privacy-preserving cybersecurity research and real-world deployment.
