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

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [expenseForm, setExpenseForm] = useState(emptyExpense)
  const [registerForm, setRegisterForm] = useState(emptyRegister)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    fetch(`${apiBase}/api/dashboard`)
      .then((res) => res.json())
      .then((data) => setDashboard(data))
      .catch(() => {
        setDashboard({
          summary: {
            totalSpending: 24680,
            averageDaily: 820,
            remainingBudget: 13200,
            savingsProgress: 15200,
            financialHealthScore: 78,
          },
          expenses: [],
          budgets: [],
          goals: [],
          insights: [],
        })
      })
  }, [])

  const summary = dashboard?.summary
  const expenses = dashboard?.expenses ?? []
  const budgets = dashboard?.budgets ?? []
  const goals = dashboard?.goals ?? []
  const insights = dashboard?.insights ?? []

  const handleRegister = async (event) => {
    event.preventDefault()
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    try {
      const response = await fetch(`${apiBase}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Registration failed')
      setMessage(`Welcome ${data.user.name}! Your CashLy account is ready.`)
      setRegisterForm(emptyRegister)
    } catch (error) {
      setMessage(error.message)
    }
  }

  const handleExpenseAdd = async (event) => {
    event.preventDefault()
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    try {
      const response = await fetch(`${apiBase}/api/expenses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...expenseForm,
          amount: Number(expenseForm.amount),
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Expense add failed')
      setMessage(`Expense added: ${data.title} for ₹${data.amount}`)
      setExpenseForm(emptyExpense)
      const dashboardResponse = await fetch(`${apiBase}/api/dashboard`)
      const dashboardData = await dashboardResponse.json()
      setDashboard(dashboardData)
    } catch (error) {
      setMessage(error.message)
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
            <button type="button">Get Started</button>
            <button type="button" className="secondary">
              Login
            </button>
          </div>
        </section>

        <aside className="dashboard-card" id="dashboard">
          {summary ? (
            <>
              <div className="stat-card">
                <label>Total spending this month</label>
                <strong>₹{summary.totalSpending.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card muted">
                <label>Average daily spending</label>
                <strong>₹{summary.averageDaily.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card success">
                <label>Remaining budget</label>
                <strong>₹{summary.remainingBudget.toLocaleString('en-IN')}</strong>
              </div>
              <div className="stat-card primary">
                <label>Financial health score</label>
                <strong>{summary.financialHealthScore} / 100</strong>
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
      </section>

      <section className="content-grid">
        <div className="panel">
          <h2>Recent expenses</h2>
          <ul>
            {expenses.map((expense) => (
              <li key={expense.id}>
                <span>{expense.title}</span>
                <strong>₹{expense.amount.toLocaleString('en-IN')}</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="panel">
          <h2>Budgets</h2>
          <ul>
            {budgets.map((budget) => (
              <li key={budget.category}>
                <span>{budget.category}</span>
                <strong>{Math.round((budget.spent / budget.limit) * 100)}%</strong>
              </li>
            ))}
          </ul>
        </div>

        <div className="panel">
          <h2>Goals</h2>
          <ul>
            {goals.map((goal) => (
              <li key={goal.name}>
                <span>{goal.name}</span>
                <strong>₹{goal.saved_amount.toLocaleString('en-IN')}</strong>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="insights" className="insights">
        <h2>AI-powered insights</h2>
        <ul>
          {insights.map((item) => (
            <li key={item.title}>{item.title}</li>
          ))}
        </ul>
      </section>

      {message ? <p className="status-message">{message}</p> : null}
    </div>
  )
}

export default App
