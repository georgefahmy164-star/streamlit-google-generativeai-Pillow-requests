import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# 1. إعدادات النواة (Setup)
st.set_page_config(page_title="Joseph AI Infinity", page_icon="🎓", layout="wide")

# جلب المفتاح المجاني من Secrets
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ خطأ: GEMINI_KEY غير موجود في Secrets!")
except Exception as e:
    st.error(f"⚠️ فشل في إعداد Gemini: {str(e)}")

# 2. وظيفة تحويل اللوجو لـ 3D
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

# 3. واجهة الـ 3D (Holographic Core)
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

# 4. إدارة الحالة
if "code_result" not in st.session_state: st.session_state.code_result = ""
if "study_result" not in st.session_state: st.session_state.study_result = ""
if "history" not in st.session_state: st.session_state.history = []

# 5. لوحة التحكم الجانبية (Sidebar)
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
                    res = model.generate_content(["استخرج الكود من هذه الصورة فقط بدقة.", img])
                    st.session_state.code_result = res.text
        with col2:
            if st.button("📚 مود المذاكرة"):
                with st.spinner("جاري التحليل..."):
                    res = model.generate_content(["اشرح منطق هذا الكود البرمجي بالتفصيل.", img])
                    st.session_state.study_result = res.text

# 6. عرض النتائج التعليمية
if st.session_state.code_result:
    with st.expander("💻 الملف البرمجي المستخرج", expanded=True):
        st.code(st.session_state.code_result)
        st.download_button("⬇️ تحميل الملف .py", st.session_state.code_result, "joseph_code.py")

if st.session_state.study_result:
    with st.expander("📖 شرح المعلم الرقمي", expanded=True):
        st.write(st.session_state.study_result)

# 7. نظام الدردشة (Chat) - التعديل الأهم هنا
st.divider()
for m in st.session_state.history:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("تحدث مع جوزيف..."):
    # التأكد أن الرسالة ليست فارغة قبل الإرسال
    if prompt.strip():
        st.session_state.history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            try:
                # إضافة سياق لـ Gemini لضمان ردود احترافية
                full_prompt = f"أنت جوزيف AI المساعد الشخصي لجورج فهمي. أجب على: {prompt}"
                response = model.generate_content(full_prompt)
                
                if response and response.text:
                    st.write(response.text)
                    st.session_state.history.append({"role": "assistant", "content": response.text})
                else:
                    st.error("جوزيف لم يستطع توليد رد، حاول مرة أخرى.")
            except Exception as e:
                st.error(f"خطأ في الاتصال: {str(e)}")
