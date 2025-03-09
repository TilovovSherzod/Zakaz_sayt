"""
Asosiy ilova URL konfiguratsiyasi
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.asosiy, name='asosiy'),
    path('maxsulot/<int:maxsulot_id>/', views.maxsulot_tafsilotlari, name='maxsulot_tafsilotlari'),
    path('savat/', views.savat, name='savat'),
    path('savatga-qoshish/', views.savatga_qoshish, name='savatga_qoshish'),
    path('savat-yangilash/', views.savat_yangilash, name='savat_yangilash'),
    path('savat-tozalash/', views.savat_tozalash, name='savat_tozalash'),
    path('buyurtma-yaratish/', views.buyurtma_yaratish, name='buyurtma_yaratish'),
    path('buyurtma-tasdiqlandi/<int:buyurtma_id>/', views.buyurtma_tasdiqlandi, name='buyurtma_tasdiqlandi'),
    path('buyurtmalarim/', views.buyurtmalarim, name='buyurtmalarim'),

    # Yangi URL manzillar
    path('kassa/', views.kassa, name='kassa'),
    path('kassa/barcode-qidirish/', views.barcode_qidirish, name='barcode_qidirish'),
    path('kassa/savdo-yaratish/', views.savdo_yaratish, name='savdo_yaratish'),
    path('hisobotlar/', views.hisobotlar, name='hisobotlar'),
    path('hisobotlar/savdo/', views.savdo_hisoboti, name='savdo_hisoboti'),
    path('hisobotlar/ombor/', views.ombor_hisoboti, name='ombor_hisoboti'),
    path('ombor/', views.ombor, name='ombor'),
    path('ombor/kirim/', views.ombor_kirim, name='ombor_kirim'),
    path('ombor/chiqim/', views.ombor_chiqim, name='ombor_chiqim'),
    path('ombor/inventarizatsiya/', views.ombor_inventarizatsiya, name='ombor_inventarizatsiya'),
]

