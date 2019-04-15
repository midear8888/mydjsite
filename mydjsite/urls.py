# """mydjsite URL Configuration
#
# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/2.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
# 导入include函数使包含前后台路由
from django.urls import include, path
from django.conf.urls import url
from mydjsite import settings
from django.views.static import serve  # 导入相关静态文件处理的views控制包

# urlpatterns = [
#
#     url(r'users/', include('users.urls')),
#     url(r'admins/', include('admins.urls')),
#     url(r'admin/', admin.site.urls),
#     url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
# ]
urlpatterns = [
    path('', include('users.urls')),
    path('admins/', include('admins.urls')),
    path('admin/', admin.site.urls),
    url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# 把media设置为静态文件夹
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
