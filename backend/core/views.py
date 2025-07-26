from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Problem
from .serializers import ProblemSerializer, ProblemDetailSerializer
from rest_framework.generics import ListCreateAPIView
from .models import Submission
from .serializers import SubmissionSerializer
from rest_framework import generics
from .serializers import RegisterSerializer
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import subprocess
import tempfile
from kubernetes import client, config
from celery import current_app
import redis
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from .models import SolvedProblem
from .serializers import SolvedProblemSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import time


User = get_user_model()

class ProblemListView(ListAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

class ProblemDetailView(RetrieveAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemDetailSerializer
    lookup_field = 'id'

class SubmissionListCreateView(ListCreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def perform_create(self, serializer):
        submission = serializer.save()
        from .tasks import evaluate_submission
        evaluate_submission.delay(submission.id)



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

from rest_framework.generics import RetrieveAPIView

class SubmissionDetailView(RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    lookup_field = 'id'

@api_view(['GET'])
def health_check(request):
    """Health check endpoint for Render deployment"""
    return Response({
        "status": "healthy", 
        "message": "Algozen Backend is running",
        "timestamp": time.time()
    }, status=status.HTTP_200_OK)

class CustomLoginView(APIView):
    def post(self, request):
        university_name = request.data.get('university_name')
        university = request.data.get('university')
        year_of_passing = request.data.get('year_of_passing')
        password = request.data.get('password')
        debug = {
            'received': {
                'university_name': university_name,
                'university': university,
                'year_of_passing': year_of_passing,
                'password': '(hidden)',
            }
        }
        if not (university_name and university and year_of_passing and password):
            debug['error'] = 'Missing one or more required fields.'
            return Response({'error': 'All fields are required.', 'debug': debug}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(university_name=university_name, university=university, year_of_passing=year_of_passing)
        except User.DoesNotExist:
            debug['error'] = 'No user found with these credentials.'
            debug['users_found'] = list(User.objects.filter(university=university, year_of_passing=year_of_passing).values('university_name'))
            return Response({'error': 'No user found with these credentials.', 'debug': debug}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password):
            debug['error'] = 'Password mismatch.'
            return Response({'error': 'Password incorrect.', 'debug': debug}, status=status.HTTP_401_UNAUTHORIZED)
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        debug['success'] = True
        return Response({
            'message': 'Login successful!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'debug': debug
        }, status=status.HTTP_200_OK)

class SolvedProblemView(generics.CreateAPIView):
    queryset = SolvedProblem.objects.all()
    serializer_class = SolvedProblemSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        problem = request.data.get('problem_id') or request.data.get('problem')
        if not user or not problem:
            return Response({'error': 'user and problem_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        # Prevent duplicates
        obj, created = SolvedProblem.objects.get_or_create(user_id=user, problem_id=problem)
        if created:
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)

# If not already present, add a compile_result endpoint
@api_view(['GET'])
def compile_result(request, task_id):
    # Dummy implementation, replace with your actual task result logic
    # Example: fetch from Celery/Redis
    # Here, just return a fake result for demonstration
    # Replace this with your actual result fetching logic
    import random
    import time
    # Simulate a finished task
    return Response({
        'status': 'SUCCESS',
        'results': [
            {'output': 'Sample output', 'expected_output': 'Sample output', 'passed': True},
            {'output': 'Sample output', 'expected_output': 'Sample output', 'passed': True},
        ]
    })