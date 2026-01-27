from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.students.models import StudentProfile
from app.teachers.models import TeacherProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates demo users (Admin, Teacher, Student)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo users...')

        # 1. Admin
        if not User.objects.filter(email='admin@admin.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@admin.com',
                password='123',
                is_admin_user=True
            )
            self.stdout.write(self.style.SUCCESS('Created Admin: admin@admin.com / 123'))
        else:
            self.stdout.write('Admin already exists')

        # 2. Teacher
        if not User.objects.filter(email='teacher@teacher.com').exists():
            teacher = User.objects.create_user(
                username='teacher',
                email='teacher@teacher.com',
                password='123',
                is_teacher=True
            )
            TeacherProfile.objects.create(user=teacher, grade_level=3)
            self.stdout.write(self.style.SUCCESS('Created Teacher: teacher@teacher.com / 123'))
        else:
            self.stdout.write('Teacher already exists')

        # 3. Student
        if not User.objects.filter(email='student@student.com').exists():
            student = User.objects.create_user(
                username='student',
                email='student@student.com',
                password='123',
                is_student=True
            )
            StudentProfile.objects.create(user=student, grade_level=3)
            self.stdout.write(self.style.SUCCESS('Created Student: student@student.com / 123'))
        else:
            print('Student already exists')
