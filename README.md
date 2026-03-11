# AI Adaptive Diagnostic Engine

This project implements a **1‑Dimensional Adaptive Testing System** based on **Item Response Theory (IRT)**. The system dynamically selects questions based on a student's estimated ability and produces an **AI‑generated personalized study plan** after the diagnostic test.

The goal is to simulate the core mechanics used in modern adaptive exams such as:

* GRE
* GMAT
* Duolingo English Test

---

# System Architecture

## Backend

* Python
* FastAPI
* MongoDB

## Frontend

* Streamlit

## AI

* Google Gemini API

---

# Project Structure

```
adaptive.py
    Core adaptive testing algorithm
    Ability estimation and question selection

app.py
    FastAPI backend and API endpoints

frontend.py
    Streamlit interface for running the adaptive test

seed.py
    Seeds GRE‑style question bank into MongoDB

llm.py
    Gemini integration for generating personalized study plans

database.py
    MongoDB connection and collection initialization
```

---

# Adaptive Testing Algorithm

The system uses a **2‑Parameter Item Response Theory (IRT) model**.

Probability that a student answers a question correctly:

```
P(correct) = 1 / (1 + e^( -a(θ - b) ))
```

Where

| Symbol | Meaning                 |
| ------ | ----------------------- |
| θ      | Student ability         |
| b      | Question difficulty     |
| a      | Question discrimination |

---

# Adaptive Workflow

1. Student begins with **initial ability θ = 0.5**.

2. The system selects a question that **maximizes Fisher Information** near the student's current ability.

3. After the student answers the question, ability is updated using an online update rule:

```
θ_new = θ + learning_rate * (r - P(correct))
```

Where

```
r = 1 if answer is correct
r = 0 if answer is incorrect
```

4. Updated ability is stored in the session.

5. The system selects the next question using the updated ability estimate.

6. The test continues for **10 adaptive questions**.

7. After the test finishes:

* Weak topics are identified
* Performance score is computed
* Gemini generates a personalized study plan

---

# Question Selection Strategy

Questions are selected using **Fisher Information maximization**.

```
I(θ) = a² * P(θ) * (1 − P(θ))
```

Questions with the highest information value near the student's ability are prioritized.

Additional safeguards:

* Difficulty selection window of **±0.15** around current ability
* Small randomness added to prevent identical question sequences

---

# Performance Score

The system computes an overall performance metric using:

```
Performance Score =
0.5 * Final Ability
+ 0.3 * Accuracy
+ 0.2 * Average Difficulty of Correct Answers
```

This score prevents late correct answers from artificially inflating ability.

---

# MongoDB Schema

## Questions Collection

```
{
    question_text: string

    options: {
        A: string
        B: string
        C: string
        D: string
    }

    correct_answer: string

    difficulty: float
    discrimination: float

    topic: string
    tags: [string]
}
```

Indexes:

```
difficulty
topic
```

---

## UserSessions Collection

```
{
    session_id: string

    current_ability: float

    ability_history: [float]

    questions_asked: [ObjectId]

    answers: [
        {
            question_id: string
            response: string
            correct: boolean
        }
    ]
}
```

Indexes:

```
session_id
```

---

# API Endpoints

## Start Adaptive Session

```
POST /start_session
```

Creates a new diagnostic test session.

Response

```
{
  "session_id": "uuid"
}
```

---

## Get Next Question

```
GET /next_question/{session_id}
```

Returns the next adaptive question.

Response

```
{
  "question_text": "string",
  "options": {"A": "", "B": "", "C": "", "D": ""},
  "difficulty": 0.45,
  "topic": "Algebra"
}
```

---

## Submit Answer

```
POST /submit_answer/{session_id}
```

Body

```
{
  "answer": "A"
}
```

Response

```
{
  "correct": true,
  "new_ability": 0.63
}
```

---

## Generate Study Plan

```
GET /study_plan/{session_id}
```

Response

```
{
  "study_plan": "AI generated learning plan",
  "final_ability": 0.72,
  "performance_score": 0.68,
  "topic_errors": {
    "Algebra": 2,
    "Vocabulary": 1
  },
  "ability_history": [0.5, 0.56, 0.61, ...]
}
```

---

# Frontend Features

The Streamlit UI provides:

* Adaptive question interface
* Real‑time ability updates
* Test progress tracking
* Diagnostic report after completion

Visual analytics include:

**Ability Progression Graph**

Shows how estimated ability evolves across questions.

**Difficulty vs Ability Graph**

Compares question difficulty with the student ability trajectory.

---

# Setup Instructions

## 1 Install Dependencies

```
pip install -r requirements.txt
```

---

## 2 Create Environment File

Create a `.env` file:

```
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

---

## 3 Seed Question Bank

```
python seed.py
```

---

## 4 Start Backend

```
uvicorn app:app --reload
```

Backend runs at

```
http://127.0.0.1:8000
```

---

## 5 Start Frontend

```
streamlit run frontend.py
```

---

# AI Usage Log

AI tools used:

* ChatGPT
* Cursor

AI was used to assist with:

* adaptive algorithm scaffolding
* FastAPI endpoint structure
* Gemini API integration
* debugging MongoDB TLS connection issues

Manual engineering work included:

* implementing Fisher information selection
* designing MongoDB schema
* building performance scoring logic
* constructing the Streamlit diagnostic interface
* improving the LLM prompt design for actionable study plans

---

# Key Design Decisions

1. **Information‑based question selection** instead of naive difficulty matching.

2. **Online ability updates** allow the system to adjust after every answer.

3. **Performance score metric** prevents late correct answers from inflating ability.

4. **LLM tutoring output** focuses on concrete study actions instead of generic feedback.

---

# Future Improvements

Potential research extensions include:

* Multi‑dimensional IRT
* Bayesian ability estimation
* Standard error / confidence interval estimation
* Question exposure control
* Larger calibrated item bank
* Response time modeling

---

# Summary

This project demonstrates the core mechanics of a modern **AI‑assisted adaptive diagnostic system** combining:

* psychometric modeling
* real‑time ability estimation
* adaptive item selection
* data‑driven performance analytics
* AI‑generated personalized tutoring
