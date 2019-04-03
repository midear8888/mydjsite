from django.views import View
from .helper import *
from django.utils.decorators import method_decorator


@method_decorator(admin_auth, name='dispatch')
class Index(View):
    def get(self, request):
        return render(request, 'admins/index.html', INFO)

    def post(self, request):
        return render(request, 'admins/index.html', INFO)


@method_decorator(admin_auth, name='dispatch')
class AddAdmin(View):
    """添加管理员"""
    def get(self, request):
        return render(request, 'admins/addadmin.html', INFO)

    def post(self, request):
        response = add_admin_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class AddDoctor(View):
    def get(self, request):
        return render(request, 'admins/adddoctor.html', INFO)

    def post(self, request):
        response = add_doctor_handle(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class EditAdmin(View):
    def get(self, request):
        return render(request, 'admins/editadmin.html', INFO)

    def post(self, request):
        return render(request, 'admins/editadmin.html', INFO)


@method_decorator(admin_auth, name='dispatch')
class EditDoctor(View):

    def get(self, request):
        return render(request, 'admins/editdoctor.html', INFO)

    def post(self, request):
        return render(request, 'admins/editdoctor.html', INFO)


@method_decorator(admin_auth, name='dispatch')
class ListAdmin(View):
    """显示管理员列表"""
    def get(self, request):
        response = list_admin_handle(request)
        return response

    def post(self, request):
        return render(request, 'admins/listadmin.html', INFO)


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
        return render(request, 'admins/listecg_img.html', INFO)


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
        return render(request, 'admins/listadmin.html', INFO)

    def post(self, request):
        response = del_admin(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class DelDoctor(View):
    def get(self, request):
        """
        应该不会有用户直接输入这个网址来访问，即便有，那么也是返回医生列表，让他选择相应的医生删除，所以get请求直接返回医生列表给用户
        """
        return render(request, 'admins/listdoctor.html', INFO)

    def post(self, request):
        response = del_doctor(request)
        return response


@method_decorator(admin_auth, name='dispatch')
class Logout(View):
    """注销"""
    def get(self, request):
        response = redirect('/login/')  # 重定向
        response.delete_cookie('status', path='/')
        response.delete_cookie('username', path='/')
        print("用户注销")
        return response

