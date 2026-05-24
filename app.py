import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Voice Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي الـ Long Case الصوتي التلقائي")
st.write("مرحباً بك يا دكتور أمين وزملائك. اضغط على المايك وتحدث مباشرة مع المريضة لأخذ الـ History.")

# 2. حقن مفتاح الـ API الخاص بك
GEMINI_API_KEY = "AIzaSyCEfS8-uK42rx0AgZP8711a6M9TCXRPiZw"

# 3. الـ System Prompt الطبي لتوجيه المريضة بلهجة عامية
SYSTEM_PROMPT = """
You are acting as a medical simulation bot for a 4th-year medical student practicing OB/GYN history taking. 
Your role is to simulate a Libyan/Arab pregnant or gynecological patient.

CRITICAL RULES:
1. Speak ONLY in a very realistic, simple, local Arabic dialect (لهجة عامية بسيطة كأنك مريضة حقيقية في المستشفى).
2. Keep your answers SHORT (1-2 sentences maximum) to mimic a real voice conversation.
3. If they ask for your name, give a typical local name (e.g., فاطمة، مريم، سالمة). If they ask for age, say 28 or 30.
4. Randomly pick ONE specific OB/GYN case (e.g., Placenta Previa, Pre-eclampsia, Ectopic pregnancy, Abruptio placentae, Ovarian cyst rupture). Do NOT reveal it until requested via evaluation.
5. You are the patient. Do NOT break character until the user asks for evaluation.
"""

# 4. إدارة الجلسة والذاكرة في المتصفح للحفاظ على سير الحالة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_started" not in st.session_state:
    st.session_state.case_started = False
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

def ask_gemini_audio(audio_path_input=None, text_input=None):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # بناء الذاكرة والسياق يدوياً
        full_contents = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        for msg in st.session_state.messages:
            role_type = "model" if msg["role"] == "patient" else "user"
            full_contents.append({"role": role_type, "parts": [msg["text"]]})
        
        # إضافة المدخل الحالي
        if audio_path_input:
            uploaded_audio = genai.upload_file(audio_path_input)
            full_contents.append({"role": "user", "parts": [uploaded_audio, "ردي على سؤال الدكتور بصفتك المريضة بالعامية وفي سطر واحد قصير جداً ومباشر"]])
            response = model.generate_content(full_contents)
            genai.delete_file(uploaded_audio.name)
        else:
            full_contents.append({"role": "user", "parts": [text_input]})
            response = model.generate_content(full_contents)
            
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# زر بدء حالة جديدة
if st.button("🎬 دخول مريضة جديدة العيادة"):
    st.session_state.messages = []
    st.session_state.case_started = True
    st.session_state.last_processed_audio = None
    
    with st.spinner("المريضة تدخل الآن..."):
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([SYSTEM_PROMPT, "ابدئي الحالة واشتكي من العرض الرئيسي بلهجة عامية في سطر واحد"])
        initial_reply = response.text
        
        tts_path = "reply_start.mp3"
        tts = gTTS(text=initial_reply, lang='ar', slow=False)
        tts.save(tts_path)
        
        st.session_state.messages.append({"role": "patient", "text": initial_reply, "audio_path": tts_path})

# 5. عرض المحادثة الحالية بشكل منظم لتفادي الأخطاء البرمجية
for index, msg in enumerate(st.session_state.messages):
    if msg["role"] == "patient":
        with st.chat_message("user", avatar="🤰"):
            st.write(msg["text"])
            if "audio_path" in msg and os.path.exists(msg["audio_path"]):
                # إضافة key فريد لكل عنصر صوتي لحل مشكلة السيرفر تماماً
                st.audio(msg["audio_path"], autoplay=(index == len(st.session_state.messages)-1), key=f"audio_key_{index}")
    else:
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            st.write(msg["text"])

# 6. التفاعل التلقائي عبر المايك المدمج
if st.session_state.case_started:
    st.write("---")
    st.subheader("🎙️ تحدث مع المريضة مباشرة:")
    
    # مسجل الصوت الافتراضي للمتصفح
    audio_value = st.audio_input("اضغط على زر المايك واسأل المريضة (ما اسمك؟ كم عمرك؟ شو يوجع فيك؟)")
    
    # خيار كتابي سريع للاحتياط
    user_text_input = st.chat_input("أو اكتب سؤالك هنا...")

    # أ) معالجة الصوت التلقائي وتفادي التكرار
    if audio_value and audio_value != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio_value
        
        with open("user_voice.wav", "wb") as f:
            f.write(audio_value.read())
            
        with st.spinner("المريضة تستمع وتجيب..."):
            response_text = ask_gemini_audio(audio_path_input="user_voice.wav")
            
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
            response_text = ask_gemini_audio(text_input=user_text_input)
            
            tts_path = f"reply_{len(st.session_state.messages)}.mp3"
            tts = gTTS(text=response_text, lang='ar', slow=False)
            tts.save(tts_path)
            
            st.session_state.messages.append({"role": "doctor", "text": user_text_input})
            st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
            st.rerun()

# 7. التقييم النهائي
if st.session_state.case_started:
    st.write("---")
    if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
        with st.spinner("جاري إعداد تقرير اللجنة الطبية..."):
            response_text = ask_gemini_audio(text_input="انتهي من تقمص الدور الآن، واكتب لي التقييم الطبي الكامل للحالة باللغة العربية الفصحى، واذكر ما هو التشخيص السري، وما هي الأسئلة الهامة التي نسي الطلاب طرحها.")
            st.markdown("### 📝 تقرير تقييم اللجنة الطبية:")
            st.info(response_text)
