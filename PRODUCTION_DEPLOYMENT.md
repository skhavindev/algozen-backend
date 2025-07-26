# Production Deployment Guide for Algozen Backend

This guide will help you deploy the Algozen backend to Render for production use.

## Prerequisites

1. A Render account
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)
3. A PostgreSQL database (can be created on Render)

## Step 1: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your Git repository
4. Configure the service:

### Basic Settings
- **Name**: `algozen-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: `algozen-backend/backend` (if your Django project is in a subdirectory)

### Build & Deploy Settings
- **Build Command**: `pip install -r requirements_production.txt`
- **Start Command**: `gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`

## Step 2: Environment Variables

Add these environment variables in your Render service settings:

### Required Variables
```
DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=algozen-backend.onrender.com,your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://algozen.vercel.app,https://your-frontend-domain.com
```

### Database Variables (if using PostgreSQL)
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

### Celery/Redis Variables (if using background tasks)
```
CELERY_BROKER_URL=redis://your-redis-url:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0
```

## Step 3: Create PostgreSQL Database (Optional)

1. In Render Dashboard, click "New +" and select "PostgreSQL"
2. Configure the database:
   - **Name**: `algozen-db`
   - **Database**: `algozen_db`
   - **User**: `algozen_user`
3. Copy the connection details to your environment variables

## Step 4: Update Frontend Configuration

Update your frontend API configuration to point to the new backend:

```javascript
// In src/config/api.js
const API_CONFIG = {
  BASE_URL: 'https://algozen-backend.onrender.com',
};
```

## Step 5: Database Migration

After deployment, you'll need to run migrations. You can do this via Render's shell:

1. Go to your service in Render Dashboard
2. Click on "Shell" tab
3. Run these commands:

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
python manage.py collectstatic --noinput
```

## Step 6: Health Check

Your service should respond to health checks at:
- `https://algozen-backend.onrender.com/api/health/`

## Troubleshooting

### Common Issues

1. **"Body stream already read" error**
   - ✅ Fixed: Updated views to use `request.data` instead of `json.loads(request.body)`

2. **CORS errors**
   - ✅ Fixed: Updated CORS settings in Django settings
   - Make sure your frontend domain is in `CORS_ALLOWED_ORIGINS`

3. **400 Bad Request**
   - Check that all required environment variables are set
   - Verify the request format matches your API expectations

4. **Database connection issues**
   - Ensure PostgreSQL is properly configured
   - Check database credentials in environment variables

### Debug Mode

For debugging, temporarily set:
```
DEBUG=True
```

This will show detailed error messages (don't use in production).

### Logs

Check Render logs for detailed error information:
1. Go to your service in Render Dashboard
2. Click on "Logs" tab
3. Look for error messages and stack traces

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY`
- [ ] Proper `ALLOWED_HOSTS` configuration
- [ ] CORS properly configured
- [ ] Database credentials secured
- [ ] HTTPS enabled (automatic on Render)

## Performance Optimization

1. **Static Files**: Use a CDN for static files
2. **Database**: Use connection pooling for PostgreSQL
3. **Caching**: Implement Redis caching for frequently accessed data
4. **Background Tasks**: Use Celery for heavy computations

## Monitoring

Set up monitoring for:
- Response times
- Error rates
- Database performance
- Memory usage

## Backup Strategy

- Enable automatic PostgreSQL backups on Render
- Consider additional backup solutions for critical data

## SSL/HTTPS

Render automatically provides SSL certificates for your domain.

## Custom Domain (Optional)

1. Add your custom domain in Render settings
2. Update DNS records to point to Render
3. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` with your domain

## Support

If you encounter issues:
1. Check Render documentation
2. Review Django deployment checklist
3. Check application logs
4. Verify environment variables 