# Local Development Setup Guide

This guide will help you set up the cryptocurrency dashboard on your local system with your own credentials.

## Prerequisites

1. **Python 3.11+** installed on your system
2. **PostgreSQL** database server running locally
3. **AWS Account** with SES configured (for email notifications)
4. **Git** (to clone and manage the project)

## Step 1: Environment Variables Setup

Create a `.env` file in the project root directory with your credentials:

```bash
# Database Configuration
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/crypto_dashboard
PGHOST=localhost
PGPORT=5432
PGUSER=your_username
PGPASSWORD=your_password
PGDATABASE=crypto_dashboard

# Flask Configuration
SESSION_SECRET=your-super-secret-key-here
FLASK_ENV=development

# AWS Credentials (for email notifications)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key

# Email Configuration
SES_FROM_EMAIL=your-verified-email@yourdomain.com
SES_TO_EMAIL=recipient@yourdomain.com

# Optional: CoinGecko API Key (for higher rate limits)
COINGECKO_API_KEY=your-coingecko-api-key

# Logging
LOG_LEVEL=DEBUG
```

## Step 2: Database Setup

### Option A: Using PostgreSQL Locally

1. **Install PostgreSQL** on your system
2. **Create a database**:
   ```sql
   CREATE DATABASE crypto_dashboard;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE crypto_dashboard TO your_username;
   ```

### Option B: Using Docker for PostgreSQL

```bash
docker run --name postgres-crypto \
  -e POSTGRES_DB=crypto_dashboard \
  -e POSTGRES_USER=your_username \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

## Step 3: AWS SES Setup

1. **Verify your email addresses** in AWS SES console
2. **Create IAM user** with SES permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ses:SendEmail",
           "ses:SendRawEmail"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
3. **Get access keys** for the IAM user
4. **Update your .env file** with the credentials

## Step 4: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or if using uv (recommended)
uv sync
```

## Step 5: Initialize Database

```bash
# Run the application once to create tables
python main.py
```

## Step 6: Test the Setup

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Visit** `http://localhost:5000` in your browser

3. **Test data refresh** by clicking the "Refresh" button

## Configuration Files to Modify

### 1. `app.py` - Main Application Configuration

**Current (Replit)**:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://localhost/crypto_dashboard")
```

**For Local**:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://your_username:your_password@localhost:5432/crypto_dashboard")
```

### 2. `services/email_service.py` - Email Configuration

**Update lines 14-16**:
```python
self.region = os.environ.get("AWS_REGION", "us-east-1")
self.from_email = os.environ.get("SES_FROM_EMAIL", "your-verified-email@yourdomain.com")
self.to_email = os.environ.get("SES_TO_EMAIL", "recipient@yourdomain.com")
```

### 3. `lambda_function.py` - AWS Lambda (Optional for Local)

If you want to test the Lambda function locally:

```python
# Add at the top of lambda_function.py
import os
from dotenv import load_dotenv
load_dotenv()  # Load .env file for local testing
```

## Environment-Specific Configurations

### Development Environment (`.env`)
```bash
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
```

### Production Environment
```bash
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=INFO
SESSION_COOKIE_SECURE=True
```

## Testing Your Setup

### 1. Test Database Connection
```bash
python -c "
from app import db
print('Database connection successful!')
print(f'Database URL: {db.engine.url}')
"
```

### 2. Test API Integration
```bash
python -c "
from services.crypto_service import CryptoService
crypto_service = CryptoService()
data = crypto_service.fetch_top_10_cryptocurrencies()
print(f'Fetched {len(data)} cryptocurrencies')
"
```

### 3. Test Email Service
```bash
python -c "
from services.email_service import EmailService
email_service = EmailService()
print('Email service initialized successfully')
"
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error**:
   - Check PostgreSQL is running
   - Verify credentials in .env file
   - Ensure database exists

2. **AWS SES Error**:
   - Verify email addresses in SES console
   - Check IAM permissions
   - Ensure you're not in SES sandbox mode

3. **API Rate Limit**:
   - Get a CoinGecko API key for higher limits
   - Add it to your .env file

4. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python version (3.11+ required)

## Running in Production

For production deployment:

1. **Use a production WSGI server**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

2. **Set up SSL/TLS** for secure connections

3. **Configure reverse proxy** (nginx/Apache)

4. **Set up monitoring** and logging

5. **Use environment variables** instead of .env files

## Daily Updates Setup

To enable automatic daily updates at 9 AM CST:

1. **Set up a cron job**:
   ```bash
   0 9 * * * cd /path/to/your/project && python lambda_function.py
   ```

2. **Or use AWS Lambda** with CloudWatch Events for cloud deployment

## Next Steps

1. Customize the dashboard styling in `static/css/dashboard.css`
2. Modify email templates in `services/email_service.py`
3. Add more cryptocurrencies by changing the API parameters
4. Set up automated backups for your database
5. Configure monitoring and alerting

## Support

If you encounter any issues:
1. Check the application logs
2. Verify all environment variables are set correctly
3. Test each component individually using the test commands above