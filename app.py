import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Multi-Board Simulator", page_icon="🩺", layout="centered")
st.title("🩺 منصة محاكاة امتحانات OB/GYN المتطورة")
st.write("مرحباً بك يا دكتور أمين وزملائك في المنظومة الشاملة المحدثة وفقاً لمنهج الكلية وأوراق الامتحانات.")

# 2. مجمّع المفاتيح السبعة المحمية بنظام التناوب الذكي
API_KEYS_POOL = [
    "AIzaSyCTMSL1mCU2J3W0vEueR0n1mM3qd5-DpQE",
    "AIzaSyCDcFCqFkVV-qA9wk8rXAEWW10VrDNvMig",
    "AIzaSyB7tmDNDxgpIefg_-hud2vpAP5sOrByQxs",
    "AIzaSyCk8izLy73ACSWAqxq1XAPMBe0QKzENPWo",
    "AIzaSyAxtThGXNx3RfHv9bWHO_nxrRuILqeg-_4",
    "AIzaSyATL8FABjR8ECyUyx-rUVAuEHTsBCfrBEg",
    "AIzaSyDb5Thpjzk2YjtmNUiecR4NzxQzsJaelb4"
]

# بنك المواضيع المعتمدة (81 موضوعاً) لتغذية السيرفر بالأسئلة والمناهج
CURRICULUM_TOPICS = [
    "Antenatal care (Dr. Zahra)", "Ultrasound (Dr. Zahra Al-Sedd)", "Perinatal Screening (Dr. Karima)",
    "Teratogenic Drugs (Dr. Rania)", "Abortion (Dr. Rania)", "Ectopic Pregnancy (Dr. Sumaya Al-Jarbi)",
    "Hydatidiform Mole (Dr. Ibtisam)", "Antepartum Hemorrhage (Dr. Karima)", "Postpartum Hemorrhage (Dr. Rania)",
    "DIC (Dr. Rania)", "Shock & Uterine Rupture (Dr. Ibtisam & Dr. Amal)", "IV therapy & Blood Transfusion (Dr. Ibtisam)",
    "Hypertension in pregnancy (Dr. Heba)", "D.M in pregnancy (Dr. Heba)", "Heart disease in pregnancy (Dr. Rania)",
    "Hyperemesis Gravidarum (Dr. Karima)", "UTI in pregnancy (Dr. Zahra)", "Anemia of Pregnancy (Dr. Heba)",
    "DVT (Dr. Omaima)", "Thyroid disease in pregnancy (Dr. Rania)", "Liver disease during pregnancy (Dr. Heba)",
    "Abdominal pain in pregnancy (Dr. Heba)", "Anatomy of pelvis & Fetal skull (Dr. Naziha & Dr. Rania)",
    "Stages & Management of labour (Dr. Naziha & Dr. Omaima)", "Intrapartum assessment & LCG",
    "Breech Presentation & Malposition (Dr. Omaima)", "Contracted pelvis (Dr. Rania)", "Shoulder Dystocia (Dr. Heba)",
    "Preterm labour & PPROM (Dr. Naziha & Dr. Sumaya)", "Amniotic Fluid abnormalities (Dr. Sumaya)",
    "Multiple Pregnancy (Dr. Omaima)", "Rh Allo-immunization (Dr. Naziha)", "Infectious diseases in pregnancy (Dr. Heba)",
    "Fetal growth restriction & Macrosomia (Dr. Naziha)", "IUFD (Dr. Amal)", "Puerperium & Lactation (Dr. Zahra & Dr. Sumaya)",
    "Maternal mortality rate in Libya (Dr. Amal)", "Induction of labor (Dr. Ibtisam)", "Operative vaginal delivery (Dr. Naziha)",
    "Instruments in Obstetrics & Gynecology (Dr. Heba)", "Cesarean section (Dr. Amal)", "Perineal and cervical tears (Dr. Naziha)",
    "Anaesthesia in pregnancy (Dr. Amal)", "Menstrual cycle & Puberty", "Menopause (Dr. Rania)", "Amenorrhea (Dr. Heba)",
    "PCOS (Dr. Ibtisam)", "Dysmenorrhea & Dyspareunia (Dr. Sumaya)", "Premenstrual syndrome & Hirsutism",
    "Hyperprolactinaemia & Infertility", "Recurrent Pregnancy Loss (Dr. Heba)", "Uterine Abnormalities (Dr. Sumaya)",
    "Endometriosis and adenomyosis (Dr. Zahra)", "Abnormal Uterine bleeding (Dr. Amal)", "Benign ovarian cysts (Dr. Sumaya)",
    "Fibroid Uterus (Dr. Heba)", "Endometrial hyperplasia & Cancer (Dr. Rania)", "Cancer cervix (Dr. Naziha)",
    "Ovarian Cancer (Dr. Omaima)", "Vaginal Discharge, Pruritis & PID", "Pelvic organ prolapse (Dr. Naziha)",
    "Genitourinary fistula & Urinary Incontinence (Dr. Heba)", "Family planning (Dr. Naziha)", "Hysterectomy & Hysteroscopy (Dr. Amal)"
]

ARABIC_NAMES = ["فاطمة", "مريم", "سالمة", "خديجة", "عائشة", "نجاة", "هناء", "أمل", "منى"]
LIBYAN_CITIES = ["طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "الخمس"]

# دالة ذكية لإرسال الطلبات وتدوير المفاتيح
def ask_gemini_direct(prompt_context, messages_list, current_input):
    valid_keys = [k for k in API_KEYS_POOL if k and k != "AIzaSy..."]
    if not valid_keys: return "Error: No valid API keys found!"
    start_index = random.randint(0, len(valid_keys) - 1)
    
    for i in range(len(valid_keys)):
        idx = (start_index + i) % len(valid_keys)
        selected_key = valid_keys[idx]
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={selected_key}"
        
        contents = [{"role": "user", "parts": [{"text": prompt_context}]}]
        for msg in messages_list:
            role_type = "model" if msg["role"] in ["patient", "assistant"] else "user"
            contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
        
        contents.append({"role": "user", "parts": [{"text": current_input}]})
        try:
            res = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": contents}, timeout=12)
            if res.status_code == 200: return res.json()['candidates'][0]['content']['parts'][0]['text']
        except: continue
    return "RESOURCE_EXHAUSTED: All API keys are packed, retry in a few seconds."

# الهيكل الأساسي لاختيار اللجان الثلاث
st.markdown("---")
board_selection = st.sidebar.radio("🎯 اختر اللجنة الامتحانية (Select Board):", 
    ["اللجنة الأولى: History Taking Case (عربي)", 
     "اللجنة الثانية: OSCE Short Cases (English)", 
     "اللجنة الثالثة: Curriculum & Instruments Quiz (English)"])

# تهيئة متغيرات الجلسة العامة
if "history_msgs" not in st.session_state: st.session_state.history_msgs = []
if "osce_msgs" not in st.session_state: st.session_state.osce_msgs = []
if "quiz_msgs" not in st.session_state: st.session_state.quiz_msgs = []
if "active_prompt" not in st.session_state: st.session_state.active_prompt = ""
if "hidden_meta" not in st.session_state: st.session_state.hidden_meta = ""

# ==========================================
# 1. اللجنة الأولى: محاكي الـ History Taking
# ==========================================
if board_selection == "اللجنة الأولى: History Taking Case (عربي)":
    st.subheader("🤰 محاكي حالات الـ Long Case بالعامية الليبية")
    case_type = st.radio("نوع الحالة السريرية للامتحان:", ["Antenatal History (حالة حامل)", "Postnatal History (حالة نفاس)"], horizontal=True)
    
    if st.button("🎬 توليد مريضة جديدة والدخول للعيادة"):
        st.session_state.history_msgs = []
        name, city = random.choice(ARABIC_NAMES), random.choice(LIBYAN_CITIES)
        
        if case_type == "Antenatal History (حالة حامل)":
            st.session_state.active_prompt = "You are a Libyan pregnant patient in Arabic dialect. Answer shortly (1-2 lines). Mimic symptoms of major antenatal issues like Pre-eclampsia or Placenta Previa naturally only when asked. Stick strictly to local Libyan terms."
            st.session_state.hidden_meta = f"Patient: {name}, Location: {city}, Antenatal simulated long case."
        else:
            st.session_state.active_prompt = "You are a Libyan postpartum patient in Arabic ward. Answer very shortly (1-2 lines) in Libyan dialect. Simulate lochia/afterpain symptoms according to standard medical presentation."
            st.session_state.hidden_meta = f"Patient: {name}, Location: {city}, Postnatal simulated long case."
        st.success("تم توليد مريضة عشوائية بنجاح، إنها صامتة وتنتظر سؤالك الأول الآن صوتياً أو كتابياً!")

    # عرض المحادثة
    for m in st.session_state.history_msgs:
        avatar = "🤰" if m["role"] == "patient" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    user_text = st.chat_input("اسأل المريضة هنا (مثال: شن تحسي يا خالة؟)...")
    if user_text:
        with st.spinner("المريضة تجيب..."):
            ans = ask_gemini_direct(st.session_state.active_prompt, st.session_state.history_msgs, user_text)
            st.session_state.history_msgs.append({"role": "doctor", "text": user_text})
            st.session_state.history_msgs.append({"role": "patient", "text": ans})
            st.rerun()
            
    if st.session_state.history_msgs and st.button("📊 إنهاء وطلب تقييم البروفيسور"):
        with st.spinner("جاري إعداد تقرير التقييم السريري الدقيق..."):
            report = ask_gemini_direct("Act as an OB/GYN Professor. Evaluate the student history based on strict guidelines. Provide a report in Arabic.", st.session_state.history_msgs, "Provide final clinical review.")
            st.info(report)

# ==========================================
# 2. اللجنة الثانية: OSCE Short Cases (English)
# ==========================================
elif board_selection == "اللجنة الثانية: OSCE Short Cases (English)":
    st.subheader("🔬 OSCE Station: Short Cases Discussion")
    st.write("This station generates 2 structured short cases (1 Gynecology, 1 Obstetrics) followed by interactive exam questions.")
    
    if st.button("🎲 Generate New Double Short Cases"):
        st.session_state.osce_msgs = []
        osce_prompt = """You are an expert OB/GYN OSCE Examiner. Generate exactly two clinical short cases:
        1. One Obstetrics short case (e.g., Shoulder dystocia management, Breech options).
        2. One Gynecology short case (e.g., Postmenopausal bleeding, PCOS workup).
        Provide the cases, then list 3 clear, sequential questions for the student to solve. Stop and wait for answers."""
        
        with st.spinner("Formulating OSCE Station scenarios..."):
            initial_cases = ask_gemini_direct(osce_prompt, [], "Generate the station.")
            st.session_state.osce_msgs.append({"role": "assistant", "text": initial_cases})
            st.session_state.active_prompt = "You are the OSCE Examiner reviewing short cases answers in English. Grade strictly."

    for m in st.session_state.osce_msgs:
        avatar = "🔬" if m["role"] == "assistant" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    student_ans = st.chat_input("Type your answers to the OSCE questions here in English...")
    if student_ans:
        with st.spinner("Examiner is analyzing your answers..."):
            feedback = ask_gemini_direct(st.session_state.active_prompt, st.session_state.osce_msgs, student_ans)
            st.session_state.osce_msgs.append({"role": "doctor", "text": student_ans})
            st.session_state.osce_msgs.append({"role": "assistant", "text": feedback})
            st.rerun()

# ==========================================
# 3. اللجنة الثالثة: Curriculum & Instruments Quiz
# ==========================================
else:
    st.subheader("📚 Board 3: Curriculum Topics & Instruments Viva")
    st.write("Practice theoretical questions and surgical instruments/tools questions from Dr. Heba's lectures.")
    
    quiz_mode = st.radio("Select Quiz Domain:", ["General Syllabus (81 Topics)", "Surgical Instruments & Equipment (Dr. Heba)"], horizontal=True)
    
    if st.button("❓ Pull a Random Exam Question"):
        st.session_state.quiz_msgs = []
        selected_topic = random.choice(CURRICULUM_TOPICS)
        
        if quiz_mode == "General Syllabus (81 Topics)":
            quiz_prompt = f"Act as an OB/GYN external viva examiner. Pick this topic: '{selected_topic}'. Ask a tough, high-yield clinical question suitable for a final 4th year medical student. Do not give the answer yet."
        else:
            quiz_prompt = "Act as an OB/GYN examiner testing clinical instruments (e.g., Ventouse, Forceps, Sims Speculum, Foley catheter complications, Curettes from Dr. Heba's lectures). Describe a specific surgical instrument scenario/indications or complications, and ask 2 questions about it."
            
        with st.spinner("Extracting standard exam question..."):
            q_text = ask_gemini_direct(quiz_prompt, [], "Give me the question.")
            st.session_state.quiz_msgs.append({"role": "assistant", "text": q_text})
            st.session_state.active_prompt = "You are the final medical viva examiner validating the clinical accuracy of the student response."

    for m in st.session_state.quiz_msgs:
        avatar = "📚" if m["role"] == "assistant" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    quiz_input = st.chat_input("Write your academic answer here in English...")
    if quiz_input:
        with st.spinner("Evaluating your answer accuracy..."):
            evaluation = ask_gemini_direct(st.session_state.active_prompt, st.session_state.quiz_msgs, quiz_input)
            st.session_state.quiz_msgs.append({"role": "doctor", "text": quiz_input})
            st.session_state.quiz_msgs.append({"role": "assistant", "text": evaluation})
            st.rerun()
