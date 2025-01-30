import streamlit as st
import folium
from streamlit_folium import folium_static

# Streamlit UI
st.title("Crime Hotspot Mapping from User Input")

# Input fields for latitude, longitude, and crime description
st.subheader("Enter crime details manually")

# Collecting input from the user
latitude = st.number_input("Enter latitude", format="%.6f")
longitude = st.number_input("Enter longitude", format="%.6f")
crime_description = st.text_input("Enter crime description")

# Button to plot the crime location on the map
if st.button("Plot on Map"):
    if latitude and longitude:
        # Initialize the map centered at the given coordinates
        crime_map = folium.Map(location=[latitude, longitude], zoom_start=13, tiles="CartoDB Dark_Matter")

        # Plot the user-provided location
        folium.CircleMarker(
            location=[latitude, longitude],
            radius=8,
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.7,
            popup=f"Crime: {crime_description}" if crime_description else "Crime Location"
        ).add_to(crime_map)

        # Show the map
        folium_static(crime_map)
    else:
        st.warning("Please provide valid latitude and longitude values.")
