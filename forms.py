from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, SelectField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import TextArea
from models import ExpenseCategory, Loan
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    household_name = StringField('Household Name', validators=[DataRequired(), Length(min=2, max=100)])
    display_name = StringField('Your Display Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class JoinHouseholdForm(FlaskForm):
    household_id = IntegerField('Household ID', validators=[DataRequired()])
    display_name = StringField('Your Display Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class ExpenseForm(FlaskForm):
    category_id = SelectField('Category', validators=[DataRequired()], coerce=int)
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    expense_date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])
    
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            # Get categories for current household and default categories
            categories = ExpenseCategory.query.filter(
                (ExpenseCategory.household_id == current_user.household_id) |
                (ExpenseCategory.is_default == True)
            ).all()
            self.category_id.choices = [(c.id, c.name) for c in categories]

class IncomeForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired(), Length(max=100)])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    income_date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])

class LoanForm(FlaskForm):
    lender_name = StringField('Lender Name', validators=[Optional(), Length(max=100)])
    principal = DecimalField('Principal Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    interest_rate = DecimalField('Annual Interest Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], places=2)
    term_months = IntegerField('Term (Months)', validators=[DataRequired(), NumberRange(min=1)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    loan_type = StringField('Loan Type', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])

class LoanPaymentForm(FlaskForm):
    loan_id = SelectField('Loan', validators=[DataRequired()], coerce=int)
    payment_date = DateField('Payment Date', validators=[DataRequired()])
    amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    principal_portion = DecimalField('Principal Portion', validators=[DataRequired(), NumberRange(min=0)], places=2)
    interest_portion = DecimalField('Interest Portion', validators=[DataRequired(), NumberRange(min=0)], places=2)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])
    
    def __init__(self, *args, **kwargs):
        super(LoanPaymentForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            loans = Loan.query.filter_by(household_id=current_user.household_id).all()
            self.loan_id.choices = [(l.id, f"{l.lender_name or 'Loan'} - ${l.principal:,.2f}") for l in loans]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])

class SavingsGoalForm(FlaskForm):
    purpose = StringField('Savings Goal Purpose', validators=[DataRequired(), Length(max=100)])
    goal_amount = DecimalField('Goal Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    submit = SubmitField('Create Goal')

class SavingsForm(FlaskForm):
    savings_goal_id = SelectField('Savings Goal', validators=[Optional()], coerce=int)
    purpose = StringField('Savings Purpose', validators=[DataRequired(), Length(max=100)])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    savings_date = DateField('Date', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Add Savings')
    
    def __init__(self, *args, **kwargs):
        super(SavingsForm, self).__init__(*args, **kwargs)
        from models import SavingsGoal
        from flask_login import current_user
        if current_user.is_authenticated:
            goals = SavingsGoal.query.filter_by(household_id=current_user.household_id).all()
            self.savings_goal_id.choices = [(0, 'No specific goal')] + [(g.id, f"{g.purpose} (${g.current_amount:.2f}/${g.goal_amount:.2f})") for g in goals]

class BudgetPlanForm(FlaskForm):
    category = StringField('Budget Category', validators=[DataRequired(), Length(max=100)])
    planned_amount = DecimalField('Planned Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    actual_amount = DecimalField('Actual Spent', validators=[Optional(), NumberRange(min=0)], places=2)
    budget_month = DateField('Budget Month', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=255)])

class AddUserForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=200)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_admin = SelectField('Role', choices=[('False', 'Regular User'), ('True', 'Administrator')], default='False')
    submit = SubmitField('Add User')
