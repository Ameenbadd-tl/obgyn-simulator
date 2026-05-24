import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Multi-Board Simulator", page_icon="🩺", layout="centered")
st.title("🩺 منصة محاكاة امتحانات OB/GYN المتطورة")
st.write("مرحباً بك يا دكتور أمين وزملائك. تم تحديث الكود ليتوافق مع السيرفرات ويمنع الضغط.")

# 2. مجمّع المفاتيح (ضع مفاتيحك الجديدة هنا)
# تأكد أن المفاتيح تبدأ بـ AIzaSy وتعمل بشكل صحيح
API_KEYS_POOL = [
    "AIzaSyCGXIIx3HIMC7GeFZFrcSmXpxZGgUG8K5Q",
    "AIzaSyBXxYZNFlVmpKf1f_oSgWqYVfgC7_spNCU",
    "AIzaSyAA5E6EziXwrm8U3fFFCPkH-s9If3tP674",
    "AIzaSyAn8q3hwFn0K0i_OTOVHdhdTxR5j0MHUyw",
    "AIzaSyC0uiwlDJW_STJL6i9Edl1gDdOiEE63MFc",
    "AIzaSyBHtq_8zblQ52ca93jpGDrhDWwaEll0BuM",
    "AIzaSyAyr2tZVOcYgoCOfF1kXCnPCD41PGSEjxI"
]

# بنك المواضيع (مختصر لتقليل حجم البيانات المرسلة للسيرفر ومنع الحظر)
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

# دالة إرسال الطلبات المعدلة والمحمية ضد الحظر والتهنيج
def ask_gemini_direct(prompt_context, messages_list, current_input):
    valid_keys = [k for k in API_KEYS_POOL if k and not k.startswith("ضع_هنا")]
    if not valid_keys: 
        return "خطأ: لم تقم بإدخال مفاتيحك الخاصة الفعالة في قائمة API_KEYS_POOL داخل الكود!"
        
    start_index = random.randint(0, len(valid_keys) - 1)
    
    for i in range(len(valid_keys)):
        idx = (start_index + i) % len(valid_keys)
        selected_key = valid_keys[idx]
        
        # استخدام موديل flash المستقر والخفيف لتفادي الحظر المجاني
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={selected_key}"
        
        # بناء سياق المحادثة بشكل خفيف ومباشر
        contents = [{"role": "user", "parts": [{"text": prompt_context}]}]
        for msg in messages_list[-5:]: # إرسال آخر 5 رسائل فقط لمنع تخطي حدود حجم الـ Context في الحساب المجاني
            role_type = "model" if msg["role"] in ["patient", "assistant"] else "user"
            contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
        
        contents.append({"role": "user", "parts": [{"text": current_input}]})
        
        try:
            res = requests.post(url, headers={"Content-Type": "application/json"}, json={"contents": contents}, timeout=10)
            if res.status_code == 200: 
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            elif res.status_code == 400:
                return f"API Error (400): خطأ في صياغة الطلب أو أن المفتاح غير مفعل لنموذج جينيريت."
            elif res.status_code == 403:
                return f"API Error (403): المفتاح المستعمل غير صحيح أو محظور من جوجل."
            elif res.status_code == 429:
                continue # إذا كان مشغexpressions تخطاه للمفتاح التالي
        except Exception as e:
            continue
            
    return "⚠️ تنبيه من السيرفر: جميع المفاتيح المسجلة تعطي خطأ في الاتصال حالياً. تأكد من نسخ المفاتيح الجديدة بشكل كامل وبدون فراغات."

# الهيكل الأساسي واختيار اللجان
st.markdown("---")
board_selection = st.sidebar.radio("🎯 اختر اللجنة الامتحانية (Select Board):", 
    ["اللجنة الأولى: History Taking Case (عربي)", 
     "اللجنة الثانية: OSCE Short Cases (English)", 
     "اللجنة الثالثة: Curriculum & Instruments Quiz (English)"])

if "history_msgs" not in st.session_state: st.session_state.history_msgs = []
if "osce_msgs" not in st.session_state: st.session_state.osce_msgs = []
if "quiz_msgs" not in st.session_state: st.session_state.quiz_msgs = []
if "active_prompt" not in st.session_state: st.session_state.active_prompt = ""
if "selected_topic" not in st.session_state: st.session_state.selected_topic = ""

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
            st.session_state.active_prompt = "You are a Libyan pregnant patient. Answer very shortly in Libyan dialect (1 line). Act as a patient with severe headache and blurred vision (Pre-eclampsia) or painless bleeding. Do not say diagnosis."
        else:
            st.session_state.active_prompt = "You are a Libyan postpartum patient. Answer shortly in Libyan dialect (1 line). You complain of high fever and heavy vaginal bleeding (Postpartum Endometritis). Do not say diagnosis."
        st.success("تم دخول المريضة بنجاح. ابدأ بسؤالها الآن.")

    for m in st.session_state.history_msgs:
        avatar = "🤰" if m["role"] == "patient" else "👨‍⚕️"
        with st.chat_message(m["role"], avatar=avatar): st.write(m["text"])
            
    user_text = st.chat_input("اسأل المريضة هنا (مثال: السلام عليكم، شن اسمك يا خالة؟)...")
    if user_text:
        with St.spinner("المريضة تجيب..."):
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
        osce_prompt = "Act as an OB/GYN OSCE Examiner. Present one brief Obstetrics case and one brief Gynecology case, followed by 2 simple questions. Keep it compact."
        with st.spinner("Formulating OSCE Station..."):
            initial_cases = ask_gemini_direct(osce_prompt, [], "Generate cases.")
            st.session_state.osce_msgs.append({"role": "assistant", "text": initial_cases})
            st.session_state.active_prompt = "You are the OSCE Examiner. Grade the response strictly in English."

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
        st.session_state.selected_topic = random.choice(CURRICULUM_TOPICS)
        
        if quiz_mode == "General Syllabus Topics":
            quiz_prompt = f"Ask a high-yield medical exam question for a 4th-year student regarding this specific topic: '{st.session_state.selected_topic}'."
        else:
            quiz_prompt = "Ask a clinical question about one standard OB/GYN instrument (like Ventouse, Forceps, Speculum, or Foley Catheter). Describe its use or complication."
            
        with st.spinner("Extracting question..."):
            q_text = ask_gemini_direct(quiz_prompt, [], "Give me the question.")
            st.session_state.quiz_msgs.append({"role": "assistant", "text": q_text})
            st.session_state.active_prompt = "You are the clinical viva examiner validating this topic answer."

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
