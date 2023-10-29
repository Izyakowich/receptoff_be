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
from bmstu_lab import views
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.GetProducts),
    path("product/<int:id>/", views.GetProduct, name="product_url"),
    path("delete", views.DeleteProduct),

    path('', include(router.urls)),
    path('products/', views.GetProductss, name="products-list"),
    path('products/<int:pk>', views.GetProductsById, name="get-product-by-id"),
    path('products/<int:pk>/delete', views.deleteProduct, name="delete-product"),
    path('products/<int:pk>/post', views.PostProductToApplication, name="add-product-to-application"),
    path('products/<int:pk>/put', views.putProducts, name="put-product"),
    path('products/post', views.PostProduct, name="post-product"),

    path('applications', views.getApplications, name = 'applications-list'),
    path('applications/<int:pk>', views.getApplication, name = 'application'),
    path('applications/<int:pk>/delete', views.deleteApplication, name = 'application_delete'),
    path('applications/<int:pk>/put', views.putApplication, name = 'application_put'),

    path('applications/<int:pk>/adminput', views.putApplicationByAdmin, name = 'application_by_admin'),
    path('applications/userput', views.putApplicationByUser, name = 'application_by_user'),

    path('application_product/<int:pk>/put', views.PutApplicationProduct, name = 'application_product_put'),
    path('application_product/<int:pk>/delete', views.DeleteApplicationProduct, name = 'application_product_delete'),

]
