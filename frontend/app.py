"""
Route10 AI - CAV Road Readiness Assessment Dashboard
Enterprise Demo Interface
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Route10 AI - CAV Road Readiness",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = st.secrets.get("API_URL", "http://localhost:8080")

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .risk-badge-high {
        background-color: #ef4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .risk-badge-medium {
        background-color: #f59e0b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .risk-badge-low {
        background-color: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚗 Route10 AI - CAV Road Readiness Platform</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Infrastructure Assessment for Autonomous Vehicle Deployment</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Route10+AI",
             use_container_width=True)

    st.markdown("### 🎯 Assessment Mode")
    mode = st.radio(
        "Select assessment type:",
        ["Location Assessment", "Route Assessment", "UK Overview"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 📊 Quick Stats")

    try:
        stats_response = requests.get(
            f"{API_BASE_URL}/api/v1/stats", timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            st.metric("Total Segments",
                      f"{stats['total_segments_assessed']:,}")
            st.metric("Avg Readiness", f"{stats['average_readiness_score']}%")
            st.metric("Coverage", f"{stats['coverage_km']} km")
    except Exception as e:
        st.warning("Unable to load stats")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This platform assesses UK road infrastructure readiness for Connected 
    Autonomous Vehicles (CAVs) using AI computer vision and geospatial analytics.
    
    **Built by Route10 AI**  
    Supporting the UK's 2026 AV rollout targets.
    """)

# Main content area
if mode == "Location Assessment":
    st.markdown("## 📍 Single Location Assessment")
    st.markdown("Assess CAV readiness at a specific geographic coordinate.")

    col1, col2 = st.columns(2)

    with col1:
        # Preset locations for demo
        preset = st.selectbox(
            "Choose a preset location:",
            [
                "Custom",
                "Port of Dover (51.1279, 1.3134)",
                "Magna Park MK (52.0406, -0.7594)",
                "M25 Junction 15 (51.6800, -0.5500)",
                "Birmingham (52.4862, -1.8904)"
            ]
        )

        if preset != "Custom":
            lat_default = float(preset.split("(")[1].split(",")[0])
            lon_default = float(preset.split(",")[1].split(")")[0].strip())
        else:
            lat_default = 51.5074
            lon_default = -0.1278

        latitude = st.number_input(
            "Latitude", value=lat_default, format="%.6f")
        longitude = st.number_input(
            "Longitude", value=lon_default, format="%.6f")

        assess_button = st.button(
            "🔍 Assess Location", type="primary", use_container_width=True)

    with col2:
        st.markdown("### 🗺️ Location Preview")
        # Simple map placeholder
        map_data = pd.DataFrame({
            'lat': [latitude],
            'lon': [longitude]
        })
        st.map(map_data, zoom=10)

    if assess_button:
        with st.spinner("Analyzing road segment..."):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/location/readiness",
                    params={"lat": latitude, "lon": longitude},
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    # Results header
                    st.markdown("---")
                    st.markdown("## 📊 Assessment Results")

                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Readiness Score",
                            f"{data['readiness_score']}%",
                            delta=f"{data['readiness_score'] - 70:.1f}" if data['readiness_score'] > 70 else None
                        )

                    with col2:
                        risk_colors = {'COMPLIANT': '🟢',
                                       'MODERATE': '🟡', 'CRITICAL': '🔴'}
                        st.metric(
                            "Risk Level",
                            f"{risk_colors.get(data['risk_level'], '')} {data['risk_level']}"
                        )

                    with col3:
                        st.metric(
                            "Lane Marking Quality",
                            f"{data['infrastructure_quality']['lane_markings'] * 100:.0f}%"
                        )

                    with col4:
                        st.metric(
                            "Features Detected",
                            len(data['detected_features'])
                        )

                    # Detailed breakdown
                    st.markdown("### 🔎 Infrastructure Analysis")

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Infrastructure quality chart
                        quality_data = pd.DataFrame({
                            'Metric': ['Lane Markings', 'Signage Visibility', 'Surface Condition'],
                            'Quality': [
                                data['infrastructure_quality']['lane_markings'] * 100,
                                data['infrastructure_quality']['signage_visibility'] * 100,
                                data['infrastructure_quality']['surface_condition'] * 100
                            ]
                        })

                        fig = px.bar(
                            quality_data,
                            x='Quality',
                            y='Metric',
                            orientation='h',
                            title='Infrastructure Quality Metrics',
                            color='Quality',
                            color_continuous_scale=['red', 'yellow', 'green'],
                            range_color=[0, 100]
                        )
                        fig.update_layout(showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("#### Detected Features")
                        if data['detected_features']:
                            for feature in data['detected_features']:
                                st.markdown(f"- `{feature}`")
                        else:
                            st.info("No special features detected")

                        st.markdown("#### Weather Impact")
                        st.progress(
                            data['weather_impact'], text=f"{data['weather_impact']*100:.0f}% impact")

                    # Recommendations (would come from API in production)
                    st.markdown("### 💡 Recommendations")
                    if data['readiness_score'] >= 75:
                        st.success(
                            "✅ This location meets minimum readiness criteria for AV deployment")
                    elif data['readiness_score'] >= 50:
                        st.warning(
                            "⚠️ Moderate risk - consider infrastructure improvements or operational restrictions")
                    else:
                        st.error(
                            "🚫 Critical issues detected - not recommended for AV deployment without remediation")

                else:
                    st.error(
                        f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

elif mode == "Route Assessment":
    st.markdown("## 🛣️ Route Assessment")
    st.markdown(
        "Analyze CAV readiness along a complete route between two points.")

    # Preset routes
    preset_routes = {
        "Custom": None,
        "Dover to Milton Keynes": {"start": (51.1279, 1.3134), "end": (52.0406, -0.7594)},
        "London to Birmingham": {"start": (51.5074, -0.1278), "end": (52.4862, -1.8904)},
        "Manchester to Leeds": {"start": (53.4808, -2.2426), "end": (53.8008, -1.5491)}
    }

    col1, col2 = st.columns(2)

    with col1:
        route_preset = st.selectbox(
            "Choose preset route:", list(preset_routes.keys()))

        if route_preset != "Custom" and preset_routes[route_preset]:
            start_lat_default = preset_routes[route_preset]["start"][0]
            start_lon_default = preset_routes[route_preset]["start"][1]
            end_lat_default = preset_routes[route_preset]["end"][0]
            end_lon_default = preset_routes[route_preset]["end"][1]
        else:
            start_lat_default, start_lon_default = 51.1279, 1.3134
            end_lat_default, end_lon_default = 52.0406, -0.7594

        st.markdown("#### 🚩 Start Point")
        start_lat = st.number_input(
            "Start Latitude", value=start_lat_default, format="%.6f", key="start_lat")
        start_lon = st.number_input(
            "Start Longitude", value=start_lon_default, format="%.6f", key="start_lon")

    with col2:
        st.markdown("#### 🏁 End Point")
        end_lat = st.number_input(
            "End Latitude", value=end_lat_default, format="%.6f", key="end_lat")
        end_lon = st.number_input(
            "End Longitude", value=end_lon_default, format="%.6f", key="end_lon")

    assess_route_button = st.button(
        "🔍 Assess Route", type="primary", use_container_width=True)

    if assess_route_button:
        with st.spinner("Analyzing route segments... This may take a moment."):
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/v1/route/assess",
                    params={
                        "start_lat": start_lat,
                        "start_lon": start_lon,
                        "end_lat": end_lat,
                        "end_lon": end_lon
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    route_data = response.json()

                    st.markdown("---")
                    st.markdown("## 📊 Route Assessment Results")

                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric("Total Distance",
                                  f"{route_data['total_distance_km']:.1f} km")

                    with col2:
                        st.metric(
                            "Avg Readiness", f"{route_data['average_readiness_score']:.1f}%")

                    with col3:
                        risk_emoji = {'COMPLIANT': '🟢',
                                      'MODERATE': '🟡', 'CRITICAL': '🔴'}
                        st.metric(
                            "Overall Risk",
                            f"{risk_emoji.get(route_data['overall_risk_level'], '')} {route_data['overall_risk_level']}"
                        )

                    with col4:
                        st.metric("Critical Segments", len(
                            route_data['critical_segments']))

                    # Map visualization
                    st.markdown("### 🗺️ Route Visualization")

                    # Prepare map data
                    segments_df = pd.DataFrame([
                        {
                            'lat': s['latitude'],
                            'lon': s['longitude'],
                            'readiness_score': s['readiness_score'],
                            'risk_level': s['risk_level']
                        }
                        for s in route_data['segments']
                    ])

                    # Color by risk level
                    color_map = {'COMPLIANT': 'green',
                                 'MODERATE': 'yellow', 'CRITICAL': 'red'}
                    segments_df['color'] = segments_df['risk_level'].map(
                        color_map)

                    st.map(segments_df[['lat', 'lon']], zoom=7)

                    # Readiness score distribution
                    col1, col2 = st.columns(2)

                    with col1:
                        fig = px.histogram(
                            segments_df,
                            x='readiness_score',
                            nbins=20,
                            title='Readiness Score Distribution',
                            color_discrete_sequence=['#1f77b4']
                        )
                        fig.update_layout(
                            xaxis_title="Readiness Score (%)",
                            yaxis_title="Number of Segments"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        risk_counts = segments_df['risk_level'].value_counts()
                        fig = px.pie(
                            values=risk_counts.values,
                            names=risk_counts.index,
                            title='Risk Level Distribution',
                            color=risk_counts.index,
                            color_discrete_map=color_map
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Recommendations
                    st.markdown("### 💡 Recommendations")
                    for rec in route_data['recommendations']:
                        st.info(rec)

                    # Critical segments detail
                    if route_data['critical_segments']:
                        st.markdown(
                            "### 🚨 Critical Segments Requiring Attention")
                        critical_df = pd.DataFrame([
                            {
                                'Location': f"({s['latitude']:.4f}, {s['longitude']:.4f})",
                                'Score': f"{s['readiness_score']:.1f}%",
                                'Features': ', '.join(s['detected_features'][:3])
                            }
                            for s in route_data['critical_segments'][:10]
                        ])
                        st.dataframe(critical_df, use_container_width=True)

                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

else:  # UK Overview
    st.markdown("## 🇬🇧 UK CAV Readiness Overview")
    st.markdown(
        "National-level insights into road infrastructure readiness for autonomous vehicles.")

    try:
        stats_response = requests.get(
            f"{API_BASE_URL}/api/v1/stats", timeout=10)

        if stats_response.status_code == 200:
            stats = stats_response.json()

            # National metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Coverage", f"{stats['coverage_km']:.0f} km")

            with col2:
                st.metric("Segments Assessed",
                          f"{stats['total_segments_assessed']:,}")

            with col3:
                st.metric("National Avg Score",
                          f"{stats['average_readiness_score']:.1f}%")

            # Risk distribution
            st.markdown("### 📈 National Risk Distribution")

            risk_data = pd.DataFrame({
                'Risk Level': list(stats['risk_distribution'].keys()),
                'Count': list(stats['risk_distribution'].values())
            })

            fig = px.bar(
                risk_data,
                x='Risk Level',
                y='Count',
                title='Road Segments by Risk Category',
                color='Risk Level',
                color_discrete_map={'COMPLIANT': 'green',
                                    'MODERATE': 'yellow', 'CRITICAL': 'red'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Key findings
            st.markdown("### 🔍 Key Findings")

            compliant_pct = (
                stats['risk_distribution']['COMPLIANT'] / stats['total_segments_assessed']) * 100

            col1, col2 = st.columns(2)

            with col1:
                st.success(f"""
                **Deployment Ready**  
                {compliant_pct:.1f}% of assessed routes meet minimum readiness criteria
                """)

            with col2:
                st.warning(f"""
                **Requires Attention**  
                {stats['risk_distribution']['CRITICAL']} critical segments identified
                """)

        else:
            st.error("Unable to load national statistics")

    except Exception as e:
        st.error(f"Error loading overview: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Route10 AI - CAV Road Readiness Platform</strong></p>
    <p>Enterprise Demo | Version 0.1.0 | Powered by AI Computer Vision & Geospatial Analytics</p>
    <p>Supporting the UK's transition to autonomous, zero-emission mobility</p>
</div>
""", unsafe_allow_html=True)
