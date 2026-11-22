import os
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="HEALTH QUEST", page_icon="💠", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""
<style>
:root{--text:#f4f7ff;--muted:#c3d1e8}
html,body,[data-testid="stAppViewContainer"],.stApp{background:radial-gradient(ellipse at 50% 0%,#1b3764 0%,#0b1730 45%,#070d1b 100%)!important;color:var(--text)!important}
.block-container{max-width:760px!important;padding:1rem .85rem 3rem!important}
p,label,span,h1,h2,h3,h4,li{color:#f4f7ff}
[data-testid="stCaptionContainer"],.stCaption{color:var(--muted)!important}
[data-testid="stMetric"]{background:#172b4b!important;border:1px solid #45618e!important;border-radius:16px;padding:12px}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"],[data-testid="stMetricLabel"] *{color:#fff!important}
input,textarea,[data-baseweb="select"]>div,[data-baseweb="input"]>div{background:#0c1730!important;color:#fff!important;border-color:#58739c!important;border-radius:12px!important}
input::placeholder,textarea::placeholder{color:#b3c3dc!important;opacity:1!important}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,.stTextInput label,.stTimeInput label,.stCheckbox label,.stSelectbox label{color:#f1f5ff!important;font-weight:700!important}
[data-testid="stTabs"] button{color:#e5edff!important;font-weight:700!important}
[data-testid="stTabs"] button[aria-selected="true"]{color:#70edf4!important}
.stButton>button,.stFormSubmitButton>button{background:linear-gradient(100deg,#397bff,#765dff)!important;color:white!important;border:1px solid #83a4ff!important;border-radius:13px!important;font-weight:800!important;min-height:2.8rem}
.hero{padding:2rem 1.2rem;border-radius:26px;border:1px solid #5273a8;background:radial-gradient(circle at 90% 8%,#4c69bb66,transparent 35%),linear-gradient(145deg,#1b3763,#111d3b 60%,#241c4b);box-shadow:0 18px 55px #0008;text-align:center;margin:.4rem 0 1.2rem}
.kicker{display:inline-block;padding:.35rem .75rem;border-radius:99px;border:1px solid #76e8f488;color:#9af7ff!important;font-size:.72rem;letter-spacing:.15em;font-weight:900}
.orb{width:88px;height:88px;border-radius:26px;margin:1.2rem auto .6rem;display:flex;align-items:center;justify-content:center;font-size:3rem;background:linear-gradient(145deg,#69f1f0,#6887ff 55%,#a66bff);box-shadow:0 0 35px #6a9eff88}
.hero-title{font-size:clamp(2.1rem,10vw,3.3rem);line-height:1.05;font-weight:950;letter-spacing:-.04em;color:#fff!important;margin:.8rem 0}
.hero-copy{color:#d8e5fa!important;line-height:1.65}
.head{font-size:1.25rem;font-weight:900;color:#fff!important;margin:.4rem 0}
.feature{background:linear-gradient(145deg,#172947,#101b32);border:1px solid #3b557d;border-radius:16px;padding:1rem;min-height:105px;margin-bottom:.6rem}
.feature b{color:#fff}.feature small{color:#c4d2e9}
.chat-intro{background:#142441;border:1px solid #38537c;border-radius:15px;padding:.85rem 1rem;margin:.4rem 0 1rem;color:#e6efff!important}
.stChatMessage{background:#142441!important;border:1px solid #304a70;border-radius:15px!important}
.stChatMessage p{color:#fff!important}
hr{border-color:#30496e!important}
@media(max-width:600px){.hero{padding:1.6rem .9rem;border-radius:22px}[data-testid="stTabs"] button{font-size:.76rem!important;padding:.35rem!important}}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state: st.session_state.page="intro"
for key, default in {
    "meds":[], "meals":[], "habits":{"규칙적인 식사하기":False,"가벼운 신체 활동하기":False,"충분히 휴식하기":False,"안내받은 식사 주의사항 확인하기":False},
    "chat":[], "notified":set()
}.items():
    if key not in st.session_state: st.session_state[key]=default

def go(page):
    st.session_state.page=page
    st.rerun()

now=datetime.now(ZoneInfo("Asia/Seoul"))
today=date.today().isoformat()

# Welcome / game-like launch screen
if st.session_state.page=="intro":
    st.markdown("""<div class="hero"><div class="kicker">YOUR DAILY HEALTH QUEST</div><div class="orb">💠</div><div class="hero-title">HEALTH<br>QUEST</div><div class="hero-copy">매일의 건강 관리, 퀘스트처럼 쉽고 즐겁게.<br>우리 가족을 위한 스마트 건강 관리 공간</div></div>""",unsafe_allow_html=True)
    st.markdown('<div class="head">건강 관리, 지금 시작해 볼까요?</div>',unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">약 복용부터 식사와 생활 습관까지 한곳에서 관리하고, AI 도우미에게 건강 고민과 실생활 속 과학적 궁금증도 물어보세요.</p>',unsafe_allow_html=True)
    if st.button("🚀 시작하기",type="primary",use_container_width=True): go("home")
    with st.expander("이 앱에서 할 수 있는 것"):
        st.write("💊 약 복용 시간 알림과 복용 여부 체크")
        st.write("🥗 식사 기록 및 🌿 생활 습관 체크")
        st.write("🤖 AI 건강 관리·생활과학 질문")
        st.caption("약 알림은 앱이 열려 있는 동안 작동합니다. 앱이 닫혀 있거나 기기가 잠겨 있을 때 울리는 백그라운드 알람은 지원하지 않습니다.")
    st.stop()

# Header
l,r=st.columns([3,1])
with l:
    st.markdown("### 💠 HEALTH QUEST")
    st.caption("우리 가족 건강 관리 공간")
with r:
    if st.button("처음 화면"): go("intro")

if st.session_state.page=="guide":
    st.markdown('<div class="head">📘 꼭 알아둘 건강 관리 안내</div>',unsafe_allow_html=True)
    st.write("**약 복용:** 등록한 시간에 앱이 열려 있으면 알림을 표시합니다. 복용 여부는 직접 확인하고 체크해 주세요.")
    st.write("**식사·생활 습관:** 의료진에게 안내받은 개인별 지침을 우선해 주세요.")
    st.write("**AI 도우미:** 건강 고민과 실생활 속 과학적 궁금증을 설명합니다. 진단이나 치료를 대신하지 않습니다.")
    st.write("**개인정보:** 이름, 주민등록번호, 처방전 사진 등 민감한 정보는 입력하지 마세요.")
    if st.button("메인으로 돌아가기",use_container_width=True): go("home")
    st.stop()

st.markdown('<div class="hero" style="text-align:left;padding:1.1rem"><div class="kicker">TODAY\'S QUEST</div><div class="head">오늘의 건강 관리</div><div class="hero-copy">작은 체크 하나부터 건강한 하루를 만들어 보세요.</div></div>',unsafe_allow_html=True)
today_meds=[m for m in st.session_state.meds if m["date"]==today]
taken=sum(m["taken"] for m in today_meds)
a,b,c=st.columns(3)
a.metric("오늘 등록한 약",f"{len(today_meds)}개")
b.metric("복용 확인",f"{taken}/{len(today_meds)}")
c.metric("습관 체크",f"{sum(st.session_state.habits.values())}/4")

# Due alerts: refresh the in-app reminder panel every 30 seconds while the app is open.
@st.fragment(run_every="30s")
def reminder_panel():
    current = datetime.now(ZoneInfo("Asia/Seoul"))
    current_day = current.date().isoformat()
    for i, med in enumerate(st.session_state.meds):
        is_for_today = med.get("repeat", False) or med.get("date") == current_day
        key = f"{i}-{current_day}"
        if med.get("enabled", True) and not med.get("taken", False) and is_for_today:
            try:
                alarm = datetime.combine(current.date(), time.fromisoformat(med["time"]))
            except Exception:
                continue
            if current >= alarm and key not in st.session_state.notified:
                st.warning(f"⏰ 복용 예정 시간이에요: **{med['name']}** ({med['time']}) 복용 후 체크해 주세요.")
                st.session_state.notified.add(key)

reminder_panel()

home,med,meal,habit,ai=st.tabs(["🏠 홈","💊 약 알림","🥗 식사","🌿 습관","🤖 AI 도우미"])

with home:
    st.markdown('<div class="head">오늘의 관리 메뉴</div>',unsafe_allow_html=True)
    x,y=st.columns(2)
    with x:
        st.markdown('<div class="feature">💊<br><b>약 복용 관리</b><br><small>복용 시간 등록과 복용 확인</small></div>',unsafe_allow_html=True)
        st.markdown('<div class="feature">🌿<br><b>생활 습관</b><br><small>오늘의 건강 습관 체크</small></div>',unsafe_allow_html=True)
    with y:
        st.markdown('<div class="feature">🥗<br><b>식사 관리</b><br><small>식사 기록과 주의사항</small></div>',unsafe_allow_html=True)
        st.markdown('<div class="feature">🤖<br><b>AI 건강 도우미</b><br><small>건강 고민과 과학 질문</small></div>',unsafe_allow_html=True)
    if st.button("📌 꼭 알아둘 안내 보기",use_container_width=True): go("guide")
    st.caption("현재 입력한 내용은 접속 세션에 임시 저장됩니다. 영구 보관 기능은 별도 데이터베이스 연결이 필요합니다.")

with med:
    st.markdown('<div class="head">💊 약 복용 알림 설정</div>',unsafe_allow_html=True)
    st.write("약과 알림 시간을 등록하면, 시간이 지난 뒤 앱 안에서 알림을 보여줘요.")
    with st.form("medform",clear_on_submit=True):
        name=st.text_input("약 이름",placeholder="예: 아침에 복용하는 약")
        alarm_time=st.time_input("알림 받을 시간",value=time(8,0),step=300)
        note=st.text_input("복용 메모 (선택)",placeholder="예: 식후 등 안내받은 방법")
        repeat=st.checkbox("매일 반복",value=True)
        add=st.form_submit_button("알림 등록하기",use_container_width=True)
    if add:
        if name.strip():
            st.session_state.meds.append({"name":name.strip(),"time":alarm_time.strftime("%H:%M"),"note":note.strip(),"date":today,"taken":False,"enabled":True,"repeat":repeat})
            st.success(f"{name.strip()} 알림을 {alarm_time.strftime('%H:%M')}로 등록했어요.")
            st.rerun()
        else: st.error("약 이름을 입력해 주세요.")
    if st.session_state.meds:
        st.markdown("#### 등록된 알림")
        for i,m in enumerate(st.session_state.meds):
            with st.container(border=True):
                st.markdown(f"**⏰ {m['time']} · {m['name']}**")
                st.caption(("매일 반복" if m["repeat"] else "오늘만")+ (f" · {m['note']}" if m["note"] else ""))
                st.session_state.meds[i]["enabled"]=st.toggle("알림 켜기",value=m["enabled"],key=f"enable{i}")
                if m["date"]==today:
                    st.session_state.meds[i]["taken"]=st.checkbox("오늘 복용했어요",value=m["taken"],key=f"taken{i}")
                if st.button("삭제",key=f"del{i}"):
                    st.session_state.meds.pop(i); st.rerun()
    st.info("중요: Streamlit 웹앱은 브라우저가 닫히거나 기기가 잠기면 알람을 울릴 수 없어요. 실제 백그라운드 푸시 알림에는 별도 앱/PWA 푸시 서버 구성이 필요합니다.")

with meal:
    st.markdown('<div class="head">🥗 식사 관리</div>',unsafe_allow_html=True)
    with st.form("mealform",clear_on_submit=True):
        kind=st.selectbox("식사 구분",["아침","점심","저녁","간식"])
        food=st.text_input("먹은 음식",placeholder="예: 밥, 생선, 채소")
        caution=st.text_input("식사 주의사항 (선택)",placeholder="예: 안내받은 식사 지침")
        save=st.form_submit_button("식사 기록 저장",use_container_width=True)
    if save:
        if food.strip():
            st.session_state.meals.append({"date":today,"kind":kind,"food":food.strip(),"caution":caution.strip()})
            st.success("식사 기록을 저장했어요.")
        else: st.warning("먹은 음식을 입력해 주세요.")
    for m in [x for x in st.session_state.meals if x["date"]==today]:
        with st.container(border=True):
            st.write(f"**{m['kind']} · {m['food']}**")
            if m["caution"]: st.caption("주의사항: "+m["caution"])

with habit:
    st.markdown('<div class="head">🌿 오늘의 건강 습관</div>',unsafe_allow_html=True)
    st.caption("오늘 실천한 항목에 체크해 보세요.")
    for h in list(st.session_state.habits):
        st.session_state.habits[h]=st.checkbox(h,value=st.session_state.habits[h],key="habit_"+h)
    count=sum(st.session_state.habits.values())
    st.progress(count/len(st.session_state.habits))
    st.success(f"오늘 {count}개 습관을 체크했어요!")

with ai:
    st.markdown('<div class="head">🤖 AI 건강 관리 도우미</div>',unsafe_allow_html=True)
    st.markdown('<div class="chat-intro">당신의 건강 관리를 돕고, 건강 고민과 실생활에서 생기는 과학적인 궁금증을 쉽게 풀어드려요.</div>',unsafe_allow_html=True)
    key=st.secrets.get("OPENAI_API_KEY",os.getenv("OPENAI_API_KEY",""))
    if not key:
        st.warning("AI 연결을 위해 Streamlit Cloud → App settings → Secrets에 OPENAI_API_KEY를 등록해 주세요.")
    else:
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        prompt=st.chat_input("건강이나 과학에 관해 무엇이 궁금한가요?")
        if prompt:
            st.session_state.chat.append({"role":"user","content":prompt})
            with st.chat_message("user"): st.markdown(prompt)
            try:
                client=OpenAI(api_key=key)
                with st.chat_message("assistant"):
                    with st.spinner("답변을 생각하고 있어요..."):
                        response=client.responses.create(
                            model="gpt-4o-mini",
                            instructions="한국어로 쉽고 친절하게 건강 관리와 실생활 과학을 설명한다. 진단·치료 처방을 하지 않고 약의 용량, 시간 변경 또는 중단을 지시하지 않는다. 개인별 의료 판단은 의사나 약사에게 확인하도록 안내한다. 민감한 개인정보를 입력하지 말라고 안내한다.",
                            input=[{"role":m["role"],"content":m["content"]} for m in st.session_state.chat[-12:]]
                        )
                        answer=response.output_text
                    st.markdown(answer)
                st.session_state.chat.append({"role":"assistant","content":answer})
            except Exception:
                st.error("AI 답변을 가져오지 못했어요. API 키와 API 사용량 설정을 확인해 주세요.")

st.divider()
st.caption("HEALTH QUEST · 건강 관리 기록을 돕는 교육용 웹앱")
