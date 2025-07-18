from rest_framework import serializers
from .models import Problem, Submission, SolvedProblem
from django.contrib.auth import get_user_model
from rest_framework import serializers

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty', 'tags', 'created_at']

class ProblemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'description', 'constrains', 'difficulty',
            'tags', 'starter_code', 'created_by', 'created_at'
        ]

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            'id', 'problem', 'user', 'code', 'language', 'verdict',
            'execution_time', 'memory', 'submitted_at'
        ]
        extra_kwargs = {
            'problem': {'required': False, 'allow_null': True},
            'user': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        # Set user from request if not provided
        request = self.context.get('request')
        if request and not validated_data.get('user'):
            validated_data['user'] = request.user
        # Set a default problem if not provided (for testing)
        if not validated_data.get('problem'):
            from .models import Problem
            validated_data['problem'] = Problem.objects.first()
        return super().create(validated_data)

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role',
            'university', 'university_name', 'year_of_passing'
        ]

    def validate(self, data):
        # Ensure register number and year of passing are provided
        if not data.get('university_name'):
            raise serializers.ValidationError({'university_name': 'Register number is required.'})
        if not data.get('year_of_passing'):
            raise serializers.ValidationError({'year_of_passing': 'Year of passing is required.'})
        return data

    def create(self, validated_data):
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=validated_data['password'],
                role=validated_data.get('role', 'user'),
                university=validated_data.get('university', ''),
                university_name=validated_data.get('university_name', ''),
                year_of_passing=validated_data.get('year_of_passing', ''),
            )
            return user
        except Exception as e:
            if 'unique_register_per_year' in str(e):
                raise serializers.ValidationError({'university_name': 'Register number must be unique for the selected year of passing.'})
            raise serializers.ValidationError({'error': str(e)})

class SolvedProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolvedProblem
        fields = ['id', 'user', 'problem', 'solved_at']
        read_only_fields = ['id', 'solved_at']