from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title='CashLy AI Service')


class CategoryRequest(BaseModel):
    merchant: str
    description: str | None = None
    category_hint: str | None = None


class CategoryResponse(BaseModel):
    category: str
    confidence: float


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/api/categories/classify', response_model=CategoryResponse)
def classify_category(payload: CategoryRequest):
    text = (payload.merchant + ' ' + (payload.description or '') + ' ' + (payload.category_hint or '')).lower()
    rules = {
        'food': ['swiggy', 'zomato', 'domino', 'pizza', 'restaurant', 'coffee', 'cafe', 'burger', 'food'],
        'travel': ['uber', 'ola', 'flight', 'train', 'air', 'metro', 'cab', 'travel'],
        'shopping': ['amazon', 'flipkart', 'myntra', 'shop', 'clothing', 'store'],
        'subscriptions': ['netflix', 'spotify', 'prime', 'subscription', 'membership'],
        'utilities': ['electricity', 'jio', 'airtel', 'internet', 'water', 'utility', 'bill'],
        'entertainment': ['bookmyshow', 'movie', 'cinema', 'theater', 'entertainment'],
        'healthcare': ['apollo', 'pharmacy', 'hospital', 'clinic', 'healthcare', 'medicine'],
        'education': ['udemy', 'coursera', 'course', 'school', 'book'],
        'groceries': ['mart', 'dmart', 'bigbasket', 'grocery', 'groceries', 'reliance'],
    }

    scores = {}
    for category, keywords in rules.items():
        scores[category] = sum(1 for keyword in keywords if keyword in text)

    best = max(scores.items(), key=lambda item: item[1], default=('Other', 0))
    if best[1] == 0:
        category = 'Other'
        confidence = 0.42
    else:
        category = best[0]
        confidence = min(0.96, 0.55 + (best[1] * 0.12))

    return CategoryResponse(category=category, confidence=round(confidence, 2))


@app.get('/api/forecast')
def forecast_demo():
    return {
        'next_7_days': 4200,
        'next_30_days': 18000,
        'monthly_forecast': 18000,
        'category_breakdown': {'Food': 6200, 'Travel': 4100, 'Shopping': 2800},
    }


@app.get('/api/anomalies')
def anomalies_demo():
    return {
        'items': [{
            'merchant': 'Luxury Purchase',
            'category': 'Shopping',
            'amount': 4500,
            'message': 'This expense is significantly higher than your typical spending in this category.'
        }]
    }
