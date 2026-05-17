import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. SETUP & API CONFIGURATION
# Streamlit ke secrets se key uthana
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# Load restaurant menu safely
@st.cache_data
def load_menu():
    try:
        return pd.read_csv("menu.csv", quotechar='"', skipinitialspace=True)
    except Exception as e:
        st.error("Menu file (menu.csv) nahi mili!")
        return pd.DataFrame()

menu_df = load_menu()

# Gemini 1.5 Flash model setup (Latest and stable)
model = genai.GenerativeModel(model_name='gemini-flash-latest',

# 2. SYSTEM PROMPT FOR CHATBOT
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

    # Prepare complete conversation for Gemini
    chat = model.start_chat(history=[])
    
    # Send system instructions first to guide the bot
    full_prompt = f"{SYSTEM_PROMPT}\n\nHere is the chat history so far. Respond to the last message logically:\n"
    for m in st.session_state.messages:
        role_label = "Customer" if m["role"] == "user" else "Ustad"
        full_prompt += f"{role_label}: {m['content']}\n"
    
    # Call Gemini API safely
    try:
        response = chat.send_message(full_prompt)
        bot_response = response.text
        
        # Add bot response to history and show it
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)
            
    except Exception as e:
        st.error("Ustad busy hain, kripya dobara try karein!")
