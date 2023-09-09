from django.urls import include, path
from rest_framework.routers import DefaultRouter

from huscy.data_protection import views


router = DefaultRouter()
router.register('dataaccessrequests', views.DataAccessRequestViewSet)
router.register('datarevocationrequests', views.DataRevocationRequestViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
]
