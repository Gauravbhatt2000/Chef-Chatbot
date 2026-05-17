import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- 1. SETUP ---
load_dotenv()
# Note: Agar aap DeepSeek use kar rahe hain toh uska code thoda alag hoga, 
# filhal hum Gemini ka stable version use kar rahe hain jo sabke liye chalta hai.
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)

# Ustad Persona
SYSTEM_PROMPT = """
You are 'Ustad', an expert Indian restaurant host. 
Be polite, professional, and help customers with the menu.
If someone asks for a dish not in the menu, apologize nicely.
"""

# Fixed: Using 'gemini-pro' because it is more stable for v1beta
try:
    model = genai.GenerativeModel(
        model_name='gemini-flash-latest',
        system_instruction=SYSTEM_PROMPT
    )
except Exception:
    # Fallback agar system_instruction support na kare
    model = genai.GenerativeModel(model_name='gemini-pro')

# --- 2. DATA LOADING ---
@st.cache_data
def load_menu():
    try:
        # quotechar is important for your CSV descriptions with commas
        return pd.read_csv('menu.csv', quotechar='"', skipinitialspace=True)
    except Exception:
        st.error("Menu file (menu.csv) nahi mili!")
        return pd.DataFrame()

menu_df = load_menu()

# --- 3. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "order_list" not in st.session_state:
    st.session_state.order_list = []

# --- 4. UI ---
st.set_page_config(page_title="Ustad AI Restaurant", page_icon="👨‍🍳")
st.title("👨‍🍳 Ustad AI - Your Expert Waiter")

# Sidebar for Order
with st.sidebar:
    st.header("🛒 Order Summary")
    if st.session_state.order_list:
        df_order = pd.DataFrame(st.session_state.order_list)
        st.table(df_order[['Item Name', 'Price']])
        st.subheader(f"Total: ₹{df_order['Price'].sum()}")
        if st.button("Clear Order"):
            st.session_state.order_list = []
            st.rerun()

# --- 5. CHAT LOGIC ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ustad se baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simple logic to check menu
    if "menu" in prompt.lower():
        with st.chat_message("assistant"):
            st.write("Ji, ye raha hamara menu:")
            st.dataframe(menu_df[['Item Name', 'Price', 'Category']], hide_index=True)
            st.session_state.messages.append({"role": "assistant", "content": "Shown the menu."})
    else:
        with st.chat_message("assistant"):
            try:
                # Chat with context
                full_prompt = f"Menu Items: {menu_df['Item Name'].tolist()}\nUser says: {prompt}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Ustad busy hain, kripya dobara try karein!")
