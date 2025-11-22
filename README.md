# 🌍 Multi-Agent Tourism System

A production-ready multi-agent system with a beautiful web interface that helps users plan their trips by providing weather information and tourist attraction suggestions for any place in the world.

## ✨ Features

- **🌤️ Weather Information**: Get current temperature (always in °C) and precipitation probability (rounded) for any location
- **📍 Tourist Attractions**: Get up to 5 suggested tourist attractions with intelligent deduplication
- **💬 Smart Query Processing**: Handles multiple queries in one sentence, greetings, and nonsensical inputs
- **🎨 Modern Web Interface**: Beautiful, responsive frontend built with Flask and vanilla JavaScript
- **🐳 Docker Support**: Ready for deployment with Docker and Docker Compose
- **🔄 Flexible Queries**: Ask for weather only, places only, or both
- **🛡️ Error Handling**: Gracefully handles non-existent places and API errors
- **🌐 Open Source APIs**: Uses free, open-source APIs (no API keys required)

## 🏗️ Architecture

The system consists of:

1. **Parent Agent (Tourism Agent)**: Orchestrates the entire system, extracts place names from user input, determines user intent, handles greetings, splits multiple queries, and coordinates child agents.

2. **Child Agent 1 (Weather Agent)**: Fetches current weather and forecast using the Open-Meteo API. Always displays temperature in °C and rounds precipitation probability.

3. **Child Agent 2 (Places Agent)**: Suggests up to 5 tourist attractions using Nominatim (for geocoding) and Overpass API (for places data). Intelligently deduplicates similar place names.

## APIs Used

1. **Open-Meteo API**: Weather data
   - Endpoint: `https://api.open-meteo.com/v1/forecast`
   - Documentation: https://open-meteo.com/en/docs

2. **Nominatim API**: Geocoding (place name to coordinates)
   - Base URL: `https://nominatim.openstreetmap.org/search`
   - Documentation: https://nominatim.org/release-docs/develop/api/Search/

3. **Overpass API**: Tourist attractions data
   - Base URL: `https://overpass-api.de/api/interpreter`
   - Documentation: https://wiki.openstreetmap.org/wiki/Overpass_API

## 🚀 Quick Start

### Option 1: Web Application (Recommended)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the Flask application:**
```bash
python app.py
```

3. **Open your browser and navigate to:**
```
http://localhost:5000
```

### Option 2: Command Line Interface

Run the CLI version:
```bash
python main.py
```

### Option 3: Docker Deployment

1. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

2. **Or build and run with Docker:**
```bash
docker build -t tourism-ai .
docker run -p 5000:5000 tourism-ai
```

3. **Access the application at:**
```
http://localhost:5000
```

## 📦 Installation

### Prerequisites
- Python 3.8+ (for local development)
- Docker and Docker Compose (for containerized deployment)

### Local Development Setup

1. **Clone or download this repository:**
```bash
git clone <repository-url>
cd Inlke
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

### Example Queries

**Example 1 - Places only:**
```
Input: I'm going to go to Bangalore, let's plan my trip.
Output: In Bangalore these are the places you can go,

- Lalbagh
- Sri Chamarajendra Park
- Bangalore palace
- Bannerghatta National Park
- Jawaharlal Nehru Planetarium
```

**Example 2 - Weather only:**
```
Input: I'm going to go to Bangalore, what is the temperature there
Output: In Bangalore it's currently 24°C with a chance of 35% to rain.
```

**Example 3 - Both weather and places:**
```
Input: I'm going to go to Bangalore, what is the temperature there? And what are the places I can visit?
Output: In Bangalore it's currently 24°C with a chance of 35% to rain. And in bangalore these are the places you can go,

- Lalbagh
- Sri Chamarajendra Park
- Bangalore palace
- Bannerghatta National Park
- Jawaharlal Nehru Planetarium
```

## 📁 Project Structure

```
.
├── agents/
│   ├── __init__.py
│   ├── tourism_agent.py    # Parent agent (orchestrator)
│   ├── weather_agent.py     # Child agent 1 (weather)
│   └── places_agent.py      # Child agent 2 (attractions)
├── templates/
│   └── index.html           # Frontend HTML template
├── static/
│   ├── css/
│   │   └── style.css        # Frontend styles
│   └── js/
│       └── app.js           # Frontend JavaScript
├── app.py                   # Flask web application
├── main.py                  # CLI entry point
├── run.py                   # Production runner
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── .dockerignore            # Docker ignore file
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## How It Works

1. User enters a query with a place name
2. Tourism Agent extracts the place name from the input
3. Tourism Agent determines user intent (weather, places, or both)
4. Places Agent gets coordinates using Nominatim API
5. If weather requested: Weather Agent fetches weather data from Open-Meteo
6. If places requested: Places Agent fetches attractions from Overpass API
7. Tourism Agent combines responses and returns formatted output

## 🎯 Key Improvements

### Place Name Deduplication
- Intelligently removes duplicate and similar place names
- Keeps the most descriptive version of each place
- Handles variations like "Park" vs "Central Park"

### Enhanced Query Processing
- **Greeting Handling**: Responds to "hi", "hello", etc. with helpful instructions
- **Multiple Queries**: Splits and processes multiple questions in one sentence
- **Input Validation**: Provides clear guidance for nonsensical or incomplete inputs

### Improved Formatting
- Temperature always displayed with °C unit
- Precipitation probability rounded to nearest integer
- Better formatting for lists and multi-line responses

## 🛡️ Error Handling

- **Non-existent Places**: Responds with: "I don't know this place exists. Could you please provide a valid place name?"
- **Greetings**: Provides helpful instructions on how to use the system
- **Empty/Invalid Inputs**: Guides users on expected input format
- **API Errors**: Handled gracefully with appropriate error messages

## 🌐 Deployment

### Production Deployment

The application is ready for deployment on platforms like:
- **Heroku**: Use the included `Procfile` (create one if needed)
- **AWS Elastic Beanstalk**: Deploy using Docker
- **Google Cloud Run**: Use Dockerfile
- **Azure Container Instances**: Use Dockerfile
- **DigitalOcean App Platform**: Use Dockerfile
- **Railway**: Use Dockerfile
- **Render**: Use Dockerfile

### Environment Variables

No environment variables are required - the application uses public APIs.

### Health Check

The application includes a health check endpoint:
```
GET /health
```

## 📝 API Endpoints

### Web Interface
- `GET /` - Main web interface

### API
- `POST /api/query` - Process a tourism query
  - Request body: `{"query": "your query here"}`
  - Response: `{"response": "agent response", "success": true/false}`

- `GET /health` - Health check endpoint

## 🧪 Testing

Test the system with various queries:

1. **Greeting**: "Hi" or "Hello"
2. **Weather Only**: "I'm going to Bangalore, what's the temperature?"
3. **Places Only**: "I'm going to Paris, what places can I visit?"
4. **Both**: "I'm going to Tokyo, what's the temperature and what places can I visit?"
5. **Multiple Queries**: "I'm going to London. What's the weather? And what places can I visit?"

## 📋 Notes

- The system uses free, open-source APIs that don't require API keys
- Nominatim API has usage policies - be respectful with request rates
- Overpass API queries may take a few seconds for complex locations
- The system searches for tourist attractions within approximately 10km radius
- All temperature values are displayed in Celsius (°C)
- Precipitation probability is rounded to the nearest integer



