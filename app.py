import streamlit as st
import os
import random
from transformers import pipeline
import whisper
from TTS.api import TTS

# 1. إعداد الصفحة
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ Long Case الصوتي (نسخة مجانية)")
st.write("مرحباً بك يا دكتور أمين وزملائك. هذه النسخة تعمل بدون مفاتيح Gemini وتعتمد على نماذج مفتوحة المصدر.")

# 2. بنك البيانات
ARABIC_NAMES = ["فاطمة", "مريم", "سالمة", "خديجة", "عائشة", "نجاة", "هناء", "أمل", "منى", "إيناس", "غادة", "روان", "سارة", "انتصار", "أحلام"]
LIBYAN_CITIES = ["طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "الخمس", "زليتن", "غريان", "البيضاء", "طبرق"]
JOBS = ["ربة بيت", "معلمة مدرسة", "موظفة إدارية", "طالبة جامعية", "مهندسة", "تشتغل في معمل", "لا تعمل"]

ANTENATAL_SCENARIOS = [
    "Placenta Previa", "Abruptio Placentae", "Severe Pre-eclampsia",
    "Ectopic Pregnancy rupture", "Preterm Labor", "Miscarriage",
    "Hyperemesis Gravidarum", "Decreased Fetal Movement",
    "Gestational Diabetes complications", "Molar Pregnancy"
]

POSTNATAL_SCENARIOS = [
    "Primary Postpartum Hemorrhage", "Secondary Postpartum Hemorrhage",
    "Postpartum Endometritis", "Deep Vein Thrombosis",
    "Postpartum Preeclampsia/Eclampsia", "Mastitis",
    "Postpartum Depression / Psychosis"
]

# 3. تحميل النماذج المفتوحة
qa_model = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct", device_map="auto")
whisper_model = whisper.load_model("base")
tts = TTS(model_name="tts_models/ar/mai/male")

# 4. دوال مساعدة
def ask_local_model(text_input):
    try:
        response = qa_model(text_input, max_length=200, do_sample=True)
        return response[0]["generated_text"]
    except Exception as e:
        return f"Error: {str(e)}"

def speech_to_text(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def text_to_speech(text, filename="reply.mp3"):
    tts.tts_to_file(text=text, file_path=filename)
    return filename

# 5. واجهة التحكم
st.subheader("📋 اختر الفئة السريرية المطلوبة للامتحان:")
case_type = st.radio("نوع الـ Long Case:", ["Antenatal History", "Postnatal History"], horizontal=True)

if st.button("🎬 توليد مريضة عشوائية"):
    st.session_state.messages = []
    st.session_state.case_started = True

    p_name = random.choice(ARABIC_NAMES)
    p_city = random.choice(LIBYAN_CITIES)
    p_job = random.choice(JOBS)

    if case_type == "Antenatal History":
        selected_scenario = random.choice(ANTENATAL_SCENARIOS)
        random_age = random.randint(19, 41)
        g_count = random.randint(1, 6)
        p_count = g_count - 1
        ga_weeks = random.randint(8, 38)
        patient_profile = f"""
        [ANTENATAL PATIENT PROFILE]:
        Name: {p_name}, Age: {random_age}, City: {p_city}, Job: {p_job}
        Gravida {g_count}, Para {p_count}, GA: {ga_weeks} weeks
        Hidden Diagnosis: {selected_scenario}
        """
    else:
        selected_scenario = random.choice(POSTNATAL_SCENARIOS)
        random_age = random.randint(22, 39)
        p_count = random.randint(1, 5)
        delivery_mode = random.choice(["Vaginal Delivery", "C-Section"])
        days_post = random.randint(1, 10)
        baby_sex = random.choice(["Male", "Female"])
        baby_weight = round(random.uniform(2.5, 4.0), 2)
        patient_profile = f"""
        [POSTNATAL PATIENT PROFILE]:
        Name: {p_name}, Age: {random_age}, City: {p_city}, Job: {p_job}
        Para {p_count}, Delivery: {delivery_mode}, {days_post} days ago
        Baby: {baby_sex}, {baby_weight}kg
        Hidden Diagnosis: {selected_scenario}
        """

    st.session_state.current_case_prompt = patient_profile
    st.success("✅ تم توليد المريضة بنجاح، ابدأ الامتحان الآن.")

# 6. التفاعل مع المريضة
if st.session_state.get("case_started", False):
    st.subheader("🎙️ ابدأ بالتحدث مع المريضة:")

    audio_value = st.audio_input("اضغط على زر المايك واسأل المريضة")
    user_text_input = st.chat_input("أو اكتب سؤالك هنا...")

    if audio_value:
        with open("user_voice.wav", "wb") as f:
            f.write(audio_value.read())
        question_text = speech_to_text("user_voice.wav")
        response_text = ask_local_model(question_text)
        tts_path = text_to_speech(response_text, f"reply_{len(st.session_state.messages)}.mp3")
        st.session_state.messages.append({"role": "doctor", "text": question_text})
        st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
        st.rerun()

    if user_text_input:
        response_text = ask_local_model(user_text_input)
        tts_path = text_to_speech(response_text, f"reply_{len(st.session_state.messages)}.mp3")
        st.session_state.messages.append({"role": "doctor", "text": user_text_input})
        st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
        st.rerun()

    # عرض المحادثة
    for msg in st.session_state.messages:
        if msg["role"] == "doctor":
            with st.chat_message("assistant", avatar="👨‍⚕️"):
                st.write(msg["text"])
        elif msg["role"] == "patient":
            with st.chat_message("user", avatar="🤰"):
                st.write(msg["text"])
                if msg.get("audio_path") and os.path.exists(msg["audio_path"]):
                    st.audio(msg["audio_path"])
