# Harmonia Backend API

A Flask-based backend API for the Harmonia application, providing health and wellness services for women.

## Features

- User authentication (register, login)
- User profile management
- Health data collection and management
- AI-powered chat assistance
- Personalized meal planning

## Project Structure

```
harmonia-backend/
├── app/                    # Application package
│   ├── api/                # API routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── chatbot.py      # Chatbot routes
│   │   └── user_details.py # User details routes
│   ├── config/             # Configuration
│   │   └── config.py       # Environment-specific configs
│   ├── models/             # Database models
│   │   ├── db.py           # Database initialization
│   │   ├── user.py         # User model
│   │   └── user_detail.py  # User details model
│   ├── services/           # Business logic
│   │   └── chatbot.py      # Chatbot service
│   ├── static/             # Static files
│   ├── templates/          # Template files
│   ├── utils/              # Utility functions
│   │   └── validators.py   # Data validation
│   └── __init__.py         # Application factory
├── migrations/             # Database migrations
├── tests/                  # Test suite
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── requirements.txt        # Dependencies
├── run.py                  # Application entry point
└── vercel.json             # Vercel deployment config
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd harmonia-backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   JWT_SECRET_KEY=your_jwt_secret_key
   DATABASE_URL=your_database_url
   GROQ_API_KEY=your_groq_api_key
   ```

5. Run the application:
   ```
   python run.py
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login a user
- `GET /api/auth/protected` - Protected route (requires authentication)

### User Details

- `POST /api/user-details` - Add user details
- `GET /api/user-details` - Get user details
- `PUT /api/user-details` - Update user details

### Chatbot

- `POST /api/chatbot/chat` - Chat with AI assistant
- `GET/POST /api/chatbot/meal-planner` - Generate personalized meal plan

## Deployment

The application is configured for deployment on Vercel. The `vercel.json` file contains the necessary configuration.

## License

[MIT License](LICENSE) 