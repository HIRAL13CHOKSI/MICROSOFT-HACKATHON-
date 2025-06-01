import streamlit as st
import requests

# Streamlit UI for Music Recommendation,
def main():
    st.title("Music Recommendation System")

# Input query from user,
    query = st.text_input("Enter a query (e.g., 'I lost a football match today, suggest me some music')")

    # Submit button
    if st.button("Get Recommendations"):
        if query:
            # Send POST request to FastAPI backend
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json={"query": query}
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Recommendations:")
                for track in data["recommendations"]:
                    st.write(f"Title: {track['title']}")
                    st.write(f"Artist: {track['artist']}")
                    st.write(f"Mood: {track.get('mood', 'N/A')}")
                    st.write(f"Genre: {track.get('genre', 'N/A')}")
                    st.write("---")
            else:
                st.error(f"Error: {response.status_code}")
        else:
            st.warning("Please enter a query.")
import streamlit as st
import requests

Streamlit UI for Music Recommendation,
def main():
    st.title("Music Recommendation System")

Input query from user,
    query = st.text_input("Enter a query (e.g., 'I lost a football match today, suggest me some music')")

    # Submit button
    if st.button("Get Recommendations"):
        if query:
            # Send POST request to FastAPI backend
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json={"query": query}
            )

            if response.status_code == 200:
                data = response.json()

                st.subheader("Recommendations:")
                for track in data["recommendations"]:
                    st.write(f"Title: {track['title']}")
                    st.write(f"Artist: {track['artist']}")
                    st.write(f"Mood: {track.get('mood', 'N/A')}")
                    st.write(f"Genre: {track.get('genre', 'N/A')}")
                    st.write("---")
            else:
                st.error(f"Error: {response.status_code}")
        else:
            st.warning("Please enter a query.")

Run the app,
if name == "main":
    main()
# Run the app,
if name == "main":
    main()
