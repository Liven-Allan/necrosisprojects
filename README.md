# Necrosis Project

A full-stack application with Django backend and React frontend for necrosis analysis.

## Project Structure

- `NecrosisApi/` - Django backend API
- `necrosisapp/` - React frontend application

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. Clone the repository:
```bash
git clone <your-repo-url>
cd necrosis_project
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Building Individual Services

#### Backend
```bash
docker build -t necrosis-backend ./NecrosisApi
```

#### Frontend
```bash
docker build -t necrosis-frontend ./necrosisapp
```

## Development

### Backend (Django)
```bash
cd NecrosisApi
pip install -r requirements.txt
python manage.py runserver
```

### Frontend (React)
```bash
cd necrosisapp
npm install
npm run dev
```

## CI/CD

This project includes GitHub Actions workflows for:
- Building Docker images on push to main branch
- Pushing images to GitHub Container Registry

## Environment Variables

Create `.env` files in the respective directories for local development:
- `NecrosisApi/.env` - Backend environment variables
- `necrosisapp/.env` - Frontend environment variables 