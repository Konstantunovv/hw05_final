from django.conf import settings
from django.core.paginator import Paginator


def paginator(object_list, request):
    # Paginator
    return Paginator(object_list, settings.PAGE_COUNT).get_page(
        request.GET.get("page")
    )
