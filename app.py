import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image

# --- الواجهة الملكية السوداء والذهبية ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1 { color: #D4AF37; text-align: center; font-family: 'serif'; font-size: 50px; }
    .stButton>button { background: linear-gradient(45deg, #D4AF37, #BF953F); color: black; font-weight: bold; border-radius: 20px; width: 100%; }
    .stTextInput>div>div>input { background-color: #111; color: white; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)

# التحقق من وجود الـ Secrets (لازم تكون ضايفهم في إعدادات Streamlit)
if "GOOGLE_API_KEY" in st.secrets and "OPENAI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model_flash = genai.GenerativeModel('gemini-1.5-flash')

    tab1, tab2 = st.tabs(["🚀 حل صاروخي", "🎨 إنشاء صور عظمة"])

    with tab1:
        st.subheader("اسأل الإمبراطور")
        user_input = st.text_input("اكتب سؤالك هنا...")
        if st.button("حل الآن"):
            with st.spinner("جاري التفكير..."):
                res = model_flash.generate_content(user_input)
                st.write(res.text)

    with tab2:
        st.subheader("تخيّل صورتك")
        img_prompt = st.text_input("وصف الصورة...")
        if st.button("إنشاء"):
            with st.spinner("جاري الرسم..."):
                response = client_openai.images.generate(model="dall-e-3", prompt=img_prompt)
                st.image(response.data[0].url)
else:
    st.warning("⚠️ يا جوزيف، اتأكد إنك ضايف المفاتيح في الـ Secrets عشان السحر يشتغل!")
