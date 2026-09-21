from __future__ import annotations

import secrets

import pandas as pd
import streamlit as st

from quiz_data import TRAITS, display_number, is_correct, make_exam


st.set_page_config(
    page_title="奶牛体型线性评定考试",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      .stApp { background: #f6f7f3; color: #17251e; }
      .block-container { max-width: 980px; padding-top: 2rem; padding-bottom: 5rem; }
      [data-testid="stHeader"] { background: transparent; }
      .hero { background: linear-gradient(125deg,#173f32,#245947); color:white;
              padding: 2.4rem 2.6rem; border-radius: 24px; margin-bottom: 1.5rem;
              box-shadow: 0 14px 40px rgba(23,63,50,.16); }
      .hero h1 { margin:0; font-size:clamp(2rem,5vw,3.3rem); letter-spacing:-.04em; }
      .hero p { margin:.65rem 0 0; color:#dcebe2; font-size:1.05rem; }
      .eyebrow { color:#b8dfc8; font-size:.78rem; font-weight:800; letter-spacing:.14em; }
      .exam-meta { display:flex; gap:.6rem; flex-wrap:wrap; margin-top:1.25rem; }
      .pill { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2);
              border-radius:999px; padding:.35rem .75rem; font-size:.82rem; }
      div[data-testid="stVerticalBlockBorderWrapper"] { background:white; border-radius:18px;
              box-shadow:0 4px 18px rgba(23,63,50,.06); border-color:#e1e7e2; }
      .q-index { color:#6a786f; font-size:.78rem; font-weight:750; letter-spacing:.08em; }
      .q-type { color:#27634c; font-weight:800; }
      .result-good { background:#e9f6ee; border:1px solid #a9d6b9; color:#17452d;
              border-radius:16px; padding:1rem 1.2rem; }
      .result-bad { background:#fff3ed; border:1px solid #f2c4ad; color:#6c2f16;
              border-radius:16px; padding:1rem 1.2rem; }
      div.stButton > button, div.stFormSubmitButton > button { border-radius:999px; min-height:2.8rem; font-weight:750; }
      #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def hero(subtitle: str) -> None:
    st.markdown(
        f"""
        <section class="hero">
          <div class="eyebrow">DAIRY CATTLE · LINEAR SCORING</div>
          <h1>奶牛体型线性评定考试</h1>
          <p>{subtitle}</p>
          <div class="exam-meta">
            <span class="pill">选择题</span><span class="pill">填空题</span>
            <span class="pill">判断题</span><span class="pill">满分 100 分</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def reset_exam() -> None:
    for key in list(st.session_state):
        if key.startswith(("answer_", "exam_")):
            del st.session_state[key]


def start_exam(question_count: int) -> None:
    seed = secrets.randbits(32)
    st.session_state.exam_seed = seed
    st.session_state.exam_questions = make_exam(question_count, seed)
    st.session_state.exam_submitted = False
    st.session_state.exam_page = "exam"


def reference_table() -> pd.DataFrame:
    rows = []
    for trait in TRAITS:
        row = {"性状": trait.name}
        row.update({str(score): display_number(value) for score, value in enumerate(trait.values, 1)})
        row["单位"] = trait.unit
        rows.append(row)
    return pd.DataFrame(rows)


if "exam_page" not in st.session_state:
    st.session_state.exam_page = "home"

if st.session_state.exam_page == "home":
    hero("依据 1–9 分测量值对照表随机组卷，提交后即时判分。")
    left, right = st.columns([1.4, 1], gap="large")
    with left:
        st.subheader("开始一次练习")
        question_count = st.slider("题目数量", min_value=9, max_value=30, value=15, step=3)
        st.caption("系统会均衡抽取三种题型。每次开始都会生成一套新试卷。")
        if st.button("开始考试", type="primary", use_container_width=True):
            start_exam(question_count)
            st.rerun()
    with right:
        with st.container(border=True):
            st.markdown("#### 考试说明")
            st.markdown(
                """
                - 每题分值相同，总分折算为 100 分
                - 填空题填写 1–9 的数字
                - 提交前可随时修改答案
                - 不需要账号，不保存答题记录
                """
            )
    with st.expander("考前复习：查看完整评分对照表"):
        st.dataframe(reference_table(), hide_index=True, use_container_width=True)
else:
    questions = st.session_state.exam_questions
    submitted = st.session_state.exam_submitted
    hero("认真作答；提交后将显示总分、正确答案和逐题解析。")

    answered = sum(
        response is not None and bool(str(response).strip())
        for q in questions
        if (response := st.session_state.get(f"answer_{q['id']}")) is not None
    )
    progress = answered / len(questions)
    st.progress(progress, text=f"答题进度：{answered} / {len(questions)}")

    if submitted:
        results = [(q, st.session_state.get(f"answer_{q['id']}"), is_correct(q, st.session_state.get(f"answer_{q['id']}"))) for q in questions]
        correct_count = sum(ok for _, _, ok in results)
        score = round(correct_count / len(questions) * 100)
        st.subheader(f"本次得分：{score} 分")
        c1, c2, c3 = st.columns(3)
        c1.metric("答对", f"{correct_count} 题")
        c2.metric("答错", f"{len(questions) - correct_count} 题")
        c3.metric("正确率", f"{correct_count / len(questions):.0%}")
        st.divider()

        for index, (question, response, ok) in enumerate(results, 1):
            css = "result-good" if ok else "result-bad"
            mark = "✓ 回答正确" if ok else "✕ 回答错误"
            shown_response = response if str(response or "").strip() else "未作答"
            st.markdown(
                f"""<div class="{css}"><strong>{index}. {mark}</strong><br>
                {question['prompt']}<br>你的答案：{shown_response}　·　正确答案：{question['answer']}<br>
                <small>{question['explanation']}</small></div>""",
                unsafe_allow_html=True,
            )
            st.write("")

        col1, col2 = st.columns(2)
        if col1.button("再考一次", type="primary", use_container_width=True):
            count = len(questions)
            reset_exam()
            start_exam(count)
            st.rerun()
        if col2.button("返回首页", use_container_width=True):
            reset_exam()
            st.session_state.exam_page = "home"
            st.rerun()
    else:
        with st.form("exam_form"):
            for index, question in enumerate(questions, 1):
                with st.container(border=True):
                    st.markdown(
                        f"<div class='q-index'>第 {index} 题 / 共 {len(questions)} 题　<span class='q-type'>{question['type']}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"#### {question['prompt']}")
                    key = f"answer_{question['id']}"
                    if question["type"] == "选择题":
                        st.radio("请选择", question["options"], index=None, key=key, label_visibility="collapsed")
                    elif question["type"] == "判断题":
                        st.radio("请选择", ("正确", "错误"), index=None, horizontal=True, key=key, label_visibility="collapsed")
                    else:
                        st.text_input("请输入分数", key=key, placeholder="填写 1–9", label_visibility="collapsed")
            submitted_now = st.form_submit_button("提交试卷并查看成绩", type="primary", use_container_width=True)
            if submitted_now:
                st.session_state.exam_submitted = True
                st.rerun()
