# EduSaaS Python Calculation Engine

Python microservice for grade calculations and report generation.

## Features
- Grade calculations with multiple grading systems
- Statistical analysis of student performance
- PDF report generation (simulated)
- RESTful API endpoints

## API Endpoints
- `GET /api/health` - Service health check
- `GET /api/test/calculation` - Test calculation
- `POST /api/calculate/grades` - Calculate grades from marks
- `POST /api/generate/report` - Generate reports

## Deployment
Deploy to Render with the Procfile provided.