import sys
import subprocess

# --- المرحلة 1: التثبيت الإجباري للمكتبات لضمان عدم حدوث أخطاء ---
def install_requirements():
    packages = ["openai", "google-generativeai", "Pillow", "requests"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_requirements()

import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# --- المرحلة 2: إعدادات الواجهة الملكية (JOSEPH FAHMY AI) ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

# تصميم الـ CSS الفخم (أسود وذهبي)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1 { color: #D4AF37; text-align: center; font-family: 'serif'; font-size: 55px; text-shadow: 3px 3px #222; }
    .stButton>button { 
        background: linear-gradient(45deg, #D4AF37, #BF953F); 
        color: black; border-radius: 25px; font-weight: bold; width: 100%; height: 3.5em; 
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
        border: 1px solid #D4AF37; background-color: #111; color: white; 
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { color: #D4AF37; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)

# --- المرحلة 3: التحقق من المفاتيح السرية (Secrets) ---
if "GOOGLE_API_KEY" in st.secrets and "OPENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model_flash = genai.GenerativeModel('gemini-1.5-flash')

    # تقسيم الموقع لتبويبين (حل الأسئلة و إنشاء الصور)
    tab1, tab2 = st.tabs(["🚀 حل الأسئلة بسرعة البرق", "🎨 توليد صور أسطورية"])

    with tab1:
        col_a, col_b = st.columns([1, 2])
        with col_a:
            uploaded_file = st.file_uploader("📸 ارفع صورة السؤال", type=["jpg", "png", "jpeg"])
            if uploaded_file:
                st.image(uploaded_file, caption="الصورة المرفوعة", use_container_width=True)
        
        with col_b:
            user_query = st.text_area("ماذا تريد أن أحل لك؟", placeholder="اكتب سؤالك هنا...")
            if st.button("🚀 حل الآن"):
                if user_query or uploaded_file:
                    with st.spinner("🔱 جاري الحل بسرعة البرق..."):
                        if uploaded_file:
                            img = Image.open(uploaded_file)
                            response = model_flash.generate_content([user_query if user_query else "حل ما في الصورة", img])
                        else:
                            response = model_flash.generate_content(user_query)
                        st.markdown("### 👑 النتيجة:")
                        st.success(response.text)
                else:
                    st.warning("⚠️ يرجى كتابة سؤال أو رفع صورة!")

    with tab2:
        st.markdown("### 🎨 حوّل خيالك إلى حقيقة")
        img_prompt = st.text_input("صِف الصورة التي تريد إنشاءها بدقة:")
        if st.button("🎨 إنشاء صورة عظمة"):
            if img_prompt:
                with st.spinner("🎨 جاري تخيل صورتك الملكية..."):
                    try:
                        response = client_openai.images.generate(
                            model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024", quality="hd"
                        )
                        st.image(response.data[0].url, caption="الصورة الناتجة من جوزيف فهمي AI")
                    except Exception as e:
                        st.error(f"حدث خطأ في إنشاء الصورة: {e}")
            else:
                st.warning("⚠️ صِف الصورة أولاً!")

else:
    st.error("⚠️ يرجى إضافة GOOGLE_API_KEY و OPENAI_API_KEY في إعدادات Secrets.")

st.markdown("<br><hr><p style='text-align: center; color: gray;'>Powered by Joseph Fahmy AI 🔱</p>", unsafe_allow_html=True)
