from core.paginators import CustomPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from services.serializers import CoursesSerializer, ExamsSerializer
from services.models import Course, Exams, UnivExamsStructure

# Create your views here.

class ExamsAPIView(generics.ListAPIView):

    serializer_class = ExamsSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        # This apiview will receive three query params to filter in
        # 
        # univ: this is 'siglas' field
        # year: this is 'year' field in examns

        queryset = Exams.objects.all()

        # Get query params to filter
        univ = self.request.query_params.get('univ')
        year = self.request.query_params.get('year')
        video_solution = self.request.query_params.get('video', None)

        if (univ is not None) and (univ != ''):
            queryset = queryset.filter(root__siglas=univ)
        if (year is not None) and (year != '0'):
            queryset = queryset.filter(year=year)
        # TODO add test for this filter
        if (video_solution is not None):
            if video_solution == 'free':
                queryset = queryset.exclude(source_video_solution=u'')
            elif video_solution == 'premium':
                queryset = queryset.exclude(source_video_solution_premium=u'')

        return queryset.order_by('-year', '-id')

class GetExamsFilterAPIView(APIView):

    def get(self, request, format=None, *args, **kwargs):

        universities = UnivExamsStructure.objects.order_by().values('university', 'siglas').distinct()
        years = Exams.objects.order_by('year').values_list('year', flat=True).distinct()

        data = {
            'universities': universities,
            'years': years
        }

        return Response(data, status=status.HTTP_200_OK)

class CoursesAPIView(generics.ListAPIView):

    serializer_class = CoursesSerializer
    pagination_class = CustomPagination

    def get_queryset(self):

        params = self.request.query_params.get('search')
        if params:
            queryset = Course.objects.filter(name__in=params)

        else:
            queryset = Course.objects.all()

        return queryset.order_by('id')

