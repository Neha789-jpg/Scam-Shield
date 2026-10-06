# TrustCheck

TrustCheck is a local full-stack MVP that helps a buyer review explainable risk signals before paying an online seller. It accepts either a public HTTP(S) link or a PNG/JPEG/WebP screenshot and returns a lower-risk, unclear, or high-risk result.

TrustCheck estimates risk from available evidence. It does not certify that a seller is genuine or fraudulent.

## 1. Architecture

```text
React + Vite browser UI
        |
        | /api requests
        v
FastAPI backend
        |
        +-- deterministic URL checks
        +-- RDAP domain-age lookup
        +-- optional Google Safe Browsing lookup
        +-- secure image validation
        +-- optional Gemini screenshot fact extraction
        +-- deterministic scoring and advice
```

AI extracts visible facts from screenshots but never chooses the verdict. The scoring service makes the final decision using explicit rules.

## 2. Project structure

```text
trustcheck/
├── backend/
│   ├── .env.example                  Environment variable template
│   ├── requirements.txt              Runtime Python packages
│   ├── requirements-dev.txt          Test packages
│   ├── app/
│   │   ├── main.py                   FastAPI application and CORS
│   │   ├── config.py                 Environment settings
│   │   ├── schemas.py                Request/response data models
│   │   ├── i18n.py                   English and Hindi backend text
│   │   ├── api/routes.py             HTTP endpoints
│   │   └── services/
│   │       ├── url_analyzer.py       Local URL warning signals
│   │       ├── domain_registration.py RDAP domain-age lookup
│   │       ├── safe_browsing.py      Optional Google threat lookup
│   │       ├── screenshot_analyzer.py Image validation and Gemini extraction
│   │       └── scoring.py            Risk score, verdict, confidence, advice
│   └── tests/                         Backend automated tests
├── frontend/
│   ├── package.json                  JavaScript packages and commands
│   ├── vite.config.ts                Vite proxy and test configuration
│   ├── index.html                    Browser entry document
│   └── src/
│       ├── main.tsx                  React entry point
│       ├── App.tsx                   Main page and application state
│       ├── api.ts                    Backend API calls
│       ├── types.ts                  Shared frontend TypeScript types
│       ├── i18n.ts                   English and Hindi interface text
│       ├── styles.css                Responsive visual design
│       └── components/
│           ├── CheckForm.tsx         Link/screenshot input forms
│           ├── VerdictCard.tsx       Result summary and advice
│           └── SignalList.tsx        Individual evidence cards
└── .gitignore
```

## 3. Create the project from scratch

```bash
mkdir trustcheck
cd trustcheck
mkdir -p backend/app/api backend/app/services backend/tests
mkdir -p frontend/src/components frontend/src/test
```

The completed source files are already present in this project, so these commands are only needed if rebuilding it manually.

## 4. Backend setup

Install Python 3.11 or newer, then run:

```bash
cd backend
python -m venv .venv
```

Activate the environment on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Or run its Python executable directly from Git Bash:

```bash
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
```

Create your private settings file:

```bash
cp .env.example .env
```

API keys are optional. Without them, local link checks still work and screenshot uploads return an honest `unclear` result explaining that vision analysis is unavailable.

```env
GOOGLE_SAFE_BROWSING_API_KEY=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

Start the backend:

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

The API runs on `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

Run backend tests:

```bash
.venv/Scripts/python.exe -m pytest -q
```

## 5. Frontend setup

Install Node.js 20 or newer. Open a second terminal:

```bash
cd trustcheck/frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite forwards `/api` calls to the FastAPI server on port 8000.

Run frontend tests and create a production build:

```bash
npm test
npm run build
```

## 6. API endpoints

### Health

```http
GET /api/health
```

### Available integrations

```http
GET /api/capabilities
```

### Analyze a link

```http
POST /api/check/url
Content-Type: application/json
```

```json
{
  "url": "https://example.com",
  "language": "en",
  "claimed_brand": "Example"
}
```

### Analyze a screenshot

```http
POST /api/check/screenshot
Content-Type: multipart/form-data
```

Fields:

- `file`: PNG, JPEG, or WebP, maximum 5 MB
- `language`: `en` or `hi`
- `expected_seller_name`: optional seller name
- `reference_price`: optional normal market price
- `currency`: defaults to `INR`

## 7. Current scoring logic

URL warnings:

- HTTP instead of HTTPS: +15
- Common link shortener: +12
- Punycode hostname: +15
- More than two subdomain levels: +8
- Sensitive words in hostname: +8
- Close but non-exact claimed-brand match: +25
- Domain younger than 30 days: +25
- Domain 30–179 days old: +15
- Domain 180–364 days old: +8
- Google Safe Browsing match: +60 and critical

Screenshot warnings:

- New profile with at least 10,000 followers: +20
- Strong stock/reused-looking image signal: +15
- Payment name mismatch: +30
- Urgency language: +10
- Extreme pressure language: +15
- Price at most 40% of reference price: +20
- Price at most 70% of reference price: +10
- Generic or repeated reviews: +10

Verdicts:

- `0–19`: lower risk when enough checks completed
- `20–44`: unclear
- `45–100`: high risk
- A critical Safe Browsing match always produces high risk
- Missing evidence adds no risk points and lowers confidence

## 8. Security decisions

- The backend accepts only HTTP(S) links with public domain names.
- Credentials, localhost, internal suffixes, IP-address URLs, and unusual ports are rejected.
- The MVP does not fetch submitted websites directly, preventing the URL endpoint from becoming an SSRF proxy.
- Images are checked by MIME type, decoded format, byte size, and pixel count.
- Uploaded screenshots are processed in memory and are not stored.
- Screenshot text is treated as untrusted input in the Gemini prompt.
- API keys remain in `backend/.env`, which is excluded from version control.

## 9. What to build after the MVP

1. Add authenticated accounts and consent-based history.
2. Add a reviewed community-report database with abuse controls.
3. Add reverse-image-search evidence instead of relying on visual similarity alone.
4. Integrate a verified payment-provider or seller-identity source before claiming ownership matches.
5. Calibrate scoring against a labeled dataset and measure false positives.
6. Add rate limits, monitoring, privacy retention rules, and production deployment configuration.
7. Build the browser extension and WhatsApp workflow proposed in the presentation.