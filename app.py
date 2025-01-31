import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# Geocoder setup
geolocator = Nominatim(user_agent="geoapiExercises")

# Streamlit app
st.title("Map Generation by Location (State and District)")

# Set Location using State and District
st.header("Enter Location (State and District)")
state = st.text_input("Enter State")
district = st.text_input("Enter District")

if st.button("Set Location"):
    if state and district:
        location_name = f"{district}, {state}"
        location = geolocator.geocode(location_name)
        
        if location:
            current_location = (location.latitude, location.longitude)
            st.success(f"Location set to: {current_location}")

            # Create a map centered around the geocoded location
            map_obj = folium.Map(location=current_location, zoom_start=12)

            # Add a marker to the map
            folium.Marker(location=current_location, popup=location_name).add_to(map_obj)

            # Display the map
            st_folium(map_obj, width=700)
        else:
            st.error("Location not found. Please check the input.")
    else:
        st.warning("Please enter both state and district.")
