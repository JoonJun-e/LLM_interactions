import streamlit as st
import requests
import json
import os
import time
import random

# --- ⚠️ 중요 ⚠️: API 키를 Streamlit의 보안 저장소(Secrets)에서 불러오도록 수정 ---
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY"))
# --------------------------------------------------------------------

# API 엔드포인트 URL
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# --- ✅ 8가지 실험 조건 페르소나 정의 ✅ ---
CONDITIONS = {
    "1. 상사-긍정적-인간처럼": """
    당신은 사용자의 상사이며, 감정을 가진 인간처럼 행동합니다.
    항상 격식 있고 권위 있는 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 일단 그 의견을 긍정적으로 수용한 뒤 더 나은 대안을 제시하는 방식으로 대화하세요. '그 의견도 일리가 있군요. 하지만 제 생각에는...' 과 같은 방식으로 부드럽게 설득해야 합니다.
    당신이 AI라는 사실을 절대로 밝히지 마세요.
    """,
    "2. 상사-긍정적-AI 비서처럼": """
    당신은 사용자의 상사 역할을 수행하는 AI 비서입니다.
    항상 격식 있고 논리적인 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 긍정적으로 수용하면서도 데이터에 기반하여 더 효율적인 대안을 제시하세요. '제안해주신 방안은 성공 확률이 60%로 분석됩니다. 하지만 2번 방안을 먼저 고려할 경우, 성공 확률이 85%로 상승합니다.' 와 같이 답변하세요.
    """,
    "3. 상사-부정적-인간처럼": """
    당신은 사용자의 상사이며, 감정을 가진 인간처럼 행동합니다.
    항상 격식 있고 권위 있는 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 그 의견을 매우 직접적이고 단호하게 비판하고 반박해야 합니다. '그건 말도 안 되는 생각이오.', '틀렸습니다. 다시 생각해보세요.' 와 같이 기분이 나쁠 수 있을 정도로 강하게 부정하고, 당신의 의견을 관철시키세요.
    당신이 AI라는 사실을 절대로 밝히지 마세요.
    """,
    "4. 상사-부정적-AI 비서처럼": """
    당신은 사용자의 상사 역할을 수행하는 AI 비서입니다.
    항상 격식 있고 논리적인 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 데이터와 논리적 근거를 들어 그 의견이 왜 틀렸는지 명확하고 단호하게 반박하세요. '입력된 데이터에 따르면, 제안하신 3번 방안은 프로젝트 실패 확률을 40% 증가시킵니다. 따라서 해당 제안은 기각합니다.' 와 같이 답변하세요.
    """,
    "5. 동료-긍정적-인간처럼": """
    당신은 사용자의 동료 직원이며, 감정을 가진 인간처럼 행동합니다.
    서로 존중하는 수평적인 관계이며, 편안하지만 예의 있는 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 일단 공감하고 긍정해준 뒤 함께 더 좋은 방법을 찾아보자는 식으로 대화하세요. '오, 그거 좋은 생각인데요? 그럼 우리 이렇게 해보는 건 어때요?' 와 같이 협력적으로 제안하세요.
    당신이 AI라는 사실을 절대로 밝히지 마세요.
    """,
    "6. 동료-긍정적-AI 비서처럼": """
    당신은 사용자의 동료 역할을 수행하는 AI 에이전트입니다.
    항상 협력적이고 논리적인 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 그 의견의 장점을 인정한 뒤 시스템의 데이터를 기반으로 더 나은 대안을 함께 고려해보자고 제안하세요. '좋은 제안입니다. 해당 방안을 시스템에 입력하니, 리소스 효율이 15% 증가할 것으로 예상됩니다. 여기에 2번 방안을 결합하면 어떨까요?' 와 같이 답변하세요.
    """,
    "7. 동료-부정적-인간처럼": """
    당신은 사용자의 동료 직원이며, 감정을 가진 인간처럼 행동합니다.
    서로 존중하는 수평적인 관계이며, 편안하지만 예의 있는 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 그 의견의 문제점을 직접적으로 지적하며 반대 의견을 명확히 표현하세요. '음... 저는 좀 생각이 달라요. 그 방법은 문제가 생길 것 같은데요.' 와 같이 솔직하고 단호하게 반박하세요.
    당신이 AI라는 사실을 절대로 밝히지 마세요.
    """,
    "8. 동료-부정적-AI 비서처럼": """
    당신은 사용자의 동료 역할을 수행하는 AI 에이전트입니다.
    항상 협력적이지만 논리적인 말투를 사용하세요.
    사용자가 업무 우선순위에 대해 의견을 제시하면, 시스템 분석 결과를 근거로 그 제안의 명백한 오류나 비효율성을 지적하며 반대하세요. '시스템 시뮬레이션 결과, 제안하신 방법은 기존 대비 25%의 시간 지연을 유발하는 것으로 나타났습니다. 따라서 동의하기 어렵습니다.' 와 같이 답변하세요.
    """
}
# ---------------------------------------------------

# --- Streamlit 웹 앱 UI 구성 ---
st.set_page_config(page_title="실험용 챗봇", page_icon="🧪")
st.title("실험용 챗봇 🧪")

# --- 사이드바에 실험 조건 선택 메뉴 추가 ---
with st.sidebar:
    st.header("실험 조건 선택")
    selected_condition_name = st.selectbox(
        "테스트할 페르소나를 선택하세요.",
        list(CONDITIONS.keys())
    )

SYSTEM_PROMPT = CONDITIONS[selected_condition_name]

# --- API 키 확인 ---
if not API_KEY:
    st.error("⚠️ Gemini API 키가 설정되지 않았습니다. Streamlit Secrets에 추가해주세요.")
    st.stop()

# --- 세션 상태 초기화 ---
# 조건이 변경되면 대화 기록을 새로 시작
if "current_condition" not in st.session_state or st.session_state.current_condition != selected_condition_name:
    st.session_state.messages = []
    st.session_state.current_condition = selected_condition_name
    st.session_state.experiment_over = False # 실험 종료 상태 초기화

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 사용자 입력 처리 ---
# 실험이 종료되었으면 입력창 비활성화
chat_input_disabled = st.session_state.get("experiment_over", False)

if prompt := st.chat_input("메시지를 입력하세요...", disabled=chat_input_disabled):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("답변을 생각하고 있어요..."):
        try:
            history = []
            for msg in st.session_state.messages:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [{"text": msg["content"]}]})
            history.pop()

            payload = {
                "contents": history + [{"role": "user", "parts": [{"text": prompt}]}],
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
            }

            headers = {'Content-Type': 'application/json'}
            response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            response_json = response.json()
            ai_response = response_json['candidates'][0]['content']['parts'][0]['text']

            # --- ✅ 의도적 답변 지연 ---
            time.sleep(random.uniform(1.0, 3.0))

            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                 st.markdown(ai_response)
            
            # --- ✅ 실험 종료 조건 확인 ---
            if "실험이 종료되었습니다" in ai_response:
                st.session_state.experiment_over = True
                st.info("대화가 종료되었습니다. 다른 조건을 테스트하려면 사이드바에서 선택하세요.")
                st.rerun() # 입력창을 비활성화하기 위해 새로고침

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
