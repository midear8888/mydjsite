from admins import views
from django.urls import path

# 应用命名空间
# app_name='admins_temp'

urlpatterns = [
    path('index/', views.Index.as_view(), name="index"),
    path('addadmin/', views.AddAdmin.as_view(), name="addadmin"),
    path('adddoctor/', views.AddDoctor.as_view(), name="adddoctor"),
    path('modify/', views.Modify.as_view(), name="modify"),
    path('edit_admin/', views.EditAdmin.as_view(), name="edit_admin"),
    path('edit_doctor/', views.EditDoctor.as_view(), name="edit_doctor"),
    path('listadmin/', views.ListAdmin.as_view(), name="listadmin"),
    path('listdoctor/', views.ListDoctor.as_view(), name="listdoctor"),
    path('listecg_img/', views.ListEcgImg.as_view(), name="listecg_img"),
    path('listecg_table/', views.ListEcgTb.as_view(), name="listecg_table"),
    path('recycle/', views.Recycle.as_view(), name="recycle"),
    path('deladmin/', views.DelAdmin.as_view(), name="del_admin"),
    path('deldoctor/', views.DelDoctor.as_view(), name="del_doctor"),
    path('admin/logout/', views.Logout.as_view(), name="logout"),

]


# urlpatterns = [
#     url(r'^index', views.Index.as_view(), name="index"),
#     url(r'^addadmin', views.AddAdmin.as_view(), name="addadmin"),
#     url(r'^adddoctor', views.AddDoctor.as_view(), name="adddoctor"),
#     url(r'^edit_admin', views.EditAdmin.as_view(), name="edit_admin"),
#     url(r'^edit_doctor', views.EditDoctor.as_view(), name="edit_doctor"),
#     url(r'^listadmin', views.ListAdmin.as_view(), name="listadmin"),
#     url(r'^listdoctor', views.ListDoctor.as_view(), name="listdoctor"),
#     url(r'^listecg_img', views.ListEcgImg.as_view(), name="listecg_img"),
#     url(r'^listecg_table', views.ListEcgTb.as_view(), name="listecg_table"),
#     url(r'^recycle', views.Recycle.as_view(), name="recycle"),
#     url(r'^deladmin', views.DelAdmin.as_view(), name="del_admin"),
#     url(r'^deldoctor', views.DelDoctor.as_view(), name="del_doctor"),
#
# ]
