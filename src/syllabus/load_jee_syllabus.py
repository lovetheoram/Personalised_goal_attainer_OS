import json
from syllabus.models import Exam, Subject, Topic, Subtopic, Concept

def load_jee_syllabus():
    with open("syllabus/jee_syllabus.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    exam_data = data["exam"]

    # Create Exam
    exam, _ = Exam.objects.get_or_create(
        name=exam_data["name"],
        defaults={
            # "description": exam_data.get("description", ""),
            "start_date": exam_data.get("start_date"),
            "end_date": exam_data.get("end_date")
        }
    )

    for subj_data in exam_data.get("subjects", []):
        subject, _ = Subject.objects.get_or_create(
            exam=exam,
            name=subj_data["name"],
            defaults={"weightage": subj_data.get("weightage", 1.0)}
        )

        for topic_data in subj_data.get("topics", []):
            topic, _ = Topic.objects.get_or_create(
                subject=subject,
                name=topic_data["name"],
                defaults={"weightage": topic_data.get("weightage", 1.0)}
            )

            for subtopic_data in topic_data.get("subtopics", []):
                subtopic, _ = Subtopic.objects.get_or_create(
                    topic=topic,
                    name=subtopic_data["name"],
                    defaults={"weightage": subtopic_data.get("weightage", 1.0)}
                )

                for concept_data in subtopic_data.get("concepts", []):
                    Concept.objects.get_or_create(
                        subtopic=subtopic,
                        name=concept_data["name"],
                        defaults={
                            "description": concept_data.get("description", ""),
                            "estimated_time": concept_data.get("estimated_time", 30),
                            "weightage": concept_data.get("weightage", 1.0),
                            # "difficulty": concept_data.get("difficulty", 1.0),
                            "resources": concept_data.get("resources", {})
                        }
                    )

    print("✅ JEE syllabus loaded successfully!")

# Call the function
load_jee_syllabus()
