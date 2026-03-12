import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_study_plan(missed_topics, final_ability):

    topics = ", ".join(
        [f"{topic} ({count} errors)" for topic, count in missed_topics]
    )

    prompt = f"""
You are an expert GRE tutor.

Student diagnostics:

Estimated ability level: {final_ability:.2f}

Weak topics:
{topics}

Generate a personalized study plan.

Rules:
- Only 3 steps
- Each step must be practical
- Include specific practice advice
- Keep it concise
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        return response.text.strip()

    except Exception:

        return f"""
Fallback Study Plan

1. Review core theory for the weak topics: {topics}

2. Practice 15–20 problems daily at difficulty {final_ability:.2f}

3. Retake an adaptive test after 1 week to measure improvement
"""