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


def find_route_segments(start_lat: float, start_lon: float,
                        end_lat: float, end_lon: float,
                        corridor_width_km: float = 2.0) -> List[Dict]:
    """Find all segments along a route corridor."""
    route_segments = []

    for segment in ROAD_SEGMENTS:
        # Calculate perpendicular distance from segment to line between start/end
        # Simplified: check if segment is within bounding box + buffer
        lat_min = min(start_lat, end_lat) - corridor_width_km / \
            111  # ~111km per degree
        lat_max = max(start_lat, end_lat) + corridor_width_km / 111
        lon_min = min(start_lon, end_lon) - corridor_width_km / \
            85  # ~85km per degree at UK latitude
        lon_max = max(start_lon, end_lon) + corridor_width_km / 85

        if (lat_min <= segment['latitude'] <= lat_max and
                lon_min <= segment['longitude'] <= lon_max):
            route_segments.append(segment)

    return route_segments


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

    return RouteAssessment(
        route_id=f"route_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        total_distance_km=round(total_distance, 2),
        average_readiness_score=round(avg_score, 1),
        overall_risk_level=overall_risk,
        # Limit to first 50 for demo
        segments=[RoadSegment(**s) for s in segments[:50]],
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
