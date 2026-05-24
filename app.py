import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ Long Case الصوتي التلقائي")

# 2. حماية مفتاح الـ API عبر الجانب الجانبي (Sidebar)
st.sidebar.header("🔑 إعدادات الاتصال الآمن")
api_input = st.sidebar.text_input("أدخل مفتاح Gemini API الجديد هنا:", type="password")
st.sidebar.markdown("[اضغط هنا لإنشاء مفتاح جديد](https://aistudio.google.com/)")

if api_input:
    GEMINI_API_KEY = api_input
elif "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    GEMINI_API_KEY = None

st.write("مرحباً بك يا دكتور أمين وزملائك. اضغط على الزر بالأسفل ثم ابدأ أنت بالتحدث مع المريضة عبر المايك.")

# 3. قائمة السيناريوهات المتنوعة
SCENARIOS = [
    "Placenta Previa (Painless vaginal bleeding in 3rd trimester)",
    "Abruptio Placentae (Painful vaginal bleeding with uterine tenderness in 3rd trimester)",
    "Severe Pre-eclampsia (Headache, blurred vision, epigastric pain, high BP)",
    "Ectopic Pregnancy rupture (Severe lower abdominal pain, missed period, fainting/shock)",
    "Preterm Labor (Regular contractions before 37 weeks with show)",
    "Ovarian Cyst Rupture (Sudden onset unilateral lower abdominal pain, post-coital or after exercise)",
    "Miscarriage / Threatened Abortion (Early pregnancy bleeding with or without mild cramps)",
    "Hyperemesis Gravidarum (Severe intractable vomiting, dehydration, ketonuria in early pregnancy)",
    "Decreased Fetal Movement (Perceived loss of fetal kicks in 3rd trimester)",
    "Molar Pregnancy (Vaginal bleeding, oversized uterus for gestational age, severe nausea)"
]

# 4. الـ System Prompt الطبي المتطور
BASE_SYSTEM_PROMPT = """
You are acting as a medical simulation bot for a 4th-year medical student practicing OB/GYN history taking. 
Your role is to simulate a Libyan/Arab pregnant or gynecological patient.

CRITICAL RULES:
1. Speak ONLY in a very realistic, simple, local Arabic dialect (لهجة عامية بسيطة كأنك مريضة حقيقية في المستشفى).
2. Keep your answers SHORT (1-2 sentences maximum) to mimic a real voice conversation.
3. If they ask for your name, give a typical local name (e.g., فاطمة، مريم، سالمة، خديجة، عائشة). If they ask for age, give a relevant age for the case (e.g., 25-35).
4. Do NOT reveal your medical condition or diagnosis directly. Only describe symptoms when asked.
5. IMPORTANT: Wait for the doctor to ask the first question. Do NOT talk first.
6. You are the patient. Do NOT break character until the user asks for evaluation.
"""

# 5. إدارة الجلسة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_started" not in st.session_state:
    st.session_state.case_started = False
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "current_case_prompt" not in st.session_state:
    st.session_state.current_case_prompt = BASE_SYSTEM_PROMPT

# دالة إرسال آمنة ومباشرة عبر الـ API الرسمي المستقر بدون مكتبات وسيطة تسبب أخطاء
def ask_gemini_direct(audio_path_input=None, text_input=None):
    if not GEMINI_API_KEY:
        return "Error: يرجى إدخال مفتاح الـ API في القائمة الجانبية أولاً لتفعيل المحاكي!"
    
    # استخدام الإصدار المستقر والنهائي v1
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # بناء الذاكرة والسياق
    contents = [{"role": "user", "parts": [{"text": st.session_state.current_case_prompt}]}]
    for msg in st.session_state.messages:
        role_type = "model" if msg["role"] == "patient" else "user"
        contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
    
    # تجهيز المدخل الحالي (صوت أو نص)
    current_parts = []
    if audio_path_input:
        with open(audio_path_input, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode("utf-8")
        current_parts.append({"inline_data": {"mime_type": "audio/wav", "data": audio_data}})
        current_parts.append({"text": "ردي على سؤال الدكتور بصفتك المريضة بالعامية الليبية في سطر واحد قصير جداً ومباشر وطبيعي"})
    else:
        current_parts.append({"text": text_input})
        
    contents.append({"role": "user", "parts": current_parts})
    payload = {"contents": contents}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = res_json.get('error', {}).get('message', 'Unknown API Error')
            return f"Error: {error_msg}"
    except Exception as e:
        return f"Error: {str(e)}"

# زر بدء حالة جديدة
if st.button("🎬 بدء أخذ History لحالة جديدة"):
    st.session_state.messages = []
    st.session_state.case_started = True
    st.session_state.last_processed_audio = None
    
    selected_case = random.choice(SCENARIOS)
    st.session_state.current_case_prompt = f"{BASE_SYSTEM_PROMPT}\nYour specific hidden condition for this session is: {selected_case}. Do NOT reveal it until requested."
    st.success("دخلت المريضة العيادة وجلست على الكرسي وهي صامتة الآن وتنتظر سؤالك. اضغط على المايك بالأسفل وابدأ بسؤالها!")

# 6. عرض المحادثة الآمن والخالي من الـ TypeError
for msg in st.session_state.messages:
    if msg.get("role") == "patient":
        with st.chat_message("user", avatar="🤰"):
            st.write(msg.get("text", ""))
            audio_path = msg.get("audio_path")
            if audio_path and os.path.exists(audio_path):
                st.audio(audio_path)
    elif msg.get("role") == "doctor":
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            st.write(msg.get("text", ""))

# 7. التفاعل عبر المايك أو الكتابة
if st.session_state.case_started:
    st.write("---")
    st.subheader("🎙️ ابدأ بالتحدث مع المريضة:")
    
    audio_value = st.audio_input("اضغط على زر المايك واسأل المريضة")
    user_text_input = st.chat_input("أو اكتب سؤالك هنا...")

    # أ) معالجة الصوت التلقائي
    if audio_value and audio_value != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_value
        
        with open("user_voice.wav", "wb") as f:
            f.write(audio_value.read())
            
        with st.spinner("المريضة تستمع وتجيب..."):
            response_text = ask_gemini_direct(audio_path_input="user_voice.wav")
            
            if "Error" not in response_text:
                tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                tts = gTTS(text=response_text, lang='ar', slow=False)
                tts.save(tts_path)
                
                st.session_state.messages.append({"role": "doctor", "text": "🎤 سؤال صوّتي من الطبيب"})
                st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
                st.rerun()
            else:
                st.error(response_text)

    # ب) معالجة الكتابة
    if user_text_input:
        with st.spinner("المريضة تجيب..."):
            response_text = ask_gemini_direct(text_input=user_text_input)
            
            if "Error" not in response_text:
                tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                tts = gTTS(text=response_text, lang='ar', slow=False)
                tts.save(tts_path)
                
                st.session_state.messages.append({"role": "doctor", "text": user_text_input})
                st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
                st.rerun()
            else:
                st.error(response_text)

# 8. التقييم النهائي
if st.session_state.case_started:
    st.write("---")
    if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
        with st.spinner("جاري تحليل الـ History وإعداد تقرير اللجنة الطبية..."):
            response_text = ask_gemini_direct(text_input="انتهي من تقمص الدور الآن، واكتب لي التقييم الطبي الكامل للحالة باللغة العربية الفصحى، واذكر ما هو التشخيص السري للحالة التي تم اختيارها، وما هي الأسئلة الهامة السريرية التي نسي الطبيب طرحها وما كان يجب عليه التركيز فيه.")
            st.markdown("### 📝 تقرير تقييم اللجنة الطبية:")
            st.info(response_text)
