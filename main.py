"""
FastAPI backend for CAV Road Readiness Assessment API
Route10 AI - Enterprise Demo
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import math
from datetime import datetime

app = FastAPI(
    title="Route10 AI - CAV Road Readiness API",
    description="Assess UK road infrastructure readiness for Connected Autonomous Vehicles",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data (in production, use Cloud SQL/Firestore)
with open('mock_cav_readiness_data.json', 'r') as f:
    ROAD_SEGMENTS = json.load(f)

# Response models


class InfrastructureQuality(BaseModel):
    lane_markings: float = Field(..., ge=0, le=1,
                                 description="Lane marking contrast ratio")
    signage_visibility: float = Field(..., ge=0, le=1)
    surface_condition: float = Field(..., ge=0, le=1)


class RoadSegment(BaseModel):
    segment_id: str
    latitude: float
    longitude: float
    readiness_score: float = Field(..., ge=0, le=100)
    risk_level: str
    risk_color: str
    detected_features: List[str]
    infrastructure_quality: InfrastructureQuality
    weather_impact: float
    timestamp: str


class RouteAssessment(BaseModel):
    route_id: str
    total_distance_km: float
    average_readiness_score: float
    overall_risk_level: str
    segments: List[RoadSegment]
    critical_segments: List[RoadSegment]
    recommendations: List[str]

# Utility functions


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km."""
    R = 6371  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * \
        math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def find_nearest_segment(lat: float, lon: float, max_distance_km: float = 1.0) -> Optional[Dict]:
    """Find nearest road segment to given coordinates."""
    nearest = None
    min_distance = float('inf')

    for segment in ROAD_SEGMENTS:
        distance = haversine_distance(
            lat, lon, segment['latitude'], segment['longitude'])
        if distance < min_distance and distance <= max_distance_km:
            min_distance = distance
            nearest = segment

    return nearest


def point_to_line_distance(px, py, x1, y1, x2, y2):
    """Calculate perpendicular distance from point to line segment."""
    # Vector from start to end
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        # Start and end are the same point
        return math.sqrt((px - x1)**2 + (py - y1)**2)

    # Calculate the parameter t for the projection
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))

    # Find the closest point on the line segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    # Return distance to closest point
    return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)


def find_route_segments(start_lat: float, start_lon: float,
                        end_lat: float, end_lon: float,
                        corridor_width_km: float = 5.0) -> List[Dict]:
    """Find segments along route corridor using perpendicular distance."""
    route_segments = []

    # Convert corridor width to approximate degrees
    corridor_degrees = corridor_width_km / 111  # ~111km per degree latitude

    for segment in ROAD_SEGMENTS:
        seg_lat = segment['latitude']
        seg_lon = segment['longitude']

        # First check bounding box for performance (quick reject)
        lat_min = min(start_lat, end_lat) - corridor_degrees
        lat_max = max(start_lat, end_lat) + corridor_degrees
        lon_min = min(start_lon, end_lon) - corridor_degrees
        lon_max = max(start_lon, end_lon) + corridor_degrees

        if not (lat_min <= seg_lat <= lat_max and lon_min <= seg_lon <= lon_max):
            continue

        # Calculate perpendicular distance to route line
        perp_distance_degrees = point_to_line_distance(
            seg_lon, seg_lat,  # Point
            start_lon, start_lat,  # Line start
            end_lon, end_lat  # Line end
        )

        # Convert to approximate km (rough approximation)
        perp_distance_km = perp_distance_degrees * 111

        # Only include if within corridor
        if perp_distance_km <= corridor_width_km:
            route_segments.append(segment)

    return route_segments


def sample_segments_evenly(segments: List[Dict], max_samples: int = 200) -> List[Dict]:
    """Sample segments evenly across the route for visualization."""
    if len(segments) <= max_samples:
        return segments

    # Calculate step size to get evenly distributed samples
    step = len(segments) / max_samples
    sampled = []

    for i in range(max_samples):
        idx = int(i * step)
        sampled.append(segments[idx])

    return sampled


def generate_recommendations(segments: List[Dict]) -> List[str]:
    """Generate actionable recommendations based on route analysis."""
    recommendations = []

    critical_count = sum(1 for s in segments if s['risk_level'] == 'CRITICAL')
    avg_lane_quality = sum(s['infrastructure_quality']['lane_markings']
                           for s in segments) / len(segments)

    if critical_count > 0:
        recommendations.append(
            f"⚠️ {critical_count} critical risk segments detected - manual review recommended")

    if avg_lane_quality < 0.6:
        recommendations.append(
            "🛣️ Lane marking quality below threshold - consider alternative route or infrastructure upgrade")

    roundabouts = sum(
        1 for s in segments if 'roundabout' in s['detected_features'])
    if roundabouts > 3:
        recommendations.append(
            f"🔄 {roundabouts} roundabouts detected - ensure AV is validated for UK-style roundabouts")

    construction = sum(
        1 for s in segments if 'construction_zone' in s['detected_features'])
    if construction > 0:
        recommendations.append(
            f"🚧 {construction} construction zones - check for real-time updates before deployment")

    return recommendations if recommendations else ["✅ Route meets minimum readiness criteria for AV deployment"]

# API Endpoints


@app.get("/")
def root():
    return {
        "service": "Route10 AI CAV Road Readiness API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "assess_route": "/api/v1/route/assess",
            "location_readiness": "/api/v1/location/readiness",
            "documentation": "/docs"
        }
    }


@app.get("/api/v1/location/readiness", response_model=RoadSegment)
def get_location_readiness(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Get CAV readiness score for a specific location."""

    segment = find_nearest_segment(lat, lon, max_distance_km=0.5)

    if not segment:
        raise HTTPException(
            status_code=404,
            detail="No road segment found within 500m of specified location"
        )

    return RoadSegment(**segment)


@app.get("/api/v1/route/assess", response_model=RouteAssessment)
def assess_route(
    start_lat: float = Query(..., description="Start latitude"),
    start_lon: float = Query(..., description="Start longitude"),
    end_lat: float = Query(..., description="End latitude"),
    end_lon: float = Query(..., description="End longitude"),
    vehicle_type: Optional[str] = Query(
        "generic", description="AV vehicle type (future use)")
):
    """Assess CAV readiness for a route between two points."""

    # Find all segments along route
    segments = find_route_segments(start_lat, start_lon, end_lat, end_lon)

    if not segments:
        raise HTTPException(
            status_code=404,
            detail="No road segments found along specified route"
        )

    # Calculate metrics
    avg_score = sum(s['readiness_score'] for s in segments) / len(segments)
    critical_segments = [s for s in segments if s['risk_level'] == 'CRITICAL']

    # Determine overall risk level
    if avg_score >= 75:
        overall_risk = 'COMPLIANT'
    elif avg_score >= 50:
        overall_risk = 'MODERATE'
    else:
        overall_risk = 'CRITICAL'

    # Calculate total distance
    total_distance = haversine_distance(start_lat, start_lon, end_lat, end_lon)

    # Generate recommendations
    recommendations = generate_recommendations(segments)

    # Sample segments for visualization (AFTER calculations)
    display_segments = sample_segments_evenly(segments, max_samples=1000)

    return RouteAssessment(
        route_id=f"route_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        total_distance_km=round(total_distance, 2),
        average_readiness_score=round(avg_score, 1),
        overall_risk_level=overall_risk,
        segments=[RoadSegment(**s) for s in display_segments],
        critical_segments=[RoadSegment(**s) for s in critical_segments],
        recommendations=recommendations
    )


@app.get("/api/v1/stats")
def get_statistics():
    """Get aggregate statistics across all assessed roads."""

    total_segments = len(ROAD_SEGMENTS)
    avg_score = sum(s['readiness_score']
                    for s in ROAD_SEGMENTS) / total_segments

    risk_distribution = {
        'COMPLIANT': sum(1 for s in ROAD_SEGMENTS if s['risk_level'] == 'COMPLIANT'),
        'MODERATE': sum(1 for s in ROAD_SEGMENTS if s['risk_level'] == 'MODERATE'),
        'CRITICAL': sum(1 for s in ROAD_SEGMENTS if s['risk_level'] == 'CRITICAL')
    }

    return {
        "total_segments_assessed": total_segments,
        "average_readiness_score": round(avg_score, 1),
        "risk_distribution": risk_distribution,
        "coverage_km": round(total_segments * 0.05, 1)  # Assuming 50m segments
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
