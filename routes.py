from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, desc
import json

from app import db
from models import User, Household, Expense,Income, Loan, LoanPayment, ExpenseCategory, Savings, BudgetPlan
from forms import (LoginForm, RegisterForm, JoinHouseholdForm, ExpenseForm, 
                   IncomeForm, LoanForm, LoanPaymentForm, CategoryForm, SavingsForm, BudgetPlanForm)
from utils import get_financial_summary, get_expense_by_category, calculate_loan_payment_split

# Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
expense_bp = Blueprint('expense', __name__)
income_bp = Blueprint('income', __name__)
loan_bp = Blueprint('loan', __name__)
savings_bp = Blueprint('savings', __name__)
budget_bp = Blueprint('budget', __name__)
report_bp = Blueprint('report', __name__)
settings_bp = Blueprint('settings', __name__)

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get financial summaries for different periods
    summaries = {}
    for period in ['today', 'week', 'month', 'year']:
        summaries[period] = get_financial_summary(current_user.household_id, period)
    
    # Get recent transactions
    recent_expenses = Expense.query.filter_by(household_id=current_user.household_id)\
        .order_by(desc(Expense.created_at)).limit(5).all()
    
    recent_income = Income.query.filter_by(household_id=current_user.household_id)\
        .order_by(desc(Income.created_at)).limit(5).all()
    
    # Get active loans
    loans = Loan.query.filter_by(household_id=current_user.household_id).all()
    loan_summary = []
    for loan in loans:
        remaining = loan.get_remaining_balance()
        if remaining > 0:
            loan_summary.append({
                'loan': loan,
                'remaining_balance': remaining,
                'total_interest_paid': loan.get_total_interest_paid()
            })
    
    # Get expense by category data for chart
    expense_by_category = get_expense_by_category(current_user.household_id, 'month')
    
    return render_template('dashboard.html', 
                         summaries=summaries,
                         recent_expenses=recent_expenses,
                         recent_income=recent_income,
                         loan_summary=loan_summary,
                         expense_by_category=expense_by_category)

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create household
        household = Household(name=form.household_name.data)
        db.session.add(household)
        db.session.flush()  # Get the ID
        
        # Create user
        user = User(
            household_id=household.id,
            display_name=form.display_name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/join', methods=['GET', 'POST'])
def join_household():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = JoinHouseholdForm()
    if form.validate_on_submit():
        # Check if household exists
        household = Household.query.get(form.household_id.data)
        if not household:
            flash('Household not found', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Create user
        user = User(
            household_id=household.id,
            display_name=form.display_name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Successfully joined household: {household.name}!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, join_mode=True)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Expense routes
@expense_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            household_id=current_user.household_id,
            category_id=form.category_id.data,
            user_id=current_user.id,
            amount=form.amount.data,
            expense_date=form.expense_date.data,
            notes=form.notes.data
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expense.list_expenses'))
    
    return render_template('expenses/add.html', form=form)

@expense_bp.route('/list')
@login_required
def list_expenses():
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.filter_by(household_id=current_user.household_id)\
        .order_by(desc(Expense.expense_date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('expenses/list.html', expenses=expenses)



from forms import ExpenseForm

#Edit Expense
@expense_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(expense)
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expense.list_expenses'))

    categories = ExpenseCategory.query.filter(
        (ExpenseCategory.is_default == True) |
        (ExpenseCategory.household_id.in_(
            db.session.query(Household.id).filter_by(id=current_user.id)
        ))
    ).all()

    return render_template('expenses/add.html', form=form, expense=expense, categories=categories)

#delete Expense

@expense_bp.route('/delete/<int:id>')
@login_required
def delete_expense(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expense.list_expenses'))

# Income routes
@income_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_income():
    form = IncomeForm()
    if form.validate_on_submit():
        income = Income(
            household_id=current_user.household_id,
            source=form.source.data,
            amount=form.amount.data,
            income_date=form.income_date.data,
            notes=form.notes.data
        )
        db.session.add(income)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('income.list_income'))
    
    return render_template('income/add.html', form=form)

@income_bp.route('/list')
@login_required
def list_income():
    page = request.args.get('page', 1, type=int)
    incomes = Income.query.filter_by(household_id=current_user.household_id)\
        .order_by(desc(Income.income_date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('income/list.html', incomes=incomes)

#income_bp = Blueprint('income', __name__)

from forms import IncomeForm

@income_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_income(id):
    #income = Income.query.filter_by(id=id).first_or_404()
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = IncomeForm(obj=income)

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(income)
        db.session.commit()
        flash('Income updated successfully!', 'success')
        return redirect(url_for('income.list_income'))

    return render_template('income/form.html', form=form, income=income)

 # categories = ExpenseCategory.query.filter(
    #     (ExpenseCategory.is_default == True) |
    #     (ExpenseCategory.household_id.in_(
    #         db.session.query(Household.id).filter_by(id=current_user.id)
    #     ))
    # ).all()
    # if request.method == 'POST':
    #     income.notes = request.form['description']
    #     income.amount = Decimal(request.form['amount'])
    #     income.income_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    #     income.source = request.form['source']
    #
    #     db.session.commit()
    #     flash('Income updated successfully!', 'success')
    #     return redirect(url_for('income.list_income'))

@income_bp.route('/delete/<int:id>')
@login_required
def delete_income(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(income)
    db.session.commit()
    flash('Income deleted successfully!', 'success')
    return redirect(url_for('income.list_income'))





# Loan routes
@loan_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_loan():
    form = LoanForm()
    if form.validate_on_submit():
        loan = Loan(
            household_id=current_user.household_id,
            lender_name=form.lender_name.data,
            principal=form.principal.data,
            interest_rate=form.interest_rate.data,
            term_months=form.term_months.data,
            start_date=form.start_date.data,
            loan_type=form.loan_type.data,
            notes=form.notes.data
        )
        db.session.add(loan)
        db.session.commit()
        flash('Loan added successfully!', 'success')
        return redirect(url_for('loan.list_loans'))
    
    return render_template('loans/add.html', form=form)

@loan_bp.route('/list')
@login_required
def list_loans():
    loans = Loan.query.filter_by(household_id=current_user.household_id).all()
    loan_data = []
    for loan in loans:
        loan_data.append({
            'loan': loan,
            'remaining_balance': loan.get_remaining_balance(),
            'total_interest_paid': loan.get_total_interest_paid(),
            'payment_count': len(loan.payments)
        })
    
    return render_template('loans/list.html', loan_data=loan_data)

@loan_bp.route('/payments/<int:loan_id>')
@login_required
def loan_payments(loan_id):
    loan = Loan.query.filter_by(id=loan_id, household_id=current_user.household_id).first_or_404()
    payments = LoanPayment.query.filter_by(loan_id=loan_id).order_by(desc(LoanPayment.payment_date)).all()
    
    return render_template('loans/payments.html', loan=loan, payments=payments)

@loan_bp.route('/add_payment', methods=['GET', 'POST'])
@login_required
def add_payment():
    form = LoanPaymentForm()
    if form.validate_on_submit():
        # Validate that principal + interest = total amount
        if abs(form.principal_portion.data + form.interest_portion.data - form.amount.data) > 0.01:
            flash('Principal and interest portions must add up to the total payment amount', 'danger')
            return render_template('loans/add_payment.html', form=form)
        
        payment = LoanPayment(
            loan_id=form.loan_id.data,
            payment_date=form.payment_date.data,
            amount=form.amount.data,
            principal_portion=form.principal_portion.data,
            interest_portion=form.interest_portion.data,
            notes=form.notes.data
        )
        db.session.add(payment)
        db.session.commit()
        flash('Loan payment recorded successfully!', 'success')
        return redirect(url_for('loan.list_loans'))
    
    return render_template('loans/add_payment.html', form=form)

# Report routes
@report_bp.route('/')
@login_required
def index():
    period = request.args.get('period', 'month')
    
    # Get financial summary
    summary = get_financial_summary(current_user.household_id, period)
    
    # Get expense by category
    expense_by_category = get_expense_by_category(current_user.household_id, period)
    
    # Get monthly trends (last 12 months)
    monthly_data = []
    for i in range(12):
        month_date = date.today().replace(day=1) - timedelta(days=30*i)
        month_summary = get_financial_summary(current_user.household_id, 'month')
        monthly_data.append({
            'month': month_date.strftime('%Y-%m'),
            'income': month_summary['income'],
            'expenses': month_summary['expenses']
        })
    monthly_data.reverse()
    
    return render_template('reports/index.html', 
                         summary=summary,
                         expense_by_category=expense_by_category,
                         monthly_data=monthly_data,
                         current_period=period)

# Settings routes
@settings_bp.route('/')
@login_required
def index():
    return render_template('settings/index.html')

@settings_bp.route('/categories')
@login_required
def categories():
    household_categories = ExpenseCategory.query.filter_by(household_id=current_user.household_id).all()
    default_categories = ExpenseCategory.query.filter_by(is_default=True).all()
    
    return render_template('settings/categories.html', 
                         household_categories=household_categories,
                         default_categories=default_categories)

@settings_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = ExpenseCategory(
            household_id=current_user.household_id,
            name=form.name.data,
            is_default=False
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    else:
        flash('Error adding category', 'danger')
    
    return redirect(url_for('settings.categories'))

@settings_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = ExpenseCategory.query.filter_by(
        id=category_id, 
        household_id=current_user.household_id
    ).first_or_404()
    
    form = CategoryForm()
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('settings.categories'))
    
    form.name.data = category.name
    return render_template('settings/edit_category.html', form=form, category=category)

@settings_bp.route('/categories/delete/<int:category_id>')
@login_required
def delete_category(category_id):
    category = ExpenseCategory.query.filter_by(
        id=category_id, 
        household_id=current_user.household_id
    ).first_or_404()
    
    # Check if category is being used
    if category.expenses:
        flash('Cannot delete category that has expenses assigned to it', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('settings.categories'))

# Savings routes
@savings_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_savings():
    form = SavingsForm()
    if form.validate_on_submit():
        savings = Savings(
            household_id=current_user.household_id,
            user_id=current_user.id,
            purpose=form.purpose.data,
            amount=form.amount.data,
            savings_date=form.savings_date.data,
            goal_amount=form.goal_amount.data,
            notes=form.notes.data
        )
        db.session.add(savings)
        db.session.commit()
        flash('Savings entry added successfully!', 'success')
        return redirect(url_for('savings.list_savings'))
    
    return render_template('savings/add.html', form=form)

@savings_bp.route('/list')
@login_required
def list_savings():
    page = request.args.get('page', 1, type=int)
    savings = Savings.query.filter_by(household_id=current_user.household_id)\
        .order_by(desc(Savings.savings_date))\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Calculate totals by purpose
    savings_summary = {}
    all_savings = Savings.query.filter_by(household_id=current_user.household_id).all()
    for saving in all_savings:
        if saving.purpose not in savings_summary:
            savings_summary[saving.purpose] = {
                'total_saved': 0.0,
                'goal_amount': float(saving.goal_amount) if saving.goal_amount else 0.0,
                'entries': 0
            }
        savings_summary[saving.purpose]['total_saved'] += float(saving.amount)
        savings_summary[saving.purpose]['entries'] += 1
        if saving.goal_amount:
            savings_summary[saving.purpose]['goal_amount'] = max(
                savings_summary[saving.purpose]['goal_amount'],
                float(saving.goal_amount)
            )
    
    return render_template('savings/list.html', savings=savings, savings_summary=savings_summary)

# Budget Plan routes
@budget_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    form = BudgetPlanForm()
    if form.validate_on_submit():
        budget = BudgetPlan(
            household_id=current_user.household_id,
            user_id=current_user.id,
            category=form.category.data,
            planned_amount=form.planned_amount.data,
            actual_amount=form.actual_amount.data or 0,
            budget_month=form.budget_month.data,
            notes=form.notes.data
        )
        db.session.add(budget)
        db.session.commit()
        flash('Budget plan added successfully!', 'success')
        return redirect(url_for('budget.list_budget'))
    
    return render_template('budget/add.html', form=form)

@budget_bp.route('/list')
@login_required
def list_budget():
    page = request.args.get('page', 1, type=int)
    current_month = request.args.get('month', date.today().replace(day=1).strftime('%Y-%m'))
    
    # Convert month string to date
    try:
        month_date = datetime.strptime(current_month + '-01', '%Y-%m-%d').date()
    except:
        month_date = date.today().replace(day=1)
    
    budgets = BudgetPlan.query.filter_by(household_id=current_user.household_id)\
        .filter(func.date_trunc('month', BudgetPlan.budget_month) == month_date)\
        .order_by(BudgetPlan.category)\
        .paginate(page=page, per_page=20, error_out=False)
    
    # Calculate monthly summary
    monthly_summary = {
        'total_planned': 0,
        'total_actual': 0,
        'categories': len(budgets.items) if budgets.items else 0
    }
    
    for budget in budgets.items:
        monthly_summary['total_planned'] += float(budget.planned_amount)
        monthly_summary['total_actual'] += float(budget.actual_amount)
    
    return render_template('budget/list.html', budgets=budgets, monthly_summary=monthly_summary, current_month=current_month)

@budget_bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    budget = BudgetPlan.query.filter_by(
        id=budget_id, 
        household_id=current_user.household_id
    ).first_or_404()
    
    form = BudgetPlanForm()
    if form.validate_on_submit():
        budget.category = form.category.data
        budget.planned_amount = form.planned_amount.data
        budget.actual_amount = form.actual_amount.data or 0
        budget.budget_month = form.budget_month.data
        budget.notes = form.notes.data
        db.session.commit()
        flash('Budget plan updated successfully!', 'success')
        return redirect(url_for('budget.list_budget'))
    
    # Pre-populate form
    form.category.data = budget.category
    form.planned_amount.data = budget.planned_amount
    form.actual_amount.data = budget.actual_amount
    form.budget_month.data = budget.budget_month
    form.notes.data = budget.notes
    
    return render_template('budget/edit.html', form=form, budget=budget)
