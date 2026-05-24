import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ Long Case الصوتي التلقائي المتطور")
st.write("مرحباً بك يا دكتور أمين وزملائك. اضغط على خيار الحالة بالأسفل لتوليد سيناريو ديناميكي فريد ثم ابدأ التحدث مع المريضة.")

# 2. مجمّع المفاتيح السبعة المحمية بنظام التناوب الذكي
API_KEYS_POOL = [
    "AIzaSyCGXIIx3HIMC7GeFZFrcSmXpxZGgUG8K5Q",
    "AIzaSyBXxYZNFlVmpKf1f_oSgWqYVfgC7_spNCU",
    "AIzaSyAA5E6EziXwrm8U3fFFCPkH-s9If3tP674",
    "AIzaSyAn8q3hwFn0K0i_OTOVHdhdTxR5j0MHUyw",
    "AIzaSyC0uiwlDJW_STJL6i9Edl1gDdOiEE63MFc",
    "AIzaSyBHtq_8zblQ52ca93jpGDrhDWwaEll0BuM",
    "AIzaSyAyr2tZVOcYgoCOfF1kXCnPCD41PGSEjxI"
]

# 3. بنك البيانات لتوليد شخصيات وهويات ليبية عشوائية ومختلفة في كل مرة
ARABIC_NAMES = ["فاطمة", "مريم", "سالمة", "خديجة", "عائشة", "نجاة", "هناء", "أمل", "منى", "إيناس", "غادة", "روان", "سارة", "انتصار", "أحلام"]
LIBYAN_CITIES = ["طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "الخمس", "زليتن", "غريان", "البيضاء", "طبرق"]
JOBS = ["ربة بيت", "معلمة مدرسة", "موظفة إدارية", "طالبة جامعية", "مهندسة", "تشتغل في معمل", "لا تعمل"]

# 4. تقسيم السيناريوهات الطبية بدقة وفق طلبك
ANTENATAL_SCENARIOS = [
    "Placenta Previa (Painless vaginal bleeding in 3rd trimester)",
    "Abruptio Placentae (Painful vaginal bleeding with uterine tenderness in 3rd trimester)",
    "Severe Pre-eclampsia (Headache, blurred vision, epigastric pain, high BP around 32 weeks)",
    "Ectopic Pregnancy rupture (Severe lower abdominal pain, missed period, fainting/shock in early weeks)",
    "Preterm Labor (Regular contractions before 37 weeks with bloody show)",
    "Miscarriage / Threatened Abortion (Early pregnancy bleeding with mild uterine cramps)",
    "Hyperemesis Gravidarum (Severe intractable vomiting, dehydration in early trimester)",
    "Decreased Fetal Movement (Perceived loss of fetal kicks in late 3rd trimester)",
    "Gestational Diabetes complications (Polyhydramnios symptoms, large for gestational age baby)",
    "Molar Pregnancy (Vaginal bleeding, oversized uterus, severe morning sickness)"
]

POSTNATAL_SCENARIOS = [
    "Primary Postpartum Hemorrhage - PPH (Heavy bleeding immediately after delivery due to uterine atony)",
    "Secondary Postpartum Hemorrhage (Vaginal bleeding 2 weeks after delivery due to retained placental fragments or infection)",
    "Postpartum Endometritis (Fever, foul-smelling lochia, lower abdominal tenderness 4 days after C-section)",
    "Deep Vein Thrombosis - DVT (Unilateral leg swelling, pain, warmth a week after delivery)",
    "Postpartum Preeclampsia/Eclampsia (New onset severe headache, high BP, or seizure 3 days postpartum)",
    "Mastitis (Painful, red, engorged breast with high fever and chills in a breastfeeding mother)",
    "Postpartum Depression / Psychosis (Severe mood changes, anxiety, or hallucinations 3 weeks after delivery)"
]

GYNAE_SCENARIOS = [
    "Ovarian Cyst Rupture (Sudden onset unilateral lower abdominal pain, post-coital or after exercise)",
    "Pelvic Inflammatory Disease - PID (Chronic pelvic pain, vaginal discharge, deep dyspareunia)",
    "Fibroid Uterus (Heavy menstrual bleeding - menorrhagia, pelvic pressure, progressive anemia)",
    "Cervical Cancer presentation (Post-coital bleeding, intermenstrual bleeding, foul discharge in an older patient)"
]

# 5. الـ System Prompt الطبي الأساسي المتطور
BASE_SYSTEM_PROMPT = """
You are acting as a medical simulation bot for a 4th-year medical student practicing OB/GYN history taking. 
Your role is to simulate a Libyan/Arab patient based on the provided profile.

CRITICAL RULES:
1. Speak ONLY in a very realistic, simple, local Libyan Arabic dialect (لهجة عامية بسيطة كأنك مريضة حقيقية في خيمة أو مستشفى ليبي).
2. Keep your answers SHORT (1-2 sentences maximum) to mimic a real voice conversation.
3. Do NOT reveal your medical condition, hidden diagnosis, or specific medical terms directly. Only describe symptoms naturally when the doctor asks about them.
4. IMPORTANT: Wait for the doctor to ask the first question. Do NOT talk first.
5. You are the patient. Do NOT break character until the user asks for evaluation.
"""

# إدارة الجلسة والذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_started" not in st.session_state:
    st.session_state.case_started = False
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "current_case_prompt" not in st.session_state:
    st.session_state.current_case_prompt = BASE_SYSTEM_PROMPT
if "hidden_case_details" not in st.session_state:
    st.session_state.hidden_case_details = ""

# دالة إرسال ذكية تدور على المفاتيح بالترتيب وتتخطى المفتاح المضغوط تلقائياً
def ask_gemini_direct(audio_path_input=None, text_input=None):
    valid_keys = [k for k in API_KEYS_POOL if k and k != "AIzaSy..."]
    if not valid_keys:
        return "Error: لم يتم العثور على مفاتيح اتصال صالحة!"
        
    start_index = random.randint(0, len(valid_keys) - 1)
    
    for i in range(len(valid_keys)):
        idx = (start_index + i) % len(valid_keys)
        selected_key = valid_keys[idx]
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={selected_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = [{"role": "user", "parts": [{"text": st.session_state.current_case_prompt}]}]
        for msg in st.session_state.messages:
            role_type = "model" if msg["role"] == "patient" else "user"
            contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
        
        current_parts = []
        if audio_path_input:
            with open(audio_path_input, "rb") as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode("utf-8")
            current_parts.append({"inline_data": {"mime_type": "audio/wav", "data": audio_data}})
            current_parts.append({"text": "ردي على سؤال الدكتور بصفتك المريضة بالعامية الليبية وبشكل قصير جداً وفي سطر واحد ومباشر وطبيعي"})
        else:
            current_parts.append({"text": text_input})
            
        contents.append({"role": "user", "parts": current_parts})
        payload = {"contents": contents}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            res_json = response.json()
            if response.status_code == 200:
                return res_json['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429 or "quota" in str(res_json).lower():
                continue
            else:
                error_msg = res_json.get('error', {}).get('message', 'Unknown API Error')
                return f"Error: {error_msg}"
        except Exception as e:
            continue
            
    return "RESOURCE_EXHAUSTED: جميع المفاتيح مشغولة حالياً بالكامل بسبب ضغط الطلاب، يرجى إعادة المحاولة بعد ثوانٍ بسيطة."

# 6. واجهة التحكم لاختيار نوع الـ History المطلوب وتوليد البيانات ديناميكياً
st.subheader("📋 اختر نوع الحالة لتوليد مريضة عشوائية:")
case_type = st.radio("نوع الحالة السريرية:", ["Antenatal Case (حالة حامل)", "Postnatal Case (حالة نفاس/بعد الولادة)", "General Gynecology (حالة نساء عامة)"], horizontal=True)

if st.button("🎬 توليد حالة ومريضة جديدة بالكامل"):
    st.session_state.messages = []
    st.session_state.case_started = True
    st.session_state.last_processed_audio = None
    
    # أ) اختيار السيناريو الطبي بناءً على الفئة المختارة
    if case_type == "Antenatal Case (حالة حامل)":
        selected_scenario = random.choice(ANTENATAL_SCENARIOS)
        random_age = random.randint(19, 41)
    elif case_type == "Postnatal Case (حالة نفاس/بعد الولادة)":
        selected_scenario = random.choice(POSTNATAL_SCENARIOS)
        random_age = random.randint(22, 39)
    else:
        selected_scenario = random.choice(GYNAE_SCENARIOS)
        random_age = random.randint(18, 52)
        
    # ب) توليد الهوية الشخصية العشوائية للمريضة
    p_name = random.choice(ARABIC_NAMES)
    p_city = random.choice(LIBYAN_CITIES)
    p_job = random.choice(JOBS)
    p_status = "متزوجة" if random_age > 24 else random.choice(["متزوجة", "عزباء"])
    
    # ج) بناء وحقن الملف السري للمريضة في الـ Prompt
    patient_profile = f"""
    YOUR GENERATED SECRET IDENTITY (Stick to it tightly):
    - Name: {p_name}
    - Age: {random_age} years old
    - Residence: {p_city}, Libya
    - Marital Status: {p_status}
    - Occupation: {p_job}
    - Your Hidden Condition/Diagnosis: {selected_scenario}
    
    Remember: Do not say your diagnosis or age or name unless explicitly asked by the student! Answer like a real patient in the clinic.
    """
    
    st.session_state.hidden_case_details = f"Patient Profile: Name: {p_name}, Age: {random_age}, From: {p_city}, Job: {p_job}. Actual Medical Case: {selected_scenario}"
    st.session_state.current_case_prompt = f"{BASE_SYSTEM_PROMPT}\n{patient_profile}"
    
    st.success(f" Done! تم دخول مريضة جديدة عشوائية إلى العيادة وهي صامتة الآن. (النوع المختار: {case_type}). ابدأ بأخذ الـ History صوتياً!")

st.write("---")

# 7. عرض شاشة المحادثة الحالية
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

# 8. إدارة مدخلات الصوت والكتابة للتفاعل مع المريضة
if st.session_state.case_started:
    st.subheader("🎙️ ابدأ بالتحدث مع المريضة:")
    audio_value = st.audio_input("اضغط على زر المايك واسأل المريضة")
    user_text_input = st.chat_input("أو اكتب سؤالك هنا...")

    if audio_value and audio_value != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_value
        with open("user_voice.wav", "wb") as f:
            f.write(audio_value.read())
            
        with st.spinner("المريضة تستمع وتجيب..."):
            response_text = ask_gemini_direct(audio_path_input="user_voice.wav")
            if "RESOURCE_EXHAUSTED" in response_text or "Error" in response_text:
                st.error(response_text)
            else:
                tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                tts = gTTS(text=response_text, lang='ar', slow=False)
                tts.save(tts_path)
                st.session_state.messages.append({"role": "doctor", "text": "🎤 سؤال صوّتي من الطبيب"})
                st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
                st.rerun()

    if user_text_input:
        with st.spinner("المريضة تجيب..."):
            response_text = ask_gemini_direct(text_input=user_text_input)
            if "RESOURCE_EXHAUSTED" in response_text or "Error" in response_text:
                st.error(response_text)
            else:
                tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                tts = gTTS(text=response_text, lang='ar', slow=False)
                tts.save(tts_path)
                st.session_state.messages.append({"role": "doctor", "text": user_text_input})
                st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
                st.rerun()

# 9. التقييم والتقرير النهائي الطبي للبروفيسور
if st.session_state.case_started:
    st.write("---")
    if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
        with st.spinner("جاري تحليل الـ History وإعداد تقرير اللجنة الطبية الموحد..."):
            eval_prompt = f"""
            Context for you: The hidden case was: {st.session_state.hidden_case_details}.
            Now, stop acting as the patient. Act as an expert OB/GYN Professor evaluating this 4th-year medical student's history taking.
            Provide a comprehensive medical evaluation report in clear formal Arabic.
            Include:
            1. The Secret Patient Profile and Diagnosis.
            2. Evaluation of the student's questions.
            3. Crucial red flags or missed historical points they should have focused on for this specific case (e.g., fluid loss, fetal movement, blood pressure checks, etc.).
            """
            response_text = ask_gemini_direct(text_input=eval_prompt)
            if "RESOURCE_EXHAUSTED" in response_text or "Error" in response_text:
                st.error(response_text)
            else:
                st.markdown("### 📝 تقرير تقييم اللجنة الطبية للـ Long Case:")
                st.info(response_text)
