from dashboard.filters import get_download_exams_filter
from dashboard.models import DownloadExams
from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.


class DashboardAPIView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        query_params = self.request.query_params

        # Filter exams based on custom function or additional logic
        filters_exams = get_download_exams_filter(query_params)
        downloads_exams = DownloadExams.objects.filter(filters_exams)

        # Aggregations for plots
        downloads_by_day = (
            downloads_exams.annotate(day=TruncDay("downloaded_at"))
            .values("day")
            .annotate(total_downloads=Count("id"))
            .order_by("day")
        )

        downloads_by_month = (
            downloads_exams.annotate(month=TruncMonth("downloaded_at"))
            .values("month")
            .annotate(total_downloads=Count("id"))
            .order_by("month")
        )

        downloads_by_exam = (
            downloads_exams.values("exam__title")
            .annotate(total_downloads=Count("id"))
            .order_by("-total_downloads")
        )

        success_rate = downloads_exams.aggregate(
            successful_downloads=Count(
                "id", filter=Q(download_successful=True)
            ),
            failed_downloads=Count("id", filter=Q(download_successful=False)),
        )

        response_data = {
            "downloads_by_day": list(downloads_by_day),
            "downloads_by_month": list(downloads_by_month),
            "downloads_by_exam": list(downloads_by_exam),
            "success_rate": {
                "successful_downloads": success_rate["successful_downloads"],
                "failed_downloads": success_rate["failed_downloads"],
            },
        }

        return Response(response_data)
