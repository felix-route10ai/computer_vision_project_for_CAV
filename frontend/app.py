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
import os

# Page config
st.set_page_config(
    page_title="Route10 AI - CAV Road Readiness",
    page_icon="assets/R10_Logo_Sq.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = st.secrets.get("API_URL")

# Custom CSS for professional styling
st.markdown("""
<style>
        :root {
        --route10-primary: #060608;
        --route10-secondary: #ffffff;
        --route10-accent: #06fd01;
        --route10-dark: #262624;
        --route10-light: #f8f9fa;
    }
    
    /* Main app background */
    .stApp {
        background: #f5f5f5;
    }
    
    /* Main content area */
    .main .block-container {
        background: linear-gradient(180deg, #ffffff 0%, #f0fff0 100%);
        padding: 2rem;
        border-radius: 10px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--route10-primary);
    }
    
    /* Sidebar text colors */
    [data-testid="stSidebar"] * {
        color: var(--route10-secondary) !important;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h3 {
        color: var(--route10-accent) !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        border-bottom: 1px solid var(--route10-accent);
        padding-bottom: 0.5rem;
        margin-top: 1rem;
    }
            
    /* Sidebar divider lines - more spacing */
    [data-testid="stSidebar"] hr {
        border-color: var(--route10-accent) !important;
        opacity: 0.3;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Hide the last HR (after ABOUT) */
    [data-testid="stSidebar"] hr:last-of-type {
        display: none;
    }

    /* Style the info box in sidebar */
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] [data-baseweb="notification"] {
        background-color: #262624 !important;
        border: none !important;
        border-left: none !important;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Remove green background from info text */
    [data-testid="stSidebar"] .stInfo {
        background-color: #262624 !important;
        border: none !important;
        color: var(--route10-secondary) !important;
    }

    /* Ensure text in info box is white */
    [data-testid="stSidebar"] .stInfo * {
        color: var(--route10-secondary) !important;
    }
    
    /* Sidebar markdown text */
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--route10-secondary) !important;
    }
    
    /* Sidebar metrics */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--route10-accent) !important;
        font-weight: 700;
        font-size: 1.5rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: var(--route10-secondary) !important;
    }
    
    /* Sidebar radio buttons */
    [data-testid="stSidebar"] label {
        color: var(--route10-secondary) !important;
    }
    
    /* Sidebar divider lines */
    [data-testid="stSidebar"] hr {
        border-color: var(--route10-accent) !important;
        opacity: 0.3;
    }
    
    /* Main content text */
    .main * {
        color: var(--route10-dark);
    }
    
    /* Main content headers */
    .main h1, .main h2, .main h3 {
        color: var(--route10-primary);
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(245deg, var(--route10-primary) 0%, var(--route10-accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background-color: white;
        color: var(--route10-dark);
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--route10-accent);
        box-shadow: 0 0 0 2px rgba(6, 253, 1, 0.1);
    }
    
    /* Select boxes */
    .stSelectbox select {
        background-color: white;
        color: var(--route10-dark);
        border: 1px solid #ddd;
        border-radius: 5px;
    }

    /* Buttons - Route10 style */
    .stButton>button {
        background: linear-gradient(135deg, var(--route10-secondary) 0%, var(--route10-primary) 100%);
        color: var(--route10-secondary);
        border: 1px solid var(--route10-accent);
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background: var(--route10-accent);
        color: var(--route10-primary);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(6, 253, 1, 0.4);
    }

    /* Risk badges - Route10 style */
    .risk-badge-compliant {
        background: var(--route10-accent);
        color: var(--route10-primary);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(6, 253, 1, 0.3);
    }

    .risk-badge-moderate {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }

    .risk-badge-critical {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }

    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left-width: 4px;
    }
    
    /* Success messages - green accent */
    [data-baseweb="notification"] {
        background-color: rgba(6, 253, 1, 0.1);
        border-left: 4px solid var(--route10-accent);
    }
            
    /* Remove top padding from columns */
    [data-testid="column"] {
        padding-top: 0 !important;
    }

    /* Align map container */
    .main .block-container > div:first-child {
        padding-top: 0.5rem;
    }

    /* Remove spacing above main header */
    .main-header {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("assets/logo.png",
             use_container_width=True)

    st.markdown("### Assessment Mode")
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

    # Header row with map
    title_col, map_col = st.columns([1, 1])

    with title_col:
        st.markdown('<div class="main-header">R10 - AV Route Assessment</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sub-header">AI-Powered Infrastructure Assessment for Autonomous Vehicles</div>',
                    unsafe_allow_html=True)
        st.markdown("## Single Location Assessment")
        st.markdown("Assess CAV readiness at a specific geographic coordinate.")

    with map_col:
        # Initialize with default if not set
        if 'latitude' not in st.session_state:
            st.session_state.latitude = 51.1279
            st.session_state.longitude = 1.3134

        map_data = pd.DataFrame({
            'lat': [st.session_state.get('latitude', 51.1279)],
            'lon': [st.session_state.get('longitude', 1.3134)]
        })
        st.map(map_data, zoom=10, height=300)

    st.markdown("---")

    # Input form
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

        # Update session state for map
        st.session_state.latitude = latitude
        st.session_state.longitude = longitude

        assess_button = st.button(
            "🔍 Assess Location", type="primary", use_container_width=True)

    with col2:
        st.markdown("#### 💡 Assessment Tips")
        st.info("""
        **Choose a preset** or enter custom coordinates.
        
        The map (top right) updates automatically as you change values.
        
        Click **Assess Location** to run the analysis.
        """)

        st.markdown("#### 📍 Current Selection")
        st.code(f"Latitude:  {latitude:.6f}\nLongitude: {longitude:.6f}")

    if assess_button:
        with st.spinner("🔍 Analyzing road segment... Checking infrastructure quality, detecting features..."):
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
                            # Red → Yellow → Green
                            color_continuous_scale=[
                                '#ef4444', '#f59e0b', '#00a86b'],
                            range_color=[0, 100]
                        )
                        fig.update_layout(
                            showlegend=False,
                            font=dict(family="Arial, sans-serif", size=12),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
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
    # Header
    st.markdown('<div class="main-header">R10 - AV Route Assessment</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Infrastructure Assessment for Autonomous Vehicles</div>',
                unsafe_allow_html=True)
    st.markdown("")
    st.markdown("## 🛣️ Route Assessment")
    st.markdown(
        "Analyze CAV readiness along a complete route between two points.")

    # Preset routes
    preset_routes = {
        "Custom": None,
        "🚢 Dover to Milton Keynes (189km)": {
            "start": (51.1279, 1.3134),
            "end": (52.0406, -0.7594),
        },
        "📦 Felixstowe to Birmingham (165km)": {
            "start": (51.9614, 1.3511),
            "end": (52.4862, -1.8904),
        },
        "🏭 Southampton to Manchester (265km)": {
            "start": (50.9097, -1.4044),
            "end": (53.4808, -2.2426),
        },
        "🏙️ London to Birmingham (193km)": {
            "start": (51.5074, -0.1278),
            "end": (52.4862, -1.8904),
        },
        "🏙️ Manchester to Leeds (64km)": {
            "start": (53.4808, -2.2426),
            "end": (53.8008, -1.5491),
        },
        "🏙️ Edinburgh to Glasgow (75km)": {
            "start": (55.9533, -3.1883),
            "end": (55.8642, -4.2518),
        },
        "🏙️ Bristol to Cardiff (72km)": {
            "start": (51.4545, -2.5879),
            "end": (51.4816, -3.1791),
        },
        "🚕 Central London Loop (15km)": {
            "start": (51.5074, -0.1278),
            "end": (51.5155, -0.0922),
        },
        "🏙️ Manchester City Centre (10km)": {
            "start": (53.4808, -2.2426),
            "end": (53.4723, -2.2360),
        },
        "🛣️ M25 West Section (50km)": {
            "start": (51.4700, -0.4543),
            "end": (51.6800, -0.5500),
        },
        "🌄 Peak District Rural (45km)": {
            "start": (53.3498, -1.5912),
            "end": (53.2058, -1.8842),
        }
    }

    # Initialize session state
    if 'selected_route' not in st.session_state:
        st.session_state.selected_route = "🚢 Dover to Milton Keynes (189km)"
    if 'start_lat' not in st.session_state:
        st.session_state.start_lat = 51.1279
    if 'start_lon' not in st.session_state:
        st.session_state.start_lon = 1.3134
    if 'end_lat' not in st.session_state:
        st.session_state.end_lat = 52.0406
    if 'end_lon' not in st.session_state:
        st.session_state.end_lon = -0.7594

    # Route selection
    route_preset = st.selectbox(
        "Choose preset route:",
        list(preset_routes.keys()),
        index=list(preset_routes.keys()).index(st.session_state.selected_route)
    )

    if route_preset != st.session_state.selected_route:
        st.session_state.selected_route = route_preset
        if route_preset != "Custom" and preset_routes[route_preset]:
            st.session_state.start_lat = preset_routes[route_preset]["start"][0]
            st.session_state.start_lon = preset_routes[route_preset]["start"][1]
            st.session_state.end_lat = preset_routes[route_preset]["end"][0]
            st.session_state.end_lon = preset_routes[route_preset]["end"][1]
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🚩 Start Point")
        start_lat = st.number_input(
            "Start Latitude",
            value=float(st.session_state.start_lat),
            format="%.6f",
            # ← Dynamic key!
            key=f"start_lat_{st.session_state.selected_route}"
        )
        start_lon = st.number_input(
            "Start Longitude",
            value=float(st.session_state.start_lon),
            format="%.6f",
            # ← Dynamic key!
            key=f"start_lon_{st.session_state.selected_route}"
        )

    with col2:
        st.markdown("#### 🏁 End Point")
        end_lat = st.number_input(
            "End Latitude",
            value=float(st.session_state.end_lat),
            format="%.6f",
            key=f"end_lat_{st.session_state.selected_route}"  # ← Dynamic key!
        )
        end_lon = st.number_input(
            "End Longitude",
            value=float(st.session_state.end_lon),
            format="%.6f",
            key=f"end_lon_{st.session_state.selected_route}"  # ← Dynamic key!
        )

    # Only allow assessment for available routes
    available_routes = [
        "🚢 Dover to Milton Keynes (189km)",
        "🏙️ London to Birmingham (193km)",
        "🏙️ Manchester to Leeds (64km)"
    ]

    route_supported = route_preset in available_routes
    assess_route_button = st.button(
        "🔍 Assess Route", type="primary", use_container_width=True, disabled=not route_supported)

    if not route_supported:
        st.warning(
            "❌ No data available for this route. Please select one of the supported routes:")
        for r in available_routes:
            st.markdown(f"- {r}")

    if route_preset != st.session_state.selected_route:
        st.session_state.selected_route = route_preset
        if route_preset != "Custom" and preset_routes[route_preset]:
            st.session_state.start_lat = preset_routes[route_preset]["start"][0]
            st.session_state.start_lon = preset_routes[route_preset]["start"][1]
            st.session_state.end_lat = preset_routes[route_preset]["end"][0]
            st.session_state.end_lon = preset_routes[route_preset]["end"][1]
        st.rerun()

    if assess_route_button:
        with st.spinner(f"🗺️ Analyzing route ({route_preset})... This may take 10-15 seconds for longer routes..."):
            # Add progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("📡 Querying API...")
            progress_bar.progress(25)

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

                status_text.text("🧮 Processing segments...")
                progress_bar.progress(75)

                if response.status_code == 200:
                    status_text.text("✅ Complete!")
                    progress_bar.progress(100)

                    # Clear progress indicators after 1 second
                    import time
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    route_data = response.json()

                    # Store in session state ← ADD THIS
                    st.session_state.route_results = route_data

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

                elif response.status_code == 404:
                    st.error(f"""
                    ❌ **No Data Available for This Route**
    
                    The mock dataset doesn't include segments for this route yet.
    
                     **Routes with data:**
                    - 🚢 Dover to Milton Keynes
                    - 🏙️ London to Birmingham  
                    - 🏙️ Manchester to Leeds
    
                    For production, all UK routes will be covered!
                """)

                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

elif mode == "UK Overview":
    st.markdown('<div class="main-header">R10 - AV Route Assessment</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Infrastructure Assessment for Autonomous Vehicles</div>',
                unsafe_allow_html=True)
    st.markdown("")
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
