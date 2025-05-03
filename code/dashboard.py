#Load cleaned data into a DataFrame Use:
# st.selectbox() will filter by genre, city, or artist
# plotly.express.bar() will show ticket price ranges
# folium.Map() will plot events by location

import os
import subprocess

# extract.py to update json file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
extract_path = os.path.join(project_root, "run_extract.py")
subprocess.run(["python", extract_path], check=True)

import streamlit as st
import pandas as pd
from transform import load_and_transform
import plotly.express as px
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import base64

# Styling Stuff
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Orbitron', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        color: white;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stTextInput label {
        color: white;
    }
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stDateInput input {
        background-color: white;
        color: #1e1e1e;
        border: 1px solid #ccc;
    }

    /* Keep Reset Filters text blue always */
    .stButton>button {
        color: #1f77b4 !important;
        background-color: #f0f2f6 !important;
        border: none;
        border-radius: 8px;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        color: #1f77b4 !important;
        background-color: #e1e5ed !important;
    }
    </style>
""", unsafe_allow_html=True)


# Load data from data
df = load_and_transform()
df = df[df["City"].str.lower() == "syracuse"]
df["Date"] = pd.to_datetime(df["Date"])

# Date range
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# Default search
if "artist_search" not in st.session_state:
    st.session_state.artist_search = ""
if "date_range" not in st.session_state:
    st.session_state.date_range = (min_date, max_date)

# Logo
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("logo.png")  

st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
        <div style="background-color: #333; border-radius: 50%; padding: 20px;">
            <img src="data:image/png;base64,{logo_base64}" width="80">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Filters
st.sidebar.header("Filter Concerts")

# Reset button
if st.sidebar.button("Reset Filters"):
    st.session_state.artist_search = ""
    st.session_state.date_range = (min_date, max_date)
    st.rerun()

# Artist Search
artist_search = st.sidebar.text_input("Search for an artist:", value=st.session_state.artist_search, key="artist_search")

# Date Slider
selected_range = st.sidebar.slider(
    "Select a date range:",
    min_value=min_date,
    max_value=max_date,
    value=st.session_state.date_range,
    format="MMMM D, YYYY",
    key="date_range"
)

# Apply Filters
filtered_df = df.copy()
if artist_search:
    filtered_df = filtered_df[filtered_df["Name"].str.contains(artist_search, case=False, na=False)]

filtered_df = filtered_df[
    (pd.to_datetime(filtered_df["Date"]).dt.date >= selected_range[0]) &
    (pd.to_datetime(filtered_df["Date"]).dt.date <= selected_range[1])
]

# Main
st.markdown("""
    <div style="background-color:#001f3f;padding:10px 20px;border-radius:6px;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">Syracuse Concert Tracker</h1>
        <p style="color:#ccc;margin:0;"></p>
    </div>
""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No concerts found for the selected filters.")
    st.markdown("Try broadening your filters.")
else:
    # Interactive Map
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    if not map_df.empty:
        st.subheader("Interactive Map")

        map_center = [map_df["Latitude"].mean(), map_df["Longitude"].mean()]
        m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB Dark_Matter")
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in map_df.iterrows():
            popup_html = f"""
            <b>{row['Name']}</b><br>
            {pd.to_datetime(row['Date']).strftime("%B %d, %Y")} at {pd.to_datetime(row['Time'], format='%H:%M:%S', errors='coerce').strftime("%I:%M %p")}<br>
            Venue: {row['Venue']}<br>
            <a href=\"{row['Ticket URL']}\" target=\"_blank\">🎟️ Buy Tickets</a>
            """
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=row["Venue"],
                icon=folium.Icon(color="purple", icon="music", prefix="fa")
            ).add_to(marker_cluster)

        st_folium(m, width=700, height=500)
        st.markdown("---")

# Concert Table
st.subheader("Upcoming Concerts")
filtered_df["Date"] = pd.to_datetime(filtered_df["Date"]).dt.strftime("%B %d, %Y")
filtered_df["Time"] = pd.to_datetime(filtered_df["Time"], format="%H:%M:%S", errors="coerce").dt.strftime("%I:%M %p")
st.dataframe(filtered_df[["Name", "Date", "Time", "Venue", "Ticket URL"]], use_container_width=True)
st.markdown("---")

# Events Chart
st.subheader("Most Popular Venue")
venue_counts = filtered_df["Venue"].value_counts().reset_index()
venue_counts.columns = ["Venue", "Event Count"]
fig = px.bar(venue_counts, x="Venue", y="Event Count", title="Events per Venue")
st.plotly_chart(fig)
st.markdown("---")

# Featured Events
st.subheader("Featured Events")
for _, row in filtered_df.head(3).iterrows():
    with st.container():
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f9f9f9; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); margin-bottom: 20px;'>
            <h3 style='margin-bottom: 5px;'>{row['Name']}</h3>
            <p><strong>{row['Date']}</strong> at <em>{row['Venue']}</em></p>
            <img src="{row['Image']}" style='width: 100%; border-radius: 10px;'/>
            <br><br>
            <a href="{row['Ticket URL']}" target="_blank" style='display: inline-block; background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;'>🎟️ Buy Tickets</a>
        </div>
        """, unsafe_allow_html=True)

# Name  
st.markdown("<div style='text-align: center; font-size: 12px;'>Created by Kailas Srinivasan</div>", unsafe_allow_html=True)
