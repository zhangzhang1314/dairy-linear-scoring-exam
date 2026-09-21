from quiz_data import TRAITS, build_question_bank, is_correct, make_exam


def test_confirmed_reference_values():
    traits = {trait.name: trait for trait in TRAITS}
    assert traits["体高"].values[8] == 150
    assert traits["乳房深度"].values[0] == -1


def test_question_bank_has_all_three_types():
    bank = build_question_bank()
    assert len(bank) == len(TRAITS) * 3
    assert {q["type"] for q in bank} == {"选择题", "填空题", "判断题"}


def test_exam_is_balanced_and_answers_work():
    exam = make_exam(15, seed=20260921)
    counts = {kind: sum(q["type"] == kind for q in exam) for kind in ("选择题", "填空题", "判断题")}
    assert counts == {"选择题": 5, "填空题": 5, "判断题": 5}
    assert all(is_correct(question, question["answer"]) for question in exam)


def test_fill_accepts_full_width_digits():
    question = {"type": "填空题", "answer": "9"}
    assert is_correct(question, "９")
    assert not is_correct(question, "8")
