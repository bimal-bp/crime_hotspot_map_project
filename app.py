import streamlit as st
import tweepy
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static

# Twitter API credentials (Replace with your own)
consumer_key = 'tOSwDf5Z96GEh65SCE6PgeOP1'
consumer_secret = '2G4mdxtWEKDOT5lv5FOBioLe0aOSUfygrYvO81aRRU8pzWA3g4'
access_token = '1877410492966113280-jfcREN0gQaCQwBm6Tdv90tRQ2ybe53'
access_token_secret = 'ye9VCmmEqAul3YM5vkDeyRme1fhWXmRJIUdiUmxDFjnZn'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAEpYygEAAAAA0RLh3ABQ2zi5yqGqVP9QkdO%2BYVs%3DCD6xF1mnWPzMZkwryFlDX3mk74tgR01kSGwlq4xi3GUyuWDnsu"

# Initialize Tweepy Client
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Streamlit UI
st.title("Crime Hotspot Mapping from Tweets")
st.subheader("Enter your location and visualize nearby crime-related tweets.")

# Location input
latitude = st.number_input("Enter your latitude", format="%f", value=37.7749)
longitude = st.number_input("Enter your longitude", format="%f", value=-122.4194)
current_location = (latitude, longitude)

def search_crime_tweets_v2(query, max_results=10):
    response = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=["geo", "created_at", "text"],
        expansions=["geo.place_id"]
    )

    tweets = []
    if response.data:
        for tweet in response.data:
            place_info = response.includes.get("places", [])
            if place_info:
                for place in place_info:
                    if "geo" in place and "bbox" in place["geo"]:
                        bbox = place["geo"]["bbox"]
                        latitude = (bbox[1] + bbox[3]) / 2
                        longitude = (bbox[0] + bbox[2]) / 2
                        tweets.append({
                            "text": tweet.text,
                            "latitude": latitude,
                            "longitude": longitude
                        })
    return tweets

# Button to generate the map
if st.button("Generate Map"):
    # Query for crime-related tweets
    query = "crime OR theft OR robbery lang:en"
    tweets = search_crime_tweets_v2(query, max_results=50)

    if current_location != (0.0, 0.0):
        # Initialize Folium map
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

        # Display the Folium map in Streamlit
        folium_static(crime_map)
    else:
        st.warning("Please enter a valid location.")
