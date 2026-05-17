import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# 1. SETUP & API CONFIGURATION
API_KEY = st.secrets["GOOGLE_API_KEY"]

# Naye standard ke hisab se client initialize karein
client = genai.Client(api_key=API_KEY)

# Load restaurant menu safely
@st.cache_data
def load_menu():
    try:
        return pd.read_csv("menu.csv", quotechar='"', skipinitialspace=True)
    except Exception as e:
        st.error("Menu file (menu.csv) nahi mili!")
        return pd.DataFrame()

menu_df = load_menu()

# SYSTEM PROMPT FOR CHATBOT
SYSTEM_PROMPT = """
You are 'Ustad', an expert Indian restaurant host.
Be polite, professional, and help customers with the menu.
If someone asks for a dish not in the menu, apologize nicely.
"""

st.title("👨‍🍳 Ustad AI - Your Expert Waiter")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Welcome to our restaurant. How can Ustad help you today?"}]

# Display past chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input Box
if user_input := st.chat_input("Ustad se baat karein..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Naye SDK ke format mein history convert karein
    formatted_contents = []
    for m in st.session_state.messages:
        # Naya SDK 'user' aur 'model' roles accept karta hai
        sdk_role = "user" if m["role"] == "user" else "model"
        formatted_contents.append(
            types.Content(
                role=sdk_role,
                parts=[types.Part.from_text(text=m["content"])]
            )
        )

    # Call Gemini API safely using the latest recommended model
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            )
        )
        bot_response = response.text
        
        # Add bot response to history and show it
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)
            
    except Exception as e:
        st.error("Ustad busy hain, kripya dobara try karein!")
