# MNIST Digit Recognition – API Backend

Django + MySQL backend with advanced CNN. Connect your own frontend via the REST API.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Django, Django REST Framework |
| Database | MySQL (PyMySQL) |
| ML | TensorFlow/Keras, Advanced CNN with residual blocks |

## Quick Start

```bash
pip install -r requirements.txt

# MySQL: create DB first (see below)
python manage.py migrate
python manage.py runserver   # http://localhost:8000
```

API base: **http://localhost:8000/api/**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | API info |
| GET | `/api/health` | Health check |
| GET | `/api/model/status` | Model loaded? |
| POST | `/api/predict` | Predict from file upload |
| POST | `/api/predict/base64` | Predict from base64 image |
| POST | `/api/train` | Train model |
| GET | `/api/samples?count=10&digit=5` | MNIST samples |
| GET | `/api/evaluate` | Accuracy & metrics |
| GET | `/api/predictions` | Stored predictions |
| GET | `/api/training-runs` | Training history |

## Connect via API

Example: predict from base64 (e.g. canvas):

```bash
curl -X POST http://localhost:8000/api/predict/base64 \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/png;base64,..."}'
```

Example: predict from file:

```bash
curl -X POST http://localhost:8000/api/predict \
  -F "file=@digit.png"
```

## MySQL Setup

```sql
CREATE DATABASE mnist_digit_recognition CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set `DB_NAME`, `DB_USER`, `DB_PASSWORD` in `.env` or environment.

## Neural System Test

```bash
python run_neural_test.py
```
