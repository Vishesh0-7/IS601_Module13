# 🧮 Calculator API with JWT Authentication

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20playwright-green?logo=pytest)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?logo=codecov)](https://codecov.io/)
[![CI/CD](https://github.com/Vishesh0-7/IS601_Module12/actions/workflows/ci.yml/badge.svg)](https://github.com/Vishesh0-7/IS601_Module12/actions)

A professional RESTful API built with FastAPI featuring JWT authentication, calculation history tracking, and a modern responsive web interface.

**🔗 Links:**  
📦 [Docker Hub](https://hub.docker.com/r/vishy211/is601_module13) | 💻 [GitHub Repository](https://github.com/Vishesh0-7/IS601_Module12)

---

## ✨ Features

### Core Functionality
- 🔐 **JWT Authentication** - Secure user registration and login
- ➕ **Arithmetic Operations** - Add, subtract, multiply, divide with validation
- 📊 **Calculation History** - Track all calculations with user association
- 👥 **User Management** - Complete CRUD operations for users
- 🎨 **Modern Web UI** - Responsive frontend with real-time validation

### Technical Excellence
- ✅ **100% Test Coverage** - Unit, integration, and E2E tests
- 🚀 **CI/CD Pipeline** - Automated testing and deployment
- 🐳 **Docker Ready** - Full containerization with Docker Compose
- 📝 **API Documentation** - Auto-generated Swagger/ReDoc docs
- 🔒 **Security** - Password hashing, JWT tokens, input validation

---

## 🛠 Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[PostgreSQL](https://www.postgresql.org/)** - Advanced open-source relational database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation using Python type hints
- **[python-jose](https://python-jose.readthedocs.io/)** - JWT token generation and validation
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Secure password hashing
- **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server

### Frontend
- **Vanilla JavaScript** - Clean, dependency-free client-side code
- **HTML5/CSS3** - Modern, responsive design with gradient backgrounds

### Testing & DevOps
- **[pytest](https://pytest.org/)** - Powerful Python testing framework
- **[Playwright](https://playwright.dev/)** - End-to-end browser automation
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD automation
- **[Docker](https://www.docker.com/)** - Container platform for consistent deployments

---

## 📁 Project Structure

```
calculator--FastApi/
│
├── 📂 app/                       # Core application
│   ├── main.py                   # FastAPI app & configuration
│   ├── database.py               # Database connection & session
│   ├── models.py                 # SQLAlchemy database models
│   ├── schemas.py                # Pydantic validation schemas
│   ├── crud.py                   # Database CRUD operations
│   ├── security.py               # JWT & password utilities
│   ├── operations.py             # Calculation business logic
│   ├── routes_auth.py            # Authentication endpoints
│   ├── routes_calculations.py    # Calculation CRUD endpoints
│   ├── routes_users.py           # User management endpoints
│   └── 📂 static/
│       └── index.html            # Calculator web interface
│
├── 📂 frontend/                  # Authentication pages
│   ├── index.html                # Landing page
│   ├── login.html                # User login page
│   ├── register.html             # User registration page
│   └── common.js                 # Shared frontend utilities
│
├── 📂 tests/                     # Python test suite
│   ├── conftest.py               # Pytest fixtures & config
│   ├── test_auth.py              # Authentication tests
│   ├── test_comprehensive.py     # Integration tests
│   ├── 📂 unit/                  # Unit tests
│   │   └── test_operations.py
│   └── 📂 integration/           # Integration tests
│       └── test_api.py
│
├── 📂 e2e/                       # End-to-end tests
│   ├── 📂 tests/
│   │   ├── auth.spec.ts          # Auth flow E2E tests
│   │   └── calculations.spec.ts  # Calculation E2E tests
│   ├── package.json              # Node.js dependencies
│   └── playwright.config.ts      # Playwright configuration
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── ci.yml                # CI/CD pipeline configuration
│
├── docker-compose.yml            # Multi-container Docker setup
├── Dockerfile                    # Application container definition
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Vishesh0-7/IS601_Module12.git
cd IS601_Module12
```

### 2️⃣ Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3️⃣ Run with Docker (Recommended)
```bash
# Start all services (app, database, pgAdmin)
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

**Access the application:**
- 🌐 Web Interface: http://localhost:8000
- 📚 API Documentation: http://localhost:8000/docs
- 🔧 pgAdmin: http://localhost:5050

### 4️⃣ Run Locally (Development)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL must be running)
export DATABASE_URL="postgresql://user:pass@localhost:5432/calculator_db"

# Run the server
uvicorn app.main:app --reload

# Server available at http://localhost:8000
```

---

## 🧪 Testing

### Run All Tests
```bash
# Unit + Integration tests with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run E2E Tests
```bash
cd e2e
npm install
npx playwright install chromium
npm test
```

### Run Specific Test Suites
```bash
# Authentication tests only
pytest tests/test_auth.py -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v
```

---

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username_or_email": "user@example.com",
  "password": "SecurePass123"
}
```

### Calculation Endpoints

#### Create Calculation
```http
POST /calculations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "a": 10,
  "b": 5,
  "type": "Add"
}
```

**Response:**
```json
{
  "id": 1,
  "a": 10,
  "b": 5,
  "type": "Add",
  "result": 15,
  "user_id": 1,
  "created_at": "2025-11-30T12:00:00"
}
```

#### Get All Calculations
```http
GET /calculations/
Authorization: Bearer <token>
```

#### Get Calculation by ID
```http
GET /calculations/{id}
Authorization: Bearer <token>
```

#### Update Calculation
```http
PUT /calculations/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "a": 20,
  "b": 4,
  "type": "Multiply"
}
```

#### Delete Calculation
```http
DELETE /calculations/{id}
Authorization: Bearer <token>
```

### User Endpoints

#### Get All Users
```http
GET /users/
```

#### Get User by ID
```http
GET /users/{id}
```

#### Update User
```http
PUT /users/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "newusername"
}
```

#### Delete User
```http
DELETE /users/{id}
Authorization: Bearer <token>
```

---

## 🔐 Security Features

- **Password Hashing**: bcrypt with automatic salt generation
- **JWT Tokens**: HS256 algorithm, 30-minute expiration
- **Input Validation**: Pydantic schemas with type checking
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **CORS Configuration**: Properly configured cross-origin requests
- **Error Handling**: Secure error messages without sensitive data exposure

---

## 🐳 Docker Configuration

### Services

**App (FastAPI)**
- Port: 8000
- Auto-reload on file changes
- Environment variables from .env

**PostgreSQL Database**
- Port: 5432
- Persistent volume storage
- Health checks configured

**pgAdmin**
- Port: 5050
- Web-based database management
- Pre-configured connection

### Docker Commands
```bash
# Build and start
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v

# Rebuild app only
docker-compose build app
docker-compose up -d app
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Maintain 100% code coverage
- Follow PEP 8 style guide
- Update documentation as needed
- Run tests before committing

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Vishesh Patel**

- GitHub: [@Vishesh0-7](https://github.com/Vishesh0-7)
- LinkedIn: [Vishesh Patel](https://linkedin.com/in/vishesh-patel)

---

## 🙏 Acknowledgments

- FastAPI documentation and community
- NJIT IS601 Course Materials
- All contributors and testers

---

## 📞 Support

If you have any questions or issues, please:
- Open an issue on [GitHub](https://github.com/Vishesh0-7/IS601_Module12/issues)
- Check the [API Documentation](http://localhost:8000/docs)
- Review the [QUICKSTART Guide](QUICKSTART.md)

---

**Made with ❤️ using FastAPI**
