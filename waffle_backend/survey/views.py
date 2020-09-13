from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from survey.serializers import OperatingSystemSerializer, SurveyResultSerializer
from survey.models import OperatingSystem, SurveyResult


class SurveyResultViewSet(viewsets.GenericViewSet):
    queryset = SurveyResult.objects.all()
    serializer_class = SurveyResultSerializer

    def list(self, request):
        surveys = self.get_queryset().select_related('os')
        return Response(self.get_serializer(surveys, many=True).data)

    def retrieve(self, request, pk=None):
        survey = get_object_or_404(SurveyResult, pk=pk)
        return Response(self.get_serializer(survey).data)

    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            EXPERIENCE_DEGREE = ('very low', 'low', 'middle', 'high', 'very high')
            python = request.data.get('python')
            rdb = request.data.get('rdb')
            programming = request.data.get('programming')
            os = request.data.get('os')

            if not python or not rdb or not programming or not os:
                print(1)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif (python not in EXPERIENCE_DEGREE) or (rdb not in EXPERIENCE_DEGREE):
                print(2)
                print(python, programming, rdb, os)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                print(3)
                operating_system, created = OperatingSystem.objects.get_or_create(name=os)
                print(operating_system)
                print(created)
                survey = SurveyResult.objects.create(os=operating_system, python=EXPERIENCE_DEGREE.index(python)+1, rdb=EXPERIENCE_DEGREE.index(rdb)+1,
                                            programming=EXPERIENCE_DEGREE.index(programming)+1, user=request.user)

                return Response(self.get_serializer(survey).data, status=status.HTTP_201_CREATED)

class OperatingSystemViewSet(viewsets.GenericViewSet):
    queryset = OperatingSystem.objects.all()
    serializer_class = OperatingSystemSerializer

    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    def retrieve(self, request, pk=None):
        try:
            os = OperatingSystem.objects.get(id=pk)
        except OperatingSystem.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(os).data)
