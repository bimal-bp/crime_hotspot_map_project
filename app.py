import tweepy
import streamlit as st
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static
import time

# Twitter API Bearer Token (Replace with your own bearer token)
bearer_token = "AAAAAAAAAAAAAAAAAAAAANxYygEAAAAAxv9BHK27MAArTnGhV6w5QnA7JUc%3DXsj3FQmRH5wrs70FK0UZrm4WX8VeRB53oGsDSnGXboliT7GPh9"

# Initialize Tweepy Client
client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)

# Function to search for crime-related tweets
def search_crime_tweets(query, latitude, longitude, max_results=50):
    try:
        # Perform the Twitter API request to search for recent tweets
        response = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=["geo", "created_at", "text"],
            expansions=["geo.place_id"]
        )

        tweets = []
        if response.data:
            # Loop through the tweets to check for geographical information
            for tweet in response.data:
                if tweet.geo:
                    tweet_location = tweet.geo['coordinates']
                    tweet_latitude = tweet_location['lat']
                    tweet_longitude = tweet_location['long']

                    # Calculate distance between the tweet location and the input location
                    distance = geodesic((latitude, longitude), (tweet_latitude, tweet_longitude)).km
                    if distance <= 5:  # Consider tweets within 5 km radius
                        tweets.append({
                            "text": tweet.text,
                            "latitude": tweet_latitude,
                            "longitude": tweet_longitude
                        })
        return tweets

    except tweepy.errors.TooManyRequests as e:
        # Handle rate limit error
        print("Rate limit exceeded, waiting for reset...")
        time.sleep(900)  # Wait for 15 minutes before retrying
        return search_crime_tweets(query, latitude, longitude)

# Streamlit UI
st.title("Crime Hotspot Mapping from Tweets")
st.subheader("Enter your location and visualize nearby crime-related tweets.")

# Location input
latitude = st.number_input("Enter your latitude", format="%f")
longitude = st.number_input("Enter your longitude", format="%f")
current_location = (latitude, longitude)

# Button to generate the map and display tweets
if st.button("Generate Map"):
    query = "crime OR theft OR robbery lang:en"
    tweets = search_crime_tweets(query, latitude, longitude, max_results=50)

    if current_location != (0.0, 0.0):
        # Initialize Folium map
        crime_map = folium.Map(location=current_location, zoom_start=12, tiles="CartoDB Dark_Matter")

        # Plot tweets on the map if they are within 5km radius
        for tweet in tweets:
            tweet_location = (tweet["latitude"], tweet["longitude"])
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
