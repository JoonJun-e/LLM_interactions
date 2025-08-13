import streamlit as st
import requests
import json
import os

# --- ⚠️ 중요 ⚠️: API 키를 Streamlit의 보안 저장소(Secrets)에서 불러오도록 수정 ---
# 로컬 테스트 시에는 이 줄에서 오류가 날 수 있지만, 배포 시에는 정상 작동합니다.
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))
# --------------------------------------------------------------------

# API 엔드포인트 URL
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- Streamlit 웹 앱 UI 구성 ---
st.set_page_config(page_title="간단한 AI 챗봇", page_icon="💬")
st.title("Prototype - AI Privacy Paradox 💬")
st.write("AI와 자유롭게 대화해보세요.")

# API 키가 설정되지 않았을 경우 에러 메시지 표시
if not API_KEY:
    st.error("⚠️ Gemini API 키가 설정되지 않았습니다. Streamlit Secrets에 추가해주세요.")
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"})

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
            # 대화 기록을 포함하여 API에 전송
            history = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [{"text": msg["content"]}]})
            history.pop() # 마지막 사용자 메시지는 중복되므로 제거

            payload = {
                "contents": history + [{"role": "user", "parts": [{"text": prompt}]}]
            }
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
            st.error("API 응답 형식이 예상과 다릅니다.")
            st.write(response.json())
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")
