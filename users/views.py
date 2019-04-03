from django.views import View
from .helper import *
from django.utils.decorators import method_decorator
from django.urls import reverse
# from users.form import *

# Create your views here.


class Login(View):

    def get(self, request):
        user_info = get_truename(request)
        return render(request, 'commons/login.html', user_info)

    def post(self, request):
        response = login_handle(request)
        return response


class Signup(View):
    def get(self, request):
        obj = Doctor()
        response = all_hospital(request)
        return render(request, 'commons/signup.html', {"hospitals": response, "obj": obj})

    def post(self, request):
        status = request.POST.get("status")  # status决定是谁注册（医院、医生、普通用户）
        if status == "1":
            print("医院注册")
            response = hospital_signup(request)
            return response
        if status == "2":
            print("医生注册")
            response = doctor_signup(request)
            return response
        if status == "3":
            print("普通用户注册")
            response = patient_signup(request)
            return response
        # 按理说是不会有这第四种情况出现的，但是以防万一
        return render(request, 'commons/login.html', INFO)


@method_decorator(user_auth, name='dispatch')
class AboutUs(View):
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/about.html', INFO)

    def post(self, request):
        return render(request, 'users/about.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Contact(View):
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/contact.html', INFO)

    def post(self, request):
        response = contact_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Services(View):
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/services.html', INFO)

    def post(self, request):
        return render(request, 'users/services.html', INFO)


@method_decorator(user_auth, name='dispatch')
class UserCenter(View):
    def get(self, request):
        response = get_userinfo(request)
        return response

    def post(self, request):
        response = post_userinfo(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Upload(View):
    def get(self, request):
        print("是get")
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/upload.html', INFO)

    def post(self, request):
        print("是post")
        response = upload_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class History(View):
    def get(self, request):
        response = history_get_handle(request)
        return response

    def post(self, request):
        response = history_post_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Home(View):
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/home.html', INFO)

    def post(self, request):
        return render(request, 'users/home.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Gallery(View):
    def get(self, request):
        response = gallery_handle(request)
        return response

    def post(self, request):
        return render(request, 'users/gallery.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Test(View):
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/test.html', INFO)

    def post(self, request):
        return render(request, 'users/test.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Process(View):
    """上传图片页的，请求处理图片触发的操作"""
    def get(self, request):
        user_info = get_truename(request)
        INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
        return render(request, 'users/upload.html', INFO)

    def post(self, request):
        # 接收ajax处理图片的请求
        response = process_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Logout(View):
    """注销"""
    def get(self, request):
        response = redirect('/login/')  # 重定向,也可以使用下面这种
        # response = redirect(reverse('users:login'))  # 这个重定向牵扯到namespace        response.delete_cookie('username', path='/')
        response.delete_cookie('status', path='/')
        response.delete_cookie('username', path='/')
        return response




