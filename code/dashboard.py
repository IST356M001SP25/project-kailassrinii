#Load cleaned data into a DataFrame Use:
# st.selectbox() will filter by genre, city, or artist
# plotly.express.bar() will show ticket price ranges
# folium.Map() will plot events by location

import os
import subprocess

# Run extract.py from the root directory
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

# Load data from local JSON
df = load_and_transform()
df = df[df["City"].str.lower() == "syracuse"]
df["Date"] = pd.to_datetime(df["Date"])

# Set default date range
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

# --- Set defaults in session state ---
if "artist_search" not in st.session_state:
    st.session_state.artist_search = ""
if "date_range" not in st.session_state:
    st.session_state.date_range = (min_date, max_date)

# --- Sidebar Filters ---
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

# ---- Main App ----
st.title("Kailas Srinivasan Concert & Event Tracker — Syracuse")
st.markdown("---")

if filtered_df.empty:
    st.warning("No concerts found for the selected filters.")
    st.markdown("Try broadening your filters — clear the artist field or expand the date range.")
else:
    # Interactive Folium Map
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    if not map_df.empty:
        st.subheader("🗺️ Interactive Map")

        map_center = [map_df["Latitude"].mean(), map_df["Longitude"].mean()]
        m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB Positron")
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
    st.subheader("🎵 Upcoming Concerts")
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"]).dt.strftime("%B %d, %Y")
    filtered_df["Time"] = pd.to_datetime(filtered_df["Time"], format="%H:%M:%S", errors="coerce").dt.strftime("%I:%M %p")

    st.dataframe(filtered_df[["Name", "Date", "Time", "Venue", "Ticket URL"]], use_container_width=True)
    st.markdown("---")

    # Events per Venue Chart
    st.subheader("📊 Events per Venue")
    venue_counts = filtered_df["Venue"].value_counts().reset_index()
    venue_counts.columns = ["Venue", "Event Count"]
    fig = px.bar(venue_counts, x="Venue", y="Event Count", title="Events per Venue")
    st.plotly_chart(fig)
    st.markdown("---")

    # Featured Events
    st.subheader("🎤 Featured Events")
    for _, row in filtered_df.head(3).iterrows():
        with st.container():
            st.markdown(f"### {row['Name']}")
            st.markdown(f"**{row['Date']}** at *{row['Venue']}*")
            st.image(row["Image"], use_container_width=True)
            st.link_button("🎟️ Buy Tickets", row["Ticket URL"])
            st.markdown("---")
