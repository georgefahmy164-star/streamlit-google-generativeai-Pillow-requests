import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. تصميم الواجهة الإمبراطورية ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #D4AF37; }
    h1 { text-align: center; font-size: 50px; text-shadow: 0 0 10px #D4AF37; }
    .stChatInputContainer { border: 2px solid #D4AF37 !important; border-radius: 25px; }
    </style>
    """, unsafe_allow_html=True)

# عرض الاسم
st.markdown("<h1>🔱 JOSEPH FAHMY AI | OS </h1>", unsafe_allow_html=True)

# --- 2. تفعيل العقل (The Engine) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # الذاكرة البسيطة
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض المحادثة
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # المدخلات
    with st.sidebar:
        st.header("📸 Vision AI")
        img_file = st.file_uploader("ارفع صورة للتحليل", type=["jpg", "png", "jpeg"])

    if prompt := st.chat_input("أمرك مطاع يا جوزيف..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                if img_file:
                    img = Image.open(img_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            except Exception as e:
                st.error(f"⚠️ المحرك واجه مشكلة: {e}")
else:
    st.error("🛑 يا جوزيف، مفتاح API مش شغال أو مش موجود في الـ Secrets!")

st.markdown("<p style='text-align: center; color: #333;'>Joseph Fahmy Transformer Engine v2.0</p>", unsafe_allow_html=True)
