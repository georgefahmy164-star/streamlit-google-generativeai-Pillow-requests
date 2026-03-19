import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# 1. إعدادات النظام (العقل الرقمي)
st.set_page_config(page_title="Joseph AI Infinity", page_icon="🎓", layout="wide")

# ربط مفتاح Gemini من إعدادات Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ خطأ: يرجى إضافة GEMINI_KEY في إعدادات Secrets في Streamlit Cloud")

# 2. وظيفة تحويل اللوجو لـ 3D
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

# 3. واجهة الـ 3D الهولوغرافية
hologram = f"""
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

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH AI - ULTIMATE CORE</h1>", unsafe_allow_html=True)
components.html(hologram, height=200)

# 4. إدارة الحالة (لحفظ النتائج)
if "code_result" not in st.session_state: st.session_state.code_result = ""
if "study_result" not in st.session_state: st.session_state.study_result = ""

# 5. لوحة التحكم الجانبية (الرفع والمعالجة)
with st.sidebar:
    st.header("⚙️ أدوات جوزيف")
    file = st.file_uploader("ارفع صورة الكود هنا", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 استخراج الكود"):
                with st.spinner("جاري الاستخراج..."):
                    res = model.generate_content(["استخرج الكود من الصورة بدقة كملف نصي فقط بدون شرح.", img])
                    st.session_state.code_result = res.text
        with col2:
            if st.button("📚 مود المذاكرة"):
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(["اشرح منطق هذا الكود بالتفصيل للمبتدئين.", img])
                    st.session_state.study_result = res.text

# 6. عرض النتائج التعليمية
if st.session_state.code_result:
    with st.expander("💻 الملف البرمجي المستخرج", expanded=True):
        st.code(st.session_state.code_result)
        st.download_button("⬇️ تحميل الملف .py", st.session_state.code_result, "joseph_code.py")

if st.session_state.study_result:
    with st.expander("📖 شرح المعلم الرقمي", expanded=True):
        st.write(st.session_state.study_result)

# 7. نظام الدردشة (الذكاء الاصطناعي)
st.divider()
if "history" not in st.session_state: st.session_state.history = []

for m in st.session_state.history:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("تحدث مع جوزيف..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.write(response.text)
        st.session_state.history.append({"role": "assistant", "content": response.text})
