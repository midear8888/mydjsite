from django.views import View
from .helper import *
from django.utils.decorators import method_decorator

# Create your views here.


class Login(View):

    def get(self, request):
        try:
            is_login = request.session.get('user').get('is_login')
        except Exception as er:
            print("用户请求登录：", er)
            return render(request, 'commons/login.html', {"status": True})
        if is_login:
            return redirect('/')  # 若用户已经是登录的用户，那么就返回的是主页，否则就返回登录页面
        return render(request, 'commons/login.html', {"status": True})

    def post(self, request):
        response = login_handle(request)
        return response


class Signup(View):
    def get(self, request):
        hospitals = all_hospital()
        return render(request, 'commons/signup.html', {"status": True, "hospitals": hospitals})

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
        return render(request, 'commons/signup.html', {"status": False, "error": "未知类型用户"})  # 重定向到注册界面


@method_decorator(user_auth, name='dispatch')
class Home(View):
    def get(self, request):
        """user_info是一个字典{"truename": "", "hospital": ""}"""
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/home.html', user_info)

    def post(self, request):
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/home.html', user_info)


@method_decorator(user_auth, name='dispatch')
class AboutUs(View):
    def get(self, request):
        """user_info是一个字典{"truename": "", "hospital": ""}"""
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/about.html', user_info)

    def post(self, request):
        return render(request, 'users/about.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Contact(View):
    """联系我们，用户发邮件"""
    def get(self, request):
        """user_info是一个字典{"truename": "", "hospital": ""}"""
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/contact.html', user_info)

    def post(self, request):
        """用户是用ajax提交的"""
        response = contact_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Services(View):
    """服务？？？"""
    def get(self, request):
        """user_info是一个字典{"truename": "", "hospital": ""}"""
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/services.html', user_info)

    def post(self, request):
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/services.html', user_info)


@method_decorator(user_auth, name='dispatch')
class UserCenter(View):
    """用户个人中心"""
    def get(self, request):
        """获取用户的信息并返回"""
        user_obj = get_userinfo(request)  # 返回给用户的信息，dict
        info = {
            "data": user_obj,  # 用户对象
            "truename": user_obj.name  # 用户真实姓名
        }
        return render(request, 'users/user_center.html', info)

    def post(self, request):
        """用户修改资料"""
        response = post_userinfo(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Upload(View):
    """上传图片"""
    def get(self, request):
        """user_info是一个字典{"truename": "", "hospital": ""}"""
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/upload.html', user_info)

    def post(self, request):
        response = upload_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class History(View):
    """历史记录"""
    def get(self, request):
        response = history_get_handle(request)
        return response

    def post(self, request):
        response = history_post_handle(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Gallery(View):
    """画廊"""
    def get(self, request):
        response = gallery_handle(request)
        return response

    def post(self, request):
        return render(request, 'users/gallery.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Test(View):
    def get(self, request):
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/test.html', user_info)

    def post(self, request):
        return render(request, 'users/test.html', INFO)


@method_decorator(user_auth, name='dispatch')
class Process(View):
    """上传图片页的，请求处理图片触发的操作"""
    def get(self, request):
        flag = request.COOKIES.get('flag')
        user_info = get_truename(request, flag)
        return render(request, 'users/upload.html', user_info)

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
        # response.delete_cookie('status', path='/')
        # response.delete_cookie('username', path='/')
        response.flush()  # 删除所有cookie
        request.session.flush()  # 删除所有session
        return response




