import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from app.accounts.models import User
from app.dashboard.models import (
    TermsAndConditionsModel,
    PrivacyAndPolicyModel,
    PlatformConfigModel,
    AiAssistantConfigModel,
)
from app.story.models import StoryModel, ReadingTrack
from app.students.models import StudentProfile, StudentActivity, VocabularySearch
from app.teachers.models import TeacherProfile

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed fake data safely (idempotent, OneToOne-safe)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("🚀 Seeding fake data..."))

        self.create_admin()
        teachers = self.create_teachers(5)
        students = self.create_students(15, teachers)
        stories = self.create_stories(students)
        self.create_reading_tracks(students, stories)
        self.create_student_activities(students)
        self.create_vocab()
        self.create_static_content()

        self.stdout.write(self.style.SUCCESS("✅ Fake data generated successfully"))

    # ------------------------------------------------------------------
    def create_admin(self):
        User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "is_admin_user": True,
            },
        )

    # ------------------------------------------------------------------
    def create_teachers(self, count):
        teachers = []

        existing_teachers = User.objects.filter(is_teacher=True)

        for user in existing_teachers:
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "grade_level": random.choice([3, 4, 5]),
                    "bio": fake.paragraph(),
                },
            )
            teachers.append(user)

        remaining = count - len(teachers)

        for _ in range(max(0, remaining)):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password="password123",
                is_teacher=True,
            )

            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    "grade_level": random.choice([3, 4, 5]),
                    "bio": fake.paragraph(),
                },
            )

            teachers.append(user)

        return teachers

    # ------------------------------------------------------------------
    def create_students(self, count, teachers):
        students = []

        existing_students = User.objects.filter(is_student=True)

        for user in existing_students:
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "grade_level": random.choice([3, 4, 5]),
                    "vocabulary_proficiency": random.choice(
                        ["beginner", "intermediate", "advanced"]
                    ),
                    "assigned_teacher": random.choice(teachers),
                    "total_books_read": random.randint(0, 20),
                    "words_learned": random.randint(50, 1000),
                },
            )
            students.append(user)

        remaining = count - len(students)

        for _ in range(max(0, remaining)):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                password="password123",
                is_student=True,
            )

            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "grade_level": random.choice([3, 4, 5]),
                    "vocabulary_proficiency": random.choice(
                        ["beginner", "intermediate", "advanced"]
                    ),
                    "assigned_teacher": random.choice(teachers),
                    "total_books_read": random.randint(0, 20),
                    "words_learned": random.randint(50, 1000),
                },
            )

            students.append(user)

        return students

    # ------------------------------------------------------------------
    def create_stories(self, students):
        stories = []

        for student in students:
            for _ in range(random.randint(1, 3)):
                stories.append(
                    StoryModel.objects.create(
                        user=student,
                        title=fake.sentence(nb_words=5),
                        content=fake.paragraph(nb_sentences=8),
                        is_draft=random.choice([True, False]),
                    )
                )

        return stories

    # ------------------------------------------------------------------
    def create_reading_tracks(self, students, stories):
        for student in students:
            for story in random.sample(stories, k=min(3, len(stories))):
                ReadingTrack.objects.get_or_create(
                    student=student,
                    story=story,
                    defaults={
                        "current_page": random.randint(1, 10),
                        "total_pages": 10,
                        "completion_percentage": random.randint(0, 100),
                    },
                )

    # ------------------------------------------------------------------
    def create_student_activities(self, students):
        actions = [
            "STORY_CREATE",
            "STORY_UPDATE",
            "READ_START",
            "READ_COMPLETE",
            "VOCAB_SEARCH",
        ]

        for student in students:
            for _ in range(random.randint(3, 6)):
                StudentActivity.objects.create(
                    student=student,
                    action_type=random.choice(actions),
                    description=fake.sentence(),
                )

    # ------------------------------------------------------------------
    def create_vocab(self):
        for _ in range(30):
            VocabularySearch.objects.get_or_create(
                word=fake.unique.word(),
                defaults={
                    "definition": fake.sentence(),
                    "search_count": random.randint(1, 50),
                },
            )

    # ------------------------------------------------------------------
    def create_static_content(self):
        TermsAndConditionsModel.objects.get_or_create(
            defaults={"content": fake.text(max_nb_chars=1500)}
        )

        PrivacyAndPolicyModel.objects.get_or_create(
            defaults={"content": fake.text(max_nb_chars=1500)}
        )

        PlatformConfigModel.objects.get_or_create(
            platform_name="Story Time",
            defaults={
                "contact_email": "contact@storytime.com",
                "support_email": "support@storytime.com",
            },
        )

        AiAssistantConfigModel.objects.get_or_create(
            assistant_name="StoryBuddy",
            defaults={
                "ai_behaviour_settings": {
                    "tone": "friendly",
                    "audience": "kids",
                    "reading_level": "grade_3_5",
                }
            },
        )
