from rest_framework import serializers

from survey.models import OperatingSystem, SurveyResult
from django.contrib.auth.models import User


class SurveyResultSerializer(serializers.ModelSerializer):
    os = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SurveyResult
        fields = (
            'id',
            'os',
            'python',
            'rdb',
            'programming',
            'major',
            'grade',
            'backend_reason',
            'waffle_reason',
            'say_something',
            'timestamp',
            'user',
        )

    def get_os(self, survey):
        return OperatingSystemSerializer(survey.os, context=self.context).data

    def get_user(self, survey):
        return UserSerializer(survey.user, context=self.context).data

class OperatingSystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OperatingSystem
        fields = (
            'id',
            'name',
            'description',
            'price',
        )

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # Django 기본 User 모델에 존재하는 필드 중 일부
        fields = (
            'id',
            'username',
            'email',
            'last_login',  # 가장 최근 로그인 시점
            'date_joined', # 가입 시점
            'first_name',
            'last_name',
        )