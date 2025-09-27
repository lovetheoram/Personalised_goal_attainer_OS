# from django.contrib.auth import get_user_model
# from syllabus.models import Concept
# from target.models import UserProgress

# User = get_user_model()
# user = User.objects.get(id=1)

# concepts = Concept.objects.all()

# for concept in concepts:
#     progress, created = UserProgress.objects.get_or_create(
#         user=user,
#         concept=concept,
#         defaults={
#             'mastery': 0.0,
#             'revision_count': 0,
#             'carryover_flag': False,
#             'ease_factor': 2.5,
#             'interval_days': 0
#         }
#     )
#     if created:
#         print(f'Created progress for concept: {concept.name}')
#     else:
#         print(f'Progress already exists for concept: {concept.name}')

# print('✅ All UserProgress records initialized!')
