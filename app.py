import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Streamlit UI
st.title("Crime Hotspot Mapping")

# File upload section
uploaded_file = st.file_uploader("Upload Crime Data CSV", type=["csv"])

if uploaded_file:
    # Load the CSV data
    df = pd.read_csv(uploaded_file)

    # Check if the required columns are present
    required_columns = {"latitude", "longitude", "crime_description"}
    if required_columns.issubset(df.columns):
        st.success("Data loaded successfully!")

        # Center the map on the average coordinates
        avg_lat = df["latitude"].mean()
        avg_lon = df["longitude"].mean()
        crime_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="CartoDB Dark_Matter")

        # Plot each crime point on the map
        for _, row in df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=8,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.7,
                popup=f"Crime: {row['crime_description']}"
            ).add_to(crime_map)

        # Display the Folium map in Streamlit
        folium_static(crime_map)

    else:
        st.error(f"CSV must contain the following columns: {', '.join(required_columns)}")

else:
    st.info("Please upload a CSV file containing crime data.")
