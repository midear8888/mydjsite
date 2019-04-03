from users import views
from django.urls import path


# urlpatterns = [
#     url(r'^login', views.Login.as_view(), name="login"),
#     url(r'^signup', views.Signup.as_view(), name="signup"),
#     url(r'^about', views.AboutUs.as_view(), name="about"),
#     url(r'^home', views.Home.as_view(), name="home"),
#     url(r'^gallery', views.Gallery.as_view(), name="gallery"),
#     url(r'^history', views.History.as_view(), name="history"),
#     url(r'^test', views.Test.as_view(), name="test"),
#     url(r'^contact', views.Contact.as_view(), name="contact"),
#     url(r'^service', views.Services.as_view(), name="service"),
#     url(r'^user_center', views.UserCenter.as_view(), name="user_center"),
#     url(r'^upload', views.Upload.as_view(), name="upload"),
#     url(r'^process', views.Process.as_view(), name="process"),
#     url(r'^save_img', views.SaveImg.as_view(), name="save_img"),
#     # url(r'^analyse')
#
# ]

urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('signup/', views.Signup.as_view(), name="signup"),
    path('about/', views.AboutUs.as_view(), name="about"),
    path('', views.Home.as_view(), name="home"),
    # path('home/', views.Home.as_view(), name="home"),
    path('gallery/', views.Gallery.as_view(), name="gallery"),
    path('history/', views.History.as_view(), name="history"),
    path('test/', views.Test.as_view(), name="test"),
    path('contact/', views.Contact.as_view(), name="contact"),
    path('service/', views.Services.as_view(), name="service"),
    path('user_center/', views.UserCenter.as_view(), name="user_center"),
    path('upload/', views.Upload.as_view(), name="upload"),
    path('process/', views.Process.as_view(), name="process"),
    path('logout/', views.Logout.as_view(), name="logout"),
    # url(r'^analyse')

]
