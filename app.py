import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

# --- 1. إعدادات النواة ---
st.set_page_config(page_title="Joseph AI Infinity", page_icon="🧬", layout="wide")

# الربط بمفتاح Gemini (تأكد أنك وضعته في Secrets باسم GEMINI_KEY)
try:
    if "GEMINI_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_KEY"])
        # تم تغيير الاسم هنا لضمان التوافق التام وحل خطأ 404
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ خطأ: GEMINI_KEY غير موجود في إعدادات Secrets!")
except Exception as e:
    st.error(f"⚠️ فشل في الاتصال بالنظام: {str(e)}")

# --- 2. واجهة الـ 3D (Core) ---
def get_image_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_data = get_image_base64("logo.jpg")

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

st.markdown("<h1 style='text-align: center; color: #00f2ff;'>JOSEPH AI - GENESIS</h1>", unsafe_allow_html=True)
components.html(hologram_ui, height=200)

# --- 3. حفظ البيانات (State) ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "code_out" not in st.session_state: st.session_state.code_out = ""

# --- 4. لوحة التحكم الجانبية ---
with st.sidebar:
    st.header("⚙️ مركز التحكم")
    file = st.file_uploader("ارفع صورة كود بايثون", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, use_container_width=True)
        if st.button("🤖 استخراج الكود وفهمه"):
            with st.spinner("جوزيف يحلل..."):
                res = model.generate_content(["Extract and explain this code in Arabic:", img])
                st.session_state.code_out = res.text

if st.session_state.code_out:
    with st.expander("💻 نتائج التحليل", expanded=True):
        st.write(st.session_state.code_out)

# --- 5. نظام الدردشة المباشر ---
st.divider()
for m in st.session_state.chat_history:
    with st.chat_message(m["role"]): st.write(m["content"])

if prompt := st.chat_input("اسأل جوزيف عن أي شيء..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.write(prompt)
    
    with st.chat_message("assistant"):
        try:
            # استخدام الموديل للرد على الدردشة
            response = model.generate_content(f"أنت جوزيف فهمي AI، مساعد ذكي ومحترف. أجب على: {prompt}")
            st.write(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"حدث خطأ في الرد: {str(e)}")
