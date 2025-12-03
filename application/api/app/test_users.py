import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_registration():
    print("\n" + "="*50)
    print("=== Testing User Registration ===")
    print("="*50)
    
    user_data = {
        "firstName": "Demo",
        "lastName": "Tester",
        "email": "demo.tester@test.com",
        "password": "securepass456",
        "bio": "Demo test user for GatorGuides testing"
    }
    
    print(f"\nRegistering user: {user_data['email']}")
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Registration successful!")
        print(f"Response: {json.dumps(data, indent=2)}")
        return data['user']['uid']
    else:
        print(f"✗ Registration failed!")
        print(f"Error: {response.json()}")
        return None

def test_login(email, password):
    print("\n" + "="*50)
    print("=== Testing User Login ===")
    print("="*50)
    
    login_data = {
        "email": email,
        "password": password
    }
    
    print(f"\nLogging in with: {email}")
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Login failed!")
        print(f"Error: {response.json()}")

def test_wrong_password(email):
    print("\n" + "="*50)
    print("=== Testing Wrong Password ===")
    print("="*50)
    
    login_data = {
        "email": email,
        "password": "wrongpassword"
    }
    
    print(f"\nAttempting login with wrong password...")
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✓ Correctly rejected wrong password!")
        print(f"Error message: {response.json()['detail']}")
    else:
        print(f"✗ Wrong password was accepted (security issue!)")

def test_get_user(uid):
    print("\n" + "="*50)
    print("=== Testing Get User ===")
    print("="*50)
    
    print(f"\nGetting user with uid={uid}")
    response = requests.get(f"{BASE_URL}/users/{uid}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ User retrieved successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Get user failed!")
        print(f"Error: {response.json()}")

def test_create_tutor(uid):
    print("\n" + "="*50)
    print("=== Testing Create Tutor ===")
    print("="*50)
    
    tutor_data = {
        "uid": uid,
        "rating": 4.5,
        "status": "available"
    }
    
    print(f"\nConverting user {uid} to tutor...")
    response = requests.post(f"{BASE_URL}/tutors", json=tutor_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tutor created successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
        return data['tid']
    else:
        print(f"✗ Create tutor failed!")
        print(f"Error: {response.json()}")
        return None

def test_add_tags(tid):
    print("\n" + "="*50)
    print("=== Testing Add Tutor Tags ===")
    print("="*50)
    
    tags_data = {
        "tagIds": [1, 2, 3]
    }
    
    print(f"\nAdding expertise tags to tutor {tid}...")
    response = requests.post(f"{BASE_URL}/tutors/{tid}/tags", json=tags_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tags added successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Add tags failed!")
        print(f"Error: {response.json()}")

def test_approve_tutor(tid):
    print("\n" + "="*50)
    print("=== Testing Approve Tutor ===")
    print("="*50)
    
    approval_data = {
        "status": "approved"
    }
    
    print(f"\nApproving tutor {tid}...")
    response = requests.put(f"{BASE_URL}/tutors/{tid}/verification", json=approval_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tutor approved successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Approve tutor failed!")
        print(f"Error: {response.json()}")

def test_get_tutor(tid):
    print("\n" + "="*50)
    print("=== Testing Get Tutor ===")
    print("="*50)
    
    print(f"\nGetting tutor with tid={tid}")
    response = requests.get(f"{BASE_URL}/tutors/{tid}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Tutor retrieved successfully!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Get tutor failed!")
        print(f"Error: {response.json()}")

def verify_in_database():
    print("\n" + "="*50)
    print("=== SQL Verification Queries ===")
    print("="*50)
    
    print("\n-- Check user was created (password should be hashed):")
    print("SELECT uid, firstName, lastName, email, LEFT(password, 20) as password_hash FROM User WHERE email = 'demo.tester@test.com';")
    
    print("\n-- Check tutor was created:")
    print("SELECT t.*, u.email FROM Tutor t JOIN User u ON t.uid = u.uid WHERE u.email = 'demo.tester@test.com';")
    
    print("\n-- Check tutor with tags and verification status:")
    query = """SELECT 
    t.tid, 
    CONCAT(u.firstName, ' ', u.lastName) as name,
    u.email,
    t.rating,
    t.status,
    t.verificationStatus, 
    GROUP_CONCAT(tg.tags ORDER BY tg.tags) as expertise
FROM Tutor t
JOIN User u ON t.uid = u.uid
LEFT JOIN TutorTags tt ON t.tid = tt.tid
LEFT JOIN Tags tg ON tt.tagsID = tg.tagsID
WHERE u.email = 'demo.tester@test.com'
GROUP BY t.tid;"""
    print(query)
    
    print("\n-- Verify password is hashed (should start with '$2b$'):")
    print("SELECT LEFT(password, 7) as hash_prefix FROM User WHERE email = 'demo.tester@test.com';")

def main():
    # Run all tests
    print("\n" + "="*50)
    print("   GatorGuides User & Tutor Testing")
    print("="*50)
    print("\nMake sure FastAPI is running on http://localhost:8001")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Test user registration
        uid = test_registration()
        
        if not uid:
            print("\n✗ Registration failed. Stopping tests.")
            return
        
        # Test login with correct password
        test_login("demo.tester@test.com", "securepass456")
        
        # Test login with wrong password
        test_wrong_password("demo.tester@test.com")
        
        # Test get user
        test_get_user(uid)
        
        # Test creating tutor
        tid = test_create_tutor(uid)
        
        if not tid:
            print("\n✗ Tutor creation failed. Stopping tests.")
            return
        
        # Test adding expertise tags
        test_add_tags(tid)
        
        # Test getting tutor info
        test_get_tutor(tid)
        
        # Test approving tutor
        test_approve_tutor(tid)
        
        # Get tutor info again to see approval
        test_get_tutor(tid)
        
        # Show SQL verification queries
        verify_in_database()
        
        print("\n" + "="*50)
        print("   All Tests Complete!")
        print("="*50)
        print("\nRun the SQL queries above to verify data in your database.")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to FastAPI server.")
        print("Make sure the server is running with: make api-dev")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")

if __name__ == "__main__":
    main()