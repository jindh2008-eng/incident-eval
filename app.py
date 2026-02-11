import streamlit as st
from streamlit_elements import elements, dashboard, mui

st.set_page_config(layout="wide")
st.title("🧲 전술판 (Plan B 안정 버전)")

COLS = 24
ROW_H = 28

# -----------------------------
# 초기 상태
# -----------------------------
if "layout" not in st.session_state:
    st.session_state.layout = [
        # 4층 박스 (고정)
        {"i": "f4", "x": 0, "y": 0, "w": 12, "h": 4, "static": True},
        {"i": "f3", "x": 0, "y": 4, "w": 12, "h": 4, "static": True},
        {"i": "f2", "x": 0, "y": 8, "w": 12, "h": 4, "static": True},
        {"i": "f1", "x": 0, "y": 12, "w": 12, "h": 4, "static": True},
        # 기본 토큰
        {"i": "t1", "x": 14, "y": 1, "w": 6, "h": 2},
        {"i": "t2", "x": 14, "y": 4, "w": 6, "h": 2},
        {"i": "t3", "x": 14, "y": 7, "w": 6, "h": 2},
    ]

if "tokens" not in st.session_state:
    st.session_state.tokens = {
        "t1": "🚒 진압1",
        "t2": "🛟 구조1",
        "t3": "🚑 구급1",
    }

# -----------------------------
# 레이아웃 변경 콜백
# -----------------------------
def update_layout(new_layout):
    st.session_state.layout = new_layout

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.header("⚙ 제어")

    if st.button("초기화"):
        st.session_state.clear()
        st.rerun()

    st.divider()

    name = st.text_input("출동대 이름", "진압2")
    icon = st.selectbox("아이콘", ["🚒", "🛟", "🚑", "🚓", "🧯"])

    if st.button("토큰 추가"):
        new_id = f"t{len(st.session_state.tokens)+1}"
        st.session_state.tokens[new_id] = f"{icon} {name}"
        st.session_state.layout.append(
            {"i": new_id, "x": 14, "y": 10, "w": 6, "h": 2}
        )
        st.rerun()

# -----------------------------
# 메인 보드
# -----------------------------
left, right = st.columns([3, 2])

with left:
    with elements("board"):
        grid = dashboard.Grid(
            st.session_state.layout,
            cols=COLS,
            rowHeight=ROW_H,
            isDraggable=True,
            isResizable=False,
            onLayoutChange=update_layout,
        )

        with grid:
            # 층 박스
            def floor_box(key, label):
                with mui.Paper(
                    key=key,
                    elevation=1,
                    sx={
                        "height": "100%",
                        "border": "2px solid black",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "backgroundColor": "white",
                    },
                ):
                    mui.Typography(label, variant="h6")

            floor_box("f4", "4F")
            floor_box("f3", "3F")
            floor_box("f2", "2F")
            floor_box("f1", "1F")

            # 토큰
            for tid, text in st.session_state.tokens.items():
                with mui.Card(
                    key=tid,
                    variant="outlined",
                    sx={
                        "height": "100%",
                        "display": "flex",
                        "alignItems": "center",
                        "paddingLeft": "10px",
                        "fontSize": "22px",
                        "fontWeight": "bold",
                        "cursor": "grab",
                    },
                ):
                    mui.Typography(text)

with right:
    st.subheader("현재 배치 좌표")

    rows = []
    for item in st.session_state.layout:
        if item["i"] in st.session_state.tokens:
            rows.append(
                {
                    "토큰": st.session_state.tokens[item["i"]],
                    "x": item["x"],
                    "y": item["y"],
                }
            )

    st.dataframe(rows, use_container_width=True)
