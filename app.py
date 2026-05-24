import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# 1. إعداد الصفحة والعنوان والمظهر
st.set_page_config(page_title="OB/GYN Long Case Simulator", page_icon="🩺", layout="centered")
st.title("🩺 محاكي امتحان الـ Long Case (نساء وولادة)")
st.write("مرحباً بك يا دكتور أمين وزملائك. سجلوا أسئلتكم كفويس نوت على الموبايل وارفعوها هنا للتحدث مع المريضة.")

# 2. إعداد مفتاح الـ API الخاص بك
GEMINI_API_KEY = "AIzaSyCEfS8-uK42rx0AgZP8711a6M9TCXRPiZw"

# 3. التعليمات البرمجية لتوجيه الذكاء الاصطناعي (System Prompt)
SYSTEM_PROMPT = """
You are acting as a medical simulation bot for a 4th-year medical student practicing OB/GYN history taking. 
Your role is to simulate a Libyan/Arab pregnant or gynecological patient.

CRITICAL RULES:
1. Speak in a very realistic, simple, local Arabic dialect (لهجة عامية بسيطة كأنك مريضة حقيقية في المستشفى).
2. Keep your answers SHORT (1-2 sentences maximum) as this is a voice-based conversation. Long text sounds unrealistic.
3. Randomly pick ONE specific OB/GYN case (e.g., Placenta Previa, Pre-eclampsia, Ectopic pregnancy, Abruptio placentae, Ovarian cyst rupture). Do NOT reveal it until requested via evaluation.
4. You are the patient. Do NOT break character until the user asks for evaluation.
"""

# 4. إدارة الجلسة والذاكرة في المتصفح للحفاظ على سير الحالة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "case_started" not in st.session_state:
    st.session_state.case_started = False

# دالة لتوليد الردود تم تعديل مسار الموديل فيها لحل مشكلة الـ 404 نهائياً
def ask_gemini(prompt_input):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # تم استخدام الموديل مباشرة بدون بادئة وتغييره إلى النسخة الأكثر استقراراً للـ API
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        full_contents = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        for msg in st.session_state.messages:
            role_type = "model" if msg["role"] == "patient" else "user"
            full_contents.append({"role": role_type, "parts": [msg["text"]]})
        
        full_contents.append({"role": "user", "parts": [prompt_input]})
        
        response = model.generate_content(full_contents)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# زر بدء حالة جديدة
if st.button("🎬 ابدأ حالة سريرية جديدة (مريضة جديدة)"):
    st.session_state.messages = []
    st.session_state.case_started = True
    
    with st.spinner("جاري دخول المريضة إلى العيادة..."):
        initial_reply = ask_gemini("ابدئي الحالة واشتكي من العرض الرئيسي بلهجة عامية في سطر واحد")
        
        # توليد الصوت للشكوى الأولى
        tts_path = "reply_start.mp3"
        tts = gTTS(text=initial_reply, lang='ar', slow=False)
        tts.save(tts_path)
        
        st.session_state.messages.append({"role": "patient", "text": initial_reply, "audio_path": tts_path})

# 5. عرض المحادثة الحالية بشكل منظم
for index, msg in enumerate(st.session_state.messages):
    if msg["role"] == "patient":
        with st.chat_message("user", avatar="🤰"):
            st.write(msg["text"])
            if "audio_path" in msg and os.path.exists(msg["audio_path"]):
                st.audio(msg["audio_path"])
    else:
        with st.chat_message("assistant", avatar="👨‍⚕️"):
            st.write(msg["text"])

# 6. التفاعل مع المريضة
if st.session_state.case_started:
    st.write("---")
    st.subheader("🎙️ وجه سؤالك للمريضة:")
    
    # ميزة رفع ملف صوتي
    audio_file = st.file_uploader("ارفع تسجيل سؤالك الصوتي هنا:", type=["wav", "mp3", "m4a", "ogg"])
    
    # مربع نصي كخيار احتياطي وسريع
    user_text_input = st.chat_input("أو اكتب سؤالك هنا مباشرة...")

    # أ) معالجة الملف الصوتي إذا تم رفعه
    if audio_file is not None:
        with open("temp_user_voice.wav", "wb") as f:
            f.write(audio_file.read())
        
        with st.spinner("المريضة تستمع وتجيب بصوتها..."):
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                uploaded_audio = genai.upload_file("temp_user_voice.wav")
                
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content([uploaded_audio, f"{SYSTEM_PROMPT}\n\nردي على سؤال الدكتور بصفتك المريضة بالعامية وفي سطر واحد"])
                
                tts_path = f"reply_{len(st.session_state.messages)}.mp3"
                tts = gTTS(text=response.text, lang='ar', slow=False)
                tts.save(tts_path)
                
                st.session_state.messages.append({"role": "doctor", "text": "🎤 تم إرسال سؤال صوتي"})
                st.session_state.messages.append({"role": "patient", "text": response.text, "audio_path": tts_path})
                
                genai.delete_file(uploaded_audio.name)
                st.rerun()
            except Exception as e:
                st.error("حدثت مشكلة في معالجة الملف الصوتي، يرجى المحاولة مرة أخرى أو استخدام الكتابة.")

    # ب) معالجة الإدخال النصي
    if user_text_input:
        with st.spinner("المريضة تجيب..."):
            response_text = ask_gemini(user_text_input)
            
            tts_path = f"reply_{len(st.session_state.messages)}.mp3"
            tts = gTTS(text=response_text, lang='ar', slow=False)
            tts.save(tts_path)
            
            st.session_state.messages.append({"role": "doctor", "text": user_text_input})
            st.session_state.messages.append({"role": "patient", "text": response_text, "audio_path": tts_path})
            st.rerun()

    # 7. قسم إنهاء الحالة والتقييم الطبي النهائي
    st.write("---")
    if st.button("📊 إنهاء الحالة وطلب التقييم من البروفيسور"):
        with st.spinner("جاري تحليل الـ History وإعداد تقرير اللجنة الطبية..."):
            response_text = ask_gemini("انتهي من تقمص الدور الآن، واكتب لي التقييم الطبي الكامل للحالة باللغة العربية الفصحى الطبية، واذكر ما هو التشخيص السري، وما هي الأسئلة الهامة التي نسي الطلاب طرحها وما يجب فعله في الـ Examination.")
            st.markdown("### 📝 تقرير تقييم اللجنة الطبية:")
            st.info(response_text)
