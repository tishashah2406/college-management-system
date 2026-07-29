from rest_framework import serializers
from .models import Course, Note, Assignment
from students.models import CourseProgress


# ================= COURSE =================
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


# ================= NOTE =================
class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


# ================= ASSIGNMENT =================
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


# ================= COURSE PROGRESS =================
class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = '__all__'

