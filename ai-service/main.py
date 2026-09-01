from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

app = FastAPI(title='CashLy AI Service')


class CategoryRequest(BaseModel):
    merchant: str
    description: str | None = None
    category_hint: str | None = None


class CategoryResponse(BaseModel):
    category: str
    confidence: float


class ForecastRequest(BaseModel):
    historical_expenses: list[dict]
    days_ahead: int = 30


class AnomalyRequest(BaseModel):
    historical_expenses: list[dict]
    new_expense: dict


class AnomalyResponse(BaseModel):
    is_anomalous: bool
    reason: str
    severity: str  # low, medium, high


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.post('/api/categories/classify', response_model=CategoryResponse)
def classify_category(payload: CategoryRequest):
    """Classify merchant/description into a spending category"""
    text = (payload.merchant + ' ' + (payload.description or '') + ' ' + (payload.category_hint or '')).lower()
    rules = {
        'food': ['swiggy', 'zomato', 'domino', 'pizza', 'restaurant', 'coffee', 'cafe', 'burger', 'food', 'diner', 'pizza hut', 'mcdonald', 'kfc'],
        'transport': ['uber', 'ola', 'flight', 'train', 'air', 'metro', 'cab', 'travel', 'bus', 'taxi', 'railway'],
        'shopping': ['amazon', 'flipkart', 'myntra', 'shop', 'clothing', 'store', 'mall', 'retail', 'boutique'],
        'subscriptions': ['netflix', 'spotify', 'prime', 'subscription', 'membership', 'premium', 'youtube'],
        'utilities': ['electricity', 'jio', 'airtel', 'internet', 'water', 'utility', 'bill', 'power', 'gas'],
        'entertainment': ['bookmyshow', 'movie', 'cinema', 'theater', 'theatre', 'entertainment', 'concert'],
        'healthcare': ['apollo', 'pharmacy', 'hospital', 'clinic', 'healthcare', 'medicine', 'doctor', 'medical'],
        'education': ['udemy', 'coursera', 'course', 'school', 'book', 'tuition', 'college', 'university'],
        'groceries': ['mart', 'dmart', 'bigbasket', 'grocery', 'groceries', 'reliance', 'supermarket', 'bakery'],
    }

    scores = {}
    for category, keywords in rules.items():
        scores[category] = sum(1 for keyword in keywords if keyword in text)

    best = max(scores.items(), key=lambda item: item[1], default=('Other', 0))
    if best[1] == 0:
        category = 'Other'
        confidence = 0.42
    else:
        category = best[0].capitalize()
        confidence = min(0.96, 0.55 + (best[1] * 0.12))

    return CategoryResponse(category=category, confidence=round(confidence, 2))


@app.get('/api/forecast')
def forecast_demo():
    """Legacy demo forecast endpoint"""
    return {
        'next_7_days': 4200,
        'next_30_days': 18000,
        'monthly_forecast': 18000,
        'category_breakdown': {'Food': 6200, 'Travel': 4100, 'Shopping': 2800},
    }


@app.post('/api/forecast')
def forecast(payload: ForecastRequest):
    """Generate forecast based on historical expenses"""
    if not payload.historical_expenses:
        # No data, return demo values
        return {
            'next_7_days': 0,
            'next_30_days': 0,
            'monthly_forecast': 0,
            'category_breakdown': {},
            'confidence': 0.0,
            'data_points': 0,
        }
    
    expenses = payload.historical_expenses
    days_ahead = payload.days_ahead or 30
    
    # Calculate daily average
    by_date = defaultdict(float)
    for exp in expenses:
        date = exp.get('date', '')
        amount = exp.get('amount', 0)
        if date:
            by_date[date] += amount
    
    if not by_date:
        return {
            'next_7_days': 0,
            'next_30_days': 0,
            'monthly_forecast': 0,
            'category_breakdown': {},
            'confidence': 0.0,
            'data_points': len(expenses),
        }
    
    daily_amounts = list(by_date.values())
    if daily_amounts:
        avg_daily = statistics.mean(daily_amounts)
        std_dev = statistics.stdev(daily_amounts) if len(daily_amounts) > 1 else 0
    else:
        avg_daily = 0
        std_dev = 0
    
    # Category breakdown
    by_category = defaultdict(float)
    for exp in expenses:
        category = exp.get('category', 'Other')
        amount = exp.get('amount', 0)
        by_category[category] += amount
    
    total_spending = sum(by_category.values())
    category_breakdown = {}
    if total_spending > 0:
        for cat, amount in by_category.items():
            # Project category spending
            category_ratio = amount / total_spending
            category_breakdown[cat] = round(avg_daily * days_ahead * category_ratio)
    
    # Calculate forecasts
    forecast_7 = round(avg_daily * 7)
    forecast_30 = round(avg_daily * 30)
    
    # Confidence based on data points
    data_points = len(expenses)
    confidence = min(0.95, 0.3 + (data_points * 0.01))
    
    return {
        'next_7_days': forecast_7,
        'next_30_days': forecast_30,
        'monthly_forecast': forecast_30,
        'category_breakdown': category_breakdown,
        'confidence': round(confidence, 2),
        'data_points': data_points,
        'average_daily': round(avg_daily, 2),
    }


@app.get('/api/anomalies')
def anomalies_demo():
    """Legacy demo anomalies endpoint"""
    return {
        'items': [{
            'merchant': 'Luxury Purchase',
            'category': 'Shopping',
            'amount': 4500,
            'message': 'This expense is significantly higher than your typical spending in this category.'
        }]
    }


@app.post('/api/anomalies')
def detect_anomalies(payload: AnomalyRequest):
    """Detect anomalous expenses based on historical data"""
    if not payload.historical_expenses or not payload.new_expense:
        return {'items': []}
    
    historical = payload.historical_expenses
    new_exp = payload.new_expense
    
    # Group by category
    by_category = defaultdict(list)
    for exp in historical:
        category = exp.get('category', 'Other')
        amount = exp.get('amount', 0)
        by_category[category].append(amount)
    
    anomalies = []
    new_category = new_exp.get('category', 'Other')
    new_amount = new_exp.get('amount', 0)
    new_merchant = new_exp.get('title', 'Unknown')
    
    if new_category in by_category:
        amounts = by_category[new_category]
        if amounts:
            avg = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else avg * 0.2
            
            # Check if new expense is > 2 standard deviations
            z_score = (new_amount - avg) / std_dev if std_dev > 0 else 0
            
            if new_amount > avg * 2:
                severity = 'high' if new_amount > avg * 3 else 'medium'
                anomalies.append({
                    'merchant': new_merchant,
                    'category': new_category,
                    'amount': new_amount,
                    'message': f'This expense ({new_amount:.0f}) is {(new_amount/avg - 1)*100:.0f}% higher than typical {new_category} spending (avg: {avg:.0f}).',
                    'severity': severity,
                    'z_score': round(z_score, 2),
                })
            elif new_amount > avg * 1.5:
                anomalies.append({
                    'merchant': new_merchant,
                    'category': new_category,
                    'amount': new_amount,
                    'message': f'This {new_category} expense is higher than usual.',
                    'severity': 'low',
                    'z_score': round(z_score, 2),
                })
    else:
        # Category not in history, check against overall spending
        all_amounts = [exp.get('amount', 0) for exp in historical]
        if all_amounts:
            avg_overall = statistics.mean(all_amounts)
            if new_amount > avg_overall * 2.5:
                anomalies.append({
                    'merchant': new_merchant,
                    'category': new_category,
                    'amount': new_amount,
                    'message': f'First time seeing {new_category} spending. This amount is higher than typical overall spending.',
                    'severity': 'medium',
                })
    
    return {'items': anomalies}

