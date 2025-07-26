from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
import tempfile
import os
import time
from kubernetes import client, config
from threading import Lock
import shlex
import traceback
import shutil
import subprocess
import getpass
from core.tasks import run_code_job
from celery.result import AsyncResult
from django.conf import settings

LANGUAGE_CONFIG = {
    'python': {
        'image': 'python:3.10-slim',
        'run_cmd': 'python /code/user_code.py',
        'file_name': 'user_code.py',
    },
    'cpp': {
        'image': 'gcc:latest',
        'run_cmd': 'g++ /code/user_code.cpp -o /code/a.out && /code/a.out',
        'file_name': 'user_code.cpp',
    },
    'java': {
        'image': 'openjdk:latest',
        'run_cmd': 'javac /code/UserCode.java && java -cp /code UserCode',
        'file_name': 'UserCode.java',
    },
}

# Simple in-memory rate limiter (per-process, not distributed)
RATE_LIMIT = 20  # max concurrent jobs
active_jobs = 0
rate_limit_lock = Lock()

def acquire_job_slot():
    global active_jobs
    with rate_limit_lock:
        if active_jobs >= RATE_LIMIT:
            return False
        active_jobs += 1
        return True

def release_job_slot():
    global active_jobs
    with rate_limit_lock:
        if active_jobs > 0:
            active_jobs -= 1

@csrf_exempt
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def compile_code(request):
    try:
        data = json.loads(request.body)
        language = data.get('language')
        code = data.get('code')
        stdin = data.get('input', '')
        config_obj = LANGUAGE_CONFIG.get(language.lower())
        if not config_obj:
            return JsonResponse({'error': 'Unsupported language'}, status=400)
        # Use Minikube shared folder for all code files on Windows
        if os.name == 'nt':
            import getpass
            user = getpass.getuser()
            shared_base = f'C:/Users/{user}/.minikube/files/code'
        else:
            shared_base = '/home/docker/code'
        os.makedirs(shared_base, exist_ok=True)
        job_name = f"oj-job-{int(time.time()*1000)}"
        shared_dir = f'{shared_base}/{job_name}'
        os.makedirs(shared_dir, exist_ok=True)
        code_path = f'{shared_dir}/user_code.py' if language.lower() == 'python' else (
            f'{shared_dir}/user_code.cpp' if language.lower() == 'cpp' else f'{shared_dir}/UserCode.java')
        with open(code_path, 'w') as f:
            f.write(code)
        input_path = f'{shared_dir}/input.txt'
        with open(input_path, 'w') as f:
            f.write(stdin)
        # Submit to Celery, passing the shared_dir
        task = run_code_job.delay(language, code, stdin, shared_dir)
        return JsonResponse({'task_id': task.id, 'status': 'PENDING'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def compile_result(request, task_id):
    try:
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            return JsonResponse({'status': 'PENDING'})
        elif result.state == 'SUCCESS':
            return JsonResponse({'status': 'SUCCESS', 'result': result.result})
        elif result.state == 'FAILURE':
            return JsonResponse({'status': 'FAILURE', 'error': str(result.result)})
        else:
            return JsonResponse({'status': result.state})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)