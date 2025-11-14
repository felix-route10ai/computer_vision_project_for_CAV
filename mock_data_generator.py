"""
Generate mock CAV readiness data for demonstration purposes.
Based on Route10 AI's 21-feature taxonomy.
"""

import json
import random
from typing import Dict, List
from datetime import datetime

# Feature taxonomy from your prototype
RISK_FEATURES = [
    'construction_zone', 'lane_merge', 'motorway_signage', 'multiple_lanes',
    'bridge', 'bus_stop', 'curve', 'foggy', 'hard_shoulder', 'junction',
    'no_hard_shoulder', 'objects', 'obscured_signage', 'parked_cars',
    'pedestrian_crossing', 'residential', 'roundabout', 'rural', 'signage',
    'single_lane', 'tunnel', 'urban'
]

# Risk weights aligned with your research findings
RISK_WEIGHTS = {
    'construction_zone': 0.85,
    'lane_merge': 0.65,
    'obscured_signage': 0.75,
    'roundabout': 0.70,
    'no_hard_shoulder': 0.60,
    'junction': 0.68,
    'pedestrian_crossing': 0.55,
    'foggy': 0.80,
    'curve': 0.50,
    'tunnel': 0.45,
    'urban': 0.40,
    'residential': 0.35,
    'multiple_lanes': -0.30,  # Positive features
    'hard_shoulder': -0.25,
    'motorway_signage': -0.20,
}

# Major UK logistics routes from your research
MAJOR_ROUTES = [
    {
        'name': 'Dover to Milton Keynes (M2/M25/M1)',
        'start': {'lat': 51.1279, 'lon': 1.3134, 'name': 'Port of Dover'},
        'end': {'lat': 52.0406, 'lon': -0.7594, 'name': 'Magna Park, MK'},
        'distance_km': 189,
        'road_types': ['motorway', 'dual_carriageway']
    },
    {
        'name': 'London to Birmingham (M1)',
        'start': {'lat': 51.5074, 'lon': -0.1278, 'name': 'London'},
        'end': {'lat': 52.4862, 'lon': -1.8904, 'name': 'Birmingham'},
        'distance_km': 193,
        'road_types': ['motorway', 'urban']
    },
    {
        'name': 'Manchester to Leeds (M62)',
        'start': {'lat': 53.4808, 'lon': -2.2426, 'name': 'Manchester'},
        'end': {'lat': 53.8008, 'lon': -1.5491, 'name': 'Leeds'},
        'distance_km': 64,
        'road_types': ['motorway']
    }
]


def generate_segment_data(route: Dict, segment_idx: int, total_segments: int) -> Dict:
    """Generate realistic mock data for a road segment."""

    # Interpolate position along route
    progress = segment_idx / total_segments
    lat = route['start']['lat'] + \
        (route['end']['lat'] - route['start']['lat']) * progress
    lon = route['start']['lon'] + \
        (route['end']['lon'] - route['start']['lon']) * progress

    # Base readiness score (60-95 for motorways, lower for urban)
    base_score = random.uniform(
        70, 90) if 'motorway' in route['road_types'] else random.uniform(50, 75)

    # Randomly assign features based on road type
    detected_features = []
    risk_adjustments = 0

    if 'motorway' in route['road_types']:
        # Motorway-typical features
        if random.random() > 0.7:
            detected_features.append('multiple_lanes')
            risk_adjustments -= RISK_WEIGHTS.get('multiple_lanes', 0)
        if random.random() > 0.8:
            detected_features.append('hard_shoulder')
            risk_adjustments -= RISK_WEIGHTS.get('hard_shoulder', 0)
        if random.random() > 0.95:
            detected_features.append('construction_zone')
            risk_adjustments += RISK_WEIGHTS.get('construction_zone', 0)
    else:
        # Urban/residential features
        if random.random() > 0.6:
            detected_features.append('urban')
            risk_adjustments += RISK_WEIGHTS.get('urban', 0)
        if random.random() > 0.7:
            detected_features.append('pedestrian_crossing')
            risk_adjustments += RISK_WEIGHTS.get('pedestrian_crossing', 0)
        if random.random() > 0.85:
            detected_features.append('roundabout')
            risk_adjustments += RISK_WEIGHTS.get('roundabout', 0)

    # Random challenging conditions
    if random.random() > 0.92:
        detected_features.append('junction')
        risk_adjustments += RISK_WEIGHTS.get('junction', 0)

    # Calculate final score (clamped 0-100)
    final_score = max(0, min(100, base_score - (risk_adjustments * 20)))

    # Risk category based on research thresholds
    if final_score >= 75:
        risk_level = 'COMPLIANT'
        risk_color = 'green'
    elif final_score >= 50:
        risk_level = 'MODERATE'
        risk_color = 'yellow'
    else:
        risk_level = 'CRITICAL'
        risk_color = 'red'

    return {
        'segment_id': f"{route['name'].replace(' ', '_')}_{segment_idx}",
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'readiness_score': round(final_score, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'detected_features': detected_features,
        'infrastructure_quality': {
            # Based on research: 0.5 = critical
            'lane_markings': round(random.uniform(0.4, 0.95), 2),
            'signage_visibility': round(random.uniform(0.6, 1.0), 2),
            'surface_condition': round(random.uniform(0.5, 0.9), 2)
        },
        # Future: real-time API
        'weather_impact': round(random.uniform(0, 0.3), 2),
        'timestamp': datetime.utcnow().isoformat()
    }


def generate_mock_dataset(segments_per_km: int = 20) -> List[Dict]:
    """Generate complete mock dataset for all major routes."""

    all_segments = []

    for route in MAJOR_ROUTES:
        num_segments = int(route['distance_km'] * segments_per_km)

        for i in range(num_segments):
            segment = generate_segment_data(route, i, num_segments)
            segment['route_name'] = route['name']
            all_segments.append(segment)

    return all_segments


if __name__ == "__main__":
    # Generate dataset
    dataset = generate_mock_dataset(segments_per_km=20)  # Every 50m

    print(f"Generated {len(dataset)} road segments")
    print(f"Sample segment:\n{json.dumps(dataset[0], indent=2)}")

    # Save to JSON
    with open('mock_cav_readiness_data.json', 'w') as f:
        json.dump(dataset, f, indent=2)

    print("\nDataset saved to mock_cav_readiness_data.json")
