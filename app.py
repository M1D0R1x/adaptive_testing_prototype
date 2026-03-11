import uuid
from collections import Counter
from typing import Dict, List

from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

from adaptive import select_next_question, update_ability
from database import sessions_collection, questions_collection
from llm import generate_study_plan

app = FastAPI(title="Adaptive Diagnostic Engine")


class SubmitAnswer(BaseModel):
    answer: str


class SessionResponse(BaseModel):
    session_id: str


class QuestionResponse(BaseModel):
    question_text: str
    options: Dict[str, str]
    difficulty: float
    topic: str


class AnswerResponse(BaseModel):
    correct: bool
    new_ability: float


class StudyPlanResponse(BaseModel):
    study_plan: str
    final_ability: float
    performance_score: float
    topic_errors: Dict[str, int]
    ability_history: List[float]


def ability_band(theta: float) -> str:

    if theta < 0.35:
        return "beginner"
    if theta < 0.65:
        return "intermediate"
    if theta < 0.85:
        return "advanced"
    return "expert"


def compute_performance_score(session):

    answers = session["answers"]

    total = len(answers)
    correct = sum(1 for a in answers if a["correct"])

    accuracy = correct / total if total else 0

    correct_difficulties = []

    for ans in answers:
        if ans["correct"]:
            q = questions_collection.find_one(
                {"_id": ObjectId(ans["question_id"])}
            )
            if q:
                correct_difficulties.append(q["difficulty"])

    avg_difficulty = (
        sum(correct_difficulties) / len(correct_difficulties)
        if correct_difficulties else 0
    )

    ability = session["current_ability"]

    score = (
        0.5 * ability +
        0.3 * accuracy +
        0.2 * avg_difficulty
    )

    return round(score, 3)


@app.post("/start_session", response_model=SessionResponse)
def start_session():

    session_id = str(uuid.uuid4())

    session = {
        "session_id": session_id,
        "current_ability": 0.5,
        "ability_history": [0.5],
        "answers": [],
        "questions_asked": [],
    }

    sessions_collection.insert_one(session)

    return {"session_id": session_id}


@app.get("/next_question/{session_id}", response_model=QuestionResponse)
def get_next_question(session_id: str = Path(...)):

    session = sessions_collection.find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(session["questions_asked"]) >= 10:
        raise HTTPException(status_code=400, detail="Test completed")

    question = select_next_question(session_id)

    sessions_collection.update_one(
        {"session_id": session_id},
        {"$push": {"questions_asked": question["_id"]}},
    )

    return {
        "question_text": question["question_text"],
        "options": question["options"],
        "difficulty": question["difficulty"],
        "topic": question["topic"],
    }


@app.post("/submit_answer/{session_id}", response_model=AnswerResponse)
def submit_answer(session_id: str, body: SubmitAnswer):

    session = sessions_collection.find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question_id = session["questions_asked"][-1]

    question = questions_collection.find_one({"_id": question_id})

    correct = body.answer.upper() == question["correct_answer"].upper()

    answer_record = {
        "question_id": str(question_id),
        "response": body.answer,
        "correct": correct,
    }

    sessions_collection.update_one(
        {"session_id": session_id},
        {"$push": {"answers": answer_record}},
    )

    new_ability = update_ability(session_id)

    sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$set": {"current_ability": new_ability},
            "$push": {"ability_history": new_ability},
        },
    )

    return {"correct": correct, "new_ability": new_ability}


@app.get("/study_plan/{session_id}", response_model=StudyPlanResponse)
def get_study_plan(session_id: str):

    session = sessions_collection.find_one({"session_id": session_id})

    if len(session["answers"]) < 10:
        raise HTTPException(status_code=400, detail="Test incomplete")

    missed_topics = []

    for answer in session["answers"]:
        if not answer["correct"]:
            q_id = ObjectId(answer["question_id"])
            question = questions_collection.find_one({"_id": q_id})
            if question:
                missed_topics.append(question["topic"])

    topic_counts = Counter(missed_topics)

    final_ability = session["current_ability"]

    band = ability_band(final_ability)

    performance_score = compute_performance_score(session)

    plan = generate_study_plan(
        topic_counts.most_common(),
        final_ability,
        band
    )

    return {
        "study_plan": plan,
        "final_ability": final_ability,
        "performance_score": performance_score,
        "topic_errors": dict(topic_counts),
        "ability_history": session.get("ability_history", []),
    }