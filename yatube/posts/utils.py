from django.conf import settings as st
from django.core.paginator import Paginator


def paginator_func(post_list, request):
    # Paginator
    paginator = Paginator(post_list, st.PAGE_COUNT)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)