from core.paginators import CustomPagination
from rest_framework import generics
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
        # type: this is 'exam_type' field
        # area: this is 'area' field

        queryset = Exams.objects.all()

        # Get query params to filter
        univ = self.request.query_params.get('univ')
        type_ = self.request.query_params.get('type')
        area = self.request.query_params.get('area')

        if univ is not None:
            queryset = queryset.filter(root__siglas=univ)
        if type_ is not None:
            queryset = queryset.filter(root__exam_type=type_)
        if area is not None:
            queryset = queryset.filter(root__area=area)

        return queryset.order_by('-id')
        