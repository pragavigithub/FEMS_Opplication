# Household Finance Manager

## Overview

This is a Flask-based web application designed for multi-user household financial management. The system allows multiple family members to track shared expenses, income, and loans within a household context. It features user authentication, expense categorization, financial reporting, and loan management capabilities.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Authentication**: Flask-Login for session management
- **Forms**: WTForms with Flask-WTF for form handling and CSRF protection
- **Database Migrations**: Flask-Migrate for schema versioning

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.0
- **Charts**: Chart.js for financial visualizations
- **Responsive Design**: Mobile-first approach using Bootstrap grid system

### Security Considerations
- CSRF protection enabled via Flask-WTF
- Password hashing using Werkzeug's security utilities
- Session-based authentication with secure session keys
- Proxy-aware configuration for deployment behind reverse proxies

## Key Components

### Database Models
- **Household**: Central organizational unit containing multiple users
- **User**: Individual household members with authentication
- **ExpenseCategory**: Categorization system with default and custom categories
- **Expense**: Individual expense transactions linked to users and categories
- **Income**: Income tracking for household members
- **Loan**: Loan management with payment tracking capabilities
- **Savings**: Savings tracking with goals and purposes (reduces available income)
- **BudgetPlan**: Budget planning with planned vs actual amounts (tracking only)
- **LoanPayment**: Individual loan payment records with principal/interest split

### Route Blueprints
- **main_bp**: Dashboard and core application routes
- **auth_bp**: User registration, login, and authentication
- **expense_bp**: Expense management (add, list, categorize)
- **income_bp**: Income tracking and management
- **loan_bp**: Loan and payment management
- **savings_bp**: Savings tracking with goal progress (affects income calculations)
- **budget_bp**: Budget planning with planned vs actual tracking (tracking only)
- **report_bp**: Financial reporting and analytics
- **settings_bp**: Configuration and category management

### Form Handling
- **LoginForm**: User authentication
- **RegisterForm**: New household creation
- **JoinHouseholdForm**: Existing household joining
- **ExpenseForm**: Expense entry with dynamic category loading
- **IncomeForm**: Income recording
- **LoanForm**: Loan setup and management
- **LoanPaymentForm**: Recording loan payments with principal/interest split
- **SavingsForm**: Savings entry with optional goal tracking
- **BudgetPlanForm**: Budget planning with planned vs actual amounts
- **CategoryForm**: Category management (create/edit custom categories)

## Data Flow

### User Registration Flow
1. User chooses to create new household or join existing one
2. Form validation ensures data integrity
3. Password hashing occurs before database storage
4. Household creation includes default expense categories
5. User session establishment upon successful registration

### Expense Tracking Flow
1. User selects expense category (household-specific or default)
2. Amount and date validation
3. Transaction storage with user and household association
4. Real-time dashboard updates
5. Category-based reporting aggregation

### Financial Reporting Flow
1. Date range calculation based on selected period
2. SQLAlchemy aggregation queries for summaries
3. Category-based expense breakdown
4. Chart.js visualization rendering
5. Responsive data presentation across devices

## External Dependencies

### Python Packages
- Flask: Web application framework
- Flask-SQLAlchemy: Database ORM integration
- Flask-Login: User session management
- Flask-Migrate: Database migration support
- Flask-WTF: Form handling and CSRF protection
- WTForms: Form validation library
- Werkzeug: WSGI utilities and security functions

### Frontend Libraries
- Bootstrap 5: CSS framework with dark theme support
- Font Awesome 6.0: Icon library
- Chart.js: JavaScript charting library

### Development Dependencies
- SQLite: Default development database
- Environment variable configuration for production deployment

## Deployment Strategy

### Configuration Management
- Environment-based configuration using os.environ
- Configurable database URLs (SQLite default, PostgreSQL production)
- Secure session key management
- Database connection pooling with automatic reconnection

### Production Considerations
- ProxyFix middleware for reverse proxy deployment
- Connection pool management for database stability
- Logging configuration for debugging and monitoring
- WSGI-compatible application structure

### Database Flexibility
- SQLAlchemy ORM allows easy database backend switching
- Migration support for schema evolution
- Household-based data isolation for multi-tenancy

## Changelog

Recent Changes:
- July 12, 2025: Implemented admin-only user creation and comprehensive user management
  - Restricted user creation to admin users only - removed public join household functionality
  - Added admin user management panel with add/delete/role toggle capabilities
  - Created comprehensive user management templates with role indicators
  - Implemented safety checks preventing admin self-deletion and ensuring at least one admin
  - Added user management to Settings dropdown with admin crown indicator
  - Updated login page to remove join household option and direct users to contact admins
  - Created SavingsGoal model for persistent goal tracking with progress indicators
  - Added category-based savings splitting - users can link savings to specific goals
  - Fixed CSRF token issues in Settings/Categories management page
  - Implemented savings goals management with add/list functionality
  - Updated Savings form to include goal selection dropdown
  - Added admin role functionality with proper permissions for all financial data
  - Fixed Income model missing user_id field causing edit/delete errors
  - Connected to PostgreSQL database with environment variable support
- July 05, 2025: Completed Savings and Budget Planning modules with templates
  - Added Savings tracking with goal progress (reduces available income)
  - Added Budget Planning with planned vs actual tracking (tracking only)
  - Updated financial calculations to include savings in net income calculation
  - Created comprehensive templates for add/list/edit functionality
  - Integrated navigation and dashboard display
- July 05, 2025: Initial setup with core financial management features

## User Preferences

Preferred communication style: Simple, everyday language.