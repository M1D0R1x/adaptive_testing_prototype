import random
from typing import Dict, Any

import numpy as np
from bson.objectid import ObjectId

from database import questions_collection, sessions_collection

WINDOW = 0.15


def logistic(theta: float, a: float, b: float) -> float:
    return 1 / (1 + np.exp(-a * (theta - b)))


def information(theta: float, a: float, b: float) -> float:
    p = logistic(theta, a, b)
    return (a ** 2) * p * (1 - p)


def select_next_question(session_id: str) -> Dict[str, Any]:

    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise ValueError("Session not found")

    asked_ids = session.get("questions_asked", [])
    ability = session.get("current_ability", 0.5)

    questions = list(
        questions_collection.find({
            "_id": {"$nin": asked_ids},
            "difficulty": {
                "$gte": ability - WINDOW,
                "$lte": ability + WINDOW
            }
        })
    )

    if not questions:
        questions = list(
            questions_collection.find({"_id": {"$nin": asked_ids}})
        )

    if not questions:
        raise ValueError("No more questions available")

    scored = []

    for q in questions:
        a = q.get("discrimination", 1.0)
        b = q["difficulty"]

        info = information(ability, a, b)

        info += random.uniform(0, 0.02)

        scored.append((info, q))

    scored.sort(reverse=True, key=lambda x: x[0])

    return scored[0][1]


def update_ability(session_id: str) -> float:

    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise ValueError("Session not found")

    answers = session.get("answers", [])

    if not answers:
        return 0.5

    last = answers[-1]

    question = questions_collection.find_one(
        {"_id": ObjectId(last["question_id"])}
    )

    if not question:
        raise ValueError("Question not found")

    theta = session.get("current_ability", 0.5)

    a = question.get("discrimination", 1.0)
    b = question["difficulty"]

    p = logistic(theta, a, b)

    r = 1 if last["correct"] else 0

    learning_rate = 0.25

    new_theta = theta + learning_rate * a * (r - p)

    new_theta = max(0.0, min(1.0, new_theta))

    return float(new_theta)