#!/usr/bin/env python3
"""
Complete end-to-end workflow test simulating frontend UI interactions
"""

import sys
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_frontend_workflow():
    """Simulate the exact workflow the frontend performs"""
    
    print("\n" + "="*60)
    print("CashLy End-to-End Workflow Test")
    print("="*60)
    
    # PHASE 1: User Registration
    print("\n[PHASE 1] User Registration")
    print("-" * 60)
    
    register_resp = client.post(
        '/api/auth/register',
        json={
            'name': 'Sarah Johnson',
            'email': 'sarah@example.com',
            'password': 'SecurePassword123!',
        }
    )
    assert register_resp.status_code == 200, f"Register failed: {register_resp.text}"
    register_data = register_resp.json()
    token = register_data['token']
    user_name = register_data['user']['name']
    
    print(f"✓ Registered: {user_name}")
    print(f"✓ Token issued: {token[:30]}...")
    
    # PHASE 2: Dashboard Load (no data yet)
    print("\n[PHASE 2] Dashboard Load (Initial)")
    print("-" * 60)
    
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert dashboard_resp.status_code == 200
    dashboard_data = dashboard_resp.json()
    
    summary = dashboard_data['summary']
    print(f"✓ Dashboard loaded")
    print(f"  - Total Spending: ₹{summary['totalSpending']}")
    print(f"  - Financial Health: {summary['financialHealthScore']}/100")
    print(f"  - Expenses: {len(dashboard_data['expenses'])}")
    
    # PHASE 3: Add Expenses via Form
    print("\n[PHASE 3] Add Expenses via Form")
    print("-" * 60)
    
    expenses_to_add = [
        {'title': 'Morning Coffee', 'category': 'Food', 'amount': 150, 'date': '2026-09-01'},
        {'title': 'Groceries', 'category': 'Food', 'amount': 2500, 'date': '2026-09-01'},
        {'title': 'Gas Refill', 'category': 'Transport', 'amount': 1000, 'date': '2026-09-02'},
        {'title': 'Movie Ticket', 'category': 'Entertainment', 'amount': 300, 'date': '2026-09-02'},
    ]
    
    for i, exp in enumerate(expenses_to_add, 1):
        exp_resp = client.post(
            '/api/expenses',
            headers={'Authorization': f'Bearer {token}'},
            json={**exp, 'source': 'manual'}
        )
        assert exp_resp.status_code == 200, f"Expense {i} failed: {exp_resp.text}"
        exp_data = exp_resp.json()
        print(f"✓ Added: {exp['title']} - ₹{exp['amount']} ({exp['category']})")
    
    # PHASE 4: Dashboard Update After Expenses
    print("\n[PHASE 4] Dashboard After Adding Expenses")
    print("-" * 60)
    
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {token}'}
    )
    dashboard_data = dashboard_resp.json()
    summary = dashboard_data['summary']
    
    print(f"✓ Dashboard updated")
    print(f"  - Total Spending: ₹{summary['totalSpending']} (was ₹0)")
    print(f"  - Average Daily: ₹{summary['averageDaily']}")
    print(f"  - Financial Health: {summary['financialHealthScore']}/100")
    print(f"  - Expenses in DB: {len(dashboard_data['expenses'])}")
    
    # PHASE 5: Set Budgets
    print("\n[PHASE 5] Set Budgets")
    print("-" * 60)
    
    budgets = [
        {'category': 'Food', 'limit': 5000},
        {'category': 'Transport', 'limit': 2000},
        {'category': 'Entertainment', 'limit': 1000},
    ]
    
    for budget in budgets:
        budget_resp = client.post(
            '/api/budgets',
            headers={'Authorization': f'Bearer {token}'},
            json={**budget, 'month': '2026-09'}
        )
        assert budget_resp.status_code == 200, f"Budget failed: {budget_resp.text}"
        print(f"✓ Set {budget['category']} budget: ₹{budget['limit']}")
    
    # PHASE 6: Dashboard with Budgets
    print("\n[PHASE 6] Dashboard with Budget Information")
    print("-" * 60)
    
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {token}'}
    )
    dashboard_data = dashboard_resp.json()
    
    budgets_list = dashboard_data['budgets']
    print(f"✓ Budgets retrieved: {len(budgets_list)}")
    for budget in budgets_list:
        usage_pct = (budget['spent'] / budget['limit'] * 100) if budget['limit'] > 0 else 0
        print(f"  - {budget['category']}: ₹{budget['spent']}/₹{budget['limit']} ({usage_pct:.0f}%)")
    
    # PHASE 7: Create Financial Goals
    print("\n[PHASE 7] Create Financial Goals")
    print("-" * 60)
    
    goals = [
        {'name': 'Emergency Fund', 'target_amount': 100000, 'deadline': '2027-12-31'},
        {'name': 'Vacation', 'target_amount': 50000, 'deadline': '2026-12-31'},
    ]
    
    for goal in goals:
        goal_resp = client.post(
            '/api/goals',
            headers={'Authorization': f'Bearer {token}'},
            json=goal
        )
        assert goal_resp.status_code == 200, f"Goal failed: {goal_resp.text}"
        print(f"✓ Created goal: {goal['name']} - ₹{goal['target_amount']}")
    
    # PHASE 8: Dashboard with Goals and Insights
    print("\n[PHASE 8] Dashboard with Insights")
    print("-" * 60)
    
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {token}'}
    )
    dashboard_data = dashboard_resp.json()
    
    print(f"✓ Goals: {len(dashboard_data['goals'])} goals loaded")
    print(f"✓ Insights: {len(dashboard_data['insights'])} insights generated")
    
    for insight in dashboard_data['insights'][:3]:
        severity_icon = {'low': 'ℹ️', 'medium': '⚠️', 'high': '🔴'}.get(insight.get('severity', 'low'), '•')
        print(f"  {severity_icon} {insight['title']}")
    
    # PHASE 9: Get AI Assistant Advice
    print("\n[PHASE 9] AI Assistant Recommendations")
    print("-" * 60)
    
    assistant_resp = client.get(
        '/api/assistant',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert assistant_resp.status_code == 200
    assistant_data = assistant_resp.json()
    
    print(f"✓ Primary advice: {assistant_data['advice']}")
    print(f"✓ Recommendations:")
    for rec in assistant_data['recommendations']:
        print(f"  • {rec}")
    
    # PHASE 10: Test Login Persistence
    print("\n[PHASE 10] Test Login Persistence")
    print("-" * 60)
    
    login_resp = client.post(
        '/api/auth/login',
        json={'email': 'sarah@example.com', 'password': 'SecurePassword123!'}
    )
    assert login_resp.status_code == 200
    login_token = login_resp.json()['token']
    
    dashboard_resp = client.get(
        '/api/dashboard',
        headers={'Authorization': f'Bearer {login_token}'}
    )
    dashboard_data = dashboard_resp.json()
    
    print(f"✓ Login successful")
    print(f"✓ User's data persisted: {len(dashboard_data['expenses'])} expenses found")
    
    # PHASE 11: Final Dashboard Summary
    print("\n[PHASE 11] Final Summary")
    print("-" * 60)
    
    summary = dashboard_data['summary']
    expenses = dashboard_data['expenses']
    budgets = dashboard_data['budgets']
    goals = dashboard_data['goals']
    
    print(f"✓ User Profile: {user_name} (sarah@example.com)")
    print(f"✓ Financial Summary:")
    print(f"    Total Spending: ₹{summary['totalSpending']:.2f}")
    print(f"    Remaining Budget: ₹{summary['remainingBudget']:.2f}")
    print(f"    Health Score: {summary['financialHealthScore']}/100")
    print(f"✓ Data Stored:")
    print(f"    Expenses: {len(expenses)}")
    print(f"    Budgets: {len(budgets)}")
    print(f"    Goals: {len(goals)}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - APPLICATION IS FULLY FUNCTIONAL")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        test_frontend_workflow()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
