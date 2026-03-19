import streamlit as st
from openai import OpenAI
import streamlit.components.v1 as components
import base64

# 1. إعداد الصفحة (الستايل والقوة)
st.set_page_config(page_title="Joseph AI Infinity", page_icon="🚀", layout="wide")

# 2. كود تحويل اللوجو لـ Base64 عشان يظهر في الـ 3D
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

try:
    logo_base64 = get_image_base64("logo.jpg")
except:
    logo_base64 = "" # لو مفيش لوجو هيشتغل عادي

# 3. واجهة الـ 3D الهولوغرافية (حقن HTML/JS داخل Streamlit)
hologram_code = f"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<div id="container" style="width: 100%; height: 300px;"></div>
<script>
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 300, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
    renderer.setSize(window.innerWidth, 300);
    document.getElementById('container').appendChild(renderer.domElement);

    // تحميل اللوجو من الـ Base64
    const loader = new THREE.TextureLoader();
    const texture = loader.load('data:image/jpeg;base64,{logo_base64}');
    
    const geometry = new THREE.SphereGeometry(2, 32, 32);
    const material = new THREE.MeshPhongMaterial({{ map: texture, shininess: 100 }});
    const core = new THREE.Mesh(geometry, material);
    scene.add(core);

    const light = new THREE.PointLight(0x3b82f6, 2, 50);
    light.position.set(5, 5, 5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040));

    camera.position.z = 5;

    function animate() {{
        requestAnimationFrame(animate);
        core.rotation.y += 0.02;
        core.position.y = Math.sin(Date.now() * 0.002) * 0.2;
        renderer.render(scene, camera);
    }}
    animate();
</script>
"""

# 4. تصميم الواجهة في Streamlit
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>JOSEPH FAHMY AI - INFINITY</h1>", unsafe_allow_html=True)

# عرض النواة الـ 3D في المنتصف
components.html(hologram_code, height=300)

# 5. منطق الشات (الذاكرة والذكاء)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثات السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إدخال المستخدم
if prompt := st.chat_input("تحدث مع الوعي الرقمي..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # استدعاء OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_KEY"]) # استخدم st.secrets للأمان
    
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت جوزيف فهمي AI، خبير في Battlegrounds والترجمة."},
                *st.session_state.messages
            ]
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
