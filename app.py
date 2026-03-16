import streamlit as st
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import requests
from io import BytesIO

# --- 1. إعدادات الصفحة والواجهة الملكية (Dark & Gold) ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

# تصميم الواجهة بالـ CSS (أسود ملكي وذهبي)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stApp { background-color: #000000; }
    h1 { color: #D4AF37; text-align: center; font-family: 'serif'; font-size: 50px; text-shadow: 2px 2px #333; }
    h3 { color: #D4AF37; font-family: 'sans-serif'; }
    .stButton>button { 
        background: linear-gradient(45deg, #D4AF37, #BF953F); 
        color: black; border: none; border-radius: 20px; 
        font-weight: bold; width: 100%; height: 3.5em; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.03); color: white; background: linear-gradient(45deg, #BF953F, #D4AF37); }
    .stTextInput>div>div>input { border: 1px solid #D4AF37; background-color: #111; color: white; }
    .stTextArea>div>div>textarea { border: 1px solid #D4AF37; background-color: #111; color: white; }
    .stFileUploader { border: 2px dashed #D4AF37; border-radius: 15px; padding: 15px; text-align: center; }
    .success-box { border: 2px solid #D4AF37; border-radius: 10px; padding: 15px; background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# العنوان الملكي
st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #D4AF37;'>نظام الذكاء الاصطناعي المتكامل - سرعة البرق وإنشاء الصور ⚡</p>", unsafe_allow_html=True)

# --- 2. إعدادات المفاتيح السرية (API Keys) ---
if "GOOGLE_API_KEY" not in st.secrets or "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ تأكد من إضافة GOOGLE_API_KEY و OPENAI_API_KEY في إعدادات Streamlit Secrets!")
    st.stop()

# إعداد جوجل (للتحليل والسرعة)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model_flash = genai.GenerativeModel('gemini-1.5-flash')

# إعداد أوبن إيه آي (لإنشاء الصور)
client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# --- 3. واجهة التطبيق الرئيسية (تقسيم الشاشة) ---
col1, col2 = st.columns([1, 2], gap="large")


with col1:
    st.markdown("### 🛠️ غرفة العمليات")
    
    # اختيار نوع العملية (تحليل أم إنشاء صور)
    operation_type = st.radio("ماذا تريد أن تفعل؟", ["💬 تحليل وحل (نص/صورة)", "🎨 إنشاء صورة جديدة"])
    
    # قسم رفع الصور (يظهر فقط في حالة التحليل)
    uploaded_file = None
    if operation_type == "💬 تحليل وحل (نص/صورة)":
        st.markdown("#### 📸 ارفع سؤالك هنا")
        uploaded_file = st.file_uploader("صور المسألة أو السؤال وارفع الصورة", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="الصورة المرفوعة جاهزة", use_container_width=True)

with col2:
    if operation_type == "💬 تحليل وحل (نص/صورة)":
        st.markdown("### 💬 اسأل الإمبراطور (للتحليل)")
        user_query = st.text_area("ماذا تريد أن أحل لك؟ (اكتب سؤالك هنا أو اطلب شرح الصورة)", placeholder="مثال: حل هذه المسألة، أو اشرح لي هذه الفقرة...")
        submit_flash = st.button("🚀 حل بسرعة الصاروخ")
        
        # تنفيذ التحليل (Flash)
        if submit_flash:
            if user_query or uploaded_file:
                with st.spinner("🔱 جاري التحليل بسرعة البرق..."):
                    try:
                        if uploaded_file:
                            image = Image.open(uploaded_file)
                            # دمج الصورة مع النص في طلب واحد
                            response = model_flash.generate_content([user_query if user_query else "اشرح هذه الصورة بالتفصيل وحل ما بها", image])
                        else:
                            response = model_flash.generate_content(user_query)
                        
                        st.markdown("---")
                        st.markdown("### 👑 الحل المقترح:")
                        st.markdown(f"<div class='success-box'>{response.text}</div>", unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"حدث خطأ فني في التحليل: {e}")
            else:
                st.warning("⚠️ اكتب سؤالاً أو ارفع صورة أولاً!")

    else: # في حالة إنشاء الصور
        st.markdown("### 🎨 أنشئ صورتك الأسطورية")
        image_prompt = st.text_area("صِف الصورة التي تريد إنشاءها بدقة:", placeholder="مثال: أسد ذهبي ملكي يرتدي تاجاً، يجلس على عرش أسود فخم، في مدينة تكنولوجية متطورة، أسلوب واقعي ثلاثي الأبعاد")
        submit_image = st.button("🎨 إنشاء صورة عظمة")
        
        # تنفيذ إنشاء الصور (DALL-E 3)
        if submit_image:
            if image_prompt:
                with st.spinner("🎨 جاري تخيل وإنشاء صورتك الأسطورية..."):
                    try:
                        # إنشاء الصورة عبر OpenAI DALL-E 3
                        response = client_openai.images.generate(
                            model="dall-e-3",
                            prompt=image_prompt,
                            n=1,
                            size="1024x1024",
                            quality="hd", # جودة عالية
                            style="vivid" # ألوان زاهية
                        )
                        
                        image_url = response.data[0].url
                        
                        # تحميل الصورة لعرضها وحفظها
                        image_response = requests.get(image_url)
                        img = Image.open(BytesIO(image_response.content))
                        
                        st.markdown("---")
                        st.markdown("### 👑 الصورة التي تم إنشاؤها:")
                        st.image(img, caption="صورتك الملكية جاهزة", use_container_width=True)
                        
                        # زر تحميل الصورة
                        st.download_button(label="💾 تحميل الصورة", data=image_response.content, file_name="joseph_fahmy_ai_art.png", mime="image/png")
                        st.snow() # احتفال بالإنشاء
                        
                    except Exception as e:
                        st.error(f"حدث خطأ فني في إنشاء الصورة: {e}")
            else:
                st.warning("⚠️ صِف الصورة أولاً!")

# --- 4. تذييل الصفحة الملكي ---
st.markdown("<br><hr><p style='text-align: center; color: gray;'>Powered by Joseph Fahmy AI - Gemini 1.5 Flash & DALL-E 3</p>", unsafe_allow_html=True)
import streamlit as st
import google.generativeai as genai
from openai import OpenAI  # تأكد أن ملف requirements.txt يحتوي على openai
from PIL import Image
import requests
from io import BytesIO

# --- الواجهة الملكية ---
st.set_page_config(page_title="JOSEPH FAHMY AI", page_icon="🔱", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1 { color: #D4AF37; text-align: center; font-size: 50px; }
    .stButton>button { background: linear-gradient(45deg, #D4AF37, #BF953F); color: black; font-weight: bold; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔱 JOSEPH FAHMY AI 🔱</h1>", unsafe_allow_html=True)

# التحقق من المفاتيح السرية
if "GOOGLE_API_KEY" not in st.secrets or "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ ناقصك مفاتيح الـ API في الـ Secrets!")
    st.stop()

# إعداد الموديلات
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model_flash = genai.GenerativeModel('gemini-1.5-flash')
client_openai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# باقي الكود الخاص بالتحليل وإنشاء الصور...
# (استخدم نفس المنطق اللي بعتهولك في الرد اللي فات)
