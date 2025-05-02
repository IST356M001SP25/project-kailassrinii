#Load cleaned data into a DataFrame Use:
# st.selectbox() will filter by genre, city, or artist
# plotly.express.bar() will show ticket price ranges
# folium.Map() will plot events by location

import streamlit as st
import pandas as pd
from transform import load_and_transform
import plotly.express as px

# Load data
df = load_and_transform()
df["Date"] = pd.to_datetime(df["Date"])

# ---- Sidebar Filters ----
st.sidebar.header("🔎 Filter Concerts")

# City Filter
city_filter = st.sidebar.selectbox("Choose a city:", sorted(df["City"].dropna().unique()))
filtered_df = df[df["City"] == city_filter]

# Date Filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_range = st.sidebar.slider(
    "Select a date range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="MMMM D, YYYY",
    help="Slide to filter concerts by date"
)

filtered_df = filtered_df[
    (df["Date"].dt.date >= selected_range[0]) &
    (df["Date"].dt.date <= selected_range[1])
]

# Artist Search
artist_search = st.sidebar.text_input("Search for an artist:")
if artist_search:
    filtered_df = filtered_df[filtered_df["Name"].str.contains(artist_search, case=False)]

# ---- Main App ----
st.title("🎤 Kailas Srinivasan Concert & Event Tracker")
st.markdown("---")

# Map of venues (optional if lat/lon present)
if "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
    st.subheader("🗺️ Venue Locations")
    st.map(filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
    st.markdown("---")

# Table of concerts
st.subheader(f"🎶 Upcoming Concerts in {city_filter}")
st.dataframe(filtered_df[["Name", "Date", "Time", "Venue", "Ticket URL"]], use_container_width=True)
st.markdown("---")

# Events per venue bar chart
st.subheader("📊 Events per Venue")
venue_counts = filtered_df["Venue"].value_counts().reset_index()
venue_counts.columns = ["Venue", "Event Count"]

fig = px.bar(venue_counts, x="Venue", y="Event Count", title="Events per Venue")
st.plotly_chart(fig)
st.markdown("---")

# Featured Events
st.subheader("🎟️ Featured Events")
for _, row in filtered_df.head(3).iterrows():
    st.markdown(f"**{row['Name']}** - {row['Date']} at {row['Venue']}")
    st.image(row["Image"], width=300)
    st.markdown(f"[Buy Tickets]({row['Ticket URL']})")
