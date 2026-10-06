# 🛡️ ScamShield

**ScamShield** is an AI-powered scam detection and seller risk assessment tool designed to help users identify suspicious online sellers, payment requests, and potentially fraudulent shopping interactions.

Instead of relying on a single AI-generated verdict, ScamShield combines **AI-powered evidence extraction, deterministic security checks, external threat intelligence, and rule-based risk scoring** to produce an explainable risk assessment.

> ScamShield estimates risk from the available evidence. It does not guarantee that a seller is genuine or fraudulent.

---

## ✨ Key Features

* 🔗 **URL Risk Analysis** — identifies suspicious characteristics in submitted links
* 📸 **Screenshot Analysis** — extracts visible scam-related signals from seller screenshots
* 🤖 **AI Agent** — coordinates different analysis tools to investigate available evidence
* 🌐 **Domain Intelligence** — checks domain registration information and domain age
* 🛡️ **Threat Detection** — optionally checks URLs against Google Safe Browsing
* 💳 **Seller & Payment Analysis** — detects suspicious seller/payment-name mismatches
* ⚠️ **Scam Signal Detection** — identifies urgency, pressure tactics, suspicious pricing, repeated reviews, and other warning signs
* 📊 **Explainable Risk Score** — provides individual signals instead of a black-box prediction
* 🌍 **English & Hindi Support**
* 🔒 **Privacy-focused Processing** — uploaded screenshots are processed in memory and are not stored

---

## 🏗️ Architecture


                    User
                      |
                      v
              React + Vite UI
                      |
                /api requests
                      |
                      v
               FastAPI Backend
                      |
                      v
                ScamShield Agent
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
     URL Analysis  Screenshot   External
                    Analysis    Intelligence
          |           |           |
          |           v           |
          |       AI Extraction  |
          |           |           |
          +-----------+-----------+
                      |
                      v
              Risk Scoring Engine
                      |
                      v
             Explainable Verdict
                      |
          +-----------+-----------+
          |           |           |
       Lower Risk   Unclear    High Risk


### Agentic workflow

The ScamShield agent coordinates the available analysis tools instead of depending on a single model response.

The tools can provide evidence such as:

* URL structure warnings
* Domain registration information
* Safe Browsing results
* Screenshot-derived seller signals
* Pricing and urgency indicators
* Payment identity mismatches
* Repeated or generic review patterns

The collected evidence is then passed through the deterministic scoring system to generate the final risk assessment.

---

## 📁 Project Structure


scam-shield/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   │
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── schemas.py
│   │   ├── i18n.py
│   │   │
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   └── tools.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── url_analyzer.py
│   │       ├── domain_registration.py
│   │       ├── safe_browsing.py
│   │       ├── screenshot_analyzer.py
│   │       └── scoring.py
│   │
│   └── tests/
│       ├── test_main.py
│       ├── test_scoring.py
│       └── test_url_analyzer.py
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       ├── types.ts
│       ├── i18n.ts
│       ├── styles.css
│       │
│       ├── components/
│       │   ├── CheckForm.tsx
│       │   ├── VerdictCard.tsx
│       │   └── SignalList.tsx
│       │
│       └── test/
│           └── setup.ts
│
└── .gitignore


---

## 🚀 Running Locally

### Prerequisites

* Python 3.11+
* Node.js 20+
* Git

### 1. Clone the repository

```bash
git clone https://github.com/Neha789-jpg/Scam-Shield.git
cd Scam-Shield
```

---

## ⚙️ Backend Setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
copy .env.example .env
```

Configure the required API keys in `.env`.

**Never commit `.env` to GitHub.**

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

The backend runs at:


http://127.0.0.1:8000


Interactive API documentation:


http://127.0.0.1:8000/docs

### Run backend tests

```bash
pytest -q
```

---

## 💻 Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

http://127.0.0.1:5173


The Vite development server forwards `/api` requests to the FastAPI backend.

### Run frontend tests

```bash
npm test
```

### Create a production build

```bash
npm run build
```

---

## 🔍 Analysis Pipeline

### URL Analysis

ScamShield checks submitted URLs for signals including:

* HTTP instead of HTTPS
* Common URL shorteners
* Punycode hostnames
* Excessive subdomain levels
* Suspicious keywords in hostnames
* Claimed-brand mismatches
* Recently registered domains
* Known threats reported by Safe Browsing

### Screenshot Analysis

For seller screenshots, ScamShield can identify signals such as:

* New profiles with unusually high follower counts
* Stock/reused-looking product images
* Seller/payment-name mismatches
* Urgency language
* High-pressure language
* Unusually low prices
* Generic or repeated reviews

The AI component extracts visible evidence; it does **not independently decide whether the seller is fraudulent**.

---

## 📊 Risk Scoring

ScamShield uses explicit scoring rules to make its results explainable.

### URL signals

| Signal                                  |           Risk |
| --------------------------------------- | -------------: |
| HTTP instead of HTTPS                   |            +15 |
| Common link shortener                   |            +12 |
| Punycode hostname                       |            +15 |
| More than two subdomain levels          |             +8 |
| Suspicious hostname keywords            |             +8 |
| Close but non-exact claimed-brand match |            +25 |
| Domain younger than 30 days             |            +25 |
| Domain 30–179 days old                  |            +15 |
| Domain 180–364 days old                 |             +8 |
| Google Safe Browsing match              | +60 + Critical |

### Screenshot signals

| Signal                             | Risk |
| ---------------------------------- | ---: |
| New profile with ≥10,000 followers |  +20 |
| Strong stock/reused-image signal   |  +15 |
| Payment-name mismatch              |  +30 |
| Urgency language                   |  +10 |
| Extreme pressure language          |  +15 |
| Price ≤40% of reference price      |  +20 |
| Price ≤70% of reference price      |  +10 |
| Generic/repeated reviews           |  +10 |

### Verdicts


0–19     → Lower Risk
20–44    → Unclear
45–100   → High Risk


A critical Safe Browsing match produces a **High Risk** verdict regardless of the calculated score.

Missing evidence does not automatically increase the risk score. Instead, it can reduce the confidence of the assessment.

---

## 🔐 Security & Privacy

ScamShield follows several security-focused design decisions:

* Only HTTP(S) URLs with public domain names are accepted.
* Credentials, localhost URLs, internal domains, IP-address URLs, and unusual ports are rejected.
* Submitted URLs are not directly fetched by the application, reducing SSRF risk.
* Uploaded images are validated by MIME type, decoded format, file size, and pixel count.
* Screenshots are processed in memory and are not permanently stored.
* Screenshot content is treated as untrusted input during AI analysis.
* API keys are stored in `.env` and excluded from version control.

---

## 🧪 Testing

The backend includes automated tests covering:

* API health and application behavior
* URL analysis
* Risk scoring

The frontend also includes automated tests for application behavior.

Run backend tests:

```bash
pytest -q
```

Run frontend tests:

```bash
npm test
```

---

## 🔮 Future Improvements

Potential next steps include:

1. Build a reviewed community scam-report database with abuse controls.
2. Add reverse-image-search evidence for stronger image verification.
3. Integrate verified seller/payment identity sources.
4. Calibrate the scoring system using a labeled scam dataset.
5. Measure false-positive and false-negative rates.
6. Add authentication and consent-based analysis history.
7. Add rate limiting, monitoring, and production deployment configuration.
8. Extend ScamShield into a browser extension.
9. Explore messaging-platform workflows for real-time scam analysis.

---

## 🎯 Why ScamShield?

Online scams increasingly rely on **social engineering rather than obviously malicious links**. A seller may use a convincing profile, attractive product images, fake reviews, urgency, and a legitimate-looking payment request.

ScamShield aims to bring these scattered signals together into a single, **explainable risk assessment** so users can make a more informed decision before sending money.

---

## 🛠️ Tech Stack

**Frontend**

* React
* TypeScript
* Vite
* CSS

**Backend**

* Python
* FastAPI

**AI / Analysis**

* AI-powered screenshot analysis
* Agent-based tool orchestration
* Rule-based risk scoring

**Security / External Intelligence**

* RDAP domain registration data
* Google Safe Browsing
* Secure image validation

**Testing**

* Pytest
* Vitest

---

## 📌 Disclaimer

ScamShield is a prototype designed to assist users in identifying potential scam signals.

A **Lower Risk** result does not prove that a seller is genuine, and a **High Risk** result does not by itself prove fraud. Users should independently verify sellers and payment information before making transactions.
