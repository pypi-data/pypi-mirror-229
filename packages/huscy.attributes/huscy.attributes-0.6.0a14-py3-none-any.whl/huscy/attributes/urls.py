from django.urls import include, path
from rest_framework.routers import DefaultRouter

from huscy.attributes import views


router = DefaultRouter()
router.register('attributesets', views.AttributeSetViewSet, basename='attributeset')

urlpatterns = [
    path('api/attributeschema/', views.AttributeSchemaView.as_view(), name='attributeschema'),
    path('api/', include(router.urls)),
]
