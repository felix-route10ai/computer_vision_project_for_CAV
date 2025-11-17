# Route10 AI - CAV Road Readiness Assessment API

## Overview

The Route10 AI CAV (Connected Autonomous Vehicle) Road Readiness Assessment API provides AI-powered infrastructure analysis to evaluate UK road network readiness for autonomous vehicle deployment.

**Live API Base URL:**
```
https://route10-cav-api-494243287657.europe-west2.run.app
```

---

## Quick Start

### Test the API

```bash
# Health check
curl https://route10-cav-api-494243287657.europe-west2.run.app/

# Get national statistics
curl https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/stats

# Assess a location (Port of Dover)
curl "https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/location/readiness?lat=51.1279&lon=1.3134"
```

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /`

**Description:** Verify API service status

**Example Request:**
```bash
curl https://route10-cav-api-494243287657.europe-west2.run.app/
```

**Response:**
```json
{
  "service": "Route10 AI - CAV Road Readiness API",
  "version": "1.0.0",
  "status": "operational"
}
```

---

### 2. National Statistics

**Endpoint:** `GET /api/v1/stats`

**Description:** Retrieve aggregate statistics for the UK road network assessment

**Example Request:**
```bash
curl https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/stats
```

**Response:**
```json
{
  "total_segments_assessed": 15420,
  "average_readiness_score": 67.3,
  "coverage_km": 2847,
  "risk_distribution": {
    "COMPLIANT": 8234,
    "MODERATE": 5128,
    "CRITICAL": 2058
  }
}
```

---

### 3. Single Location Assessment

**Endpoint:** `GET /api/v1/location/readiness`

**Description:** Assess CAV readiness at a specific geographic coordinate

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | Yes | Latitude (decimal, WGS84) |
| `lon` | float | Yes | Longitude (decimal, WGS84) |

**Example Request:**
```bash
curl "https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/location/readiness?lat=51.1279&lon=1.3134"
```

**Response:**
```json
{
  "latitude": 51.1279,
  "longitude": 1.3134,
  "readiness_score": 72.5,
  "risk_level": "MODERATE",
  "infrastructure_quality": {
    "lane_markings": 0.75,
    "signage_visibility": 0.82,
    "surface_condition": 0.68
  },
  "detected_features": [
    "motorway",
    "good_lighting",
    "clear_signage"
  ],
  "weather_impact": 0.15,
  "timestamp": "2025-01-17T10:30:00Z"
}
```

**Risk Levels:**

| Level | Score Range | Description |
|-------|-------------|-------------|
| `COMPLIANT` | 75-100 | Ready for AV deployment |
| `MODERATE` | 50-74 | Deployment with caution/restrictions |
| `CRITICAL` | 0-49 | Not recommended without remediation |

---

### 4. Route Assessment

**Endpoint:** `GET /api/v1/route/assess`

**Description:** Analyze CAV readiness along a complete route between two points

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_lat` | float | Yes | Starting point latitude |
| `start_lon` | float | Yes | Starting point longitude |
| `end_lat` | float | Yes | Ending point latitude |
| `end_lon` | float | Yes | Ending point longitude |

**Example Request:**
```bash
# Dover to Milton Keynes route
curl "https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/route/assess?start_lat=51.1279&start_lon=1.3134&end_lat=52.0406&end_lon=-0.7594"
```

**Response:**
```json
{
  "start_location": {
    "latitude": 51.1279,
    "longitude": 1.3134
  },
  "end_location": {
    "latitude": 52.0406,
    "longitude": -0.7594
  },
  "total_distance_km": 189.2,
  "average_readiness_score": 68.4,
  "overall_risk_level": "MODERATE",
  "segments": [
    {
      "segment_id": 1,
      "latitude": 51.1279,
      "longitude": 1.3134,
      "readiness_score": 72.5,
      "risk_level": "COMPLIANT",
      "detected_features": ["motorway", "clear_markings"]
    }
  ],
  "critical_segments": [
    {
      "segment_id": 45,
      "latitude": 51.8234,
      "longitude": 0.2156,
      "readiness_score": 42.1,
      "risk_level": "CRITICAL",
      "detected_features": ["poor_markings", "complex_junction"]
    }
  ],
  "recommendations": [
    "Consider alternative routing around critical segments",
    "Infrastructure upgrades recommended for 12 segments"
  ]
}
```

---

## Code Examples

### Python

```python
import requests

BASE_URL = "https://route10-cav-api-494243287657.europe-west2.run.app"

# Get statistics
response = requests.get(f"{BASE_URL}/api/v1/stats")
stats = response.json()
print(f"Total segments assessed: {stats['total_segments_assessed']}")
print(f"Average readiness score: {stats['average_readiness_score']}%")

# Assess single location
response = requests.get(
    f"{BASE_URL}/api/v1/location/readiness",
    params={"lat": 51.1279, "lon": 1.3134}
)
location_data = response.json()
print(f"Readiness Score: {location_data['readiness_score']}%")
print(f"Risk Level: {location_data['risk_level']}")

# Assess route
response = requests.get(
    f"{BASE_URL}/api/v1/route/assess",
    params={
        "start_lat": 51.1279,
        "start_lon": 1.3134,
        "end_lat": 52.0406,
        "end_lon": -0.7594
    }
)
route_data = response.json()
print(f"Total Distance: {route_data['total_distance_km']} km")
print(f"Average Score: {route_data['average_readiness_score']}%")
print(f"Critical Segments: {len(route_data['critical_segments'])}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'https://route10-cav-api-494243287657.europe-west2.run.app';

// Get statistics
async function getStats() {
  const response = await axios.get(`${BASE_URL}/api/v1/stats`);
  console.log('Statistics:', response.data);
}

// Assess location
async function assessLocation(lat, lon) {
  const response = await axios.get(`${BASE_URL}/api/v1/location/readiness`, {
    params: { lat, lon }
  });
  console.log('Location Assessment:', response.data);
}

// Assess route
async function assessRoute(startLat, startLon, endLat, endLon) {
  const response = await axios.get(`${BASE_URL}/api/v1/route/assess`, {
    params: {
      start_lat: startLat,
      start_lon: startLon,
      end_lat: endLat,
      end_lon: endLon
    }
  });
  console.log('Route Assessment:', response.data);
}

// Execute
getStats();
assessLocation(51.1279, 1.3134);
assessRoute(51.1279, 1.3134, 52.0406, -0.7594);
```

### cURL

```bash
# Assess Dover to Milton Keynes route
curl -X GET "https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/route/assess?start_lat=51.1279&start_lon=1.3134&end_lat=52.0406&end_lon=-0.7594" \
  -H "Accept: application/json" | jq .

# Assess multiple locations
for lat in 51.5074 52.4862 53.4808; do
  curl -X GET "https://route10-cav-api-494243287657.europe-west2.run.app/api/v1/location/readiness?lat=${lat}&lon=-0.1278" \
    -H "Accept: application/json" | jq .readiness_score
done
```

---

## Response Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Bad Request - Invalid parameters |
| `404` | Not Found - No data for requested location/route |
| `500` | Internal Server Error |

---

## Data Notes

- **Coordinate System:** WGS84 decimal format
- **Timestamps:** ISO 8601 format (UTC)
- **Current Coverage:** Major UK logistics routes (mock data for demo)
- **Production Features:** Real-time weather overlays, traffic integration, and comprehensive UK coverage

---

## Project Structure

```
computer_vision_project_for_CAV/
├── Dockerfile                  # Container configuration
├── main.py                     # FastAPI application
├── mock_data_generator.py      # Mock data generation
├── requirements.txt            # Python dependencies
├── .dockerignore              # Docker build exclusions
├── .gitignore                 # Git exclusions
└── frontend/                   # Streamlit dashboard
    ├── app.py
    └── assets/
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Docker (optional, for containerization)

### Setup

```bash
# Clone repository
git clone https://github.com/felix-route10ai/computer_vision_project_for_CAV.git
cd computer_vision_project_for_CAV

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate mock data
python mock_data_generator.py

# Run API locally
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

API will be available at: `http://localhost:8080`

### Docker

```bash
# Build image
docker build -t route10-cav-api .

# Run container
docker run -p 8080:8080 route10-cav-api
```

---

## Deployment

The API is deployed on **Google Cloud Run** with automatic scaling and high availability.

### Deploy to GCP Cloud Run

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy route10-cav-api \
  --source . \
  --region europe-west2 \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 60
```

---

## Support & Contact

- **Website:** [route10ai.com](https://route10ai.com)
- **Email:** felix@route10ai.com
- **Project:** CAV Road Readiness Assessment Platform
- **Status:** Demo/Testing Phase

---

## License

© 2025 Route10 AI Ltd. All rights reserved.

---

## Acknowledgments

Built using:
- FastAPI - Modern Python web framework
- Google Cloud Run - Serverless container platform
- Streamlit - Interactive dashboard framework

Supporting the UK's transition to autonomous, zero-emission mobility.
