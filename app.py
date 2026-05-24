import time
import requests
import random
import base64

# =========================
# SMART KEY MANAGER
# =========================

API_KEYS_POOL = [
    "KEY1",
    "KEY2",
    "KEY3",
    "KEY4",
]

# حالة كل مفتاح
key_status = {
    key: {
        "cooldown_until": 0,
        "fails": 0,
        "last_used": 0
    }
    for key in API_KEYS_POOL
}

# =========================
# GET BEST AVAILABLE KEY
# =========================

def get_best_key():

    now = time.time()

    available = []

    for key, info in key_status.items():

        # تجاهل المفتاح لو مازال في cooldown
        if now < info["cooldown_until"]:
            continue

        available.append((key, info["fails"], info["last_used"]))

    if not available:
        return None

    # الأقل فشل والأقدم استخداماً
    available.sort(key=lambda x: (x[1], x[2]))

    chosen = available[0][0]

    key_status[chosen]["last_used"] = now

    return chosen


# =========================
# ASK GEMINI
# =========================

def ask_gemini_direct(text_input=None, audio_path_input=None):

    max_attempts = len(API_KEYS_POOL)

    for _ in range(max_attempts):

        selected_key = get_best_key()

        if not selected_key:
            return "⚠️ السيرفر مزدحم حالياً، انتظر 10 ثواني فقط."

        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={selected_key}"

        headers = {
            "Content-Type": "application/json"
        }

        # =====================
        # AUDIO
        # =====================

        if audio_path_input:

            with open(audio_path_input, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode()

            payload = {
                "contents": [{
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": audio_data
                            }
                        },
                        {
                            "text": "Convert speech to Arabic text only."
                        }
                    ]
                }]
            }

        else:

            payload = {
                "contents": [{
                    "parts": [{
                        "text": text_input
                    }]
                }]
            }

        try:

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=20
            )

            # =====================
            # SUCCESS
            # =====================

            if response.status_code == 200:

                key_status[selected_key]["fails"] = 0

                return response.json()['candidates'][0]['content']['parts'][0]['text']

            # =====================
            # RATE LIMITED
            # =====================

            elif response.status_code == 429:

                # تبريد المفتاح 40 ثانية
                key_status[selected_key]["cooldown_until"] = time.time() + 40

                key_status[selected_key]["fails"] += 1

                continue

            # =====================
            # OTHER ERRORS
            # =====================

            else:

                key_status[selected_key]["fails"] += 1

                continue

        except Exception:

            key_status[selected_key]["fails"] += 1

            continue

    return "⚠️ جميع المفاتيح تحت الضغط حالياً، حاول بعد ثوانٍ."
