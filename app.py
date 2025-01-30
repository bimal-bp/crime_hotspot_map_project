import tweepy
import streamlit as st
from geopy.distance import geodesic
import folium
from streamlit_folium import folium_static
import time

# Twitter API Bearer Token (Replace with your own bearer token)
bearer_token = "AAAAAAAAAAAAAAAAAAAAAIG8yQEAAAAA8S51rxYBhq6zoRZm9AO34G%2BuTQU%3D16QOXFQ4p3Ef2eyR52GmMBvvi4Pcf9y81GKKTi6Kvj5kmGV9Xv"  # Replace with actual bearer token

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
            expansions=["geo.place_id"],
            place_fields=["geo"]
        )

        tweets = []
        places = {place["id"]: place["geo"] for place in response.includes.get("places", [])} if response.includes else {}

        if response.data:
            for tweet in response.data:
                place_id = tweet.geo["place_id"] if tweet.geo else None
                if place_id and place_id in places:
                    # Extract center coordinates from the bounding box
                    bounding_box = places[place_id]["bbox"]
                    tweet_latitude = (bounding_box[1] + bounding_box[3]) / 2
                    tweet_longitude = (bounding_box[0] + bounding_box[2]) / 2

                    # Calculate distance between tweet location and user location
                    distance = geodesic((latitude, longitude), (tweet_latitude, tweet_longitude)).km
                    if distance <= 5:  # Filter tweets within 5 km
                        tweets.append({
                            "text": tweet.text,
                            "latitude": tweet_latitude,
                            "longitude": tweet_longitude
                        })
        return tweets

    except tweepy.errors.TooManyRequests:
        # Handle rate limit error
        st.error("Rate limit exceeded. Please wait for 15 minutes and try again.")
        time.sleep(900)  # Wait for 15 minutes before retrying
        return search_crime_tweets(query, latitude, longitude)

    except Exception as e:
        st.error(f"Error fetching tweets: {str(e)}")
        return []

# Streamlit UI
st.title("Crime Hotspot Mapping from Tweets")
st.subheader("Enter your location and visualize nearby crime-related tweets.")

# Location input
latitude = st.number_input("Enter your latitude", format="%f")
longitude = st.number_input("Enter your longitude", format="%f")
current_location = (latitude, longitude)

# Button to generate the map and display tweets
if st.button("Generate Map"):
    if current_location != (0.0, 0.0):
        query = "crime OR theft OR robbery lang:en"
        tweets = search_crime_tweets(query, latitude, longitude, max_results=50)

        # Initialize Folium map
        crime_map = folium.Map(location=current_location, zoom_start=12, tiles="CartoDB Dark_Matter")

        # Plot tweets on the map
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
        if tweets:
            folium_static(crime_map)
        else:
            st.info("No nearby crime-related tweets found within a 5 km radius.")
    else:
        st.warning("Please enter a valid location.")
