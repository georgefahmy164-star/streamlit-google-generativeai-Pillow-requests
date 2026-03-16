import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image

# إعدادات الواجهة الملكية
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1 { color: #D4AF37; text-align: center; font-size: 45px; text-shadow: 2px 2px #000; }
    .stButton>button { background: linear-gradient(45deg, #D4AF37, #BF953F); color: black; font-weight: bold; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)

# التأكد من وجود المفاتيح السرية (API Keys)
if "GOOGLE_API_KEY" in st.secrets and "OPENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # استخدام موديل Flash لسرعة الاستجابة
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    tab1, tab2 = st.tabs(["🚀 حل الأسئلة", "🎨 إنشاء الصور"])
    
    with tab1:
        img_file = st.file_uploader("ارفع صورة السؤال", type=["jpg", "png", "jpeg"])
        prompt = st.text_input("اكتب سؤالك هنا يا إمبراطور:")
        if st.button("حل الآن"):
            with st.spinner("جاري الحل..."):
                if img_file:
                    res = model.generate_content([prompt if prompt else "حل ما في الصورة", Image.open(img_file)])
                else:
                    res = model.generate_content(prompt)
                st.write(res.text)
                
    with tab2:
        img_prompt = st.text_input("وصف الصورة التي تريد إنشائها:")
        if st.button("إنشاء صورة عظمة"):
            with st.spinner("جاري التخيل..."):
                response = client.images.generate(model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024")
                st.image(response.data[0].url)
else:
    st.error("⚠️ يرجى إضافة GOOGLE_API_KEY و OPENAI_API_KEY في إعدادات Secrets")
