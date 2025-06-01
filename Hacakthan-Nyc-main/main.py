import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from openai import OpenAI
import opik
from opik.integrations.openai import track_openai

# Initialize FastAPI app
app = FastAPI(title="Music Recommendation System")

# Configuration for Spotify
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID') or 'your-spotify-client-id'
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET') or 'your-spotify-client-secret'

# Configure Opik for tracing
opik.configure(api_key=os.getenv('OPIK_API_KEY'))  # Use Opik API key from environment
os.environ["OPIK_PROJECT_NAME"] = "music-recommendation-system"

# Models for request and response
class MusicQuery(BaseModel):
    query: str

class Track(BaseModel):
    title: str
    artist: str
    mood: Optional[str] = None
    genre: Optional[str] = None

class MusicRecommendationResponse(BaseModel):
    query: str
    recommendations: List[Track]

# Initialize Spotify client
def get_spotify_client():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                                client_secret=SPOTIPY_CLIENT_SECRET))
    return sp

# Initialize Friendli client
def get_friendli_client():
    friendli_client = OpenAI(
        base_url="https://api.friendli.ai/serverless/v1",
        api_key=os.environ.get('FRIENDLI_TOKEN')
    )
    return friendli_client

@opik.track
def call_llm(client, messages):
    """Call the Friendli LLM to generate recommendations"""
    response = client.chat.completions.create(
      model="meta-llama-3.3-70b-instruct",
      messages=messages
    )
    return response

@opik.track
def generate_response(friendli_client, user_query):
    """Generate a response based on the user query"""
    prompt = f"""
    You're a helpful music recommendation assistant. Reply to a user message for someone inquiring for
    music recommendations. The user query was: {user_query}

    Based on the user's mood or genre preferences, suggest some tracks that would help.
    """

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = call_llm(friendli_client, messages)
    return response.choices[0].message.content

@opik.track(name="music-recommendation-flow")
def recommendation_flow(user_query):
    """The full recommendation flow, tracked with Opik"""
    # Get clients
    friendli_client = get_friendli_client()
    spotify_client = get_spotify_client()
    
    # Generate response with Friendli
    response_text = generate_response(friendli_client, user_query)
    
    # Use Spotify to fetch real songs based on the context (genre or mood)
    genre = "pop"  # Default genre if none is extracted from the query
    sp_results = spotify_client.search(q=genre, type="track", limit=3)
    spotify_tracks = []
    
    for track in sp_results['tracks']['items']:
        spotify_tracks.append({
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "mood": "Uplifting" if not track.get('mood') else track['mood'],  # Add default if no mood
            "genre": track['genre'] if track.get('genre') else "Pop"  # Add default if no genre
        })

    return {
        "query": user_query,
        "response": response_text,
        "spotify_tracks": spotify_tracks
    }

@app.post("/recommend", response_model=MusicRecommendationResponse)
async def recommend_music(query: MusicQuery):
    """Endpoint to get music recommendations based on user query"""
    result = recommendation_flow(query.query)
    return {
        "query": query.query,
        "recommendations": result["spotify_tracks"],
        "response": result["response"]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the Music Recommendation API! Use /recommend to get music recommendations."}

# Startup event to ensure environment is set up correctly
@app.on_event("startup")
async def startup_event():
    # Check for required environment variables
    if not os.environ.get("FRIENDLI_TOKEN"):
        print("FRIENDLI_TOKEN not found in environment, please set it to use the API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

