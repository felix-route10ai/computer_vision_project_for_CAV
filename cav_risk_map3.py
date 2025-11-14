# 📍 Streamlit App: Interactive CAV Inference Map

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from PIL import Image
import base64
import os

# === Load metadata ===
CSV_PATH = "D:\Google Drive\My Drive\CAV\inference_results\streamlit_metadata.csv"
df = pd.read_csv(CSV_PATH)

# === Sidebar Filters ===
st.sidebar.header("🔍 Filter Options")
features = sorted(df["feature"].unique())
selected_features = st.sidebar.multiselect(
    "Select Feature(s)", features, default=features)
confidence_threshold = st.sidebar.slider(
    "Minimum Confidence", 0.0, 1.0, 0.5, 0.01)

# === Filter Data ===
df_filtered = df[(df["feature"].isin(selected_features)) &
                 (df["confidence"] >= confidence_threshold)]

# === Create Folium Map ===
mid_lat = df_filtered["lat"].mean()
mid_lng = df_filtered["lng"].mean()
m = folium.Map(location=[mid_lat, mid_lng], zoom_start=9, control_scale=True)
marker_cluster = MarkerCluster().add_to(m)

# === Risk Color Mapping (adjustable logic) ===


def get_risk_color(label):
    critical = ["roundabout", "junction", "pedestrian_crossing"]
    medium = ["lane_merge", "construction_zone", "curve"]
    low = ["mutiple_lanes", "signage", "bus_stop"]
    if label in critical:
        return "red"
    elif label in medium:
        return "orange"
    else:
        return "green"


# === Add Markers ===
for _, row in df_filtered.iterrows():
    popup_html = f"""
    <b>Feature:</b> {row['feature']}<br>
    <b>Confidence:</b> {row['confidence']:.2f}<br>
    <img src='file://{row['image_path']}' width='300'>
    """
    folium.Marker(
        location=[row["lat"], row["lng"]],
        icon=folium.Icon(color=get_risk_color(
            row["feature"]), icon="info-sign"),
        popup=folium.Popup(popup_html, max_width=350)
    ).add_to(marker_cluster)

# === Display Map ===
st.title("Route10 - Route Risk Detection Viewer")
st.markdown("""This map shows detected road features along the Dover to Milton Keynes route, with classification results overlayed as colored markers. Click on a marker for details""")
st_data = st_folium(m, width=3000, height=800)
