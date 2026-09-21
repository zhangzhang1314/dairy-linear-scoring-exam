"""奶牛 9 分制线性评定考试的唯一数据源。"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class Trait:
    name: str
    unit: str
    values: tuple[float, ...]


# 分数位置依次对应 1～9 分。
TRAITS: tuple[Trait, ...] = (
    Trait("体高", "cm", (130, 132, 135, 137, 140, 142, 145, 147, 150)),
    Trait("胸宽", "cm", (13, 16, 19, 22, 25, 28, 31, 34, 37)),
    Trait("尻角度", "cm", (-4, -2, 0, 2, 4, 5.5, 7, 8.5, 10)),
    Trait("尻宽", "cm", (10, 12, 14, 16, 18, 20, 22, 24, 25)),
    Trait("蹄角度", "度", (20, 30, 35, 40, 45, 50, 55, 60, 70)),
    Trait("蹄踵深度", "cm", (0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5)),
    Trait("后肢侧视", "度", (165, 160, 155, 150, 145, 140, 135, 130, 125)),
    Trait("后肢后视", "度", (90, 80, 60, 50, 40, 30, 20, 10, 0)),
    Trait("乳房深度", "cm", (-1, 0, 4, 7, 10, 12, 14, 16, 18)),
    Trait("中央悬韧带", "cm", (0, 0.5, 1.5, 2, 3, 4, 5, 6, 7)),
    Trait("前乳房附着", "度", (70, 80, 90, 100, 110, 120, 130, 140, 150)),
    Trait("前乳头长度", "cm", (2, 3, 3.5, 4, 5, 6, 7, 8.5, 10)),
    Trait("后附着高度", "cm", (32, 30, 28, 26, 24, 22, 20, 18, 16)),
    Trait("后附着宽度", "cm", (8, 9.5, 11, 12.5, 14, 15.5, 17, 18.5, 20)),
)


def display_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else str(value)


def build_question_bank() -> list[dict]:
    """每个性状生成选择、填空、判断各一道题。"""
    questions: list[dict] = []
    for trait_index, trait in enumerate(TRAITS):
        # 使用不同分值覆盖整张表，同时保证两处人工确认值进入题库。
        score = (trait_index * 3) % 9 + 1
        if trait.name == "体高":
            score = 9
        elif trait.name == "乳房深度":
            score = 1
        value = trait.values[score - 1]

        distractor_scores = sorted(
            (candidate for candidate in range(1, 10) if candidate != score),
            key=lambda candidate: (abs(candidate - score), candidate),
        )[:3]
        option_values = [value] + [trait.values[s - 1] for s in distractor_scores[:3]]
        options = tuple(f"{display_number(v)} {trait.unit}" for v in dict.fromkeys(option_values))
        questions.append(
            {
                "id": f"choice-{trait_index}",
                "type": "选择题",
                "prompt": f"{trait.name}评为 {score} 分时，对应的测量值是多少？",
                "answer": f"{display_number(value)} {trait.unit}",
                "options": options,
                "explanation": f"{trait.name} {score} 分对应 {display_number(value)} {trait.unit}。",
            }
        )

        fill_score = (trait_index * 5 + 2) % 9 + 1
        fill_value = trait.values[fill_score - 1]
        questions.append(
            {
                "id": f"fill-{trait_index}",
                "type": "填空题",
                "prompt": f"{trait.name}测量值为 {display_number(fill_value)} {trait.unit}，应评为几分？",
                "answer": str(fill_score),
                "explanation": f"{display_number(fill_value)} {trait.unit}对应 {fill_score} 分。",
            }
        )

        judge_score = (trait_index * 7 + 4) % 9 + 1
        is_true = trait_index % 2 == 0
        shown_index = judge_score - 1 if is_true else judge_score % 9
        shown_value = trait.values[shown_index]
        questions.append(
            {
                "id": f"judge-{trait_index}",
                "type": "判断题",
                "prompt": (
                    f"{trait.name}评为 {judge_score} 分时，对应值是 "
                    f"{display_number(shown_value)} {trait.unit}。"
                ),
                "answer": "正确" if is_true else "错误",
                "explanation": (
                    f"{trait.name} {judge_score} 分的正确值是 "
                    f"{display_number(trait.values[judge_score - 1])} {trait.unit}。"
                ),
            }
        )
    return questions


def make_exam(question_count: int, seed: int) -> list[dict]:
    """按题型均衡抽题，并打乱题目与选择项顺序。"""
    rng = Random(seed)
    bank = build_question_bank()
    grouped = {kind: [q.copy() for q in bank if q["type"] == kind] for kind in ("选择题", "填空题", "判断题")}
    result: list[dict] = []
    base, remainder = divmod(question_count, 3)
    for index, kind in enumerate(grouped):
        count = base + (1 if index < remainder else 0)
        selected = rng.sample(grouped[kind], count)
        for question in selected:
            if "options" in question:
                options = list(question["options"])
                rng.shuffle(options)
                question["options"] = tuple(options)
        result.extend(selected)
    rng.shuffle(result)
    return result


def is_correct(question: dict, response: object) -> bool:
    if response is None:
        return False
    if question["type"] == "填空题":
        text = str(response).strip().translate(str.maketrans("１２３４５６７８９", "123456789"))
        try:
            return float(text) == float(question["answer"])
        except ValueError:
            return False
    return str(response).strip() == question["answer"]
