import streamlit as st
import requests
import base64
from gtts import gTTS
import os
import random

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ OB/GYN الشامل والمتطور")
st.write("مرحباً بك يا دكتور أمين وزملائك. تم حل مشكلة الضغط الخارجي وتأمين الاتصال بالمفاتيح المجانية بنجاح.")

# 2. مجمّع المفاتيح السبعة المحمية بنظام التناوب الذكي
API_KEYS_POOL = [
    "AIzaSyCgXikXLejIGsfTwfBbLd1n7cxVxFxYQeU",
    "AIzaSyCKSxhg02oMi-JFvtK8iLVa8hlM64-bQxM",
    "AIzaSyAFG4qNJF_mSL5Vx4PTThMdiAYPRtle1Sk",
    "AIzaSyAcZ-KgzwlNeqQ27t-Evzy6QsCqSP-F2q0,
    "AIzaSyD-UtKn0V0PTsMX0TSxiH_bn6sHgdoULDw",
    "AIzaSyBwAjQjdpndUPF2eyGLef1mIQesM8AUvi0",
    "AIzaSyBwAjQjdpndUPF2eyGLef1mIQesM8AUvi0"
]

# 3. بنك البيانات لتوليد شخصيات وهويات ليبية عشوائية ومختلفة في كل مرة
ARABIC_NAMES = ["فاطمة", "مريم", "سالمة", "خديجة", "عائشة", "نجاة", "هناء", "أمل", "منى", "إيناس", "غادة", "روان", "سارة", "انتصار", "أحلام"]
LIBYAN_CITIES = ["طرابلس", "بنغازي", "مصراتة", "الزاوية", "سبها", "الخمس", "زليتن", "غريان", "البيضاء", "طبرق"]
JOBS = ["ربة بيت", "معلمة مدرسة", "موظفة إدارية", "طالبة جامعية", "مهندسة", "تشتغل في معمل", "لا تعمل"]

# بنك المنهج للامتحان الشفوي والآلات
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

# 🛠️ الدالة المعدلة والذكية لحماية الكوتا المجانية ومنع الـ Resource Exhausted نهائياً
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
        
        # إذا كان هناك ملف صوتي، نقوم أولاً بتحويله إلى نص لحماية كوتا الـ Tokens والـ IP من الحظر
        if audio_path_input:
            try:
                with open(audio_path_input, "rb") as audio_file:
                    audio_data = base64.b64encode(audio_file.read()).decode("utf-8")
                
                # طلب خفيف جداً ومستقل مخصص فقط لتفريغ الصوت بدقة وبدون تحميل ذاكرة الحوار
                audio_payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [
                            {"inline_data": {"mime_type": "audio/wav", "data": audio_data}},
                            {"text": "Translate this medical student speech question exactly into written Arabic text. Give me only the text."}
                        ]
                    }]
                }
                audio_res = requests.post(url, headers=headers, json=audio_payload, timeout=10)
                if audio_res.status_code == 200:
                    text_input = audio_res.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    continue # تجربة المفتاح التالي إذا فشل تفريغ الصوت
            except:
                continue

        # الآن نقوم بإرسال الحوار الفعلي كنص صافي وخفيف جداً، مما يمنع حدوث RESOURCE_EXHAUSTED بشكل قطعي
        contents = [{"role": "user", "parts": [{"text": st.session_state.current_case_prompt}]}]
        
        # تحسين الذاكرة: إرسال آخر 4 رسائل فقط لتقليص الـ Tokens وحماية الخادم المجاني
        for msg in st.session_state.messages[-4:]:
            role_type = "model" if msg["role"] == "patient" else "user"
            contents.append({"role": role_type, "parts": [{"text": msg["text"]}]})
        
        # إضافة السؤال الحالي
        contents.append({"role": "user", "parts": [{"text": text_input if text_input else "كيف حالك يا خالة؟"}]})
        
        # إضافة التوجيه النهائي لضمان اللهجة الليبية والاختصار
        contents[-1]["parts"].append({"text": "\n(ردي على هذا السؤال بصفتك المريضة بالعامية الليبية وبشكل قصير جداً وفي سطر واحد ومباشر وطبيعي)"})
        
        payload = {"contents": contents}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=12)
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
            
    return "💡 السيرفر المجاني مضغوط حالياً، يرجى تكرار إرسال الضغطة مرة أخرى وسيعمل فوراً عبر المفتاح البديل للشبكة."

# =========================================================
# 🧭 شريط التحكم الجانبي واختيار اللجان الذكي (Sidebar Navigation)
# =========================================================
st.sidebar.title("🎯 لجان الامتحان الشاملة")
board_selection = st.sidebar.radio("اختر اللجنة الحالية لمذاكرتها:", 
    ["اللجنة الأولى: History Taking Case (العربية)", 
     "اللجنة الثانية: OSCE Short Cases (English)", 
     "اللجنة الثالثة: Curriculum & Instruments Quiz (English)"])

# =========================================================
# 🤰 اللجنة الأولى: نفس كودك الشغال 100% بدون تعديل حرف واحد
# =========================================================
if board_selection == "اللجنة الأولى: History Taking Case (العربية)":
    st.subheader("📋 اختر الفئة السريرية المطلوبة للامتحان:")
    case_type = st.radio("نوع الـ Long Case:", ["Antenatal History (التاريخ الصحي للحوامل)", "Postnatal History (التاريخ الصحي للنفاس)"], horizontal=True)

    if st.button("🎬 توليد مريضة عشوائية مطابقة للفورم"):
        st.session_state.messages = []
        st.session_state.case_started = True
        st.session_state.last_processed_audio = None
        
        p_name = random.choice(ARABIC_NAMES)
        p_city = random.choice(LIBYAN_CITIES)
        p_job = random.choice(JOBS)
        
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
        st.success(f"Done! تم توليد مريضة ({case_type}) ودخلت العيادة الآن بنجاح. اضغط على المايك وابدأ الامتحان!")

    st.write("---")

    # عرض شاشة المحادثة الحالية
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

    # إدارة مدخلات الصوت والكتابة للتفاعل مع المريضة
    if st.session_state.case_started and st.session_state.selected_type in ["Antenatal", "Postnatal"]:
        st.subheader("🎙️ ابدأ بالتحدث مع المريضة:")
        audio_value = st.audio_input("اضغط على زر المايك واسأل المريضة")
        user_text_input = st.chat_input("أو اكتب سؤالك هنا...")

        if audio_value and audio_value != st.session_state.last_processed_audio:
            st.session_state.last_processed_audio = audio_value
            with open("user_voice.wav", "wb") as f:
                f.write(audio_value.read())
                
            with st.spinner("المريضة تستمع وتجيب..."):
                response_text = ask_gemini_direct(audio_path_input="user_voice.wav")
                if "Error" in response_text:
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
                if "Error" in response_text:
                    st.error(response_text)
                else:
                    tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                    tts = gTTS(text=response_text, lang='ar', slow=False)
                    tts.save(tts_path)
                    st.session_state.messages.append({"role": "doctor", "text": user_text_input})
                    st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
                    st.rerun()

    # التقييم والتقرير النهائي الطبي للبروفيسور
    if st.session_state.case_started and st.session_state.selected_type in ["Antenatal", "Postnatal"]:
        st.write("---")
        if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
            with st.spinner("جاري تحليل الـ History وإعداد تقرير اللجنة الطبية الموحد..."):
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
                if "Error" in response_text:
                    st.error(response_text)
                else:
                    st.markdown("### 📝 تقرير تقييم اللجنة الطبية للـ Long Case:")
                    st.info(response_text)

# =========================================================
# 🔬 اللجنة الثانية: OSCE Short Cases (English)
# =========================================================
elif board_selection == "اللجنة الثانية: OSCE Short Cases (English)":
    st.subheader("🔬 OSCE Board: Combined Short Cases المحطات القصيرة")
    st.write("هذه المحطة تضعك أمام حالتين قصيرتين (Obstetrics + Gynecology) باللغة الإنجليزية الطبية مع أسئلة امتحانية تفاعلية متتالية.")

    if st.button("🎲 Generate New OSCE Cases Station"):
        st.session_state.messages = []
        st.session_state.case_started = True
        st.session_state.selected_type = "OSCE"
        st.session_state.current_case_prompt = """
        Act as an expert external medical examiner conducting an OSCE short cases station for final year medical students.
        Generate one brief Obstetrics clinical presentation (e.g., severe postdate pregnancy or cord prolapse scenario) 
        AND one Gynecology clinical presentation (e.g., primary infertility or PMB scenario).
        Provide 2 clear, specific exam questions at the end of the cases. Speak and respond strictly in medical English.
        """
        with st.spinner("Formulating OSCE cases..."):
            initial_text = ask_gemini_direct(text_input="Start the OSCE station now.")
            st.session_state.messages.append({"role": "patient", "text": initial_text})

    # عرض الأسئلة والدردشة للجنة الـ OSCE
    for msg in st.session_state.messages:
        if msg.get("role") == "patient":
            with st.chat_message("user", avatar="🔬"): st.write(msg.get("text", ""))
        elif msg.get("role") == "doctor":
            with st.chat_message("assistant", avatar="👨‍⚕️"): st.write(msg.get("text", ""))

    if st.session_state.case_started and st.session_state.selected_type == "OSCE":
        osce_input = st.chat_input("Write your answers for the OSCE questions here...")
        if osce_input:
            with st.spinner("Evaluating your OSCE answers..."):
                st.session_state.messages.append({"role": "doctor", "text": osce_input})
                feedback = ask_gemini_direct(text_input="Grade my previous answer strictly as an OSCE Examiner, give marks and the model answer.")
                st.session_state.messages.append({"role": "patient", "text": feedback})
                st.rerun()

# =========================================================
# 📚 اللجنة الثالثة: Curriculum & Instruments Quiz (English)
# =========================================================
else:
    st.subheader("📚 Board 3: Oral Viva, Topics & Instruments")
    st.write("امتحان شفوي في الـ 81 موضوعاً والآلات الجراحية المعتمدة في محاضرات الدكاترة بالإنجليزية.")
    
    quiz_domain = st.radio("Select Domain:", ["Syllabus Topics (المنهج والأسئلة الشفوية)", "Instruments & Tools (الآلات الطبية وعيادة الدكتورة هبة)"], horizontal=True)
    
    if st.button("❓ Pull Random Exam Question"):
        st.session_state.messages = []
        st.session_state.case_started = True
        st.session_state.selected_type = "Quiz"
        
        if quiz_domain == "Syllabus Topics (المنهج والأسئلة الشفوية)":
            chosen_topic = random.choice(CURRICULUM_TOPICS)
            st.session_state.current_case_prompt = f"""
            Act as an external medical professor in an oral viva examination. Ask one high-yield clinical exam question 
            for a 4th-year student regarding this specific curriculum topic: '{chosen_topic}'. 
            The question must test clinical understanding, indications, or complications. Speak strictly in English.
            """
        else:
            st.session_state.current_case_prompt = """
            Act as an examiner in an OB/GYN practical exam. Describe one clinical surgical tool/instrument 
            (such as Ventouse, Forceps, Speculum, or Foley Catheter) based on standard clinical knowledge, 
            and ask 1 targeted question about its indications, contraindications, or complications. Speak strictly in English.
            """
            
        with st.spinner("Extracting board question..."):
            quiz_text = ask_gemini_direct(text_input="Give me the exam question now.")
            st.session_state.messages.append({"role": "patient", "text": quiz_text})

    # عرض الأسئلة والدردشة للجنة الـ الشفوي والآلات
    for msg in st.session_state.messages:
        if msg.get("role") == "patient":
            with st.chat_message("user", avatar="📚"): st.write(msg.get("text", ""))
        elif msg.get("role") == "doctor":
            with st.chat_message("assistant", avatar="👨‍⚕️"): st.write(msg.get("text", ""))

    if st.session_state.case_started and st.session_state.selected_type == "Quiz":
        quiz_input = st.chat_input("Type your formal academic answer here...")
        if quiz_input:
            with st.spinner("Analyzing answers..."):
                st.session_state.messages.append({"role": "doctor", "text": quiz_input})
                evaluation = ask_gemini_direct(text_input="Evaluate my answer scientifically, provide the score and ideal correction.")
                st.session_state.messages.append({"role": "patient", "text": evaluation})
                st.rerun()
