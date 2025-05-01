#Load cleaned data into a DataFrame Use:
# st.selectbox() will filter by genre, city, or artist
# plotly.express.bar() will show ticket price ranges
# folium.Map() will plot events by location

import streamlit as st
from transform import load_and_transform
import plotly.express as px

# Load data
df = load_and_transform()

# App title
st.title("🎤 Concert & Event Tracker")

# Filters
city_filter = st.selectbox("Choose a city:", sorted(df["City"].dropna().unique()))
filtered_df = df[df["City"] == city_filter]

st.subheader(f"Upcoming concerts in {city_filter}")
st.dataframe(filtered_df[["Name", "Date", "Time", "Venue", "Ticket URL"]], use_container_width=True)

# Visualization: Number of events per venue
st.subheader(f"📊 Events per Venue in {city_filter}")
venue_counts = filtered_df["Venue"].value_counts().reset_index()
venue_counts.columns = ["Venue", "Event Count"]

fig = px.bar(venue_counts, x="Venue", y="Event Count", title="Events per Venue")
st.plotly_chart(fig)

# Optional: Show images for first 3 events
st.subheader("🎟️ Featured Events")
for _, row in filtered_df.head(3).iterrows():
    st.markdown(f"**{row['Name']}** - {row['Date']} at {row['Venue']}")
    st.image(row["Image"], width=300)
    st.markdown(f"[Buy Tickets]({row['Ticket URL']})")

