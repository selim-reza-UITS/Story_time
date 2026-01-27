from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.students.models import StudentProfile, StudentActivity, VocabularySearch
from app.teachers.models import TeacherProfile
from app.story.models import StoryModel
from django.utils import timezone
import random
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with fake data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Create Students
        self.stdout.write('Creating 300 Students...')
        students = []
        for _ in range(300):
            email = fake.email()
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_student=True
                )
                
                grade = random.choice([3, 4, 5])
                proficiency = random.choice(['beginner', 'intermediate', 'advanced'])
                
                StudentProfile.objects.create(
                    user=user,
                    grade_level=grade,
                    vocabulary_proficiency=proficiency,
                    total_books_read=random.randint(0, 50),
                    # words_learned calculated dynamically or set here
                )
                students.append(user)

        # 2. Create Teachers
        self.stdout.write('Creating 10 Teachers...')
        teachers = []
        for _ in range(10):
            email = fake.email()
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_teacher=True
                )
                TeacherProfile.objects.create(
                    user=user,
                    grade_level=random.choice([3, 4, 5])
                )
                teachers.append(user)

        # 3. Create Admin Stories
        self.stdout.write('Creating 50 Stories...')
        # Get or create admin
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@cyndi.com', 'is_staff': True, 'is_superuser': True})
        if not admin_user.check_password('admin'):
             admin_user.set_password('admin')
             admin_user.save()

        for i in range(50):
            StoryModel.objects.create(
                user=admin_user,
                title=fake.catch_phrase(),
                content=fake.text(max_nb_chars=5000),
                grade=random.choice([3, 4, 5]),
                is_draft=random.choice([True, False]),
                word_count=random.randint(100, 1000),
                total_pages=random.randint(1, 10),
                author_name="Cyndi Admin"
            )

        # 4. Generate Student Activity
        self.stdout.write('Generating Activities...')
        actions = ['READ_START', 'READ_COMPLETE', 'VOCAB_SEARCH']
        for student in students[:100]: # heavy activity for first 100
            for _ in range(random.randint(5, 20)):
                action = random.choice(actions)
                desc = fake.sentence()
                if action == 'VOCAB_SEARCH':
                    word = fake.word()
                    desc = f"Searched: {word}"
                    # Add to vocab search
                    v, _ = VocabularySearch.objects.get_or_create(word=word)
                    v.search_count += 1
                    v.save()
                
                StudentActivity.objects.create(
                    student=student,
                    action_type=action,
                    description=desc
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
