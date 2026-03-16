import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Joseph FAHMY AI", page_icon="🔱")
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("⚠️ يرجى إضافة المفتاح في Secrets")

model = genai.GenerativeModel('gemini-1.5-flash')

with st.sidebar:
    st.markdown("### 👑 لوحة التحكم")
    img_file = st.file_uploader("📸 ارفع صورة السؤال", type=["jpg", "png", "jpeg"])

prompt = st.chat_input("أمرك مطاع يا جوزيف...")

if prompt:
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        if img_file:
            res = model.generate_content([prompt, Image.open(img_file)])
        else:
            res = model.generate_content(prompt)
        st.write(res.text)
