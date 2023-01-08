from core.paginators import CustomPagination
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from services.serializers import ExamsSerializer
from services.models import Exams, UnivExamsStructure

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

        if (univ is not None) and (univ != ''):
            queryset = queryset.filter(root__siglas=univ)
        if (year is not None) and (year != '0'):
            queryset = queryset.filter(year=year)

        return queryset.order_by('-year')

class GetExamsFilterAPIView(APIView):

    def get(self, request, format=None, *args, **kwargs):

        universities = UnivExamsStructure.objects.order_by().values('university', 'siglas').distinct()
        years = Exams.objects.order_by('year').values_list('year', flat=True).distinct()

        data = {
            'universities': universities,
            'years': years
        }

        return Response(data, status=status.HTTP_200_OK)