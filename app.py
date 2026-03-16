import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- إعدادات الواجهة الملكية ---
st.set_page_config(
    page_title="JOSEPH FAHMY AI", 
    page_icon="👑", # تم تغيير الأيقونة لتاج ملكي
    layout="centered"
)

# --- CSS العظمة والتصميم الملكي (أسود ملكي وذهبي براق) ---
# هذا التصميم مصمم ليكون خفيفاً وسريع التحميل جداً
st.markdown("""
    <style>
    /* خلفية سوداء ملكية عميقة */
    .stApp { 
        background-color: #000000; 
        background-image: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
    }
    
    /* عنوان عريض وفخم جداً باللون الذهبي البراق وبنفس خط اللوجو */
    h1 { 
        color: #D4AF37; /* ذهبي براق */
        text-align: center; 
        font-family: 'Times New Roman', serif; /* خط كلاسيكي فخم */
        font-size: 70px; /* حجم كبير جداً */
        font-weight: bold;
        text-shadow: 0px 4px 10px rgba(212, 175, 55, 0.5); /* وهج ذهبي خفيف */
        margin-bottom: 50px;
    }
    
    /* وهج التاج الملكي */
    .crown-glow {
        color: #D4AF37;
        font-size: 80px;
        text-align: center;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.8);
        margin-bottom: -30px;
    }

    /* تعديل شكل صندوق الإدخال (الدردشة) */
    .stChatInputContainer { 
        border-radius: 50px; 
        border: 3px solid #D4AF37; /* إطار ذهبي سميك */
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3); /* وهج ذهبي */
        background-color: rgba(26, 26, 26, 0.8);
    }
    
    /* تعديل النص داخل صندوق الإدخال */
    .stChatInput textarea { 
        color: #ffffff !important; 
        font-size: 18px; 
    }
    
    /* تعديل زر الإرسال */
    .stChatInput button { 
        background: linear-gradient(45deg, #D4AF37, #BF953F); /* تدرج ذهبي */
        color: black !important; 
        border-radius: 50%; 
        font-weight: bold;
    }
    
    /* تذييل الصفحة */
    .footer {
        text-align: center;
        color: #BF953F;
        font-family: 'Times New Roman', serif;
        font-size: 20px;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# إضافة التاج الملكي قبل العنوان
st.markdown("<div class='crown-glow'>👑</div>", unsafe_allow_html=True)
st.markdown("<h1>JOSEPH FAHMY AI</h1>", unsafe_allow_html=True)

# --- تشغيل المحرك الذكي الصاروخي ---
# نستخدم موديل Gemini 1.5 Flash لضمان أسرع استجابة ممكنة
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash') # هذا هو سر السرعة الصاروخية
    
    # واجهة الدردشة (الدردشة الملكية)
    if prompt := st.chat_input("أمرك مطاع يا جوزيف... اطلب العظمة"):
        with st.chat_message("assistant"):
            with st.spinner("🚀 جاري الاختراق وتنفيذ الأمر الملكي..."):
                try:
                    # طلب الحل بسرعة البرق
                    response = model.generate_content(prompt)
                    
                    # عرض النتيجة
                    st.markdown(response.text)
                    st.balloons() # احتفال بالنجاح
                except Exception as e:
                    st.error(f"حدث خطأ بسيط في تنفيذ الأمر: {e}")
else:
    st.error("⚠️ يا إمبراطور، تأكد من وضع مفتاح GOOGLE_API_KEY في الـ Secrets بالموقع!")

# إضافة تذييل الصفحة الملكي
st.markdown("<div class='footer'>powered by Joseph Fahmy Ai 👑</div>", unsafe_allow_html=True)
