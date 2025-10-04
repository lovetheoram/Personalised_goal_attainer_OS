from achievement.models import Achievement

# Define achievements
achievements = [
    {
        "name": "1-Day Streak",
        "description": "Study at least 1 day in a row",
        "criteria_type": "streak",
        "criteria_value": 1,
    },
    {
        "name": "3-Day Streak",
        "description": "Study 3 consecutive days",
        "criteria_type": "streak",
        "criteria_value": 3,
    },
    {
        "name": "5-Day Streak",
        "description": "Study 5 consecutive days",
        "criteria_type": "streak",
        "criteria_value": 5,
    },
    {
        "name": "Mastery Level 80%",
        "description": "Achieve 80% mastery in any concept",
        "criteria_type": "mastery",
        "criteria_value": 80,
    },
    {
        "name": "Daily Target Completed",
        "description": "Complete all your daily targets",
        "criteria_type": "daily_target",
        "criteria_value": 1,
    },
    {
        "name": "Weak Area Improved",
        "description": "Improve weak concepts",
        "criteria_type": "weak_area",
        "criteria_value": 3,
    },
    {
        "name": "Earn 100 Points",
        "description": "Accumulate 100 points from learning",
        "criteria_type": "points",
        "criteria_value": 100,
    },
]

# Seed achievements
for ach in achievements:
    Achievement.objects.get_or_create(
        name=ach["name"],
        defaults={
            "description": ach["description"],
            "criteria_type": ach["criteria_type"],
            "criteria_value": ach["criteria_value"],
        }
    )

print("Achievements seeded successfully!")
