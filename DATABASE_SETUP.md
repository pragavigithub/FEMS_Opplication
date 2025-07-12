# Database Configuration Guide

## Current Setup

Your Household Finance Manager is now connected to a **PostgreSQL database** provided by Replit. The database is automatically configured and ready to use.

## Environment Variables

The following database environment variables are automatically available:

- `DATABASE_URL` - Complete PostgreSQL connection string
- `PGHOST` - Database host
- `PGPORT` - Database port (usually 5432)
- `PGUSER` - Database username
- `PGPASSWORD` - Database password
- `PGDATABASE` - Database name

## Custom Database Configuration

If you want to use your own external database:

1. Create a `.env` file in the project root
2. Add your custom database URL:
   ```
   CUSTOM_DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_database
   ```
3. The application will automatically use your custom database instead of the default Replit one

## Database Management

### Check Database Status
The database is ready and working. You can verify the connection anytime.

### Database Migrations
The app automatically creates all necessary tables when it starts. If you need to make schema changes, use Flask migrations:

```bash
flask db init      # Initialize migrations (already done)
flask db migrate   # Create a migration
flask db upgrade   # Apply migrations
```

## Security Notes

- Database credentials are securely managed by Replit
- All connections use proper authentication
- The database is isolated to your project

Your application is now successfully connected to PostgreSQL and ready for production use!