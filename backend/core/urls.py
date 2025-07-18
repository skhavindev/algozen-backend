from .views import ProblemListView
from django.urls import path
from rest_framework.generics import ListAPIView
from .views import ProblemListView, ProblemDetailView
from .views import SubmissionListCreateView
from .views import RegisterView
from .views import SubmissionDetailView
from rest_framework.generics import RetrieveAPIView
from .models import Submission
from .serializers import SubmissionSerializer
from .views_compile import compile_code, compile_result
from .views import CustomLoginView
from .views import SolvedProblemView

urlpatterns = [
    path('problems/', ProblemListView.as_view(), name='problem-list'),
    path('problems/<int:id>/', ProblemDetailView.as_view(), name='problem-detail'),
    path('submissions/', SubmissionListCreateView.as_view(), name='submission-list-create'),
    path('auth/register/', RegisterView.as_view(), name='register'),
]

urlpatterns += [
    path('submissions/<int:id>/', SubmissionDetailView.as_view(), name='submission-detail'),
]

urlpatterns += [
    path('compile/', compile_code, name='compile_code'),
    path('compile/result/<str:task_id>/', compile_result, name='compile_result'),
]

urlpatterns += [
    path('auth/login/', CustomLoginView.as_view(), name='custom-login'),
]

urlpatterns += [
    path('solved/', SolvedProblemView.as_view(), name='solved-problem'),
]