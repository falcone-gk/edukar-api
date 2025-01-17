from dashboard.models import DownloadExams
from django.contrib import admin

# Register your models here.


class DownloadExamAdmin(admin.ModelAdmin):
    list_display = ("user", "exam", "downloaded_at", "download_successful")


admin.site.register(DownloadExams, DownloadExamAdmin)
