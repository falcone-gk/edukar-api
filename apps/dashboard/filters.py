from django.db.models import Q


def get_download_exams_filter(query_params):
    """
    Get the queryset after applying filters to download exams
    """

    date_start = query_params.get("date_start", None)
    date_end = query_params.get("date_end", None)

    filters = Q()

    if date_start:
        filters &= Q(downloaded_at__gte=date_start)
    if date_end:
        filters &= Q(downloaded_at__lte=date_end)

    return filters
