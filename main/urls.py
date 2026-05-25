from django.urls import path
from . import views

#Для генерации пространства имен, чтобы могли обращаться к определенным функциям для генерации url в шаблоне
app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name = 'index'),
    path('catalog/',views.CatalogView.as_view(), name = 'catalog_all'),
    #Для фильтрации по категориям
    path('catalog/<slug:category_slug>/', views.CatalogView.as_view(), name='catalog'),
    # product/<slug:slug> - это форматирование url, чтобы он принимал только те значения, что заданы
    path('product/<slug:slug>', views.ProductDetailView.as_view(), name = 'product_detail'),
]