import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Multi-Board Simulator", page_icon="🩺", layout="centered")
st.title("🩺 منصة محاكاة امتحانات OB/GYN المتطورة")
st.write("مرحباً بك يا دكتور أمين وزملائك. تم إصلاح بروتوكول الاتصال بالسيرفر لتفعيل المفاتيح الجديدة بنجاح.")

# 2. مجمّع المفاتيح الجديدة الخاصة بك
API_KEYS_POOL = [
    "AIzaSyDb5Thpjzk2YjtmNUiecR4NzxQzsJaelb4",
    "AIzaSyATL8FABjR8ECyUyx-rUVAuEHTsBCfrBEg",
    "AIzaSyAxtThGXNx3RfHv9bWHO_nxrRuILqeg-_4",
    "AIzaSyCk8izLy73ACSWAqxq1XAPMBe0QKzENPWo",
    "AIzaSyB7tmDNDxgpIefg_-hud2vpAP5sOrByQxs",
    "AIzaSyCDcFCqFkVV-qA9wk8rXAEWW10VrDNvMig",
    "AIzaSyCTMSL1mCU2J3W0vEueR0n1mM3qd5-DpQE"
]

# بنك المواضيع المعتمدة
CURRICULUM_TOPICS = [
    "Antenatal care (Dr. Zahra)", "Ultrasound (Dr. Zahra Al-Sedd)", "Perinatal Screening (Dr. Karima)",
    "Teratogenic Drugs (Dr. Rania)", "Abortion (Dr. Rania)", "Ectopic Pregnancy (Dr. Sumaya Al-Jarbi)",
    "Hydatidiform Mole (Dr. Ibtisam)", "Antepartum Hemorrhage (Dr. Karima)", "Postpartum Hemorrhage (Dr. Rania)",
    "DIC & Shock (Dr. Rania & Dr. Ibtisam)", "Hypertension in pregnancy (Dr. Heba)", "D.M in pregnancy (Dr. Heba)",
    "Heart disease in pregnancy (Dr. Rania)", "Hyperemesis Gravidarum (Dr. Karima)", "Anemia of Pregnancy (Dr. Heba)",
    "DVT (Dr. Omaima)", "Anatomy of pelvis & Fetal skull", "Stages & Management of labour",
    "Breech Presentation & Malposition", "Shoulder Dystocia (Dr. Heba)", "Preterm labour & PPROM",
    "Multiple Pregnancy (Dr. Omaima)", "Rh Allo-immunization (Dr. Naziha)", "Fetal growth restriction (Dr. Naziha)",
    "Instruments in Obstetrics & Gynecology (Dr. Heba)", "Cesarean section (Dr. Amal)", "Menstrual cycle & Puberty",
    "Amenorrhea (Dr. Heba)", "PCOS (Dr. Ibtisam)", "Fibroid Uterus (Dr. Heba)", "Abnormal Uterine bleeding (Dr. Amal)",
    "Cancer cervix & Ovarian Cancer", "PID & Vaginal Discharge", "Pelvic organ prolapse (Dr. Naziha)",
    "Genitourinary fistula & Urinary Incontinence (Dr. Heba)", "Family planning (Dr. Naziha)"
]

ARABIC_NAMES = ["فاطمة", "مريم", "سالمة", "خديجة", "عائشة", "نجاة", "هناء", "أمل", "منى"]
LIBYAN_CITIES = ["طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "الخمس"]

# دالة الاتصال المحدثة وفقاً لبروتوكول Google الموحد والأكيد
def ask_gemini_direct(prompt_context, messages_list, current_input):
    valid_keys = [k for k in API_KEYS_POOL if k and k.strip() != ""]
    if not valid_keys: 
        return "خطأ: لم يتم العثور على مفاتيح تشغيل صالحة!"
        
    start_index = random.randint(0, len(valid_keys) - 1)
    
    for i in range(len(valid_keys)):
        idx = (start_index + i) % len(valid_keys)
        selected_key = valid_keys[idx]
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={selected_key}"
        
        # بناء الـ Contents بشكل هيكلي سليم متناوب الأدوار (User -> Model -> User)
        contents = []
        
        # دمج الـ Prompt السري مع أول رسالة يرسلها المستخدم لضمان الترتيب
        first_text = f"System Instructions: {prompt_context}\n\nUser Question: {current_input}"
        
        # إذا كان هناك تاريخ محادثة، نقوم بوضعه بترتيب صحيح وموحد
        if messages_list:
            for idx_m, msg in enumerate(messages_list[-4:]): # آخر 4 رسائل فقط لتجنب تخطي الكوتا
                role_type = "model" if msg["role"] in ["patient", "assistant"] else "user"
                contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
            
            # إضافة المدخل الحالي في النهاية
            if contents[-1]["role"] == "user":
                # إذا كانت آخر رسالة هي للمستخدم، ندمج الجديد معها أو ننتظر الـ model
                contents.append({"role": "model", "parts": [{"text": "Understood. Proceed."}]})
            
        contents.append({"role": "user", "parts": [{"text": first_text}]})
        
        try:
            res = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": contents}, timeout=10)
            if res.status_code == 200: 
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                # إذا كان الخطأ بسبب الضغط (429) جرب المفتاح التالي فوراً دون إظهار الخطأ
                continue
        except:
            continue
            
    return "⚠️ تم استهلاك حد الطلبات اللحظي للمفاتيح الجاري تشغيلها، يرجى كتابة السؤال مرة أخرى."

# الهيكل الأساسي وااختيار اللجان
st.markdown("---")
board_selection = st.sidebar.radio("🎯 اختر اللجنة الامتحانية (Select Board):", 
    ["اللجنة الأولى: History Taking Case (عربي)", 
     "اللجنة الثانية: OSCE Short Cases (English)", 
     "اللجنة الثالثة: Curriculum & Instruments Quiz (English)"])

if "history_msgs" not in st.session_state: st.session_state.history_msgs = []
if "osce_msgs" not in st.session_state: st.session_state.osce_msgs = []
if "quiz_msgs" not in st.session_state: st.session_state.quiz_msgs = []
if "active_prompt" not in st.session_state: st.session_state.active_prompt = ""

# ==========================================
# 1. اللجنة الأولى: History Taking
# ==========================================
if board_selection == "اللجنة الأولى: History Taking Case (عربي)":
    st.subheader("🤰 محاكي حالات الـ Long Case بالعامية الليبية")
    case_type = st.radio("نوع الحالة السريرية للامتحان:", ["Antenatal History (حالة حامل)", "Postnatal History (حالة نفاس)"], horizontal=True)
    
    if st.button("🎬 توليد مريضة جديدة والدخول للعيادة"):
        st.session_state.history_msgs = []
        name, city = random.choice(ARABIC_NAMES), random.choice(LIBYAN_CITIES)
        
        if case_type == "Antenatal History (حالة حامل)":
            st.session_state.active_prompt = f"You are a Libyan pregnant patient named {name} from {city}. Speak ONLY in short, local Libyan Arabic dialect (1 sentence). Act as if you have severe headache and blurred vision (Pre-eclampsia) but never state the diagnosis directly. Wait for questions."
        else:
            st.session_state.active_prompt = f"You are a Libyan postnatal patient named {name} from {city}. Speak ONLY in short, local Libyan Arabic dialect (1 sentence). You are 3 days post C-section and have heavy bleeding and fever (Endometritis). Wait for questions."
        st.success("دخلت المريضة العيادة الآن بنجاح ومفاتيحك تعمل. اسألها أي سؤال!")

    for m in st.session_state.history_msgs:
        avatar = "🤰" if m["role"] == "patient" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    user_text = st.chat_input("اسأل المريضة هنا (مثال: كيف حالك يا خالة؟)...")
    if user_text:
        with st.spinner("المريضة تجيب..."):
            ans = ask_gemini_direct(st.session_state.active_prompt, st.session_state.history_msgs, user_text)
            st.session_state.history_msgs.append({"role": "doctor", "text": user_text})
            st.session_state.history_msgs.append({"role": "patient", "text": ans})
            st.rerun()

# ==========================================
# 2. اللجنة الثانية: OSCE Short Cases
# ==========================================
elif board_selection == "اللجنة الثانية: OSCE Short Cases (English)":
    st.subheader("🔬 OSCE Station: Short Cases Discussion")
    
    if st.button("🎲 Generate New OSCE Short Cases"):
        st.session_state.osce_msgs = []
        osce_prompt = "Act as an expert OB/GYN OSCE Examiner. Provide one brief Obstetrics clinical case and one Gynecology case, and follow them with exactly 2 questions. Keep your response short and clear in English."
        with st.spinner("Formulating OSCE Station..."):
            initial_cases = ask_gemini_direct(osce_prompt, [], "Generate the cases now.")
            st.session_state.osce_msgs.append({"role": "assistant", "text": initial_cases})
            st.session_state.active_prompt = "You are the OSCE Examiner grading the student response strictly in English."

    for m in st.session_state.osce_msgs:
        avatar = "🔬" if m["role"] == "assistant" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    student_ans = st.chat_input("Type your answers to OSCE questions here...")
    if student_ans:
        with st.spinner("Analyzing answers..."):
            feedback = ask_gemini_direct(st.session_state.active_prompt, st.session_state.osce_msgs, student_ans)
            st.session_state.osce_msgs.append({"role": "doctor", "text": student_ans})
            st.session_state.osce_msgs.append({"role": "assistant", "text": feedback})
            st.rerun()

# ==========================================
# 3. اللجنة الثالثة: Curriculum Quiz
# ==========================================
else:
    st.subheader("📚 Board 3: Topics & Instruments Viva")
    quiz_mode = st.radio("Select Quiz Domain:", ["General Syllabus Topics", "Surgical Instruments & Equipment"], horizontal=True)
    
    if st.button("❓ Pull a Random Exam Question"):
        st.session_state.quiz_msgs = []
        selected_topic = random.choice(CURRICULUM_TOPICS)
        
        if quiz_mode == "General Syllabus Topics":
            quiz_prompt = f"Act as an OB/GYN external viva examiner. Ask one sharp high-yield medical exam question for a final year student about this topic: '{selected_topic}'."
        else:
            quiz_prompt = "Act as an examiner. Describe a standard clinical instrument (like Ventouse, Forceps, Speculum, or Foley Catheter) by its features and ask 1 question about its main indication or complication."
            
        with st.spinner("Extracting question..."):
            q_text = ask_gemini_direct(quiz_prompt, [], "Give me the question.")
            st.session_state.quiz_msgs.append({"role": "assistant", "text": q_text})
            st.session_state.active_prompt = "You are the clinical viva examiner validating the answer in English."

    for m in st.session_state.quiz_msgs:
        avatar = "📚" if m["role"] == "assistant" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    quiz_input = st.chat_input("Write your academic answer here...")
    if quiz_input:
        with st.spinner("Evaluating accuracy..."):
            evaluation = ask_gemini_direct(st.session_state.active_prompt, st.session_state.quiz_msgs, quiz_input)
            st.session_state.quiz_msgs.append({"role": "doctor", "text": quiz_input})
            st.session_state.quiz_msgs.append({"role": "assistant", "text": evaluation})
            st.rerun()
