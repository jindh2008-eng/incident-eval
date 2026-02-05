import streamlit as st
from datetime import datetime
import pandas as pd
import json

st.set_page_config(page_title="현장지휘관 실기평가(초/중/고)", layout="wide")

# 점수 환산 비율(원하시면 바꾸세요)
RATIO = {"상": 1.0, "중": 0.7, "하": 0.4}

# ====== 평가표 데이터 (PDF 기반) ======
# 초급(100점): :contentReference[oaicite:3]{index=3}
LEVEL_BEGINNER = [
    ("상황평가", "출동중 정보수집 및 임무공유", 3, False),
    ("상황평가", "출동중 상황전파", 3, False),
    ("상황평가", "최초 상황보고", 0, False),  # 배점이 표에 명시되지 않아 0 처리(원하시면 배점 입력 가능)
    ("상황평가", "지휘형태 결정 및 지휘권선언", 10, True),
    ("상황평가", "인명정보 취득 및 전파", 5, False),
    ("상황평가", "추가 소방력 판단", 3, False),

    ("대응활동", "차량배치", 5, False),
    ("대응활동", "표준대응활동", 5, False),
    ("대응활동", "후착대 임무부여", 3, False),
    ("대응활동", "위기대응 및 진행상황 관리", 5, False),
    ("대응활동", "화재현장요소 파악 관리", 5, False),
    ("대응활동", "단위지휘관 임무수행", 3, False),

    ("화재전술", "소방용수", 5, False),
    ("화재전술", "문개방 및 내부진입", 5, False),
    ("화재전술", "수관전개 주수 및 관창배치", 5, False),
    ("화재전술", "배연", 5, False),

    ("의사교환", "무전교신 원칙", 5, False),
    ("의사교환", "정보 전달력", 5, False),
    ("의사교환", "지휘팀장 도착 후 상황보고", 5, False),

    ("핵심목표달성", "인명구조 목표달성의 적절성", 10, True),
    ("핵심목표달성", "출동대 안전관리", 5, False),
]

# 중급(200점): :contentReference[oaicite:4]{index=4}
LEVEL_INTERMEDIATE = [
    ("상황평가", "출동중 정보수집", 3, False),
    ("상황평가", "선착대장 활동지원", 5, False),
    ("상황평가", "지휘권 선언", 5, False),
    ("상황평가", "최초 상황평가", 10, True),
    ("상황평가", "중요정보 파악", 5, False),

    ("지휘/의사결정", "선착대 대응활동 유효성 판단", 3, False),
    ("지휘/의사결정", "현장 위험성 판단", 5, False),
    ("지휘/의사결정", "핵심목표(대응 지침) 제시", 5, False),
    ("지휘/의사결정", "1차 출동대 임무지시 및 조정", 10, True),
    ("지휘/의사결정", "추가 자원 요청", 5, False),

    ("대응활동", "차량배치 조정", 10, True),
    ("대응활동", "소방활동구역 설정 및 통제", 5, False),
    ("대응활동", "소방용수공급체계 구축", 5, False),
    ("대응활동", "(단계별) 소방력 배치 및 조정", 5, False),
    ("대응활동", "현장분할 및 단위지휘관 운영", 5, False),
    ("대응활동", "출동대 교대관리", 5, False),
    ("대응활동", "대기절차 운영", 3, False),
    ("대응활동", "전술상황판 기록", 5, False),

    ("진행상황관리", "진행상황 파악", 10, True),
    ("진행상황관리", "상황 미개선 및 악화시 대응조치", 5, False),
    ("진행상황관리", "우선순위보고 조치", 5, False),
    ("진행상황관리", "초진선언", 5, False),
    ("진행상황관리", "전술우선순위 관리", 5, False),
    ("진행상황관리", "완진절차 준수", 5, False),

    ("의사교환", "대응초기 무전통제", 3, False),
    ("의사교환", "무전망 분리운영", 3, False),
    ("의사교환", "무전교신 원칙 준수", 5, False),
    ("의사교환", "무전교신 불능 시 조치", 5, False),
    ("의사교환", "효율적 의사교환", 10, True),

    ("위기관리/리더십", "돌발 및 위기상황 대응", 5, False),
    ("위기관리/리더십", "스트레스 관리", 5, False),
    ("위기관리/리더십", "리더로서의 능숙한 작전 운영", 5, False),
    ("위기관리/리더십", "인명구조 목표달성의 적절성", 10, True),
    ("위기관리/리더십", "출동대 안전관리의 적절성", 10, True),
    ("위기관리/리더십", "시민보호 및 피해최소화 작전의 적절성", 5, False),
]

# 고급(200점): :contentReference[oaicite:5]{index=5}
LEVEL_ADVANCED = [
    ("상황평가/의사결정", "출동중 정보수집 및 선착대장 지원", 5, False),
    ("상황평가/의사결정", "지휘권 선언", 5, False),
    ("상황평가/의사결정", "최초 상황평가", 5, False),
    ("상황평가/의사결정", "핵심목표(대응지침) 제시", 5, False),
    ("상황평가/의사결정", "1차 출동대 임무지시 및 조정", 5, False),
    ("상황평가/의사결정", "유관기관 등 추가자원 동원", 5, False),

    ("대응활동/진행상황관리", "차량배치 및 조정", 3, False),
    ("대응활동/진행상황관리", "소방활동구역 설정 및 통제", 3, False),
    ("대응활동/진행상황관리", "소방용수공급체계 구축", 3, False),
    ("대응활동/진행상황관리", "소방력 배치 및 조정", 5, False),
    ("대응활동/진행상황관리", "현장분할 및 단위지휘관 운영", 3, False),
    ("대응활동/진행상황관리", "진행상황 파악 및 개선조치", 10, True),
    ("대응활동/진행상황관리", "전술우선순위 관리", 5, False),
    ("대응활동/진행상황관리", "완진절차 준수", 5, False),
    ("대응활동/진행상황관리", "전술상황판 기록", 3, False),

    ("위기관리/소통/리더십", "무전통제", 5, False),
    ("위기관리/소통/리더십", "효율적인 의사교환", 5, False),
    ("위기관리/소통/리더십", "돌발 및 위기상황 대응", 5, False),
    ("위기관리/소통/리더십", "작전운영의 적절성", 5, False),
    ("위기관리/소통/리더십", "인명구조 목표달성 및 대원안전관리", 10, True),

    ("대응활동계획/상황판단회의", "정확한 상황인식", 5, False),
    ("대응활동계획/상황판단회의", "목표 및 우선순위 선정의 적절성", 5, False),
    ("대응활동계획/상황판단회의", "최종계획의 구체성 및 우수성", 5, False),
    ("대응활동계획/상황판단회의", "예비방안(대안) 제시", 5, False),
    ("대응활동계획/상황판단회의", "시민생활 영향성 검토 및 반영", 5, False),
    ("대응활동계획/상황판단회의", "상황판단회의 진행의 적절성", 10, True),
    ("대응활동계획/상황판단회의", "출동대 및 유관기관 간 업무조정", 5, False),
    ("대응활동계획/상황판단회의", "명확한 회의 결과 도출 및 지시", 5, False),
    ("대응활동계획/상황판단회의", "대응활동계획 조정", 5, False),

    ("언론브리핑", "브리핑 준비", 5, False),
    ("언론브리핑", "브리핑 내용의 적절성", 10, True),
    ("언론브리핑", "브리핑 태도", 5, False),
    ("언론브리핑", "전달력", 5, False),
    ("언론브리핑", "질의 응답의 적절성", 10, True),
    ("언론브리핑", "질문의 이해도", 5, False),
    ("언론브리핑", "답변태도", 5, False),
    ("언론브리핑", "언론취재의 방향성 제시", 5, False),
]

LEVELS = {
    "초급(100점)": LEVEL_BEGINNER,
    "중급(200점)": LEVEL_INTERMEDIATE,
    "고급(200점)": LEVEL_ADVANCED,
}

def calc_score(base: int, grade: str) -> float:
    if base <= 0:
        return 0.0
    return base * RATIO[grade]

# ===== UI =====
st.title("현장지휘관 실기평가 (QR 상시용 Streamlit)")
st.caption("상/중/하 체크 → 자동 합산 → 제출 시 결과 요약(다운로드 가능)")

with st.sidebar:
    st.subheader("기본정보")
    eval_date = st.date_input("평가일자", value=datetime.now().date())
    candidate_no = st.text_input("응시번호")
    evaluator = st.text_input("평가관")
    level = st.radio("평가표 선택", list(LEVELS.keys()))
    st.divider()
    st.write("점수 비율(설정)")
    st.write(f"상={RATIO['상']*100:.0f}%, 중={RATIO['중']*100:.0f}%, 하={RATIO['하']*100:.0f}%")
    st.write("※ ‘하’ 평정 시 사유 입력을 요구합니다(표 원칙 반영).")

items = LEVELS[level]

# 그룹별 출력
rows = []
total_base = sum(b for _, _, b, _ in items if b > 0)
total_score = 0.0

st.subheader(f"{level} 평가")

# 그룹(평가항목)별로 묶기
groups = {}
for cat, name, base, star in items:
    groups.setdefault(cat, []).append((name, base, star))

reasons_required = 0
star_low = False

for cat, cat_items in groups.items():
    st.markdown(f"### {cat}")
    for idx, (name, base, star) in enumerate(cat_items, start=1):
        c1, c2, c3, c4 = st.columns([6, 2, 4, 6])
        with c1:
            st.write(f"- {name}" + ("  ★" if star else ""))
        with c2:
            st.write(f"배점 {base}" if base > 0 else "배점 미표기")
        with c3:
            grade = st.radio(
                "평정",
                ["상", "중", "하"],
                horizontal=True,
                key=f"{level}_{cat}_{idx}_grade"
            )
        reason = ""
        with c4:
            if grade == "하":
                reasons_required += 1
                if star:
                    star_low = True
                reason = st.text_input("‘하’ 사유(필수)", key=f"{level}_{cat}_{idx}_reason")
            else:
                st.write("")

        score = calc_score(base, grade)
        total_score += score

        rows.append({
            "level": level,
            "category": cat,
            "item": name,
            "base": base,
            "star": star,
            "grade": grade,
            "score": round(score, 2),
            "low_reason": reason.strip()
        })

st.divider()

df = pd.DataFrame(rows)

# 필수 사유 누락 체크
missing_low_reason = df[(df["grade"] == "하") & (df["low_reason"] == "")].shape[0]

colA, colB, colC = st.columns(3)
with colA:
    st.metric("총점", f"{total_score:.1f}")
with colB:
    st.metric("만점", f"{total_base}")
with colC:
    pct = (total_score / total_base * 100) if total_base else 0
    st.metric("환산(%)", f"{pct:.1f}%")

if star_low:
    st.warning("★ 중요지표에서 ‘하’가 있습니다. 사유를 반드시 기재하세요.")

if missing_low_reason > 0:
    st.error(f"‘하’ 평정 사유 미입력 {missing_low_reason}건이 있습니다. 모두 입력해야 제출됩니다.")

st.subheader("항목별 결과")
st.dataframe(df, use_container_width=True)

st.subheader("종합평가 의견")
overall = st.text_area("종합평가 의견(권장)", help="전체적으로 잘한 점/부족한 점/개선 제안 등을 기재")

st.divider()

# 제출(저장 대신 다운로드 제공: Streamlit Cloud는 로컬 파일이 영구 저장되지 않을 수 있어 안전한 방식)
result = {
    "timestamp": datetime.now().isoformat(timespec="seconds"),
    "eval_date": str(eval_date),
    "candidate_no": candidate_no,
    "evaluator": evaluator,
    "level": level,
    "total_base": total_base,
    "total_score": round(total_score, 1),
    "pct": round(pct, 1),
    "overall_opinion": overall.strip(),
    "rows": rows,
}

submit = st.button("제출(결과 파일 생성)")
if submit:
    if missing_low_reason > 0:
        st.stop()
    st.success("제출 준비 완료! 아래에서 결과 파일을 다운로드하세요.")
    json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        "결과(JSON) 다운로드",
        data=json_bytes,
        file_name=f"eval_{level}_{candidate_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "항목별(CSV) 다운로드",
        data=csv_bytes,
        file_name=f"eval_items_{level}_{candidate_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

st.caption("참고: 상시 운영에서 ‘결과 자동 저장(누적)’까지 원하면 Google Sheets 저장 기능을 붙이면 가장 안정적입니다.")
