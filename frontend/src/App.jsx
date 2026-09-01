import { useEffect, useState } from 'react'
import './App.css'

const emptyExpense = {
  title: '',
  category: 'Food',
  amount: '',
  date: new Date().toISOString().slice(0, 10),
  source: 'manual',
}

const emptyRegister = {
  name: '',
  email: '',
  password: '',
}

const emptyLogin = {
  email: '',
  password: '',
}

const emptyBudget = {
  category: 'Food',
  limit: '',
}

const emptyGoal = {
  name: '',
  target_amount: '',
  deadline: new Date().toISOString().slice(0, 10),
}

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [dashboardError, setDashboardError] = useState(null)
  const [expenseForm, setExpenseForm] = useState(emptyExpense)
  const [registerForm, setRegisterForm] = useState(emptyRegister)
  const [loginForm, setLoginForm] = useState(emptyLogin)
  const [budgetForm, setBudgetForm] = useState(emptyBudget)
  const [goalForm, setGoalForm] = useState(emptyGoal)
  const [message, setMessage] = useState('')
  const [token, setToken] = useState(() => localStorage.getItem('authToken') || null)
  const [isLoginVisible, setIsLoginVisible] = useState(false)
  const [isBudgetVisible, setIsBudgetVisible] = useState(false)
  const [isGoalVisible, setIsGoalVisible] = useState(false)

  useEffect(() => {
    if (!token) {
      setDashboard(null)
      return
    }

    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
    const headers = { 'Authorization': `Bearer ${token}` }

    fetch(`${apiBase}/api/dashboard`, { headers })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setDashboard(data)
        setDashboardError(null)
      })
      .catch((err) => {
        console.error('Dashboard fetch failed:', err)
        setDashboardError(`Failed to load dashboard: ${err.message}`)
        setDashboard(null)
      })
  }, [token])

  const summary = dashboard?.summary
  const expenses = dashboard?.expenses ?? []
  const budgets = dashboard?.budgets ?? []
  const goals = dashboard?.goals ?? []
  const insights = dashboard?.insights ?? []

  const handleRegister = async (event) => {
    event.preventDefault()
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

    try {
      const response = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Registration failed')
      localStorage.setItem('authToken', data.token)
      setToken(data.token)
      setMessage(`Welcome ${data.user.name}! Your CashLy account is ready.`)
      setRegisterForm(emptyRegister)
    } catch (error) {
      setMessage(`❌ Registration failed: ${error.message}`)
    }
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

    try {
      const response = await fetch(`${apiBase}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Login failed')
      localStorage.setItem('authToken', data.token)
      setToken(data.token)
      setMessage(`Welcome back, ${data.user.name}!`)
      setLoginForm(emptyLogin)
      setIsLoginVisible(false)
    } catch (error) {
      setMessage(`❌ Login failed: ${error.message}`)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('authToken')
    setToken(null)
    setDashboard(null)
    setMessage('You have been logged out.')
    setIsLoginVisible(false)
    setIsBudgetVisible(false)
    setIsGoalVisible(false)
  }

  const handleExpenseAdd = async (event) => {
    event.preventDefault()
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    }

    try {
      const response = await fetch(`${apiBase}/api/expenses`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...expenseForm,
          amount: Number(expenseForm.amount),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Expense add failed')
      setMessage(`✅ Expense added: ${data.title} for ₹${data.amount}`)
      setExpenseForm(emptyExpense)
      
      // Refresh dashboard
      const dashboardResponse = await fetch(`${apiBase}/api/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json()
        setDashboard(dashboardData)
      }
    } catch (error) {
      setMessage(`❌ Failed to add expense: ${error.message}`)
    }
  }

  const handleBudgetAdd = async (event) => {
    event.preventDefault()
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    }

    try {
      const response = await fetch(`${apiBase}/api/budgets`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          category: budgetForm.category,
          limit: Number(budgetForm.limit),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Budget creation failed')
      setMessage(`✅ Budget set for ${budgetForm.category}: ₹${budgetForm.limit}`)
      setBudgetForm(emptyBudget)
      setIsBudgetVisible(false)
      
      // Refresh dashboard
      const dashboardResponse = await fetch(`${apiBase}/api/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json()
        setDashboard(dashboardData)
      }
    } catch (error) {
      setMessage(`❌ Failed to create budget: ${error.message}`)
    }
  }

  const handleGoalAdd = async (event) => {
    event.preventDefault()
    const apiBase = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    }

    try {
      const response = await fetch(`${apiBase}/api/goals`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          name: goalForm.name,
          target_amount: Number(goalForm.target_amount),
          deadline: goalForm.deadline,
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Goal creation failed')
      setMessage(`✅ Goal created: ${goalForm.name}`)
      setGoalForm(emptyGoal)
      setIsGoalVisible(false)
      
      // Refresh dashboard
      const dashboardResponse = await fetch(`${apiBase}/api/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json()
        setDashboard(dashboardData)
      }
    } catch (error) {
      setMessage(`❌ Failed to create goal: ${error.message}`)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">C</span>
          <span>CashLy</span>
        </div>
        <nav>
          <a href="#features">Features</a>
          <a href="#insights">Insights</a>
          <a href="#dashboard">Dashboard</a>
          {token && <button type="button" onClick={handleLogout} className="logout-btn">Logout</button>}
        </nav>
      </header>

      <main className="hero">
        <section className="hero-copy">
          <p className="eyebrow">AI-driven personal finance</p>
          <h1>
            Your Spending <span>Before You Know</span>
          </h1>
          <p className="subtitle">Track smarter. Predict better. Spend with confidence.</p>
          <div className="cta-row">
            <button type="button" onClick={() => {
              document.querySelector('.forms-grid')?.scrollIntoView({ behavior: 'smooth' })
            }}>Get Started</button>
            {!token && <button type="button" className="secondary" onClick={() => setIsLoginVisible(!isLoginVisible)}>
              Login
            </button>}
          </div>
        </section>

        <aside className="dashboard-card" id="dashboard">
          {!token ? (
            <p>Sign up or login to view your dashboard.</p>
          ) : dashboardError ? (
            <p className="error-message">⚠️ {dashboardError}</p>
          ) : dashboard?.summary ? (
            <>
              <div className="stat-card">
                <label>Total spending this month</label>
                <strong>₹{dashboard.summary.totalSpending.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card muted">
                <label>Average daily spending</label>
                <strong>₹{dashboard.summary.averageDaily.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card success">
                <label>Remaining budget</label>
                <strong>₹{dashboard.summary.remainingBudget.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card primary">
                <label>Financial health score</label>
                <strong>{dashboard.summary.financialHealthScore} / 100</strong>
              </div>
            </>
          ) : (
            <p>Loading your overview...</p>
          )}
        </aside>
      </main>

      <section id="features" className="feature-grid">
        <article>
          <h3>Smart expense tracking</h3>
          <p>Capture spending manually or through OCR and keep every transaction visible.</p>
        </article>
        <article>
          <h3>Predictive analytics</h3>
          <p>Forecast short-term spending and monitor overspending before it happens.</p>
        </article>
        <article>
          <h3>Goal planning</h3>
          <p>Track your savings goals and estimate monthly contributions needed to reach them.</p>
        </article>
        <article>
          <h3>CashLy AI</h3>
          <p>Ask the assistant for actual, data-backed financial guidance and recommendations.</p>
        </article>
      </section>

      <section className="forms-grid">
        {!token && (
          <>
            <form className="panel" onSubmit={handleRegister}>
              <h2>Create account</h2>
              <label>
                Name
                <input
                  value={registerForm.name}
                  onChange={(event) =>
                    setRegisterForm((prev) => ({ ...prev, name: event.target.value }))
                  }
                  placeholder="Ava Patel"
                />
              </label>
              <label>
                Email
                <input
                  type="email"
                  value={registerForm.email}
                  onChange={(event) =>
                    setRegisterForm((prev) => ({ ...prev, email: event.target.value }))
                  }
                  placeholder="ava@example.com"
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={registerForm.password}
                  onChange={(event) =>
                    setRegisterForm((prev) => ({ ...prev, password: event.target.value }))
                  }
                  placeholder="••••••••"
                />
              </label>
              <button type="submit">Register</button>
            </form>

            {isLoginVisible && (
              <form className="panel" onSubmit={handleLogin}>
                <h2>Login</h2>
                <label>
                  Email
                  <input
                    type="email"
                    value={loginForm.email}
                    onChange={(event) =>
                      setLoginForm((prev) => ({ ...prev, email: event.target.value }))
                    }
                    placeholder="ava@example.com"
                  />
                </label>
                <label>
                  Password
                  <input
                    type="password"
                    value={loginForm.password}
                    onChange={(event) =>
                      setLoginForm((prev) => ({ ...prev, password: event.target.value }))
                    }
                    placeholder="••••••••"
                  />
                </label>
                <button type="submit">Login</button>
              </form>
            )}
          </>
        )}

        {token && (
          <>
            <form className="panel" onSubmit={handleExpenseAdd}>
              <h2>Add expense</h2>
              <label>
                Title
                <input
                  value={expenseForm.title}
                  onChange={(event) =>
                    setExpenseForm((prev) => ({ ...prev, title: event.target.value }))
                  }
                  placeholder="Groceries"
                />
              </label>
              <label>
                Category
                <select
                  value={expenseForm.category}
                  onChange={(event) =>
                    setExpenseForm((prev) => ({ ...prev, category: event.target.value }))
                  }
                >
                  <option value="Food">Food</option>
                  <option value="Transport">Transport</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Bills">Bills</option>
                  <option value="Health">Health</option>
                </select>
              </label>
              <div className="inline-fields">
                <label>
                  Amount
                  <input
                    type="number"
                    value={expenseForm.amount}
                    onChange={(event) =>
                      setExpenseForm((prev) => ({ ...prev, amount: event.target.value }))
                    }
                    placeholder="2500"
                  />
                </label>
                <label>
                  Date
                  <input
                    type="date"
                    value={expenseForm.date}
                    onChange={(event) =>
                      setExpenseForm((prev) => ({ ...prev, date: event.target.value }))
                    }
                  />
                </label>
              </div>
              <button type="submit">Save expense</button>
            </form>

            {!isBudgetVisible && (
              <button type="button" onClick={() => setIsBudgetVisible(true)} className="secondary">
                + Add Budget
              </button>
            )}

            {isBudgetVisible && (
              <form className="panel" onSubmit={handleBudgetAdd}>
                <h2>Set budget</h2>
                <label>
                  Category
                  <select
                    value={budgetForm.category}
                    onChange={(event) =>
                      setBudgetForm((prev) => ({ ...prev, category: event.target.value }))
                    }
                  >
                    <option value="Food">Food</option>
                    <option value="Transport">Transport</option>
                    <option value="Shopping">Shopping</option>
                    <option value="Bills">Bills</option>
                    <option value="Health">Health</option>
                  </select>
                </label>
                <label>
                  Limit
                  <input
                    type="number"
                    value={budgetForm.limit}
                    onChange={(event) =>
                      setBudgetForm((prev) => ({ ...prev, limit: event.target.value }))
                    }
                    placeholder="5000"
                  />
                </label>
                <button type="submit">Create budget</button>
              </form>
            )}

            {!isGoalVisible && (
              <button type="button" onClick={() => setIsGoalVisible(true)} className="secondary">
                + Add Goal
              </button>
            )}

            {isGoalVisible && (
              <form className="panel" onSubmit={handleGoalAdd}>
                <h2>Create goal</h2>
                <label>
                  Goal Name
                  <input
                    value={goalForm.name}
                    onChange={(event) =>
                      setGoalForm((prev) => ({ ...prev, name: event.target.value }))
                    }
                    placeholder="Save for vacation"
                  />
                </label>
                <label>
                  Target Amount
                  <input
                    type="number"
                    value={goalForm.target_amount}
                    onChange={(event) =>
                      setGoalForm((prev) => ({ ...prev, target_amount: event.target.value }))
                    }
                    placeholder="50000"
                  />
                </label>
                <label>
                  Deadline
                  <input
                    type="date"
                    value={goalForm.deadline}
                    onChange={(event) =>
                      setGoalForm((prev) => ({ ...prev, deadline: event.target.value }))
                    }
                  />
                </label>
                <button type="submit">Create goal</button>
              </form>
            )}
          </>
        )}
      </section>

      {token && (
        <section className="content-grid">
          <div className="panel">
            <h2>Recent expenses</h2>
            {dashboard?.expenses?.length > 0 ? (
              <ul>
                {dashboard.expenses.map((expense) => (
                  <li key={expense.id}>
                    <span>{expense.title}</span>
                    <strong>₹{expense.amount.toLocaleString('en-IN')}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No expenses yet.</p>
            )}
          </div>

          <div className="panel">
            <h2>Budgets</h2>
            {dashboard?.budgets?.length > 0 ? (
              <ul>
                {dashboard.budgets.map((budget) => (
                  <li key={budget.category}>
                    <span>{budget.category}</span>
                    <strong>{Math.round((budget.spent / budget.limit) * 100)}%</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No budgets set. <button type="button" onClick={() => setIsBudgetVisible(true)}>Create one</button></p>
            )}
          </div>

          <div className="panel">
            <h2>Goals</h2>
            {dashboard?.goals?.length > 0 ? (
              <ul>
                {dashboard.goals.map((goal) => (
                  <li key={goal.name}>
                    <span>{goal.name}</span>
                    <strong>₹{goal.saved_amount.toLocaleString('en-IN')}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No goals set. <button type="button" onClick={() => setIsGoalVisible(true)}>Create one</button></p>
            )}
          </div>
        </section>
      )}

      <section id="insights" className="insights">
        <h2>AI-powered insights</h2>
        {token && dashboard?.insights?.length > 0 ? (
          <ul>
            {dashboard.insights.map((item) => (
              <li key={item.title}>{item.title}</li>
            ))}
          </ul>
        ) : token ? (
          <p>No insights yet. Add expenses and budgets to get insights.</p>
        ) : (
          <p>Sign up to get personalized insights.</p>
        )}
      </section>

      {message && <p className={`status-message ${message.includes('❌') ? 'error' : message.includes('✅') ? 'success' : ''}`}>{message}</p>}
    </div>
  )
}

export default App
