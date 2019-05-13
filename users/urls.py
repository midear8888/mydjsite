from users import views
from django.urls import path


urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),  # 登录
    path('signup/', views.Signup.as_view(), name="signup"),  # 注册
    path('about/', views.AboutUs.as_view(), name="about"),  # 关于我们
    path('', views.Home.as_view(), name="home"),  # 主页
    # path('home/', views.Home.as_view(), name="home"),
    path('gallery/', views.Gallery.as_view(), name="gallery"),  # 画廊
    path('history/', views.History.as_view(), name="history"),  # 历史记录
    path('test/', views.Test.as_view(), name="test"),
    path('contact/', views.Contact.as_view(), name="contact"),  # 联系我们
    path('service/', views.Services.as_view(), name="service"),
    path('user_center/', views.UserCenter.as_view(), name="user_center"),  # 用户中心
    path('upload/', views.Upload.as_view(), name="upload"),  # 上传图片
    path('process/', views.Process.as_view(), name="process"),  # 处理图片
    path('logout/', views.Logout.as_view(), name="logout"),  # 注销
    path('cutimg/', views.cutimg, name="cutimg"),  # 注销
    # url(r'^analyse')

]
