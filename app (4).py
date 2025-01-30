import streamlit as st
import tweepy
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static

# Twitter API credentials (use environment variables for better security)
consumer_key = 'vFzUHNDXikBatixRgHzZQQzkj'
consumer_secret = 'yOC1KeZcbjSFnl33PHvsMQPOex9Haw9B1mTbnDDGzvgCRo1W1D'
access_token = '1882523780482015232-aREdKogp0R5jffxAtpO8wGztwHK0ev'
access_token_secret = 'xkGpICzvH8er1bQjFtsA4hTPbG5Nv0yS5Khb0oFoBtFZT'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAIG8yQEAAAAA8S51rxYBhq6zoRZm9AO34G%2BuTQU%3D16QOXFQ4p3Ef2eyR52GmMBvvi4Pcf9y81GKKTi6Kvj5kmGV9Xv"

# Initialize Tweepy Client
client = tweepy.Client(bearer_token=bearer_token)

# Streamlit UI
st.title("Crime Hotspot Mapping from Tweets")
st.subheader("Enter your location and visualize nearby crime-related tweets.")

# Location input
latitude = st.number_input("Enter your latitude", format="%f")
longitude = st.number_input("Enter your longitude", format="%f")
current_location = (latitude, longitude)

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


def search_crime_tweets_v2(query, max_results=10):
    response = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=["geo", "created_at", "text"],
        user_fields=["location"],
        expansions=["geo.place_id", "author_id"]
    )

    tweets = []
    if response.data:
        for tweet in response.data:
            if response.includes and "places" in response.includes:
                place = response.includes["places"][0]
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
