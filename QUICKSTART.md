# 🚀 Quick Start Guide

## Prerequisites

Before running the Brand Mention & Reputation Tracker, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** installed
- **npm** (comes with Node.js)

## 🎯 One-Click Setup

### Windows Users
```bash
# Run the startup script
start.bat
```

### Mac/Linux Users
```bash
# Make the script executable
chmod +x start.sh

# Run the startup script
./start.sh
```

## 📱 Manual Setup

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 🌐 Access the Application

- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/api/health

## 🎪 Demo Walkthrough

### 1. Add Your First Brand
1. Navigate to the Brands page
2. Click "Add Brand"
3. Enter a popular brand name (e.g., "Apple", "Nike", "Tesla")
4. Set alert thresholds
5. Click "Add Brand"

### 2. Monitor Real-Time Data
1. Return to Dashboard
2. Select your brand from the dropdown
3. Watch live sentiment analysis
4. Monitor mention volume

### 3. Experience Real-Time Features
- **Live Mentions**: See new mentions appear in real-time
- **Sentiment Updates**: Watch sentiment scores update automatically
- **Smart Alerts**: Get notified of spikes and negative sentiment
- **WebSocket Connection**: Real-time updates without page refresh

### 4. Explore Analytics
- **Sentiment Breakdown**: Positive/Negative/Neutral distribution
- **Source Analysis**: Twitter, Reddit, News, Blog mentions
- **Trending Content**: High-engagement mentions
- **Alert History**: Past alerts and resolutions

## 🎯 Key Features to Highlight

### ✨ Real-Time Monitoring
- Live data streaming via WebSocket
- Instant sentiment analysis updates
- Real-time alert notifications

### 🧠 AI-Powered Insights
- Advanced sentiment analysis (simulated)
- Topic clustering and keyword extraction
- Anomaly detection for mention spikes

### 📊 Professional Dashboard
- Beautiful, responsive UI
- Interactive charts and visualizations
- Mobile-friendly design

### 🚨 Intelligent Alerts
- Volume spike detection
- Negative sentiment alerts
- Viral content notifications
- Customizable thresholds

## 🔧 Customization

### Adding Real Data Sources
To connect real APIs, update these files:
- `backend/app/services/mention_collector.py`
- Add your API keys to `backend/.env`

### Modifying UI
- Components are in `frontend/src/components/`
- Styling uses Tailwind CSS
- Icons from Lucide React

## 🏆 Hackathon Tips

### Demo Flow
1. **Opening**: Show the professional dashboard
2. **Brand Addition**: Add a well-known brand live
3. **Real-Time Magic**: Demonstrate live updates
4. **AI Showcase**: Highlight sentiment analysis
5. **Alert System**: Show spike detection
6. **Closing**: Emphasize scalability and business impact

### Talking Points
- "Real-time brand monitoring with AI-powered insights"
- "Scalable architecture using FastAPI and WebSockets"
- "Enterprise-ready with customizable alerts"
- "Beautiful, responsive dashboard for any device"
- "Integrates with all major social platforms"

### Technical Highlights
- Modern tech stack (FastAPI, React, WebSockets)
- Microservices architecture
- Real-time data processing
- AI/ML integration
- Professional UX/UI design

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change port in `backend/app/main.py`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Database errors**: Delete `brand_tracker.db` and restart

### Frontend Issues
- **Port 3000 in use**: Frontend will auto-select next available port
- **Build errors**: Delete `node_modules`, run `npm install` again
- **API connection**: Ensure backend is running on port 8000

### WebSocket Issues
- **Connection failed**: Check firewall settings
- **Real-time not working**: Refresh the page
- **CORS errors**: Verify CORS settings in backend

## 📞 Need Help?

The application includes comprehensive logging and error handling. Check the console output for detailed error messages and debugging information.

**Happy Hacking! 🚀**