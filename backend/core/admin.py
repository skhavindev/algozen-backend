from django.contrib import admin
from .models import Problem, TestCase, Submission, User

class TestCaseInline(admin.TabularInline):  # or admin.StackedInline for a different look
    model = TestCase
    extra = 1  # Number of empty forms to display

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'difficulty')
    inlines = [TestCaseInline]

admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(User)