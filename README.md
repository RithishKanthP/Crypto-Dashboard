# Cryptocurrency Dashboard

A comprehensive Flask-based web application that tracks and displays the top 10 cryptocurrencies by market cap. The system fetches real-time data from CoinGecko API, stores it in PostgreSQL, and provides both web interface and email notifications.

## Features

- **Real-time Data**: Fetches top 10 cryptocurrencies from CoinGecko API
- **Interactive Dashboard**: Bootstrap-based responsive web interface
- **Data Visualization**: Charts showing market cap distribution and price changes
- **Email Notifications**: Daily email reports via AWS SES
- **Database Storage**: PostgreSQL for data persistence
- **AWS Lambda**: Scheduled daily updates at 9 AM CST
- **Error Handling**: Comprehensive logging and error notifications

## Technology Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Cloud Services**: AWS SES, AWS Lambda
- **API**: CoinGecko API for cryptocurrency data

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- AWS Account (for email notifications)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd crypto-dashboard
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install flask flask-sqlalchemy boto3 requests psycopg2-binary gunicorn
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

6. **Visit**: `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/crypto_dashboard

# Flask
SESSION_SECRET=your-secret-key

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Email
SES_FROM_EMAIL=your-email@domain.com
SES_TO_EMAIL=recipient@domain.com
```

### Database Setup

The application will automatically create database tables on first run. Make sure PostgreSQL is running and the database exists.

## Project Structure

```
crypto-dashboard/
├── app.py                    # Flask application setup
├── main.py                   # Application entry point
├── config.py                 # Configuration classes
├── models.py                 # Database models
├── routes.py                 # Application routes
├── lambda_function.py        # AWS Lambda function
├── services/                 # Business logic
│   ├── crypto_service.py     # API integration
│   ├── database_service.py   # Database operations
│   └── email_service.py      # Email notifications
├── templates/                # HTML templates
├── static/                   # CSS and JavaScript
└── docs/                     # Documentation
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/crypto-data` - JSON API for crypto data
- `GET /api/refresh` - Manual data refresh
- `GET /health` - Health check

## Features Overview

### Dashboard Interface
- Top 10 cryptocurrencies by market cap
- Real-time prices and 24h changes
- Market statistics cards
- Interactive charts and graphs
- Mobile-responsive design

### Scheduled Updates
- Daily updates at 9 AM CST
- Automatic email notifications
- Error handling and logging
- Data cleanup (30-day retention)

### Email Notifications
- Daily summary reports
- Error notifications
- HTML and text formats
- Professional styling

## Development

### Running in Development
```bash
export FLASK_ENV=development
python main.py
```

### Testing
```bash
# Test database connection
python -c "from app import db; print('Database OK')"

# Test API integration
python -c "from services.crypto_service import CryptoService; print('API OK')"
```

### Adding New Features
1. Update database models in `models.py`
2. Add business logic in `services/`
3. Create routes in `routes.py`
4. Update templates in `templates/`

## Deployment

### Local Production
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

### AWS Lambda
1. Package the application
2. Deploy to AWS Lambda
3. Set up CloudWatch Events for scheduling
4. Configure environment variables

### Docker (Optional)
```bash
docker build -t crypto-dashboard .
docker run -p 5000:5000 crypto-dashboard
```

## Monitoring

- Application logs via Python logging
- Database connection monitoring
- API rate limit tracking
- Email delivery status
- Error notifications via email

## Security

- Environment variable configuration
- Session security
- Input validation
- SQL injection prevention
- CSRF protection ready

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section in `LOCAL_SETUP.md`
2. Review application logs
3. Test individual components
4. Create an issue with detailed error information

## Roadmap

- [ ] Historical price charts
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] More cryptocurrency exchanges
- [ ] Mobile app
- [ ] Advanced analytics

---

**Made with ❤️ for cryptocurrency enthusiasts**