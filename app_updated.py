import base64
import json
import random
import re
import uuid
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import streamlit as st
from streamlit.components.v1 import html as components_html
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import g4f

# ═══════════════════════════════════════════════════════════════
# Import MCQ Bank
# ═══════════════════════════════════════════════════════════════
from forensic_toxicology_mcq import (
    FORENSIC_MCQ_BANK,
    TOXICOLOGY_MCQ_BANK,
    get_random_forensic_mcqs,
    get_random_toxicology_mcqs,
    get_mixed_mcqs,
    FORENSIC_TOPICS,
    TOXICOLOGY_TOPICS
)

# ═══════════════════════════════════════════════════════════════
# Streamlit Configuration
# ═══════════════════════════════════════════════════════════════

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_path = "banner.png"  

try:
    img_b64 = get_base64_of_bin_file(image_path)
    st.markdown(
        f"""
        <div style="width:100%; margin-top: 20px;">
            <img src="data:image/png;base64,{img_b64}" style="
                width: 100%;
                display: block;
                border-radius: 14px;
                object-fit: cover;
            " alt="Simulator banner">
        </div>
        """,
        unsafe_allow_html=True,
    )
except FileNotFoundError:
    pass

st.set_page_config(page_title="4th Year Exam Simulator", page_icon="🩺", layout="wide")

# ─────────────────────────────────────────────
# Firebase Initialization
# ─────────────────────────────────────────────
if not firebase_admin._apps:
    try:
        cred_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "databaseURL": st.secrets["FIREBASE_DATABASE_URL"]
        })
    except Exception as _fb_err:
        st.error(f"خطأ في الاتصال بـ Firebase: {_fb_err}")
        st.stop()

# ─────────────────────────────────────────────
# Admin Constants
# ─────────────────────────────────────────────
ADMIN_USERNAME = "Ameenbadda"
ADMIN_PASSWORD = "862000A"

# ═══════════════════════════════════════════════════════════════
# Styling
# ═══════════════════════════════════════════════════════════════

st.markdown(
    """
    <style>
        :root {
            --ink: #123C69;
            --teal: #1D9A8A;
            --mint: #E7F6F2;
            --coral: #F46F5E;
            --amber: #F2B84B;
            --paper: #FFFFFF;
            --soft: #F5FAFA;
            --line: #D8E7E7;
            --muted: #667085;
            --shadow-sm: 0 10px 24px rgba(18, 60, 105, 0.08);
            --shadow-md: 0 18px 42px rgba(18, 60, 105, 0.14);
        }
        
        .stApp {
            background:
                linear-gradient(135deg, rgba(29,154,138,0.10) 0 18%, transparent 18% 100%),
                linear-gradient(45deg, rgba(244,111,94,0.08) 0 12%, transparent 12% 100%),
                linear-gradient(180deg, #f7fbfb 0%, #eef7f5 48%, #f9fbfd 100%);
        }
        
        .mcq-card {
            background: rgba(255,255,255,0.94);
            border: 1px solid var(--line);
            border-right: 5px solid var(--teal);
            padding: 16px 18px;
            border-radius: 14px;
            margin-bottom: 14px;
            box-shadow: var(--shadow-sm);
            animation: fadeUp 0.32s ease both;
        }
        
        .mcq-correct {
            border-right: 5px solid #28a745 !important;
            background: linear-gradient(180deg, #f0fff4, #ffffff) !important;
        }
        
        .mcq-wrong {
            border-right: 5px solid #dc3545 !important;
            background: linear-gradient(180deg, #fff5f5, #ffffff) !important;
        }
        
        .mcq-section-title {
            color: var(--ink);
            font-weight: 900;
            font-size: 1.2rem;
            margin: 18px 0 10px 0;
            border-bottom: 2px solid var(--line);
            padding-bottom: 6px;
        }
        
        .hero-panel {
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
            gap: 16px;
            align-items: stretch;
            background: linear-gradient(135deg, rgba(18,60,105,0.98) 0%, rgba(29,154,138,0.96) 72%, rgba(242,184,75,0.82) 100%);
            color: white;
            border-radius: 18px;
            padding: 28px;
            margin: 10px 0 18px 0;
            overflow: hidden;
            box-shadow: 0 22px 52px rgba(18, 60, 105, 0.22);
        }
        
        .visual-tile {
            background: rgba(255,255,255,0.16);
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: #ffffff !important;
            text-decoration: none !important;
            cursor: pointer;
            transition: transform 0.18s ease, background 0.18s ease;
        }
        
        .visual-tile:hover {
            background: rgba(255,255,255,0.24);
            transform: translateY(-4px);
        }
        
        h1 {
            text-align: center;
            color: var(--ink);
            font-weight: 900;
            text-shadow: 0 1px 0 rgba(255,255,255,0.85);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🩺 محاكي امتحانات السنة الرابعة (4th Year Exam Simulator)")

# ═══════════════════════════════════════════════════════════════
# AI Helper Functions
# ═══════════════════════════════════════════════════════════════

def ask_free_ai(system_instruction, user_input):
    """Query free AI service using g4f"""
    full_prompt = (
        f"Instruction: {system_instruction}\n"
        "CRITICAL: Be extremely concise, fast. Start immediately with response.\n\n"
        f"Input: {user_input}"
    )
    filter_words = [
        "aria", "opera", "assistant", "hello", "hi there",
        "pollinations", "support our mission", "powered by",
    ]
    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": full_prompt}],
        )
    except Exception:
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": full_prompt}],
            )
        except Exception:
            return "Unable to generate response at this time."

    clean_text = str(response).strip()
    lines = clean_text.split("\n")
    filtered_lines = [
        line for line in lines
        if not any(word in line.lower() for word in filter_words)
    ]
    return "\n".join(filtered_lines).strip()

# ═══════════════════════════════════════════════════════════════
# Session State Initialization
# ═══════════════════════════════════════════════════════════════

defaults = {
    "active_subject": "",
    "auth_username": "",
    "auth_role": "",
    "forensic_board": "",
    "ft_mcq_mode": "",
    "ft_mcq_questions": [],
    "ft_mcq_answers": {},
    "ft_mcq_submitted": False,
    "ft_mcq_generation_error": "",
}

for _key, _val in defaults.items():
    if _key not in st.session_state:
        st.session_state[_key] = _val

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def is_logged_in() -> bool:
    return bool(st.session_state.get("auth_username"))

def is_admin() -> bool:
    return st.session_state.get("auth_role") == "admin"

def reset_ft_mcq_state(mode: str = "") -> None:
    st.session_state.ft_mcq_mode = mode
    st.session_state.ft_mcq_questions = []
    st.session_state.ft_mcq_answers = {}
    st.session_state.ft_mcq_submitted = False
    st.session_state.ft_mcq_generation_error = ""

def forensic_mcq_url() -> str:
    return "?subject=forensic&ft=mcq"

# ═══════════════════════════════════════════════════════════════
# Forensic & Toxicology MCQ Committee
# ═══════════════════════════════════════════════════════════════

def render_forensic_dashboard() -> None:
    """Display Forensic & Toxicology main dashboard"""
    st.markdown(
        f"""
        <div class="hero-panel">
            <div>
                <h2>Forensic & Toxicology | لجان مادتي فرونسك و توكسو</h2>
                <p>
                    محاكي امتحان فرونسك & توكسو — لجنة MCQs النظري.
                    أسئلة معدة وفقاً لمستوى الجامعة بنمط امتحانات السنوات السابقة.
                </p>
            </div>
            <div class="hero-visual">
                <a class="visual-tile" href="{forensic_mcq_url()}" target="_self" style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="font-size: 2rem;">📝</div>
                    <div style="font-weight: bold;">لجنة MCQs النظري</div>
                    <div style="font-size: 0.9rem;">فرونسك / توكسو / مختلط</div>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("اضغط على المربع بالأعلى لاختيار لجنة MCQs.")

def render_ft_mcq_committee() -> None:
    """Display MCQ examination committee"""
    st.header("📝 لجنة MCQs النظري — Forensic Medicine & Toxicology")
    st.write("أسئلة انجليزية متقدمة من مواضيع الفرونسك والتوكسو، مع تصحيح مفصل بعد إنهاء الامتحان.")

    back_col, _ = st.columns([1, 4])
    with back_col:
        if st.button("رجوع للجان فرونسك و توكسو", key="back_to_forensic_home"):
            st.session_state.forensic_board = ""
            if "ft" in st.query_params:
                del st.query_params["ft"]
            st.rerun()

    st.markdown("### اختر نوع الأسئلة")
    col_for, col_tox, col_mix, col_past = st.columns(4)
    mode_clicked = None
    
    with col_for:
        if st.button("🔬 فرونسك فقط\n(30 سؤال)", key="ft_forensic_30", use_container_width=True):
            mode_clicked = "Forensic only"
    
    with col_tox:
        if st.button("☠️ توكسو فقط\n(30 سؤال)", key="ft_toxicology_30", use_container_width=True):
            mode_clicked = "Toxicology only"
    
    with col_mix:
        if st.button("⚖️ فرونسك + توكسو\n(60 سؤال)", key="ft_mixed_60", use_container_width=True):
            mode_clicked = "Mixed"
    
    with col_past:
        st.button("📚 أسئلة السنوات\n(قريباً)", key="ft_past_years", disabled=True, use_container_width=True)

    if mode_clicked:
        reset_ft_mcq_state(mode_clicked)
        with st.spinner("جاري تحضير الأسئلة..."):
            try:
                if mode_clicked == "Forensic only":
                    st.session_state.ft_mcq_questions = get_random_forensic_mcqs(30)
                elif mode_clicked == "Toxicology only":
                    st.session_state.ft_mcq_questions = get_random_toxicology_mcqs(30)
                else:  # Mixed
                    st.session_state.ft_mcq_questions = get_mixed_mcqs(30, 30)
            except Exception as err:
                st.session_state.ft_mcq_generation_error = str(err)
        st.rerun()

    if st.session_state.ft_mcq_generation_error:
        st.error(
            f"خطأ في تحضير الأسئلة: {st.session_state.ft_mcq_generation_error}"
        )

    questions = st.session_state.ft_mcq_questions
    if not questions:
        st.info("اختر نوع الأسئلة من الأزرار بالأعلى لبدء امتحان جديد.")
        return

    mode_ar = {
        "Forensic only": "🔬 فرونسك فقط",
        "Toxicology only": "☠️ توكسو فقط",
        "Mixed": "⚖️ فرونسك + توكسو",
    }.get(st.session_state.ft_mcq_mode, st.session_state.ft_mcq_mode)
    
    st.success(f"✅ تم تحضير: {mode_ar} — عدد الأسئلة: {len(questions)}")

    # Display all questions
    for i, mcq in enumerate(questions):
        saved = st.session_state.ft_mcq_answers.get(i)
        options_list = [f"{letter}. {mcq['opts'][letter]}" for letter in ["A", "B", "C", "D"]]

        if st.session_state.ft_mcq_submitted:
            is_correct = saved == mcq["ans"]
            card_class = "mcq-card mcq-correct" if is_correct else "mcq-card mcq-wrong"
            status_icon = "✅" if is_correct else "❌"
            chosen_text = mcq["opts"].get(saved, "لم تتم الإجابة") if saved else "لم تتم الإجابة"
            correct_text = mcq["opts"][mcq["ans"]]
            
            st.markdown(
                f"""
                <div class="{card_class}">
                    <b>{status_icon} Q{i + 1}. {mcq['q']}</b><br>
                    <span style="color:#667085;font-size:0.9rem;">الموضوع: {mcq.get('topic', '—')} | القسم: {mcq.get('section', '—')}</span><br><br>
                    <b>إجابتك:</b> {saved or '—'} - {chosen_text}<br>
                    <b>الإجابة الصحيحة:</b> {mcq['ans']} - {correct_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            default_idx = None
            if saved:
                for idx, opt in enumerate(options_list):
                    if opt.startswith(saved + "."):
                        default_idx = idx
                        break
            
            chosen = st.radio(
                f"Q{i + 1}. {mcq['q']}",
                options=options_list,
                index=default_idx,
                key=f"ft_mcq_q_{i}",
            )
            st.caption(f"الموضوع: {mcq.get('topic', '—')} | القسم: {mcq.get('section', '—')}")
            
            if chosen:
                st.session_state.ft_mcq_answers[i] = chosen[0]

    st.write("---")

    if not st.session_state.ft_mcq_submitted:
        answered = len(st.session_state.ft_mcq_answers)
        st.caption(f"أجبت على {answered} من {len(questions)} سؤال.")
        
        if st.button("✅ تحقق من إجاباتي", key="ft_mcq_submit", use_container_width=True):
            st.session_state.ft_mcq_submitted = True
            st.rerun()
    else:
        correct_count = sum(
            1 for i, mcq in enumerate(questions)
            if st.session_state.ft_mcq_answers.get(i) == mcq["ans"]
        )
        total = len(questions)
        pct = round(correct_count / total * 100) if total else 0
        
        # Score card
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#123C69,#1D9A8A);color:white;
                border-radius:14px;padding:22px 28px;text-align:center;margin:10px 0 20px 0;
                box-shadow:0 8px 24px rgba(18,60,105,0.18);">
                <div style="font-size:2.2rem;font-weight:900;">{correct_count}/{total}</div>
                <div style="font-size:1.3rem;margin:4px 0;">{pct}%</div>
                <div style="font-size:1rem;margin-top:8px;">
                    {"🌟 ممتاز!" if pct >= 80 else "👍 جيد جداً" if pct >= 65 else "📘 مقبول" if pct >= 50 else "📖 يحتاج مراجعة"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col_retry, col_new = st.columns(2)
        with col_retry:
            if st.button("🔄 إعادة الامتحان", key="ft_mcq_retry", use_container_width=True):
                st.session_state.ft_mcq_answers = {}
                st.session_state.ft_mcq_submitted = False
                st.rerun()
        
        with col_new:
            if st.button("🆕 توليد مجموعة جديدة", key="ft_mcq_new_set", use_container_width=True):
                mode = st.session_state.ft_mcq_mode or "Forensic only"
                reset_ft_mcq_state(mode)
                with st.spinner("جاري توليد مجموعة جديدة..."):
                    try:
                        if mode == "Forensic only":
                            st.session_state.ft_mcq_questions = get_random_forensic_mcqs(30)
                        elif mode == "Toxicology only":
                            st.session_state.ft_mcq_questions = get_random_toxicology_mcqs(30)
                        else:
                            st.session_state.ft_mcq_questions = get_mixed_mcqs(30, 30)
                    except Exception as err:
                        st.session_state.ft_mcq_generation_error = str(err)
                st.rerun()

# ═══════════════════════════════════════════════════════════════
# Main App Flow
# ═══════════════════════════════════════════════════════════════

# Set page based on query parameters
subject = st.query_params.get("subject", "")
ft_param = st.query_params.get("ft", "")

if subject == "forensic":
    st.session_state.active_subject = "forensic"
    if ft_param == "mcq":
        st.session_state.forensic_board = "mcq"

# Display appropriate view
if st.session_state.active_subject == "forensic":
    if st.session_state.forensic_board == "mcq":
        render_ft_mcq_committee()
    else:
        render_forensic_dashboard()
else:
    # Main subject selection
    st.write("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.72); border-radius: 18px; margin: 20px 0;">
            <h2>🎯 اختر المادة لبدء الاختبار التفاعلي</h2>
            <p style="font-size: 1.05rem; color: #444;">واجهة تدريب منظمة وسريعة</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤰🩺👶\n\nالنساء والولادة\nObstetrics & Gynecology", 
                     use_container_width=True, 
                     key="subject_gyne"):
            st.session_state.active_subject = "gyne"
            if "subject" in st.query_params:
                del st.query_params["subject"]
            st.rerun()
    
    with col2:
        if st.button("🔬💀⚖️\n\nالطب الشرعي والسموم\nForensic & Toxicology", 
                     use_container_width=True,
                     key="subject_forensic"):
            st.session_state.active_subject = "forensic"
            st.query_params["subject"] = "forensic"
            st.rerun()
