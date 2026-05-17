import streamlit as st
import pandas as pd
import openai

# 1. SETUP & API CONFIGURATION
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# DeepSeek client initialisation
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# Load restaurant menu
@st.cache_data
def load_menu():
    try:
        return pd.read_csv("menu.csv", quotechar='"', skipinitialspace=True)
    except Exception as e:
        st.error("Menu file (menu.csv) nahi mili!")
        return pd.DataFrame()

menu_df = load_menu()

# 2. USTAD SYSTEM PROMPT
SYSTEM_PROMPT = """
You are 'Ustad', an expert Indian restaurant host.
Be polite, professional, and help customers with the menu.
If someone asks for a dish not in the menu, apologize nicely.
"""

st.title("👨‍🍳 Ustad AI - Your Expert Waiter")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Welcome to our restaurant. How can Ustad help you today?"}]

if "order_list" not in st.session_state:
    st.session_state.order_list = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if user_input := st.chat_input("Ustad se baat karein..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Prepare messages for DeepSeek
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Call DeepSeek API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=api_messages,
            temperature=0.7
        )
        bot_response = response.choices[0].message.content
        
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.write(bot_response)
            
    except Exception as e:
        st.error("Ustad busy hain, kripya dobara try karein!")
