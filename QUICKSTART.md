# Quick Start Guide - FastAPI Calculator with REST API

## 🚀 Quick Start with Docker (Recommended)

### 1. Start All Services
```bash
cd /home/vishesh/is601/calculator--FastApi
docker-compose up -d
```

This starts:
- **PostgreSQL** database (port 5432)
- **FastAPI** application (port 8000)
- **pgAdmin** database management UI (port 5050)

### 2. Access the Application
- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Try it out!)
- **pgAdmin**: http://localhost:5050
  - Login: `admin@calculator.com` / `admin`

### 3. View Your Data in pgAdmin
1. Open http://localhost:5050
2. Login with credentials above
3. Add New Server:
   - **Name**: Calculator DB
   - **Host**: `db` (Docker service name)
   - **Port**: 5432
   - **Database**: calculator_db
   - **Username**: calculator_user
   - **Password**: calculator_pass
4. Navigate to: Servers → Calculator DB → Databases → calculator_db → Schemas → public → Tables
5. Right-click `calculations` → View/Edit Data → All Rows
6. See all your saved calculations!

## 🧪 Test the REST API

### Register a User
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"demo","password":"demo123"}'
```

### Login
```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"demo","password":"demo123"}'
```

### Create a Calculation
```bash
curl -X POST "http://localhost:8000/calculations/" \
  -H "Content-Type: application/json" \
  -d '{"a":10,"b":5,"type":"Add"}'
```

### List All Calculations
```bash
curl "http://localhost:8000/calculations/"
```

### Update a Calculation
```bash
curl -X PUT "http://localhost:8000/calculations/1" \
  -H "Content-Type: application/json" \
  -d '{"a":20,"b":4,"type":"Multiply"}'
```

### Delete a Calculation
```bash
curl -X DELETE "http://localhost:8000/calculations/1"
```

## 📊 Interactive API Testing

Visit http://localhost:8000/docs for Swagger UI where you can:
- See all available endpoints
- Try out requests directly in the browser
- View request/response schemas
- No need for curl or Postman!

## 🧹 Cleanup

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes database data)
docker-compose down -v
```

## 📝 Run Tests

```bash
# All tests (120 tests, 100% coverage)
pytest tests/ -k "not playwright" -v

# With coverage report
pytest --cov=app --cov-report=html tests/ -k "not playwright"
open htmlcov/index.html
```

## 🔍 Monitoring

```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# View all logs
docker-compose logs -f
```

## ✅ Verify Everything Works

1. **Web UI**: Open http://localhost:8000 → Do a calculation → Should show "Saved to DB with ID: X"
2. **API Docs**: Open http://localhost:8000/docs → Try the POST /calculations/ endpoint
3. **pgAdmin**: Open http://localhost:5050 → Connect to database → View calculations table
4. **Tests**: Run `pytest tests/ -k "not playwright" -v` → Should see 120 passed

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :5050

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Restart database with health check wait
docker-compose restart db
docker-compose restart app
```

### View Container Status
```bash
docker-compose ps
```

### Reset Everything
```bash
docker-compose down -v
docker-compose up -d
```

## 📚 Next Steps

1. Explore the API documentation at `/docs`
2. Try all BREAD operations (Browse, Read, Edit, Add, Delete)
3. Register multiple users and create calculations
4. View the data in pgAdmin
5. Run the test suite to see examples
6. Check out `REST_API_IMPLEMENTATION.md` for detailed architecture info

## 🎯 Key Features

✅ User registration & login with bcrypt password hashing  
✅ Full CRUD operations on calculations (BREAD pattern)  
✅ Automatic result computation using Factory pattern  
✅ PostgreSQL database with SQLAlchemy ORM  
✅ Interactive API documentation (Swagger UI)  
✅ pgAdmin for visual database management  
✅ 120 tests with 100% code coverage  
✅ Docker Compose for easy deployment  
✅ CI/CD with GitHub Actions  

Enjoy! 🎉
