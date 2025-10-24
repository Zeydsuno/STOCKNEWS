# Stock News Dashboard - LINE Mini App (LIFF)

Real-time stock news analysis and distribution system powered by AI, integrated with LINE Bot and LIFF (LINE Front-end Framework).

## 🎯 Features

- **📰 Real-time Stock News Collection** - Aggregates news from multiple sources
- **🤖 AI-Powered Analysis** - Analyzes news impact using GLM/Mistral AI
- **💬 LINE Bot Integration** - Sends news to LINE users automatically
- **📱 LIFF Dashboard** - Interactive web dashboard inside LINE app
  - Search by ticker or keyword
  - Filter by impact score and price impact
  - Real-time statistics
  - Beautiful mobile-optimized UI
- **🔄 Auto-scheduling** - Broadcasts news at scheduled times
- **📊 Impact Scoring** - Evaluates news impact on stock prices (0-10)
- **🌍 Web Search Integration** - Verifies high-impact news

## 🏗️ Tech Stack

### Backend
- **Framework**: Flask + CORS
- **Language**: Python 3.x
- **AI Models**: GLM-4.6, Mistral Large
- **APIs**: NewsAPI, Alpha Vantage, DuckDuckGo

### Frontend
- **LIFF**: LINE Front-end Framework
- **Hosting**: GitHub Pages
- **Tech**: HTML5, CSS3, Vanilla JavaScript

### Infrastructure
- **Tunneling**: Cloudflare Tunnel
- **Deployment**: GitHub Pages (Frontend) + Local (Backend)

## 📋 Prerequisites

- Python 3.8+
- Git & GitHub account
- LINE Developers account
- Cloudflare account (for tunnel)
- API Keys: NewsAPI, Alpha Vantage, GLM API, LINE Messaging API

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/stocknews.git
cd stocknews
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file:
```env
NEWS_API_KEY=your_newsapi_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
GLM_API_KEY=your_glm_api_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_token
LINE_CHANNEL_SECRET=your_line_secret
DATABASE_URL=sqlite:///stocknews.db
GLM_BASE_URL=https://api.z.ai/v1/messages
```

### 5. Run API Server
```bash
python -m app.api_server

# Server runs at http://localhost:5000
```

### 6. Expose with Cloudflare Tunnel
```bash
# Install cloudflared first
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

cloudflared tunnel --url http://localhost:5000
# Copy the HTTPS URL
```

## 📱 LIFF Setup & Deployment

### 1. Create LINE Login Channel
- Go to [LINE Developers Console](https://developers.line.biz/console/)
- Create new channel → Select **LINE Login**

### 2. Configure LIFF Frontend
Edit `liff/index.html`:

**Line 289 - API URL:**
```javascript
const API_BASE_URL = 'https://your-tunnel-url.trycloudflare.com/api';
```

**Line 290 - LIFF ID:** (update after creating LIFF app)
```javascript
const LIFF_ID = 'YOUR-LIFF-ID';
```

### 3. Deploy Frontend to GitHub Pages
```bash
# Push to GitHub
git add .
git commit -m "Configure LIFF"
git push

# Enable GitHub Pages in Settings
# Source: main / root
# URL: https://yourusername.github.io/stocknews/
```

### 4. Create LIFF App
- LINE Console → LINE Login Channel → **LIFF** tab
- Click **Add**
- **Endpoint URL**: `https://yourusername.github.io/stocknews/liff/index.html`
- **Scopes**: ✓ profile, ✓ openid
- **Copy LIFF ID**

### 5. Link with Messaging API Bot
- **Basic settings** → **Linked bots** → **Edit**
- Select your Messaging API Channel → **Update**

### 6. Update LIFF_ID in Code
```javascript
const LIFF_ID = '1234567890-abcdefgh';
```

Push changes and test!

## 📊 API Endpoints

- `GET /api/news/latest` - Get latest news
- `GET /api/news/search?q=NVDA` - Search news
- `GET /api/news/ticker/AAPL` - Get ticker news
- `GET /api/news/filter?min_impact=8` - Filter news
- `GET /api/status` - System status
- `GET /api/refresh` - Force refresh

## 🐛 Troubleshooting

### LIFF doesn't load
- ✅ Check LIFF ID is correct in code
- ✅ Verify Endpoint URL in LINE Console
- ✅ Make sure using HTTPS, not HTTP
- ✅ Open in LINE app, not browser
- ✅ Check browser console for errors

### API returns 500 error
- ✅ Verify all `.env` API keys are set
- ✅ Check API keys are valid and have quota
- ✅ Check server logs for detailed errors

### News not loading in LIFF
- ✅ Check `API_BASE_URL` matches Cloudflare Tunnel URL
- ✅ API server must be running
- ✅ Cloudflare Tunnel must be active
- ✅ Check browser Network tab for failed requests

## 📁 Project Structure

```
stocknews/
├── app/
│   ├── api_server.py           # Flask API server
│   ├── line_bot/
│   │   ├── handler.py          # LINE bot webhook
│   │   └── message_formatter.py # Message formatting
│   ├── pipeline/
│   │   ├── stock_news_pipeline.py  # Main pipeline
│   │   ├── news_collector.py       # News collection
│   │   ├── ai_analyzer.py          # AI analysis
│   │   └── web_search.py           # Web search
│   └── scheduler/
│       └── job_scheduler.py    # Scheduled tasks
├── liff/
│   └── index.html              # LIFF dashboard
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── .env                        # Environment variables (NOT in git)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 📝 Git Workflow

```bash
# Make changes
git add .
git commit -m "Your message"
git push

# LIFF auto-deploys to GitHub Pages
```

### Protected Files (in .gitignore)
- `.env` - Never commit secrets!
- `venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.db` - Database files

## 🔐 Security

⚠️ **IMPORTANT:**
- Never commit `.env` file to Git!
- `.env` is protected by `.gitignore`
- Keep API keys safe and secure
- Use environment variables in production

## 📖 Further Reading

- [LINE LIFF Docs](https://developers.line.biz/en/docs/liff/)
- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Made with ❤️ for Stock News Automation**