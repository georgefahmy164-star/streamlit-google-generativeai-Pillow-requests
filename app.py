import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- إعدادات الواجهة الملكية ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="centered")

# CSS لتسريع الأداء وتحسين الشكل
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; text-align: center; font-family: 'Arial'; text-shadow: 2px 2px #000; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 20px; width: 100%; font-weight: bold; }
    .stTextInput>div>div>input { border: 2px solid #D4AF37; background-color: #1c1f26; color: white; }
    .stChatMessage { border-radius: 15px; border-left: 5px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>الإصدار الأسرع بتقنية الصاروخ 🚀</p>", unsafe_allow_html=True)

# --- تسريع الاتصال بالذكاء الاصطناعي ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ المفتاح السري ناقص!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# استخدام موديل Flash لسرعة صاروخية
model = genai.GenerativeModel('gemini-1.5-flash')

# --- واجهة رفع الصور ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/georgefahmy164-star/streamlit-google-generativeai-Pillow-requests/main/logo.png", width=150) # لو رفعت اللوجو لـ GitHub
    st.markdown("### 👑 غرفة العمليات")
    uploaded_file = st.file_uploader("📸 صور السؤال وارفع هنا", type=["jpg", "jpeg", "png"])
    if st.button("🗑️ مسح المحادثة"):
        st.rerun()

# --- معالجة الطلبات بسرعة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("أمرك مطاع يا جوزيف... اكتب سؤالك هنا"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🚀 جاري التحليل بسرعة البرق..."):
            try:
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    # معالجة الصورة والنص معاً في طلب واحد طلقة
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
