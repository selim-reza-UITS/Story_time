import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from app.accounts.models import User
from app.dashboard.models import AiAssistantConfigModel,TermsAndConditionsModel,PrivacyAndPolicyModel,PlatformConfigModel
from app.story.models import StoryModel,ReadingTrack
from app.students.models import StudentActivity,StudentProfile,VocabularySearch
from app.teachers.models import TeacherProfile

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed FULL database with nested fake data (~200+ rows)"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Seeding database...")

        admin = self.create_admin()
        teachers = self.create_teachers(10)
        students = self.create_students(30, teachers)

        self.create_platform_configs()
        self.create_vocab(20)

        stories = self.create_stories(admin, students, 40)
        self.create_reading_tracks(students, stories, 60)
        self.create_student_activities(students, stories, 80)

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully"))

    # ---------------- CONFIG ----------------

    def create_platform_configs(self):
        PlatformConfigModel.objects.get_or_create(
            platform_name="Story Time",
            contact_email="contact@storytime.com",
            support_email="support@storytime.com",
        )

        AiAssistantConfigModel.objects.get_or_create(
            assistant_name="StoryBot",
            ai_behaviour_settings={
                "tone": "friendly",
                "grade_sensitive": True,
            },
        )

        TermsAndConditionsModel.objects.get_or_create(
            content="<h1>Terms</h1><p>These are fake terms.</p>"
        )

        PrivacyAndPolicyModel.objects.get_or_create(
            content="<h1>Privacy</h1><p>We respect privacy.</p>"
        )

    # ---------------- USERS ----------------

    def create_admin(self):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_admin_user": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.set_password("admin123")
        admin.save()
        return admin

    def create_teachers(self, count):
        teachers = []
        for _ in range(count):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_teacher=True,
            )
            teachers.append(
                TeacherProfile.objects.create(
                    user=user,
                    grade_level=random.choice([3, 4, 5]),
                    bio=fake.text(120),
                )
            )
        return teachers

    def create_students(self, count, teachers):
        students = []
        for _ in range(count):
            user = User.objects.create_user(
                username=fake.unique.user_name(),
                email=fake.email(),
                password="password123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_student=True,
            )
            students.append(
                StudentProfile.objects.create(
                    user=user,
                    grade_level=random.choice([3, 4, 5]),
                    vocabulary_proficiency=random.choice(
                        ["beginner", "intermediate", "advanced"]
                    ),
                    assigned_teacher=random.choice(teachers).user,
                    total_books_read=random.randint(0, 20),
                    words_learned=random.randint(0, 500),
                )
            )
        return students

    # ---------------- CONTENT ----------------

    def create_stories(self, admin, students, count):
        stories = []
        authors = [admin] + [s.user for s in students]

        for _ in range(count):
            user = random.choice(authors)
            content = "<p>" + "</p><p>".join(fake.paragraphs(5)) + "</p>"

            story = StoryModel.objects.create(
                user=user,
                title=fake.sentence(nb_words=5),
                content=content,
                rating=round(random.uniform(3.5, 5.0), 1),
                grade=random.choice([3, 4, 5]),
                is_draft=False,
            )
            stories.append(story)

        return stories

    def create_reading_tracks(self, students, stories, count):
        created = set()

        for _ in range(count):
            student = random.choice(students).user
            story = random.choice(stories)

            key = (student.id, story.id)
            if key in created:
                continue

            progress = random.randint(10, 100)
            ReadingTrack.objects.create(
                student=student,
                story=story,
                current_page=random.randint(1, story.total_pages),
                total_pages=story.total_pages,
                completion_percentage=progress,
                is_completed=progress == 100,
            )
            created.add(key)

    def create_student_activities(self, students, stories, count):
        actions = [
            "STORY_CREATE",
            "STORY_UPDATE",
            "READ_START",
            "READ_COMPLETE",
            "VOCAB_SEARCH",
        ]

        for _ in range(count):
            student = random.choice(students).user
            story = random.choice(stories)

            StudentActivity.objects.create(
                student=student,
                action_type=random.choice(actions),
                description=fake.sentence(),
                timestamp=fake.date_time_between(
                    start_date="-30d", end_date="now", tzinfo=timezone.get_current_timezone()
                ),
            )

    # ---------------- VOCAB ----------------

    def create_vocab(self, count):
        created = 0
        attempts = 0

        while created < count and attempts < count * 5:
            attempts += 1
            word = fake.word().lower()

            obj, is_created = VocabularySearch.objects.get_or_create(
                word=word,
                defaults={
                    "definition": fake.sentence(),
                    "search_count": random.randint(1, 50),
                }
            )

            if is_created:
                created += 1