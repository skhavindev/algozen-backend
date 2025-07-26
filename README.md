# AlgoZen Backend

A scalable online judge system with hybrid code execution capabilities.

## Features

- **Hybrid Code Execution**: Switch between subprocess (for development/Render) and Kubernetes (for production) execution
- **Multi-language Support**: Python, C++, Java
- **Secure Isolation**: Each code submission runs in isolated environments
- **Scalable Architecture**: Built with Django, Celery, and Redis
- **JWT Authentication**: Secure user authentication system

## Code Execution Modes

### 1. Subprocess Mode (Default - for Render, local development)
- **Environment Variable**: `USE_KUBERNETES=false` (default)
- **Execution**: Code runs directly in the Celery worker process using `subprocess`
- **Use Cases**: Development, demos, Render deployment
- **Pros**: Simple setup, works everywhere
- **Cons**: Less isolation, shared resources

### 2. Kubernetes Mode (Production - for GKE, EKS, AKS)
- **Environment Variable**: `USE_KUBERNETES=true`
- **Execution**: Each code submission creates a new Kubernetes pod
- **Use Cases**: Production deployments, high-security requirements
- **Pros**: Maximum isolation, scalable, secure
- **Cons**: Requires Kubernetes cluster

## Environment Variables

```bash
# Code Execution Mode
USE_KUBERNETES=false  # Use subprocess execution (default)
USE_KUBERNETES=true   # Use Kubernetes pod execution

# Redis Configuration
CELERY_BROKER_URL=redis://your-redis-url
CELERY_RESULT_BACKEND=redis://your-redis-url

# Django Configuration
DJANGO_SECRET_KEY=your-secret-key
DEBUG=0
ALLOWED_HOSTS=your-domain.com
```

## Deployment Options

### Option 1: Render (Subprocess Mode)
```bash
# Set environment variables in Render
USE_KUBERNETES=false
CELERY_BROKER_URL=redis://your-redis-url
CELERY_RESULT_BACKEND=redis://your-redis-url
```

### Option 2: Google Kubernetes Engine (Kubernetes Mode)
```bash
# Set environment variables
USE_KUBERNETES=true
# Configure kubeconfig for GKE cluster
```

### Option 3: Azure Container Apps (Subprocess Mode)
```bash
# Set environment variables
USE_KUBERNETES=false
CELERY_BROKER_URL=redis://your-redis-url
CELERY_RESULT_BACKEND=redis://your-redis-url
```

## Architecture

```
Frontend (Next.js) 
    ↓
Backend (Django) 
    ↓
Celery Worker
    ↓
Code Execution Engine
    ├── Subprocess Mode (Render, local)
    └── Kubernetes Mode (GKE, EKS, AKS)
```

## API Endpoints

- `POST /api/compile/` - Submit code for execution
- `GET /api/compile/result/<task_id>/` - Get execution results
- `POST /api/auth/login/` - User authentication
- `GET /api/problems/` - List coding problems

## Security Features

### Subprocess Mode
- Timeout limits (10 seconds)
- Temporary directory isolation
- Process resource limits

### Kubernetes Mode
- Pod-level isolation
- Security contexts (non-root, read-only filesystem)
- Resource limits (CPU, memory)
- Automatic pod cleanup

## Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/skhavindev/algozen-backend.git
cd algozen-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export USE_KUBERNETES=false  # For local development
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

4. **Run migrations**
```bash
cd backend
python manage.py migrate
```

5. **Start Celery worker**
```bash
celery -A backend worker --loglevel=info
```

6. **Start Django server**
```bash
python manage.py runserver
```

## Production Deployment

## License

MIT License 