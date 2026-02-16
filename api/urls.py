from django.urls import path
from . import views
from . import views_mp
from . import views_ozon

urlpatterns = [
    path('health/', views.health),
    path('mp/orders/count/value/', views_mp.mp_orders_count_value),
    path('mp/orders/count/', views_mp.mp_orders_count),
    path('mp/orders/by_status/', views_mp.mp_orders_by_status),
    path('mp/orders/by_day/', views_mp.mp_orders_by_day),
    path('mp/orders/status_by_day/', views_mp.mp_orders_status_by_day),
    path('mp/docsumjoins/summary/', views_mp.docsumjoins_summary),
    path('mp/docsumjoins/by_day/', views_mp.docsumjoins_by_day),
    path('mp/docitemssumjoins/summary/', views_mp.docitemssumjoins_summary),
    path('mp/docitemssumjoins/by_day/', views_mp.docitemssumjoins_by_day),
    # MP_OZON_GOODS_EX
    path('mp/ozon_goods/count/', views_ozon.ozon_goods_count),
    path('mp/ozon_goods/by_flags/', views_ozon.ozon_goods_by_flags),
    path('mp/ozon_goods/by_day/', views_ozon.ozon_goods_by_day),
    path('mp/ozon_goods/quant_by_day/', views_ozon.ozon_goods_quant_by_day),
    path('mp/ozon_goods/list/', views_ozon.ozon_goods_list),
]
