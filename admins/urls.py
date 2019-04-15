from admins import views
from django.urls import path


urlpatterns = [
    path('login/', views.Login.as_view(), name="admin/login"),
    path('index/', views.Index.as_view(), name="index"),  # 主页
    path('addadmin/', views.AddAdmin.as_view(), name="addadmin"),  # 增加管理员
    path('adddoctor/', views.AddDoctor.as_view(), name="adddoctor"),  # 增加医生
    path('modify/', views.Modify.as_view(), name="modify"),  # 修改个人资料
    path('edit_admin/', views.EditAdmin.as_view(), name="edit_admin"),  # 医院修改管理员资料
    path('edit_doctor/', views.EditDoctor.as_view(), name="edit_doctor"),  # 修改医生资料
    path('listadmin/', views.ListAdmin.as_view(), name="listadmin"),  # 管理员列表
    path('listdoctor/', views.ListDoctor.as_view(), name="listdoctor"),  # 医生列表
    path('listecg_img/', views.ListEcgImg.as_view(), name="listecg_img"),  # 图片展示模式
    path('listecg_table/', views.ListEcgTb.as_view(), name="listecg_table"),  # 列表展示ecg图片模式
    path('recycle/', views.Recycle.as_view(), name="recycle"),  # 图片的回收站
    path('deladmin/', views.DelAdmin.as_view(), name="del_admin"),  # 删除管理员
    path('deldoctor/', views.DelDoctor.as_view(), name="del_doctor"),  # 删除医生
    path('logout/', views.Logout.as_view(), name="back_logout"),  # 注销

]

