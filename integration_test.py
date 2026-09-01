#!/usr/bin/env python3
"""
End-to-end integration test for CashLy
Tests the full workflow: register, login, create budget/expenses, dashboard
"""

import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_workflow():
    """Test complete user workflow"""
    
    # Step 1: Register a new user
    print("\n1. Testing registration...")
    register_resp = client.post(
        '/api/auth/register',
        json={
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePass123!',
        }
    )
    assert register_resp.status_code == 200, f"Registration failed: {register_resp.text}"
    register_data = register_resp.json()
    user_id = register_data['user']['id']
    token = register_data['token']
    print(f"   ✓ User registered: {user_id}")
    print(f"   ✓ Token received: {token[:20]}...")
    
    # Step 2: Login with the same credentials
    print("\n2. Testing login...")
    login_resp = client.post(
        '/api/auth/login',
        json={
            'email': 'john.doe@example.com',
            'password': 'SecurePass123!',
        }
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    assert login_data['user']['id'] == user_id
    print(f"   ✓ Login successful")
    
    # Step 3: Create budget
    print("\n3. Creating budget...")
    budget_resp = client.post(
        '/api/budgets',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'category': 'Food',
            'limit': 5000,
            'month': '2026-09',
        }
    )
    assert budget_resp.status_code == 200, f"Budget creation failed: {budget_resp.text}"
    print(f"   ✓ Budget created: Food - ₹5000")
    
    # Step 4: Create expenses
    print("\n4. Creating expenses...")
    expenses = [
        {'title': 'Groceries', 'category': 'Food', 'amount': 1200, 'date': '2026-09-01'},
        {'title': 'Restaurant', 'category': 'Food', 'amount': 800, 'date': '2026-09-02'},
        {'title': 'Uber Ride', 'category': 'Transport', 'amount': 250, 'date': '2026-09-01'},
    ]
    
    for exp in expenses:
        resp = client.post(
            '/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={**exp, 'source': 'manual'},
        )
        assert resp.status_code == 200, f"Expense creation failed: {resp.text}"
        print(f"   ✓ {exp['title']}: ₹{exp['amount']} ({exp['category']})")
    
    # Step 5: Create goal
    print("\n5. Creating goal...")
    goal_resp = client.post(
        '/api/goals',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'Emergency Fund',
            'target_amount': 100000,
            'deadline': '2027-12-31',
        }
    )
    assert goal_resp.status_code == 200, f"Goal creation failed: {goal_resp.text}"
    print(f"   ✓ Goal created: Emergency Fund - ₹100000")
    
    # Step 6: Get dashboard
    print("\n6. Fetching dashboard...")
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert dashboard_resp.status_code == 200, f"Dashboard fetch failed: {dashboard_resp.text}"
    dashboard_data = dashboard_resp.json()
    
    # Verify dashboard structure
    assert 'summary' in dashboard_data
    assert 'expenses' in dashboard_data
    assert 'budgets' in dashboard_data
    assert 'goals' in dashboard_data
    assert 'insights' in dashboard_data
    
    summary = dashboard_data['summary']
    print(f"   ✓ Summary:")
    print(f"     - Total Spending: ₹{summary['totalSpending']}")
    print(f"     - Average Daily: ₹{summary['averageDaily']}")
    print(f"     - Financial Health: {summary['financialHealthScore']}/100")
    
    # Verify expenses are there
    expenses_list = dashboard_data['expenses']
    assert len(expenses_list) >= 3, f"Expected 3+ expenses, got {len(expenses_list)}"
    print(f"   ✓ Expenses: {len(expenses_list)} found")
    
    # Verify budgets show spending
    budgets_list = dashboard_data['budgets']
    assert len(budgets_list) > 0, "No budgets found"
    food_budget = next((b for b in budgets_list if b['category'] == 'Food'), None)
    assert food_budget is not None, "Food budget not found"
    assert food_budget['spent'] > 0, "Budget should show spending"
    print(f"   ✓ Budget usage: Food {food_budget['spent']}/₹{food_budget['limit']}")
    
    # Verify goals
    goals_list = dashboard_data['goals']
    assert len(goals_list) > 0, "No goals found"
    print(f"   ✓ Goals: {len(goals_list)} found")
    
    # Verify insights generated
    insights_list = dashboard_data['insights']
    print(f"   ✓ Insights: {len(insights_list)} generated")
    if insights_list:
        for insight in insights_list[:2]:
            print(f"     - {insight['title']}")
    
    # Step 7: Get assistant advice
    print("\n7. Getting AI assistant advice...")
    assistant_resp = client.get(
        '/api/assistant',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert assistant_resp.status_code == 200, f"Assistant fetch failed: {assistant_resp.text}"
    assistant_data = assistant_resp.json()
    print(f"   ✓ Advice: {assistant_data['advice']}")
    print(f"   ✓ Recommendations: {len(assistant_data['recommendations'])} provided")
    
    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED")
    print("="*50 + "\n")

if __name__ == '__main__':
    try:
        test_full_workflow()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
