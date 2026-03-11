from database import questions_collection

EXPECTED_COUNT = 20


def validate_questions(questions):

    required_fields = {
        "question_text",
        "options",
        "correct_answer",
        "difficulty",
        "discrimination",
        "topic",
        "tags",
    }

    for i, q in enumerate(questions):

        missing = required_fields - q.keys()

        if missing:
            raise ValueError(f"Question {i} missing fields: {missing}")

        if not (0.0 <= q["difficulty"] <= 1.0):
            raise ValueError(
                f"Question {i} difficulty must be between 0.0 and 1.0"
            )

        if q["correct_answer"] not in q["options"]:
            raise ValueError(
                f"Question {i} correct answer must exist in options"
            )


print("Clearing existing questions...")
questions_collection.delete_many({})

print("Seeding question bank...")


questions = [

# EASY

{
"question_text": "Select the synonym for 'happy'.",
"options": {"A": "Joyful", "B": "Sad", "C": "Angry", "D": "Tired"},
"correct_answer": "A",
"difficulty": 0.1,
"discrimination": 0.8,
"topic": "Vocabulary",
"tags": ["synonym"]
},

{
"question_text": "Select the antonym for 'large'.",
"options": {"A": "Huge", "B": "Small", "C": "Vast", "D": "Massive"},
"correct_answer": "B",
"difficulty": 0.15,
"discrimination": 0.8,
"topic": "Vocabulary",
"tags": ["antonym"]
},

{
"question_text": "What is 5 + 6?",
"options": {"A": "10", "B": "12", "C": "11", "D": "13"},
"correct_answer": "C",
"difficulty": 0.1,
"discrimination": 0.7,
"topic": "Algebra",
"tags": ["addition"]
},

{
"question_text": "What is 9 - 3?",
"options": {"A": "6", "B": "5", "C": "7", "D": "4"},
"correct_answer": "A",
"difficulty": 0.15,
"discrimination": 0.7,
"topic": "Algebra",
"tags": ["subtraction"]
},

{
"question_text": "Which word means 'fast'?",
"options": {"A": "Quick", "B": "Lazy", "C": "Slow", "D": "Late"},
"correct_answer": "A",
"difficulty": 0.2,
"discrimination": 0.9,
"topic": "Vocabulary",
"tags": ["synonym"]
},

{
"question_text": "Area of square with side 4",
"options": {"A": "8", "B": "16", "C": "12", "D": "20"},
"correct_answer": "B",
"difficulty": 0.3,
"discrimination": 0.9,
"topic": "Geometry",
"tags": ["area"]
},

# MEDIUM

{
"question_text": "Solve: 2x + 6 = 10",
"options": {"A": "1", "B": "2", "C": "3", "D": "4"},
"correct_answer": "B",
"difficulty": 0.4,
"discrimination": 1.0,
"topic": "Algebra",
"tags": ["equation"]
},

{
"question_text": "Perimeter of rectangle 7×3",
"options": {"A": "20", "B": "18", "C": "16", "D": "22"},
"correct_answer": "A",
"difficulty": 0.4,
"discrimination": 1.0,
"topic": "Geometry",
"tags": ["perimeter"]
},

{
"question_text": "Probability of rolling a 6",
"options": {"A": "1/2", "B": "1/6", "C": "1/4", "D": "1/3"},
"correct_answer": "B",
"difficulty": 0.45,
"discrimination": 1.0,
"topic": "Algebra",
"tags": ["probability"]
},

{
"question_text": "sin(90°)",
"options": {"A": "0", "B": "1", "C": "-1", "D": "0.5"},
"correct_answer": "B",
"difficulty": 0.5,
"discrimination": 1.1,
"topic": "Geometry",
"tags": ["trigonometry"]
},

{
"question_text": "Roots of x² − 4x + 4",
"options": {"A": "2,2", "B": "1,4", "C": "2,4", "D": "3,3"},
"correct_answer": "A",
"difficulty": 0.6,
"discrimination": 1.1,
"topic": "Algebra",
"tags": ["quadratic"]
},

{
"question_text": "Synonym for 'ubiquitous'",
"options": {"A": "Rare", "B": "Hidden", "C": "Everywhere", "D": "Scarce"},
"correct_answer": "C",
"difficulty": 0.6,
"discrimination": 1.2,
"topic": "Vocabulary",
"tags": ["advanced"]
},

# HARD

{
"question_text": "Antonym of 'mitigate'",
"options": {"A": "Ease", "B": "Reduce", "C": "Worsen", "D": "Soften"},
"correct_answer": "C",
"difficulty": 0.7,
"discrimination": 1.3,
"topic": "Vocabulary",
"tags": ["advanced"]
},

{
"question_text": "What is cos(0°)?",
"options": {"A": "0", "B": "1", "C": "-1", "D": "0.5"},
"correct_answer": "B",
"difficulty": 0.7,
"discrimination": 1.2,
"topic": "Geometry",
"tags": ["trigonometry"]
},

{
"question_text": "Solve: x² − 9 = 0",
"options": {"A": "±3", "B": "±9", "C": "3", "D": "9"},
"correct_answer": "A",
"difficulty": 0.75,
"discrimination": 1.2,
"topic": "Algebra",
"tags": ["quadratic"]
},

{
"question_text": "Synonym for 'obfuscate'",
"options": {"A": "Explain", "B": "Reveal", "C": "Confuse", "D": "Clarify"},
"correct_answer": "C",
"difficulty": 0.8,
"discrimination": 1.3,
"topic": "Vocabulary",
"tags": ["advanced"]
},

{
"question_text": "Integral of 2x dx",
"options": {"A": "x² + C", "B": "2x²", "C": "x²", "D": "2x"},
"correct_answer": "A",
"difficulty": 0.85,
"discrimination": 1.4,
"topic": "Algebra",
"tags": ["calculus"]
},

{
"question_text": "Derivative of x²",
"options": {"A": "x", "B": "2x", "C": "x²", "D": "2"},
"correct_answer": "B",
"difficulty": 0.9,
"discrimination": 1.4,
"topic": "Algebra",
"tags": ["calculus"]
},

{
"question_text": "Antonym of 'ephemeral'",
"options": {"A": "Temporary", "B": "Brief", "C": "Short", "D": "Permanent"},
"correct_answer": "D",
"difficulty": 0.9,
"discrimination": 1.3,
"topic": "Vocabulary",
"tags": ["advanced"]
},

{
"question_text": "Limit of (1 + 1/n)^n",
"options": {"A": "1", "B": "e", "C": "2", "D": "0"},
"correct_answer": "B",
"difficulty": 0.95,
"discrimination": 1.5,
"topic": "Algebra",
"tags": ["calculus"]
},

]


validate_questions(questions)

result = questions_collection.insert_many(questions)

print(f"Inserted {len(result.inserted_ids)} questions")

questions_collection.create_index("difficulty")
questions_collection.create_index("topic")

print("Indexes created")