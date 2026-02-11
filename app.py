import streamlit as st
from streamlit_elements import elements, dashboard, mui, html

st.set_page_config(page_title="전술판(플랜B)", layout="wide")
st.title("🧲 전술판 (플랜 B: streamlit-elements 드래그 토큰)")

# -----------------------------
# 초기 레이아웃/토큰
# -----------------------------
COLS = 24  # 가로 격자 수 (클수록 더 자유롭게 움직이는 느낌)
ROW_H = 26

def default_layout():
    # 4층 박스(고정: draggable False)
    # y는 위에서 아래로
    floors = [
        dict(i="floor4", x=0,  y=0,  w=12, h=4, static=True),
        dict(i="floor3", x=0,  y=4,  w=12, h=4, static=True),
        dict(i="floor2", x=0,  y=8,  w=12, h=4, static=True),
        dict(i="floor1", x=0,  y=12, w=12, h=4, static=True),
    ]
    # 토큰(드래그 가능)
    tokens = [
        dict(i="t_fire1", x=14, y=1,  w=6, h=2),
        dict(i="t_res1",  x=14, y=4,  w=6, h=2),
        dict(i="t_ems1",  x=14, y=7,  w=6, h=2),
    ]
    return floors + tokens

def default_tokens_meta():
    return {
        "t_fire1": {"text": "🚒  진압1"},
        "t_res1":  {"text": "🛟  구조1"},
        "t_ems1":  {"text": "🚑  구급1"},
    }

if "layout" not in st.session_state:
    st.session_state.layout = default_layout()

if "tokens_meta" not in st.session_state:
    st.session_state.tokens_meta = default_tokens_meta()

# -----------------------------
# 사이드바: 토큰 추가/초기화
# -----------------------------
with st.sidebar:
    st.header("⚙️ 제어판")

    if st.button("🔄 초기화"):
        st.session_state.layout = default_layout()
        st.session_state.tokens_meta = default_tokens_meta()
        st.rerun()

    st.divider()
    st.subheader("➕ 출동대 토큰 추가")
    name = st.text_input("이름", value="진압2")
    icon = st.selectbox("아이콘", ["🚒", "🛟", "🚑", "🚓", "🧯", "👮", "🏥", "🛰️"], index=0)
    if st.button("추가"):
        # 새 토큰 id 생성
        base = f"t_{len(st.session_state.tokens_meta)+1}"
        new_id = base
        n = 1
        while new_id in st.session_state.tokens_meta:
            n += 1
            new_id = f"{base}_{n}"

        st.session_state.tokens_meta[new_id] = {"text": f"{icon}  {name.strip() or '새 토큰'}"}
        # 오른쪽 공간에 배치
        st.session_state.layout.append(dict(i=new_id, x=14, y=10, w=6, h=2))
        st.rerun()

# -----------------------------
# 레이아웃 변경 콜백
# -----------------------------
def on_layout_change(new_layout):
    # streamlit-elements가 넘겨주는 layout(리스트)을 그대로 저장
    st.session_state.layout = new_layout

# -----------------------------
# 메인 보드
# -----------------------------
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("🗺️ 전술판 (드래그로 이동)")

    with elements("tactical_board"):
        # 드래그 핸들(토큰 카드 상단을 잡고 움직이게)
        grid = dashboard.Grid(
            st.session_state.layout,
            cols=COLS,
            rowHeight=ROW_H,
            isDraggable=True,
            isResizable=False,
            onLayoutChange=on_layout_change,
            margin=[10, 10],
        )

        with grid:
            # 4층 박스(고정)
            def floor_box(fid, label):
                with mui.Paper(
                    key=fid,
                    elevation=1,
                    sx={
                        "height": "100%",
                        "border": "2px solid #111",
                        "borderRadius": "10px",
                        "backgroundColor": "white",
