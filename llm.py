import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_study_plan(missed_topics, final_ability, ability_band, performance_score=None):
    """
    Generates a personalized GRE study plan using Gemini
    based on adaptive diagnostic results.
    """

    # Format weak topics
    if missed_topics:
        topics = ", ".join(
            [f"{topic} ({count} errors)" for topic, count in missed_topics]
        )
    else:
        topics = "No consistent weak topics detected."

    performance_text = ""
    if performance_score is not None:
        performance_text = f"\nOverall performance score: {performance_score:.2f}\n"

    prompt = f"""
You are an expert GRE tutor.

Student diagnostic report:

Ability score (0–1 scale): {final_ability:.2f}
Ability category: {ability_band}
{performance_text}
Weak topics identified:
{topics}

Create a concise improvement plan.

Instructions:
- Exactly 3 numbered steps
- Each step must include concrete practice advice
- Avoid motivational language
- Focus on actionable learning strategy
- Keep responses concise and practical
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

Ability category: {ability_band}

Weak topics: {topics}

1. Review core concepts for the weak topics listed above.

2. Practice 15–20 problems daily at difficulty level {final_ability:.2f} focusing on accuracy.

3. Take another adaptive diagnostic test after one week to measure improvement.
"""