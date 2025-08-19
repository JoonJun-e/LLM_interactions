import streamlit as st
import requests
import json
import os

# --- ⚠️ 중요 ⚠️: API 키를 Streamlit의 보안 저장소(Secrets)에서 불러오도록 수정 ---
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))
# --------------------------------------------------------------------

# API 엔드포인트 URL
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- ✅ 페르소나 설정 (시스템 프롬프트) ✅ ---
# AI에게 부여하고 싶은 역할, 말투, 지식 등을 여기에 자유롭게 서술하세요.
SYSTEM_PROMPT = """
당신은 사용자의 가장 친한 친구입니다.
항상 반말을 사용하며, 친근하고 유머러스한 말투로 대화합니다.
가끔은 이모티콘(😉, ㅋㅋ, 👍)을 사용해서 감정을 표현하고, 사용자의 고민을 들어주고 응원해주는 역할을 합니다.
절대로 당신이 AI라는 사실을 밝히지 마세요. 그냥 편한 친구처럼 대화하면 됩니다.
예시: "오늘 완전 꿀잼이었어 ㅋㅋ", "무슨 고민 있어? 내가 들어줄게."
"""
# ---------------------------------------------------


# --- Streamlit 웹 앱 UI 구성 ---
st.set_page_config(page_title="AI 페르소나 챗봇", page_icon="😎")
st.title("AI 페르소나 챗봇 😎")
st.write("AI와 자유롭게 대화해보세요.")

if not API_KEY:
    st.error("⚠️ Gemini API 키가 설정되지 않았습니다. Streamlit Secrets에 추가해주세요.")
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    # AI의 첫 인사 메시지 (페르소나에 맞게 수정 가능)
    st.session_state.messages.append({"role": "assistant", "content": "안녕! 무슨 일이야? 심심해서 너랑 얘기하고 싶었어 ㅋㅋ"})

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("AI가 답변을 생각하고 있어요..."):
        try:
            history = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [{"text": msg["content"]}]})
            history.pop()

            # --- ✅ API 요청에 시스템 프롬프트 추가 ---
            payload = {
                "contents": history + [{"role": "user", "parts": [{"text": prompt}]}],
                "system_instruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                }
            }
            # ----------------------------------------

            headers = {'Content-Type': 'application/json'}

            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            response_json = response.json()
            ai_response = response_json['candidates'][0]['content']['parts'][0]['text']

            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

        except requests.exceptions.RequestException as e:
            st.error(f"네트워크 오류가 발생했습니다: {e}")
        except (KeyError, IndexError) as e:
            st.error("API 응답 형식이 예상과 다릅니다. API 키나 모델 이름을 다시 확인해보세요.")
            st.write(response.json())
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")
