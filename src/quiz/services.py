from target.models import DailyTarget
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from datetime import date
from progress.services import update_progress
from syllabus.models import Concept

def generate_ai_quiz(user, study_date=None, num_questions=3):
    study_date = study_date or date.today()
    targets = DailyTarget.objects.filter(user=user, study_date=study_date)
    questions = []

    if not targets.exists():
        return [{"error": "No targets found for today"}]

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        api_key="AIzaSyA27qjOISG9jkasJ4UtzxhuyoD1kNwsai0"  # move to env vars
    )

    for t in targets:
        prompt = f"""
Generate {num_questions} multiple-choice questions for the concept:
Concept: {t.concept.name}
Description: {t.concept.description or 'N/A'}

Output as a JSON list with each question having:
- text: question text
- options: list of 4 strings
- correct: the correct option string
        """
        try:
            response = llm.invoke(prompt)
            response_text = getattr(response, "content", response).strip()

            # Remove ```json``` or ``` markers
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            q_list = json.loads(response_text)

            for q in q_list:
                q["concept_id"] = t.concept.id
                questions.append(q)

        except Exception as e:
            # Fallback question if AI fails
            questions.extend([{
                "concept_id": t.concept.id,
                "text": f"Could not generate question for {t.concept.name}",
                "options": ["N/A"]*4,
                "correct": "N/A"
            } for _ in range(num_questions)])

    return questions


def submit_quiz_results(user, study_date=None, results=None, understood=None):
    study_date = study_date or date.today()
    results = results or []

    if not results:
        return {"error": "No quiz results provided"}

    for r in results:
        try:
            concept = Concept.objects.get(id=r["concept_id"])
            score = float(r.get("score", 0))
            update_progress(user, concept, score, understood)
        except Concept.DoesNotExist:
            continue

    return {"message": "Progress updated", "date": str(study_date)}
