import streamlit as st
import tweepy
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Twitter API credentials
consumer_key = 'vFzUHNDXikBatixRgHzZQQzkj'
consumer_secret = 'yOC1KeZcbjSFnl33PHvsMQPOex9Haw9B1mTbnDDGzvgCRo1W1D'
access_token = '1882523780482015232-aREdKogp0R5jffxAtpO8wGztwHK0ev'
access_token_secret = 'xkGpICzvH8er1bQjFtsA4hTPbG5Nv0yS5Khb0oFoBtFZT'
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAIG8yQEAAAAA8S51rxYBhq6zoRZm9AO34G%2BuTQU%3D16QOXFQ4p3Ef2eyR52GmMBvvi4Pcf9y81GKKTi6Kvj5kmGV9Xv'

# Set up Tweepy Client for v2 API
client = tweepy.Client(bearer_token=bearer_token)

# Streamlit app
st.title("Crime Hotspot Mapping using Tweets")

# Set Location
st.header("Set Your Location")
latitude = st.number_input("Enter Latitude", format="%.6f")
longitude = st.number_input("Enter Longitude", format="%.6f")

if st.button("Set Location"):
    current_location = (latitude, longitude)
    st.success(f"Location set to: {current_location}")
else:
    st.warning("Please set a location.")

# Search and Map Crime Tweets
def search_crime_tweets(query, max_results=10):
    response = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=["geo", "created_at", "text"],
        expansions=["geo.place_id"],
        place_fields=["geo"]
    )

    tweets = []
    if response.data:
        for tweet in response.data:
            if tweet.geo:
                place_id = tweet.geo["place_id"]
                place = next((p for p in response.includes["places"] if p["id"] == place_id), None)
                if place and "geo" in place:
                    bbox = place["geo"].get("bbox")
                    if bbox:
                        latitude = (bbox[1] + bbox[3]) / 2
                        longitude = (bbox[0] + bbox[2]) / 2
                        tweets.append({
                            "text": tweet.text,
                            "latitude": latitude,
                            "longitude": longitude
                        })
    return tweets

if st.button("Generate Crime Hotspot Map"):
    if latitude and longitude:
        # Query for crime-related tweets
        query = "crime OR theft OR robbery lang:en"
        tweets = search_crime_tweets(query, max_results=50)

        # Initialize a folium map centered around the user's current location
        crime_map = folium.Map(location=current_location, zoom_start=12, tiles="CartoDB Dark_Matter")

        # Plot tweets on the map if within 5km radius
        for tweet in tweets:
            tweet_location = (tweet["latitude"], tweet["longitude"])
            distance = geodesic(current_location, tweet_location).km
            if distance <= 5:
                folium.CircleMarker(
                    location=tweet_location,
                    radius=10,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.7,
                    popup=f"Tweet: {tweet['text']}"
                ).add_to(crime_map)

        # Display the map
        st_folium(crime_map, width=700)
    else:
        st.error("Please set a valid location.")
