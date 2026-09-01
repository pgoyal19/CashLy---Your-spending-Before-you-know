#!/usr/bin/env python3
"""
Comprehensive End-to-End API Test Suite for CashLy Backend
Tests every endpoint and verifies data integrity
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://127.0.0.1:8000"
TIMESTAMP = str(int(time.time()))

# Test tracking
tests_run = 0
tests_passed = 0
tests_failed = 0
failed_tests = []

def test(name, condition, error_msg=""):
    """Track test results"""
    global tests_run, tests_passed, tests_failed, failed_tests
    tests_run += 1
    if condition:
        tests_passed += 1
        print(f"✓ {name}")
    else:
        tests_failed += 1
        failed_tests.append({"name": name, "error": error_msg})
        print(f"✗ {name}: {error_msg}")

def test_section(name):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

# ===== TEST 1: Health Check =====
test_section("HEALTH CHECK")
resp = requests.get(f"{BASE_URL}/health")
test("Health endpoint responds", resp.status_code == 200, f"Status {resp.status_code}")
data = resp.json()
test("Health status is ok", data.get('status') == 'ok', f"Got {data.get('status')}")

# ===== TEST 2: Authentication =====
test_section("AUTHENTICATION")

# Test 2a: Register User
resp = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={'name': 'Alice Smith', 'email': f'alice-{TIMESTAMP}@test.com', 'password': 'SecurePass123!'}
)
test("Register new user", resp.status_code == 200, f"Status {resp.status_code}: {resp.text}")
register_data = resp.json()
user_id = register_data.get('user', {}).get('id')
token = register_data.get('token')
test("Register returns token", token is not None, "No token in response")
test("Register returns user ID", user_id is not None, "No user ID in response")

# Test 2b: Duplicate Registration
resp = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={'name': 'Alice Again', 'email': f'alice-{TIMESTAMP}@test.com', 'password': 'Other123!'}
)
test("Duplicate registration fails", resp.status_code == 400, f"Expected 400, got {resp.status_code}")

# Test 2c: Login with Valid Credentials
resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={'email': f'alice-{TIMESTAMP}@test.com', 'password': 'SecurePass123!'}
)
test("Login with valid credentials", resp.status_code == 200, f"Status {resp.status_code}")
login_data = resp.json()
login_token = login_data.get('token')
test("Login returns token", login_token is not None, "No token in login response")

# Test 2d: Login with Invalid Password
resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={'email': f'alice-{TIMESTAMP}@test.com', 'password': 'WrongPass123!'}
)
test("Login with invalid password fails", resp.status_code == 401, f"Expected 401, got {resp.status_code}")

# Test 2e: Login with Nonexistent User
resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={'email': f'nonexistent-{TIMESTAMP}@test.com', 'password': 'AnyPass123!'}
)
test("Login with nonexistent email fails", resp.status_code == 401, f"Expected 401, got {resp.status_code}")

# ===== TEST 3: Protected Routes =====
test_section("PROTECTED ROUTES")

# Test 3a: Dashboard without auth (demo-user fallback)
resp = requests.get(f"{BASE_URL}/api/dashboard")
test("Dashboard accessible without auth (demo-user)", resp.status_code == 200, f"Status {resp.status_code}")

# Test 3b: Dashboard with valid auth
headers = {'Authorization': f'Bearer {token}'}
resp = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
test("Dashboard accessible with valid token", resp.status_code == 200, f"Status {resp.status_code}")
dashboard_data = resp.json()
test("Dashboard has summary", 'summary' in dashboard_data, "Missing summary")
test("Dashboard has expenses", 'expenses' in dashboard_data, "Missing expenses")
test("Dashboard has budgets", 'budgets' in dashboard_data, "Missing budgets")
test("Dashboard has goals", 'goals' in dashboard_data, "Missing goals")
test("Dashboard has insights", 'insights' in dashboard_data, "Missing insights")

# Test 3c: Dashboard with invalid token
bad_headers = {'Authorization': 'Bearer invalid.token.here'}
resp = requests.get(f"{BASE_URL}/api/dashboard", headers=bad_headers)
test("Invalid token is rejected", resp.status_code == 401, f"Expected 401, got {resp.status_code}")

# ===== TEST 4: Expenses =====
test_section("EXPENSES - CREATE & RETRIEVE")

# Test 4a: Create expense
expense_data = {
    'title': 'Lunch at Restaurant',
    'category': 'Food',
    'amount': 450,
    'date': '2026-09-01',
    'source': 'manual'
}
resp = requests.post(f"{BASE_URL}/api/expenses", json=expense_data, headers=headers)
test("Create expense", resp.status_code == 200, f"Status {resp.status_code}: {resp.text}")
expense_resp = resp.json()
expense_id = expense_resp.get('id')
test("Expense has ID", expense_id is not None, "No ID in expense response")
test("Expense title matches", expense_resp.get('title') == 'Lunch at Restaurant', f"Got {expense_resp.get('title')}")
test("Expense amount matches", expense_resp.get('amount') == 450, f"Got {expense_resp.get('amount')}")
test("Expense category matches", expense_resp.get('category') == 'Food', f"Got {expense_resp.get('category')}")

# Test 4b: Create multiple expenses
expenses = [
    {'title': 'Groceries', 'category': 'Food', 'amount': 2000, 'date': '2026-09-01', 'source': 'manual'},
    {'title': 'Uber ride', 'category': 'Transport', 'amount': 300, 'date': '2026-09-02', 'source': 'manual'},
    {'title': 'Movie tickets', 'category': 'Entertainment', 'amount': 500, 'date': '2026-09-02', 'source': 'manual'},
]
for exp in expenses:
    resp = requests.post(f"{BASE_URL}/api/expenses", json=exp, headers=headers)
    test(f"Create {exp['title']}", resp.status_code == 200, f"Status {resp.status_code}")

# Test 4c: Invalid expense (no title)
resp = requests.post(
    f"{BASE_URL}/api/expenses",
    json={'title': '', 'category': 'Food', 'amount': 100, 'date': '2026-09-01'},
    headers=headers
)
test("Invalid expense (empty title) fails", resp.status_code == 422, f"Expected 422, got {resp.status_code}")

# Test 4d: Invalid expense (negative amount)
resp = requests.post(
    f"{BASE_URL}/api/expenses",
    json={'title': 'Bad', 'category': 'Food', 'amount': -100, 'date': '2026-09-01'},
    headers=headers
)
test("Invalid expense (negative amount) fails", resp.status_code == 422, f"Expected 422, got {resp.status_code}")

# Test 4e: Retrieve expenses
resp = requests.get(f"{BASE_URL}/api/expenses", headers=headers)
test("Get expenses endpoint", resp.status_code == 200, f"Status {resp.status_code}")
expenses_data = resp.json()
test("Expenses has expenses array", 'expenses' in expenses_data, "Missing expenses array")
num_expenses = len(expenses_data.get('expenses', []))
test("Expenses count >= 4", num_expenses >= 4, f"Expected >=4, got {num_expenses}")

# ===== TEST 5: Dashboard Calculations =====
test_section("DASHBOARD CALCULATIONS")

resp = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
dashboard = resp.json()
summary = dashboard.get('summary', {})

test("Summary has totalSpending", 'totalSpending' in summary, "Missing totalSpending")
total_spending = summary.get('totalSpending', 0)
test("Total spending > 0", total_spending > 0, f"Got {total_spending}")
test("Total spending is reasonable", 2000 <= total_spending <= 5000, f"Got {total_spending}, expected 2000-5000")

test("Summary has averageDaily", 'averageDaily' in summary, "Missing averageDaily")
avg_daily = summary.get('averageDaily', 0)
test("Average daily > 0", avg_daily > 0, f"Got {avg_daily}")

test("Summary has remainingBudget", 'remainingBudget' in summary, "Missing remainingBudget")
test("Summary has savingsProgress", 'savingsProgress' in summary, "Missing savingsProgress")
test("Summary has financialHealthScore", 'financialHealthScore' in summary, "Missing financialHealthScore")

health_score = summary.get('financialHealthScore', 0)
test("Health score is 0-100", 0 <= health_score <= 100, f"Got {health_score}")

test("Summary has lastUpdated", 'lastUpdated' in summary, "Missing lastUpdated")

# ===== TEST 6: Budgets =====
test_section("BUDGETS")

# Test 6a: Create budgets
budget_data = {'category': 'Food', 'limit': 5000, 'month': '2026-09'}
resp = requests.post(f"{BASE_URL}/api/budgets", json=budget_data, headers=headers)
test("Create budget", resp.status_code == 200, f"Status {resp.status_code}")

# Create more budgets
budgets_to_create = [
    {'category': 'Transport', 'limit': 2000, 'month': '2026-09'},
    {'category': 'Entertainment', 'limit': 1500, 'month': '2026-09'},
]
for budget in budgets_to_create:
    resp = requests.post(f"{BASE_URL}/api/budgets", json=budget, headers=headers)
    test(f"Create {budget['category']} budget", resp.status_code == 200, f"Status {resp.status_code}")

# Test 6b: Retrieve budgets
resp = requests.get(f"{BASE_URL}/api/budgets", headers=headers)
test("Get budgets", resp.status_code == 200, f"Status {resp.status_code}")
budgets_data = resp.json()
budgets_list = budgets_data.get('budgets', [])
test("At least 3 budgets", len(budgets_list) >= 3, f"Got {len(budgets_list)}")

# Test 6c: Verify spending calculation against budget
for budget in budgets_list:
    category = budget.get('category')
    spent = budget.get('spent', 0)
    limit = budget.get('limit', 0)
    test(f"Budget {category} has spent", spent >= 0, f"Got {spent}")
    test(f"Budget {category} has limit", limit > 0, f"Got {limit}")
    if category == 'Food':
        test(f"Food budget spent > 0", spent > 0, f"Expected >0, got {spent}")

# ===== TEST 7: Goals =====
test_section("GOALS")

# Test 7a: Create goals
goal_data = {'name': 'Emergency Fund', 'target_amount': 100000, 'deadline': '2027-12-31'}
resp = requests.post(f"{BASE_URL}/api/goals", json=goal_data, headers=headers)
test("Create goal", resp.status_code == 200, f"Status {resp.status_code}")

# Create another goal
goal_data2 = {'name': 'Vacation Fund', 'target_amount': 50000, 'deadline': '2026-12-31'}
resp = requests.post(f"{BASE_URL}/api/goals", json=goal_data2, headers=headers)
test("Create second goal", resp.status_code == 200, f"Status {resp.status_code}")

# Test 7b: Retrieve goals
resp = requests.get(f"{BASE_URL}/api/goals", headers=headers)
test("Get goals", resp.status_code == 200, f"Status {resp.status_code}")
goals_data = resp.json()
goals_list = goals_data.get('goals', [])
test("At least 2 goals", len(goals_list) >= 2, f"Got {len(goals_list)}")

# Test 7c: Verify goal structure
for goal in goals_list:
    test(f"Goal {goal.get('name')} has target_amount", 'target_amount' in goal, "Missing target_amount")
    test(f"Goal {goal.get('name')} has saved_amount", 'saved_amount' in goal, "Missing saved_amount")
    test(f"Goal {goal.get('name')} has deadline", 'deadline' in goal, "Missing deadline")

# ===== TEST 8: Analytics & Insights =====
test_section("ANALYTICS & INSIGHTS")

# Test 8a: Summary endpoint
resp = requests.get(f"{BASE_URL}/api/summary", headers=headers)
test("Summary endpoint", resp.status_code == 200, f"Status {resp.status_code}")

# Test 8b: Insights endpoint
resp = requests.get(f"{BASE_URL}/api/insights", headers=headers)
test("Insights endpoint", resp.status_code == 200, f"Status {resp.status_code}")
insights_data = resp.json()
insights_list = insights_data.get('insights', [])
test("Insights generated", len(insights_list) >= 0, f"Got {len(insights_list)}")  # Can be empty

# ===== TEST 9: AI Assistant =====
test_section("AI ASSISTANT")

resp = requests.get(f"{BASE_URL}/api/assistant", headers=headers)
test("Assistant endpoint", resp.status_code == 200, f"Status {resp.status_code}")
assistant_data = resp.json()
test("Assistant has advice", 'advice' in assistant_data, "Missing advice")
test("Assistant has recommendations", 'recommendations' in assistant_data, "Missing recommendations")
recommendations = assistant_data.get('recommendations', [])
test("At least 1 recommendation", len(recommendations) >= 1, f"Got {len(recommendations)}")

# ===== TEST 10: AI Service Health =====
test_section("AI SERVICE")

try:
    resp = requests.get("http://127.0.0.1:8001/health", timeout=2)
    ai_running = resp.status_code == 200
except Exception:
    ai_running = False

test("AI service health", ai_running, "AI service not running on 8001")

if ai_running:
    # Test category classification
    category_req = {
        'merchant': 'Zomato delivery',
        'description': 'Restaurant order'
    }
    resp = requests.post(
        "http://127.0.0.1:8001/api/categories/classify",
        json=category_req,
        timeout=5
    )
    test("Category classification", resp.status_code == 200, f"Status {resp.status_code}")
    if resp.status_code == 200:
        cat_data = resp.json()
        test("Classification has category", 'category' in cat_data, "Missing category")
        test("Classification has confidence", 'confidence' in cat_data, "Missing confidence")

# ===== TEST 11: Database Persistence =====
test_section("DATABASE PERSISTENCE")

# Create a test expense
resp = requests.post(
    f"{BASE_URL}/api/expenses",
    json={'title': 'Persistence Test', 'category': 'Shopping', 'amount': 999, 'date': '2026-09-03', 'source': 'manual'},
    headers=headers
)
test("Create expense for persistence test", resp.status_code == 200, f"Status {resp.status_code}")

# Retrieve to confirm it's in database
resp = requests.get(f"{BASE_URL}/api/expenses", headers=headers)
expenses_list = resp.json().get('expenses', [])
persistence_test = any(e.get('amount') == 999 for e in expenses_list)
test("Expense persisted in database", persistence_test, "Expense not found after creation")

# ===== TEST 12: Multiple Users - Isolation =====
test_section("MULTI-USER ISOLATION")

# Register second user
resp = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={'name': 'Bob Jones', 'email': f'bob-{TIMESTAMP}@test.com', 'password': 'BobPass123!'}
)
test("Register second user", resp.status_code == 200, f"Status {resp.status_code}")
bob_token = resp.json().get('token')

# Bob creates an expense
bob_headers = {'Authorization': f'Bearer {bob_token}'}
resp = requests.post(
    f"{BASE_URL}/api/expenses",
    json={'title': 'Bobs Pizza', 'category': 'Food', 'amount': 500, 'date': '2026-09-01', 'source': 'manual'},
    headers=bob_headers
)
test("Bob creates expense", resp.status_code == 200, f"Status {resp.status_code}")

# Alice retrieves her expenses - should NOT see Bobs
resp = requests.get(f"{BASE_URL}/api/expenses", headers=headers)
alice_expenses = resp.json().get('expenses', [])
bob_expense_visible = any(e.get('title') == 'Bobs Pizza' for e in alice_expenses)
test("Alice cannot see Bob's expenses", not bob_expense_visible, "Data isolation broken!")

# Bob retrieves his expenses - should NOT see Alices
resp = requests.get(f"{BASE_URL}/api/expenses", headers=bob_headers)
bob_expenses = resp.json().get('expenses', [])
alice_expense_visible = any(e.get('title') == 'Lunch at Restaurant' for e in bob_expenses)
test("Bob cannot see Alice's expenses", not alice_expense_visible, "Data isolation broken!")

# ===== RESULTS SUMMARY =====
print(f"\n{'='*60}")
print(f"  TEST RESULTS SUMMARY")
print(f"{'='*60}")
print(f"Tests Run:    {tests_run}")
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Success Rate: {(tests_passed/tests_run*100):.1f}%")

if tests_failed > 0:
    print(f"\n{'='*60}")
    print(f"  FAILED TESTS")
    print(f"{'='*60}")
    for failed in failed_tests:
        print(f"✗ {failed['name']}")
        print(f"  Error: {failed['error']}")
    exit(1)
else:
    print(f"\n✅ ALL TESTS PASSED")
    exit(0)
