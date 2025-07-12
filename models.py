from datetime import datetime, date
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class Household(db.Model):
    __tablename__ = 'household'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='household', lazy=True)
    expense_categories = db.relationship('ExpenseCategory', backref='household', lazy=True)
    expenses = db.relationship('Expense', backref='household', lazy=True)
    incomes = db.relationship('Income', backref='household', lazy=True)
    loans = db.relationship('Loan', backref='household', lazy=True)
    savings = db.relationship('Savings', backref='household', lazy=True)
    budget_plans = db.relationship('BudgetPlan', backref='household', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)  # Admin role for household
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True)
    incomes = db.relationship('Income', backref='user', lazy=True)
    savings = db.relationship('Savings', backref='user', lazy=True)
    budget_plans = db.relationship('BudgetPlan', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ExpenseCategory(db.Model):
    __tablename__ = 'expense_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy=True)

class Expense(db.Model):
    __tablename__ = 'expense'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    expense_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Income(db.Model):
    __tablename__ = 'income'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(100))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    income_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Loan(db.Model):
    __tablename__ = 'loan'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    lender_name = db.Column(db.String(100))
    principal = db.Column(db.Numeric(14, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)  # Annual percentage
    term_months = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    loan_type = db.Column(db.String(50))
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('LoanPayment', backref='loan', lazy=True, order_by='LoanPayment.payment_date')
    
    def get_remaining_balance(self):
        """Calculate remaining balance based on payments made"""
        total_principal_paid = sum(payment.principal_portion for payment in self.payments)
        return float(self.principal) - float(total_principal_paid)
    
    def get_total_interest_paid(self):
        """Calculate total interest paid so far"""
        return float(sum(payment.interest_portion for payment in self.payments))

class LoanPayment(db.Model):
    __tablename__ = 'loan_payment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    principal_portion = db.Column(db.Numeric(12, 2), nullable=False)
    interest_portion = db.Column(db.Numeric(12, 2), nullable=False)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Savings(db.Model):
    __tablename__ = 'savings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purpose = db.Column(db.String(100), nullable=False)  # e.g., Emergency Fund, Vacation, Car
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    savings_date = db.Column(db.Date, nullable=False)
    goal_amount = db.Column(db.Numeric(12, 2), nullable=True)  # Optional savings goal
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BudgetPlan(db.Model):
    __tablename__ = 'budget_plan'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    household_id = db.Column(db.Integer, db.ForeignKey('household.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Budget category
    planned_amount = db.Column(db.Numeric(12, 2), nullable=False)
    actual_amount = db.Column(db.Numeric(12, 2), default=0)  # Actual spent amount
    budget_month = db.Column(db.Date, nullable=False)  # Month this budget applies to
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_remaining_budget(self):
        """Calculate remaining budget amount"""
        return float(self.planned_amount) - float(self.actual_amount)
    
    def get_usage_percentage(self):
        """Calculate budget usage percentage"""
        if self.planned_amount > 0:
            return (float(self.actual_amount) / float(self.planned_amount)) * 100
        return 0
