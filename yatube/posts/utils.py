from django.conf import settings
from django.core.paginator import Paginator


def paginator_posts(__all__, request):
    # Paginator
    paginator = Paginator(__all__, settings.PAGE_COUNT)
    return paginator.get_page(request.GET.get("page"))
