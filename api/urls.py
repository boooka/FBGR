from django.urls import path
from . import views
from . import views_mp
from . import views_ozon
from . import views_docs
from . import views_extra
from . import views_procs
from . import views_analytics

urlpatterns = [
    path('health/', views.health),
    path('mp/orders/count/value/', views_mp.mp_orders_count_value),
    path('mp/orders/count/', views_mp.mp_orders_count),
    path('mp/orders/by_status/', views_mp.mp_orders_by_status),
    path('mp/orders/by_day/', views_mp.mp_orders_by_day),
    path('mp/orders/status_by_day/', views_mp.mp_orders_status_by_day),
    path('mp/orders/list/', views_mp.mp_orders_list),
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
    # DOCS
    path('docs/count/value/', views_docs.docs_count_value),
    path('docs/count/', views_docs.docs_count),
    path('docs/by_day/', views_docs.docs_by_day),
    path('docs/by_state/', views_docs.docs_by_state),
    path('docs/state_by_day/', views_docs.docs_state_by_day),
    # MP_SUPPLIES (mp/postings, ap_logs, cashsales отключены — нет данных за 6 мес., см. check_api_data)
    path('mp/supplies/count/value/', views_extra.mp_supplies_count_value),
    path('mp/supplies/count/', views_extra.mp_supplies_count),
    path('mp/supplies/by_day/', views_extra.mp_supplies_by_day),
    path('mp/supplies/list/', views_extra.mp_supplies_list),
    # Хранимые процедуры (RPT_PAYS, RPT_PAYSPERIOD, DOC_TOTALIZE, DOC_PAY_LIST, DOC_CALCSUMTOPAY)
    path('procs/rpt_pays/', views_procs.rpt_pays),
    path('procs/rpt_paysperiod/', views_procs.rpt_paysperiod),
    path('procs/doc_totalize/', views_procs.doc_totalize),
    path('procs/doc_pay_list/', views_procs.doc_pay_list),
    path('procs/doc_calcsumtopay/', views_procs.doc_calcsumtopay),
    # Аналитика
    path('analytics/top_goods_by_quant/', views_analytics.top_goods_by_quant),
    path('analytics/heatmap_goods_by_day/', views_analytics.heatmap_goods_by_day),
    path('analytics/top_goods_by_price/', views_analytics.top_goods_by_price),
    path('analytics/revenue_by_day/', views_analytics.revenue_by_day),
]
