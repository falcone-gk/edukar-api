from dashboard.filters import get_download_exams_filter
from dashboard.models import DownloadExams
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

# Create your views here.


class DashboardAPIView(APIView):
    permission_classes = (IsAdminUser,)

    # TODO: Finish get request
    def get(self, request):
        query_params = self.request.query_params
        filters_exams = get_download_exams_filter(query_params)
        downloads_exams = DownloadExams.objects.filter(filters_exams)
