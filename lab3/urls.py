"""
URL configuration for bmstu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from recepies import views
from rest_framework import routers
from rest_framework import permissions
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router.register(r"user", views.UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", views.GetProducts),
    # path("product/<int:id>/", views.GetProduct, name="product_url"),
    # path("delete", views.DeleteProduct),
    path("", include(router.urls)),
    path("products/", views.GetProducts, name="products-list"),
    path("products/<int:pk>", views.GetProductsById, name="get-product-by-id"),
    path("products/<int:pk>/delete", views.deleteProduct, name="delete-product"),
    path(
        "products/<int:pk>/post",
        views.PostProductToApplication,
        name="add-product-to-application",
    ),
    path("products/<int:pk>/put", views.putProducts, name="put-product"),
    path("products/post", views.PostProduct, name="post-product"),
    path("applications/", views.getApplications, name="applications-list"),
    path("applications/<int:pk>", views.getApplication, name="application"),
    path(
        "applications/<int:pk>/delete",
        views.deleteApplication,
        name="application_delete",
    ),
    path("applications/<int:pk>/put", views.putApplication, name="application_put"),
    path(
        "applications/<int:pk>/adminput",
        views.putApplicationByAdmin,
        name="application_by_admin",
    ),
    path("applications/send", views.sendApplication, name="application_by_user"),
    path(
        "application_product/<int:pk>/put",
        views.PutApplicationProduct,
        name="application_product_put",
    ),
    path(
        "application_product/<int:pk>/delete",
        views.DeleteApplicationProduct,
        name="application_product_delete",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("user_info", views.user_info, name="user_info"),
]
