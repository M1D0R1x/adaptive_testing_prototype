import uuid
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from database import sessions_collection, questions_collection
from adaptive import select_next_question, update_ability
from llm import generate_study_plan
from bson.objectid import ObjectId
from collections import Counter
from typing import Dict, Any, List

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


@app.post("/start_session", response_model=SessionResponse)
def start_session():
    session_id = str(uuid.uuid4())

    session = {
        "session_id": session_id,
        "current_ability": 0.5,
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

    try:
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit_answer/{session_id}", response_model=AnswerResponse)
def submit_answer(session_id: str, body: SubmitAnswer):

    session = sessions_collection.find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session["questions_asked"]:
        raise HTTPException(status_code=400, detail="No question asked yet")

    question_id = session["questions_asked"][-1]

    question = questions_collection.find_one({"_id": question_id})

    if not question:
        raise HTTPException(status_code=500, detail="Question missing")

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

    try:

        new_ability = update_ability(session_id)

        sessions_collection.update_one(
            {"session_id": session_id},
            {"$set": {"current_ability": new_ability}},
        )

        return {
            "correct": correct,
            "new_ability": new_ability,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/study_plan/{session_id}", response_model=StudyPlanResponse)
def get_study_plan(session_id: str):

    session = sessions_collection.find_one({"session_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(session["answers"]) < 10:
        raise HTTPException(status_code=400, detail="Test incomplete")

    missed_topics: List[str] = []

    for answer in session["answers"]:

        if not answer["correct"]:

            q_id = ObjectId(answer["question_id"])

            question = questions_collection.find_one({"_id": q_id})

            if question:
                missed_topics.append(question["topic"])

    topic_counts = Counter(missed_topics).most_common()

    final_ability = session["current_ability"]

    try:

        plan = generate_study_plan(topic_counts, final_ability)

        return {"study_plan": plan}

    except Exception:

        return {
            "study_plan": "AI plan unavailable. Review missed topics and practice similar problems."
        }