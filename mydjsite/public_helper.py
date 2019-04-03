from admins.models import *
from users.models import *
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage


INFO = {
    "head_title": "心电图管理仓库",
}


def get_truename(request):
    """得到用户的真实姓名"""
    username = request.COOKIES.get("username")
    status = request.COOKIES.get("status")
    try:
        if status == "2":
            # 医生
            obj = Doctor.objects.filter(username=username).first()
            INFO["truename"] = obj.name  # 真实姓名
        if status == "3":
            # 患者
            obj = Patient.objects.filter(username=username).first()
            INFO["truename"] = obj.name  # 真实姓名
        if INFO.get("truename"):
            return INFO
        else:
            INFO["truename"] = "Personal"
            return INFO
    except Exception as er:
        print("获取用户真名失败：", er)
        return {"truename": "Personal"}


def get_page(request, data, page_count):
    """
    分页共用函数
    :param request:
    :param data: 数据库读取的，要显示在前端的内容，是一个list
    :param page_count: 每页最多显示多少内容
    :return:
    """
    after_range_num = 3  # 当前页前最多显示三页
    before_range_num = 3  # 当前页后最多显示三页
    try:
        page = int(request.GET.get('page', '1'))
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(data, page_count)  # 每页显示page_count条数据
    try:
        results = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        results = paginator.page(1)
    if page >= after_range_num:
        page_range = paginator.page_range[page - after_range_num:page + before_range_num]  # 没有这句，那么page_range表示的就是所有页的列表
    else:
        page_range = paginator.page_range[0:int(page) + before_range_num]
    return results, page_range


def hospital_id(request):
    """获取当前登录者医院的名字，这个函数只能是用户是医生或者后台人员登录时的情况下调用"""
    username = request.COOKIES.get("username")
    status = request.COOKIES.get("status")
    try:
        hospt_id = None  # 先给一个默认值
        if status == "1":
            # 登录者为医院
            obj = Hospital.objects.filter(username=username).first()
            hospt_id = obj.id
        elif status == "0":
            # 登录者为管理员
            obj = HospitalAdmin.objects.filter(username=username).first()
            hospt_id = obj.hid
        elif status == "2":
            # 登录者为医生
            obj = Doctor.objects.filter(username=username).first()
            hospt_id = obj.hid
        return hospt_id
    except Exception as er:
        print("获取医院名错误>>", er)
        return None


def all_hospital(request):
    """获取所有医院名，主要是登录时，将这些信息给医生用户，以供其选择。"""
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    hospitals_obj = Hospital.objects.all()
    hospitals = list()
    print(hospitals, hospitals_obj)
    for hospital in hospitals_obj:
        hospitals.append(hospital.h_name)
    print("到这儿了")
    return hospitals  # 返回医院列表是为了让用户选择所属医院


def set_user_info(request, index, status, user):
    """
    设置登录用户的信息，cookie等;
    index: 模板文件
    status: 用户类型
    user: 用户名
    """
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    INFO['status'] = status
    INFO['username'] = user
    response = render(request, index, INFO)
    response.set_cookie('status', status)
    response.set_cookie('username', user)
    return response


def hospital_signup(request):
    h_username = request.POST.get("h_username")  # 医院名称
    username = request.POST.get("h_phone")  # 手机号码，也是用户登录医院的账号
    h_password = request.POST.get("h_password")  # 登录密码
    h_address = request.POST.get("h_address")  # 医院地址
    try:
        hospital = Hospital.objects.filter(h_name=h_username)
        if hospital:
            print("该医院已经注册过")
            INFO["status"] = "0"
            INFO["error"] = "该医院已经注册"
            return render(request, 'commons/signup.html', INFO)
        hospital = Hospital.objects.filter(username=username)
        if hospital:
            hospt = hospital[0].h_name  # 获取医院名
            print("该手机号已经在注册了医院{}".format(hospt))
            INFO["status"] = "0"
            INFO["error"] = "该手机号已经注册了医院{}".format(hospt)
            return render(request, 'commons/signup.html', INFO)
        print("新医院注册")
        Hospital.objects.create(h_name=h_username, username=username, password=h_password, h_add=h_address)
        response = set_user_info(request, 'admins/index.html', "1", username)  # 医院注册，所以status是1
        return response
    except Exception as er:
        print("读取Hospital表失败", er)
        INFO["status"] = "0"
        INFO["error"] = "服务器出错，注册失败"
        return render(request, "commons/signup.html", INFO)


def doctor_signup(request):
    username = request.POST.get("d_phone")  # 电话号码，作为用户登录名
    d_password = request.POST.get("d_password")  # 密码
    fromwhere = request.POST.get("fromwhere")  # 所属医院
    truename = request.POST.get("truename")  # 真实姓名
    d_gender = request.POST.get("d_gender")  # 性别
    d_age = request.POST.get("d_age")  # 年龄
    d_email = request.POST.get("d_email")  # 邮箱
    details = request.POST.get("details")  # 自我描述
    try:
        rst = Hospital.objects.filter(h_name=fromwhere).first()  # 获取该医生所属医院的对象
        h_id = rst.id  # 获取该医院id, int型
        info = {
            "hid": h_id,
            "username": username,
            "password": d_password,
            "gender": d_gender,
            "age": d_age,
            "email": d_email,
            "name": truename,
            "details": details,
        }
        # print(info)
        Doctor.objects.create(**info)  # **info指定传入的是一个字典
        response = set_user_info(request, 'users/index.html', "2", username)
        return response
    except Exception as er:
        print("医生注册出错: ", er)
        INFO["status"] = str(0)
        hospitals = all_hospital(request)  # 调用函数，并让用户重新回到登录页面
        INFO["hospitals"] = hospitals
        return render(request, "commons/signup.html", INFO)


def patient_signup(request):
    username = request.POST.get("username")  # 手机号，也是用户名
    password = request.POST.get("password2")  # 密码
    name = request.POST.get("truename")  # 真实姓名
    gender = request.POST.get("psex")  # 性别
    age = request.POST.get("age")  # 年龄
    email = request.POST.get("email")  # 邮箱
    details = request.POST.get("details")  # 自我描述
    try:
        info = {
            "username": username,
            "password": password,
            "gender": gender,
            "email": email,
            "name": name,
            "details": details,
            "age": age
        }
        Patient.objects.create(**info)  # 添加数据
        response = set_user_info(request, 'users/home.html', "3", username)
        return response
    except Exception as er:
        print("患者注册失败: ", er)
        INFO["status"] = str(0)
        return render(request, 'commons/signup.html', INFO)


def login_handle(request):
    username = request.POST.get("username")  # 用户名就是手机号
    password = request.POST.get("password")
    status = request.POST.get("status")
    try:
        if status == "1":
            print("医院或者医院管理员登录")
            obj = Hospital.objects.filter(username=username)
            if obj:
                """该医院存在"""
                obj = obj.filter(password=password)
                if not obj:
                    # 密码错误
                    INFO["status"] = "0"
                    INFO["error"] = "用户名或密码错误"
                    return render(request, 'commons/login.html', INFO)
                response = set_user_info(request, 'admins/index.html', status, username)
                response.set_cookie('user_type', "Hospital")  # 给医院添加标记
            else:
                # 看是否是管理员
                obj = HospitalAdmin.objects.filter(username=username)
                if not obj:
                    # 医院和管理中都找不到，说明没有注册
                    INFO["status"] = "0"
                    INFO["error"] = "该用户尚未注册"
                    return render(request, "commons/login.html", INFO)
                obj = obj.filter(password=password)
                if obj:
                    """说明是管理员"""
                    status = "0"  # 让0代表管理员
                    response = set_user_info(request, 'admins/index.html', status, username)
                    response.set_cookie('user_type', "Admin")
                else:
                    print("用户名或密码错误")
                    INFO["error"] = "用户名或密码错误！"
                    INFO["status"] = str(0)
                    response = render(request, 'commons/login.html', INFO)
        elif status in ["2", "3"]:
            if status == "2":
                print("医生登录")
                obj = Doctor.objects.filter(username=username)
                if not obj:
                    # 用户未注册
                    INFO["status"] = "0"
                    INFO["error"] = "该用户尚未注册"
                    return render(request, "commons/login.html", INFO)
            else:
                print("患者登录")
                obj = Patient.objects.filter(username=username, password=password)
                if not obj:
                    # 用户未注册
                    INFO["status"] = "0"
                    INFO["error"] = "该用户尚未注册"
                    return render(request, "commons/login.html", INFO)
            if obj:
                print("用户名存在，验证密码")
                obj = obj.filter(password=password)
                if obj:
                    # 密码正确
                    response = set_user_info(request, 'users/home.html', status, username)
                    response.set_cookie('user_type', "Doctor") if status == "2" else response.set_cookie("user_type", "Patient")
                else:
                    print("用户名或密码错误")
                    INFO["error"] = "用户名或密码错误!"
                    INFO["status"] = str(0)
                    response = render(request, 'commons/login.html', INFO)
        else:
            print("莫名其妙的错")
            INFO["status"] = "0"
            response = render(request, "commons/login.html", INFO)
        return response
    except Exception as e:
        print("登录过程出错：", e)
        INFO["status"] = str(0)
        return render(request, "commons/login.html", INFO)
