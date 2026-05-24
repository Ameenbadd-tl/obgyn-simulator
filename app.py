import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ Long Case الصوتي التلقائي المتطور")
st.write("مرحباً بك يا دكتور أمين وزملائك. اضغط على خيار الحالة بالأسفل لتوليد سيناريو ديناميكي فريد يعتمد على أوراق الامتحانات المعتمدة.")

# 2. مجمّع المفاتيح السبعة المحمية بنظام التناوب الذكي
API_KEYS_POOL = [
    "AIzaSyDb5Thpjzk2YjtmNUiecR4NzxQzsJaelb4",
    "AIzaSyATL8FABjR8ECyUyx-rUVAuEHTsBCfrBEg",
    "AIzaSyAxtThGXNx3RfHv9bWHO_nxrRuILqeg-_4",
    "AIzaSyCk8izLy73ACSWAqxq1XAPMBe0QKzENPWo",
    "AIzaSyB7tmDNDxgpIefg_-hud2vpAP5sOrByQxs",
    "AIzaSyCDcFCqFkVV-qA9wk8rXAEWW10VrDNvMig",
    "AIzaSyCTMSL1mCU2J3W0vEueR0n1mM3qd5-DpQE"
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

# 5. الـ System Prompts المتطورة التي تدمج هياكل الملفات المرفقة بالكامل
ANTENATAL_STRUCTURE_PROMPT = """
You are simulating a Libyan pregnant patient in an Antenatal ward for a 4th-year medical student exam.
You must adhere strictly to the following history layout:
- Personal Data: Name, Age, Nationality, Occupation, Living conditions, Blood Group & RH, Gravida/Para status, Gestational Age (GA), and LNMP.
- Pregnancy Data: Whether it was planned/unplanned, spontaneous/induced, or discovered by missed period/test.
- History of Current Pregnancy: Details of Booking Visit (1st visit GA, routine investigations, ultrasound findings like viability and site, drugs/supplements given, and regular follow-ups or previous admissions).
- Gynecological History: Menarche, cycle regularity, vaginal discharge, dysmenorrhea, contraception history, or gynecological operations.
- Past Obstetric History: Previous pregnancies, dates, modes of delivery, anesthesia types, gestational lengths (preterm/term/postdate), and intrapartum/postpartum complications.
- Past Medical, Surgical, Family, and Social History (consanguinity, smoking, distance/car access to hospital).

CRITICAL RULES:
1. Speak ONLY in a realistic, simple, local Libyan Arabic dialect (عامية ليبية طبيعية).
2. Keep your answers very SHORT (1-2 sentences max).
3. Do NOT reveal your medical condition or full history background at once. Only provide details when the student explicitly asks the correct structured questions.
4. Wait for the doctor to ask the first question. Do NOT talk first.
"""

POSTNATAL_STRUCTURE_PROMPT = """
You are simulating a Libyan patient in a Postnatal ward for a 4th-year medical student exam.
You must adhere strictly to the following history layout:
- Personal Data: Name, Age, Nationality, Occupation, Living conditions, Blood Group & RH, Para status.
- Current Delivery Details: Whether you are a specific day post-vaginal delivery or post-C-Section (elective/emergency, due to a specific reason), with or without complications.
- Main Complaint & Admission details.
- Postnatal Ward Period History: 
  1. Pain (afterpain): site, severity.
  2. Lochia: color, amount, smell.
  3. Bleeding presence.
  4. Bowel/Urinary symptoms: passed stool (crucial post-C-Section), urinary symptoms (retention, incontinence).
  5. Breast: engorgement, redness, cracked nipple.
  6. Baby status: outcome, sex, weight, general condition, breastfeeding plans, and baby vaccination.
- History of past pregnancy, gynecological history, past medical/surgical/family/social histories, and future contraceptive plans.

CRITICAL RULES:
1. Speak ONLY in a realistic, simple, local Libyan Arabic dialect (عامية ليبية طبيعية).
2. Keep your answers very SHORT (1-2 sentences max).
3. Do NOT reveal your medical condition or full history background at once. Only provide details when the student explicitly asks the correct structured questions.
4. Wait for the doctor to ask the first question. Do NOT talk first.
"""

# إدارة الجلسة والذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_started" not in st.session_state:
    st.session_state.case_started = False
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "current_case_prompt" not in st.session_state:
    st.session_state.current_case_prompt = ""
if "hidden_case_details" not in st.session_state:
    st.session_state.hidden_case_details = ""
if "selected_type" not in st.session_state:
    st.session_state.selected_type = ""

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
st.subheader("📋 اختر الفئة السريرية المطلوبة للامتحان:")
case_type = st.radio("نوع الـ Long Case:", ["Antenatal History (التاريخ الصحي للحوامل)", "Postnatal History (التاريخ الصحي للنفاس)"], horizontal=True)

if st.button("🎬 توليد مريضة عشوائية مطابقة للفورم"):
    st.session_state.messages = []
    st.session_state.case_started = True
    st.session_state.last_processed_audio = None
    
    p_name = random.choice(ARABIC_NAMES)
    p_city = random.choice(LIBYAN_CITIES)
    p_job = random.choice(JOBS)
    
    # بناء الهويات التفصيلية ديناميكياً بناءً على اختيار الطالب وهيكل الـ PDF
    if case_type == "Antenatal History (التاريخ الصحي للحوامل)":
        selected_scenario = random.choice(ANTENATAL_SCENARIOS)
        random_age = random.randint(19, 41)
        g_count = random.randint(1, 6)
        p_count = g_count - 1
        ga_weeks = random.randint(8, 38)
        
        patient_profile = f"""
        [ANTENATAL PATIENT PROFILE]:
        - Name: {p_name}, Age: {random_age}, Nationality: Libyan, Occupation: {p_job}, Living in: {p_city}.
        - Obstetric: Gravida {g_count}, Para {p_count} + {random.randint(0,2)} abortions. Gestational Age: {ga_weeks} weeks.
        - Pregnancy status: Spontaneous, Regular cycle, Missed period discovery. Booking visit done at 12 weeks.
        - Hidden Diagnosis/Condition: {selected_scenario}
        """
        st.session_state.current_case_prompt = f"{ANTENATAL_STRUCTURE_PROMPT}\n{patient_profile}"
        st.session_state.selected_type = "Antenatal"
        
    else:  # Postnatal History
        selected_scenario = random.choice(POSTNATAL_SCENARIOS)
        random_age = random.randint(22, 39)
        p_count = random.randint(1, 5)
        delivery_mode = random.choice(["Vaginal Delivery", "C-Section (Elective)", "C-Section (Emergency due to fetal distress)"])
        days_post = random.randint(1, 10)
        baby_sex = random.choice(["Male", "Female"])
        baby_weight = round(random.uniform(2.5, 4.0), 2)
        
        patient_profile = f"""
        [POSTNATAL PATIENT PROFILE]:
        - Name: {p_name}, Age: {random_age}, Nationality: Libyan, Occupation: {p_job}, Living in: {p_city}.
        - Obstetric: Para {p_count} + {random.randint(0,1)}.
        - Delivery Status: She is {days_post} days post {delivery_mode}.
        - Postnatal status: Has afterpain (mild/severe according to case), Lochia variation, passed stool status depends on delivery type.
        - Baby Status: Outcome alive, Sex: {baby_sex}, Weight: {baby_weight}kg, Condition: Healthy.
        - Hidden Diagnosis/Condition: {selected_scenario}
        """
        st.session_state.current_case_prompt = f"{POSTNATAL_STRUCTURE_PROMPT}\n{patient_profile}"
        st.session_state.selected_type = "Postnatal"
        
    st.session_state.hidden_case_details = patient_profile
    st.success(f" Done! تم توليد مريضة ({case_type}) ودخلت العيادة الآن بنجاح. اضغط على المايك وابدأ الامتحان!")

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

# 9. التقييم والتقرير النهائي الطبي للبروفيسور بناءً على هياكل الـ PDF المرفوعة
if st.session_state.case_started:
    st.write("---")
    if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
        with st.spinner("جاري تحليل الـ History وإعداد تقرير اللجنة الطبية الموحد..."):
            
            # صياغة برومبت التقييم بناءً على نوع الحالة المحددة لتطابق متطلبات الدكتورة هبة
            eval_prompt = f"""
            Context for you: The chosen format structure was: {st.session_state.selected_type}. 
            The full hidden case details and identity were: {st.session_state.hidden_case_details}.
            
            Now, stop acting as the patient. Act as an expert OB/GYN Professor evaluating this 4th-year medical student's long case history taking.
            Provide a strict, professional medical evaluation report in formal Arabic structured as follows:
            
            1. 📋 ملف المريضة الكامل والتشخيص الخفي (Full Profile & Hidden Diagnosis).
            2. 🔍 تقييم الـ History المأخوذ مقارنة بالفورم الرسمي المعتمد (التحقق من استيفاء البيانات الشخصية، تفاصيل الولادة/الحمل الحالي، تفاصيل الـ Lochia والـ Breast والـ Baby إن كانت حالة بوست، أو الـ Booking والـ LNMP إن كانت حالة أنتي).
            3. ⚠️ النقاط السريرية الحرجة والعلامات الحمراء (Red Flags) التي أغفلها الطالب أو نسي التركيز عليها لتشخيص هذه الحالة بالتحديد.
            4. 🏆 نصيحة البروفيسور النهائية للطالب لتطوير أدائه في الامتحان العملي.
            """
            
            response_text = ask_gemini_direct(text_input=eval_prompt)
            if "RESOURCE_EXHAUSTED" in response_text or "Error" in response_text:
                st.error(response_text)
            else:
                st.markdown("### 📝 تقرير تقييم اللجنة الطبية للـ Long Case:")
                st.info(response_text)
