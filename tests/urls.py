from django.conf import settings
from django.urls import include, path
from django.contrib import admin

# from wagtail.admin import urls as wagtailadmin_urls
# from wagtail.core import urls as wagtail_urls
# from wagtail.documents import urls as wagtaildocs_urls

from .api import api_router

urlpatterns = [
    # path("admin/", include(wagtailadmin_urls)),
    path("api/v2/", api_router.urls),
    # path("", include(wagtail_urls)),
]

urlpatterns = urlpatterns + []
