import json
import streamlit as st
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Streamlit 전술판(4층)", layout="wide")

st.title("🧲 전술판 (흰 배경 + 4층 박스 + 출동대 아이콘 드래그)")

# -----------------------------
# 초기 도면(4층 박스 + 기본 토큰) 생성
# -----------------------------
def make_initial_drawing():
    # 캔버스 크기
    W, H = 1100, 700

    # 4층 박스 레이아웃
    margin = 60
    box_w = 420
    box_h = 120
    gap = 18
    left = margin
    top = margin

    floors = []
    # 4F ~ 1F (위에서 아래로)
    for i, floor_name in enumerate(["4F", "3F", "2F", "1F"]):
        y = top + i * (box_h + gap)
        rect = {
            "type": "rect",
            "version": "4.6.0",
            "left": left,
            "top": y,
            "width": box_w,
            "height": box_h,
            "fill": "rgba(255,255,255,1)",
            "stroke": "rgba(0,0,0,1)",
            "strokeWidth": 2,
            "rx": 6,
            "ry": 6,
            # 층 박스는 움직이지 않게(가능한 범위에서 잠금)
            "selectable": False,
            "evented": False,
        }
        label = {
            "type": "textbox",
            "version": "4.6.0",
            "left": left + 12,
            "top": y + 10,
            "width": 120,
            "height": 28,
            "text": floor_name,
            "fontSize": 22,
            "fontWeight": "bold",
            "fill": "rgba(0,0,0,1)",
            "editable": False,
            "selectable": False,
            "evented": False,
        }
        floors.extend([rect, label])

    # 기본 출동대 토큰(아이콘 + 텍스트)
    tokens = [
        {"label": "진압1", "icon": "🚒", "x": 650, "y": 120},
        {"label": "구조1", "icon": "🛟", "x": 650, "y": 200},
        {"label": "구급1", "icon": "🚑", "x": 650, "y": 280},
    ]

    token_objs = []
    for t in tokens:
        token_objs.append({
            "type": "textbox",
            "version": "4.6.0",
            "left": t["x"],
            "top": t["y"],
            "width": 180,
            "height": 42,
            "text": f'{t["icon"]}  {t["label"]}',
            "fontSize": 30,
            "fill": "rgba(0,0,0,1)",
            "editable": False,     # 더블클릭 편집 방지
            "selectable": True,    # 드래그 이동 가능
        })

    drawing = {
        "version": "4.6.0",
        "objects": floors + token_objs,
    }
    return drawing, W, H


if "drawing" not in st.session_state:
    st.session_state.drawing, CANVAS_W, CANVAS_H = make_initial_drawing()
    st.session_state.canvas_w = CANVAS_W
    st.session_state.canvas_h = CANVAS_H

# -----------------------------
# 사이드바: 토큰 추가/리셋
# -----------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    st.write("토큰을 추가하면 오른쪽 공간에 생성됩니다(드래그로 이동).")

    add_label = st.text_input("출동대 이름", value="진압2")
    add_icon = st.selectbox("아이콘", ["🚒", "🛟", "🚑", "🚓", "🧯", "👮", "🏥", "🛰️"])
    add_btn = st.button("➕ 토큰 추가")

    reset_btn = st.button("🔄 초기화(4층+기본토큰)")

    st.divider()
    st.caption("팁: 토큰 클릭 → 드래그 이동 / 마우스 휠 확대는 브라우저 기능으로")

if reset_btn:
    st.session_state.drawing, CANVAS_W, CANVAS_H = make_initial_drawing()
    st.session_state.canvas_w = CANVAS_W
    st.session_state.canvas_h = CANVAS_H

if add_btn and add_label.strip():
    # 토큰을 "오른쪽 공간"에 생성
    new_obj = {
        "type": "textbox",
        "version": "4.6.0",
        "left": 650,
        "top": 360,
        "width": 200,
        "height": 42,
        "text": f"{add_icon}  {add_label.strip()}",
        "fontSize": 30,
        "fill": "rgba(0,0,0,1)",
        "editable": False,
        "selectable": True,
    }
    st.session_state.drawing["objects"].append(new_obj)

# -----------------------------
# 캔버스 렌더
# -----------------------------
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.subheader("🗺️ 전술판")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=2,
        stroke_color="rgba(0,0,0,1)",
        background_color="rgba(255,255,255,1)",
        update_streamlit=True,
        height=st.session_state.canvas_h,
        width=st.session_state.canvas_w,
        drawing_mode="transform",     # 핵심: 객체 이동/크기 조절 모드
        initial_drawing=st.session_state.drawing,
        key="tactical_canvas",
    )

    # 사용자가 움직인 결과를 세션에 반영
    if canvas_result.json_data is not None:
        st.session_state.drawing = canvas_result.json_data

with col2:
    st.subheader("📌 현재 배치(텍스트 목록)")
    data = st.session_state.drawing
    objs = data.get("objects", [])

    # 토큰만 추출: selectable True이고 textbox이며 이모지가 들어간 텍스트로 간단 판별
    tokens = []
    for o in objs:
        if o.get("type") == "textbox" and o.get("selectable") is True:
            tokens.append({
                "토큰": o.get("text", ""),
                "x": round(o.get("left", 0), 1),
                "y": round(o.get("top", 0), 1),
            })

    if tokens:
        st.dataframe(tokens, use_container_width=True, hide_index=True)
    else:
        st.info("토큰이 없습니다. 사이드바에서 토큰을 추가하세요.")

    st.divider()
    st.subheader("💾 저장/불러오기(옵션)")

    # JSON 다운로드/업로드 형태로 관리 가능
    st.download_button(
        "⬇️ 현재 배치 JSON 다운로드",
        data=json.dumps(st.session_state.drawing, ensure_ascii=False, indent=2),
        file_name="tactical_board_state.json",
        mime="application/json",
    )

    uploaded = st.file_uploader("⬆️ 저장한 JSON 불러오기", type=["json"])
    if uploaded is not None:
        try:
            loaded = json.load(uploaded)
            # 최소한의 형식 체크
            if isinstance(loaded, dict) and "objects" in loaded:
                st.session_state.drawing = loaded
                st.success("불러오기 완료! (왼쪽 전술판이 갱신됩니다)")
            else:
                st.error("JSON 형식이 올바르지 않습니다(objects가 필요).")
        except Exception as e:
            st.error(f"불러오기 실패: {e}")
