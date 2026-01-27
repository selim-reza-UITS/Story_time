from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
import random
from app.students.models import StudentProfile, StudentActivity, VocabularySearch
from app.teachers.models import TeacherProfile
from app.story.models import StoryModel, ReadingTrack
from django.utils import timezone

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with fake data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # 1. Create Teachers
        self.stdout.write('Creating Teachers...')
        teachers = []
        for _ in range(10):
            email = fake.email()
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=fake.user_name(),
                    email=email,
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_teacher=True
                )
                TeacherProfile.objects.create(
                    user=user,
                    grade_level=random.choice([3, 4, 5]),
                    bio=fake.text()
                )
                teachers.append(user)
        
        # 2. Create Students
        self.stdout.write('Creating Students...')
        students = []
        for _ in range(50):
            email = fake.email()
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=fake.user_name(),
                    email=email,
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_student=True
                )
                StudentProfile.objects.create(
                    user=user,
                    grade_level=random.choice([3, 4, 5]),
                    vocabulary_proficiency=random.choice(['beginner', 'intermediate', 'advanced']),
                    assigned_teacher=random.choice(teachers) if teachers else None,
                    total_books_read=random.randint(0, 50),
                    words_learned=random.randint(0, 200)
                )
                students.append(user)

        # 3. Create Stories
        self.stdout.write('Creating Stories...')
        stories = []
        for _ in range(100):
            author = random.choice(teachers) if teachers else User.objects.first()
            story = StoryModel.objects.create(
                user=author,
                title=fake.sentence(nb_words=4).replace('.', ''),
                author_name=f"{author.first_name} {author.last_name}",
                content=fake.text(max_nb_chars=3000),
                rating=round(random.uniform(3.5, 5.0), 1),
                grade=random.choice([3, 4, 5]),
                word_count=random.randint(500, 2000),
                is_draft=False
            )
            stories.append(story)

        # 4. Create Student Activities
        self.stdout.write('Creating Activities...')
        actions = ['STORY_CREATE', 'STORY_UPDATE', 'READ_START', 'READ_COMPLETE', 'VOCAB_SEARCH']
        for _ in range(100):
            if students:
                StudentActivity.objects.create(
                    student=random.choice(students),
                    action_type=random.choice(actions),
                    description=fake.sentence(),
                    timestamp=fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
                )

        # 5. Create Reading Tracks
        self.stdout.write('Creating Reading Tracks...')
        for _ in range(50):
            if students and stories:
                student = random.choice(students)
                story = random.choice(stories)
                # Check uniqueness
                if not ReadingTrack.objects.filter(student=student, story=story).exists():
                    ReadingTrack.objects.create(
                        student=student,
                        story=story,
                        current_page=random.randint(1, 5),
                        total_pages=5,
                        completion_percentage=random.randint(0, 100)
                    )

        # 6. Create Vocabulary
        self.stdout.write('Creating Vocabulary...')
        for _ in range(50):
            word = fake.word()
            if not VocabularySearch.objects.filter(word=word).exists():
                VocabularySearch.objects.create(
                    word=word,
                    definition=fake.sentence(),
                    search_count=random.randint(1, 100)
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with fake data!'))
