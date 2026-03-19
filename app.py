import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# --- 1. إعدادات الصفحة الأساسية ---
st.set_page_config(page_title="Joseph AI Infinity", page_icon="🎓", layout="wide")

# --- 2. إعداد محرك الذكاء الاصطناعي (Gemini) ---
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # استخدمنا النسخة المستقرة لضمان عدم حدوث خطأ 404
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    else:
        st.error("⚠️ يرجى إضافة GEMINI_KEY في إعدادات Secrets")
except Exception as e:
    st.error(f"⚠️ خطأ في تهيئة النظام: {str(e)}")

# --- 3. وظيفة معالجة اللوجو ---
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

# --- 4. واجهة الـ 3D الهولوغرافية ---
hologram_ui = f"""
<div id="viz" style="width: 100%; height: 200px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/200, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(window.innerWidth, 200);
    document.getElementById('viz').appendChild(renderer.domElement);
    const tex = new THREE.TextureLoader().load('data:image/jpeg;base64,{logo_data}');
    const core = new THREE.Mesh(new THREE.SphereGeometry(2, 32, 32), new THREE.MeshPhongMaterial({{ map: tex }}));
    scene.add(core);
    const light = new THREE.PointLight(0x00f2ff, 2, 50); light.position.set(5, 5, 5); scene.add(light);
    camera.position.z = 5;
    function animate() {{ requestAnimationFrame(animate); core.rotation.y += 0.02; renderer.render(scene, camera); }}
    animate();
</script>
"""

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH AI - ULTIMATE</h1>", unsafe_allow_html=True)
components.html(hologram_ui, height=200)

# --- 5. حفظ حالة الأزرار والشات ---
if "code_out" not in st.session_state: st.session_state.code_out = ""
if "study_out" not in st.session_state: st.session_state.study_out = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 6. لوحة التحكم الجانبية (Sidebar) ---
with st.sidebar:
    st.header("⚙️ مركز التحكم")
    uploaded_file = st.file_uploader("ارفع صورة كود (بايثون، C++، إلخ)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        img_input = Image.open(uploaded_file)
        st.image(img_input, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🤖 استخراج الكود"):
                with st.spinner("جاري الاستخراج..."):
                    res = model.generate_content(["Extract only the code from this image as text, no explanation.", img_input])
                    st.session_state.code_out = res.text
        with c2:
            if st.button("📚 مود المذاكرة"):
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(["Explain this code in Arabic for a student step by step.", img_input])
                    st.session_state.study_out = res.text

# --- 7. عرض النتائج ---
if st.session_state.code_out:
    with st.expander("💻 الكود المستخرج", expanded=True):
        st.code(st.session_state.code_out)
        st.download_button("⬇️ تحميل الملف", st.session_state.code_out, "joseph_script.py")

if st.session_state.study_out:
    with st.expander("📖 شرح المعلم الرقمي", expanded=True):
        st.write(st.session_state.study_out)

# --- 8. نظام الدردشة المطور ---
st.divider()
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]): st.write(msg["content"])

if user_input := st.chat_input("تحدث مع جوزيف..."):
    if user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.write(user_input)
        
        with st.chat_message("assistant"):
            try:
                ai_response = model.generate_content(f"أنت جوزيف AI المساعد الشخصي لجورج فهمي. أجب باختصار وذكاء: {user_input}")
                st.write(ai_response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response.text})
            except Exception as e:
                st.error(f"خطأ في الرد: {str(e)}")
