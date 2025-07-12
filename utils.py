from datetime import datetime, timedelta, date
from sqlalchemy import func, and_
from models import Expense, Income, Loan, LoanPayment, Savings
from flask_login import current_user

def get_date_range(period):
    """Get start and end dates for different time periods"""
    today = date.today()
    
    if period == 'today':
        return today, today
    elif period == 'week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    elif period == 'month':
        start_of_month = today.replace(day=1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
        return start_of_month, end_of_month
    elif period == 'year':
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        return start_of_year, end_of_year
    else:
        return today, today

def get_financial_summary(household_id, period='month'):
    """Get financial summary for a household and time period"""
    start_date, end_date = get_date_range(period)
    
    # Get total expenses
    total_expenses = Expense.query.filter(
        and_(
            Expense.household_id == household_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).with_entities(func.sum(Expense.amount)).scalar() or 0
    
    # Get total income
    total_income = Income.query.filter(
        and_(
            Income.household_id == household_id,
            Income.income_date >= start_date,
            Income.income_date <= end_date
        )
    ).with_entities(func.sum(Income.amount)).scalar() or 0
    
    # Get loan payments
    loan_payments = LoanPayment.query.join(Loan).filter(
        and_(
            Loan.household_id == household_id,
            LoanPayment.payment_date >= start_date,
            LoanPayment.payment_date <= end_date
        )
    ).with_entities(func.sum(LoanPayment.amount)).scalar() or 0
    
    # Get savings (reduces available income)
    total_savings = Savings.query.filter(
        and_(
            Savings.household_id == household_id,
            Savings.savings_date >= start_date,
            Savings.savings_date <= end_date
        )
    ).with_entities(func.sum(Savings.amount)).scalar() or 0
    
    return {
        'expenses': float(total_expenses),
        'income': float(total_income),
        'loan_payments': float(loan_payments),
        'savings': float(total_savings),
        'net': float(total_income) - float(total_expenses) - float(loan_payments) - float(total_savings)
    }

def get_expense_by_category(household_id, period='month'):
    """Get expenses grouped by category for charts"""
    start_date, end_date = get_date_range(period)
    
    from models import ExpenseCategory
    results = Expense.query.join(ExpenseCategory).filter(
        and_(
            Expense.household_id == household_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        )
    ).with_entities(
        ExpenseCategory.name,
        func.sum(Expense.amount)
    ).group_by(ExpenseCategory.name).all()
    
    return {category: float(amount) for category, amount in results}

def calculate_loan_payment_split(principal_remaining, monthly_rate, payment_amount):
    """Calculate how much of a payment goes to principal vs interest"""
    interest_portion = principal_remaining * monthly_rate
    principal_portion = payment_amount - interest_portion
    
    # Ensure principal portion doesn't exceed remaining balance
    if principal_portion > principal_remaining:
        principal_portion = principal_remaining
        interest_portion = payment_amount - principal_portion
    
    return max(0, principal_portion), max(0, interest_portion)
