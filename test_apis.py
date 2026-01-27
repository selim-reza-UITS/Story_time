import requests
import json

BASE_URL = "http://localhost:9900/api/v1"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def print_result(context, response):
    if response.status_code in [200, 201, 204]:
        print(f"{GREEN}[PASS] {context}{RESET}")
    else:
        print(f"{RED}[FAIL] {context} - Status: {response.status_code}{RESET}")
        try:
            print(f"       Response: {response.json()}")
        except:
            print(f"       Response: {response.text}")

def login(email, password):
    url = f"{BASE_URL}/auth/login/"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    print_result(f"Login {email}", response)
    if response.status_code == 200:
        return response.json()['access']
    return None

def test_student_flow():
    print("\n--- Testing Student Flow ---")
    token = login("student@student.com", "123")
    if not token: return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Profile
    print_result("Get Profile", requests.get(f"{BASE_URL}/students/profile/", headers=headers))
    # 2. Stories Library
    print_result("Get Story Library", requests.get(f"{BASE_URL}/stories/library/", headers=headers))
    # 3. Stats
    print_result("Get My Stats", requests.get(f"{BASE_URL}/students/my-stories/stats/", headers=headers))

    # 4. Create Story (Editor)
    story_data = {
        "title": "My Test Story",
        "content": "<p>Once upon a time...</p>",
        "grade": 3
    }
    create_resp = requests.post(f"{BASE_URL}/stories/editor/", headers=headers, json=story_data)
    print_result("Create Story", create_resp)
    
    if create_resp.status_code == 201:
        story_id = create_resp.json()['id']
        print_result(f"Get Story {story_id}", requests.get(f"{BASE_URL}/stories/editor/{story_id}/", headers=headers))

def test_teacher_flow():
    print("\n--- Testing Teacher Flow ---")
    token = login("teacher@teacher.com", "123")
    if not token: return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Dashboard
    print_result("Get Dashboard", requests.get(f"{BASE_URL}/teachers/dashboard/", headers=headers))
    # 2. My Profile
    print_result("Get My Profile", requests.get(f"{BASE_URL}/teachers/my-profile/", headers=headers))
    # 3. List Students
    print_result("List Students", requests.get(f"{BASE_URL}/teachers/all/students/", headers=headers))

    # 4. Create Student
    new_student = {
        "email": "student_by_teacher@test.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "Student",
        "grade_level": 4,
        "vocabulary_proficiency": "beginner"
    }
    # Check if exists first to avoid fail on re-run
    # For now just try create
    print_result("Create Student", requests.post(f"{BASE_URL}/teachers/all/students/", headers=headers, json=new_student))

def test_admin_flow():
    print("\n--- Testing Admin Flow ---")
    token = login("admin@admin.com", "123")
    if not token: return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Overview
    print_result("Get Admin Overview", requests.get(f"{BASE_URL}/site/overview/", headers=headers))
    # 2. List Teachers
    print_result("List Teachers", requests.get(f"{BASE_URL}/site/admin/teachers/", headers=headers))
    # 3. List Students
    print_result("List Students", requests.get(f"{BASE_URL}/site/admin/students/", headers=headers))

if __name__ == "__main__":
    test_student_flow()
    test_teacher_flow()
    test_admin_flow()
