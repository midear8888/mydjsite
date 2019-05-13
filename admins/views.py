from django.views import View
from .helper import *
from django.utils.decorators import method_decorator


class Login(View):

    def get(self, request):
        try:
            is_login = request.session.get('admin').get('is_login')
        except Exception as er:
            print("用户请求登录异常, ", er)
            return render(request, 'commons/login.html', {"status": True})
        if is_login:
            return redirect('/admins/index/')
        return render(request, 'commons/login.html', {"status": True})

    def post(self, request):
        response = login_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class Index(View):
    """主页"""
    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/index.html', info)

    def post(self, request):
        return render(request, 'admins/index.html')


@method_decorator(admin_auth, name='dispatch')
class AddAdmin(View):
    """添加管理员"""
    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status,
            "status": True  # 保证get请求时，不会将错误信息显示
        }
        return render(request, 'admins/addadmin.html', info)

    def post(self, request):
        response = add_admin_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class AddDoctor(View):
    """添加医生"""
    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status,
            "status": True,
        }
        return render(request, 'admins/adddoctor.html', info)

    def post(self, request):
        response = add_doctor_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class EditAdmin(View):
    """编辑医院"""
    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/modify.html', info)

    def post(self, request):
        response = edit_admin_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class EditDoctor(View):

    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/editdoctor.html', info)

    def post(self, request):
        response = edit_doctor_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class Modify(View):
    """医院或者管理员自己修改自己的信息"""
    def get(self, request):
        response = modify_get_handle(request)
        return response

    def post(self, request):
        print("modify_post")
        response = modify_post_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class ListAdmin(View):
    """显示管理员列表"""
    def get(self, request):
        # print('get请求listAdmin')
        response = list_admin_handle(request)
        return response

    def post(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/listadmin.html', info)


@method_decorator(admin_auth, name='dispatch')
class ListDoctor(View):
    """显示医生列表"""
    def get(self, request):
        response = list_doctor_handle(request)
        return response

    def post(self, request):
        response = list_doctor_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class ListEcgImg(View):
    """图片显示"""
    def get(self, request):
        response = ecg_img_handle(request)
        return response

    def post(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": request.COOKIES.get('status')
        }
        return render(request, 'admins/listecg_img.html', info)


@method_decorator(admin_auth, name='dispatch')
class ListEcgTb(View):
    """列表展示"""
    def get(self, request):
        response = ecg_tb_handle(request)
        return response

    def post(self, request):
        response = img_tb_post_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class Recycle(View):
    """回收站"""
    def get(self, request):
        print("get回收站")
        response = get_recycle_info(request)
        return response

    def post(self, request):
        print("post回收站")
        response = recycle_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class DelAdmin(View):
    def get(self, request):
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/listadmin.html', info)

    def post(self, request):
        # 这儿是ajax提交的， 网页并没有刷新，可以不用user_type
        response = del_admin(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class DelDoctor(View):
    def get(self, request):
        """
        应该不会有用户直接输入这个网址来访问，即便有，那么也是返回医生列表，让他选择相应的医生删除，所以get请求直接返回医生列表给用户
        """
        status = request.COOKIES.get('status')
        data = get_truename(request, status)
        info = {
            "hospital": data.get('hospital'),
            "truename": data.get('truename'),
            "user_type": status
        }
        return render(request, 'admins/listdoctor.html', info)

    def post(self, request):
        response = del_doctor(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class Logout(View):
    """注销"""
    def get(self, request):
        response = redirect('admins/login/')  # 重定向
        response.delete_cookie('status', path='/')
        del request.session["admin"]  # 删除所有的session
        print("用户注销")
        return response

