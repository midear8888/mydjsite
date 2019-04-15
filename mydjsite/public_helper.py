from admins.models import *
from users.models import *
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect


INFO = {
    "head_title": "心电图管理仓库",
}


def get_truename(request, status):
    """得到用户的真实姓名和医院名，如果是前台人员的话，则不获取医院名"""
    if status in ["0", "1"]:
        try:
            # 后台人员
            hospital_id = request.session.get('admin').get('hospital_id')  # 后台人员的医院的id
            hospital_obj = Hospital.objects.filter(id=hospital_id).first()
            hospital = hospital_obj.name  # 医院名
            user_id = request.session.get('admin').get('user_id')  # 后台登录人员的id
            if status == "0":
                # 管理员
                obj = HospitalAdmin.objects.filter(id=user_id).first()
                return {"truename": obj.name, "hospital": hospital}
            else:
                # 医院
                # 医院的特殊之处在于，他的名字就是医院名，所以truename和hospital都是医院名
                return {"hospital": hospital, "truename": hospital}
        except Exception as er:
            # 这儿出错的原因是因为字典两次用get方法，如果第一个get没有获取到值，那么就会报错：NoneType not attribute 'get'
            print("获取真实姓名出错(后台人员的session丢失)：", er)
            return {"hospital": None, "truename": None}
    else:
        try:
            user_id = request.session.get('user').get('user_id')  # 前台登录人员的id
            if status == "2":
                # 医生，前台
                obj = Doctor.objects.filter(id=user_id).first()  # 用户真实姓名
                return {"truename": obj.name}
            else:
                # 患者,
                obj = Patient.objects.filter(id=user_id).first()
                return {"truename": obj.name}
        except Exception as er:
            print("获取真实姓名出错（前台人员的session丢失): ", er)
            return {"truename": None}


def get_page(request, data, page_count):
    """
    分页共用函数
    :param request:
    :param data: 数据库读取的，要显示在前端的内容，是一个list，
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


def all_hospital():
    """获取所有医院名，主要是登录时，将这些信息给医生用户，以供其选择。"""
    hospitals_obj = Hospital.objects.all()
    hospitals = list()
    for hospital in hospitals_obj:
        hospitals.append(hospital.name)
    return hospitals  # 返回医院列表是为了让用户选择所属医院


def set_user_info(request, status, username):
    """
    设置登录用户的信息，cookie等;
    index: 模板文件
    status: 用户类型
    user: 用户名
    """
    try:
        if status in ["0", "1"]:
            # 后台人员
            info = {}
            if status == "0":
                # 管理员
                response = redirect('/admins/index/')  # 重定向
                obj = HospitalAdmin.objects.filter(username=username).first()
                hospital = Hospital.objects.filter(id=obj.hid).first()
                info["hospital_id"] = hospital.id  # 医院id
                response.set_cookie('status', '0')
            else:
                # 医院
                response = redirect('/admins/index/')  # 医院，所以重定向到Index
                obj = Hospital.objects.filter(username=username).first()
                info["hospital_id"] = obj.id  # 医院id
                response.set_cookie('status', "1")
            info["user_id"] = obj.id
            info["is_login"] = True
            request.session["admin"] = info  # 当前登录的用户的类型
        else:
            # 前台人员
            info = {}
            if status == "2":
                # 医生
                response = redirect('/')  # 医生，所以重定向到home
                obj = Doctor.objects.filter(username=username).first()
                response.set_cookie('flag', '2')
            else:
                # 患者
                response = redirect('/')  # 患者，所以重定向到home
                obj = Patient.objects.filter(username=username).first()
                response.set_cookie('flag', '3')
            info["user_id"] = obj.id  # 用户id
            info["is_login"] = True
            request.session["user"] = info
        return response
    except Exception as er:
        print("set_user_info出错：", er)
        return render(request, 'commons/signup.html', {"status": False, "error": er})  # 返回注册页面，显示错误信息


def hospital_signup(request):
    """医院注册"""
    hospital_name = request.POST.get("h_username")  # 医院名称
    username = request.POST.get("h_phone")  # 手机号码，也是用户登录医院的账号
    password = request.POST.get("h_password")  # 登录密码
    address = request.POST.get("h_address")  # 医院地址
    password = make_password(password)  # 密码加密
    try:
        hospital = Hospital.objects.filter(name=hospital_name)
        if hospital:
            print("医院已被注册过")
            info = {
                "status": False,
                "error": "该医院已经被注册过了",
                "hospitals": all_hospital()
            }
            return render(request, 'commons/signup.html', info)
        hospital = Hospital.objects.filter(username=username).first()
        if hospital:
            """该手机号已经被注册了"""
            name = hospital.name  # 获取医院名
            print("该手机号已经注册了医院{}".format(name))
            info = {
                "status": False,
                "error": "手机号{}已经注册了医院{}".format(username, name),
                "hospitals": all_hospital()
            }
            return render(request, 'commons/signup.html', info)
        Hospital.objects.create(name=hospital_name, username=username, password=password, address=address)
        response = set_user_info(request, "1", username)  # 医院注册，所以status是1
        print("新医院'{}'注册成功".format(hospital_name))
        return response
    except Exception as er:
        print("读取Hospital表失败", er)
        hospitals = all_hospital()
        info = {
            "status": False,
            "error": "服务器出错，注册失败",
            "hospitals": hospitals
        }
        return render(request, "commons/signup.html", info)


def doctor_signup(request):
    """医生注册"""
    username = request.POST.get("d_phone")  # 电话号码，作为用户登录名
    password = request.POST.get("d_password")  # 密码
    fromwhere = request.POST.get("fromwhere")  # 所属医院
    truename = request.POST.get("truename")  # 医生的真实姓名
    gender = request.POST.get("d_gender")  # 性别
    age = request.POST.get("d_age")  # 年龄
    position = request.POST.get('d_position')  # 医生的职位
    email = request.POST.get("d_email")  # 邮箱
    details = request.POST.get("details")  # 自我描述
    password = make_password(password)  # 密码加密
    try:
        obj = Doctor.objects.filter(username=username).first()
        if obj:
            print("医生注册，但是用户名'{}'已经存在".format(username))
            results = {
                "status": False,
                "error": "该用户名已经存在",
                "hospitals": all_hospital()
            }
            return render(request, 'commons/signup.html', results)
        rst = Hospital.objects.filter(name=fromwhere).first()  # 获取该医生所属医院的对象
        h_id = rst.id  # 获取该医院id, int型
        info = {
            "hid": h_id,
            "username": username,
            "password": password,
            "gender": gender,
            "age": age,
            "position": position,
            "email": email,
            "name": truename,
            "details": details,
        }
        print("医生注册信息：", info)
        Doctor.objects.create(**info)  # **info指定传入的是一个字典
        response = set_user_info(request, "2", username)
        return response
    except Exception as er:
        print("医生注册出错: ", er)
        hospitals = all_hospital()  # 调用函数，并让用户重新回到登录页面
        info = {
            "status": False,
            "error": "医生注册处失败：".format(er),
            "hospitals": hospitals
        }
        return render(request, "commons/signup.html", info)


def patient_signup(request):
    """患者注册"""
    username = request.POST.get("username")  # 手机号，也是用户名
    password = request.POST.get("password2")  # 密码
    name = request.POST.get("truename")  # 真实姓名
    gender = request.POST.get("psex")  # 性别
    age = request.POST.get("age")  # 年龄
    email = request.POST.get("email")  # 邮箱
    details = request.POST.get("details")  # 自我描述
    password = make_password(password)  # 加密密码
    try:
        obj = Patient.objects.filter(username=username).first()
        if obj:
            print("患者注册，但是用户名'{}'已经存在".format(username))
            results = {
                "status": False,
                "error": "该用户名已经存在",
                "hospitals": all_hospital()
            }
            return render(request, 'commons/signup.html', results)
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
        response = set_user_info(request, "3", username)
        return response
    except Exception as er:
        print("患者注册失败: ", er)
        info = {
            "status": False,
            "error": "注册失败",
            "hospitals": all_hospital()
        }
        return render(request, 'commons/signup.html', info)


def login_handle(request):
    username = request.POST.get("username")  # 用户名就是手机号
    password = request.POST.get("password")
    status = request.POST.get("status")
    try:
        if status == "1":
            print("医院或者医院管理员登录")
            obj = Hospital.objects.filter(username=username).first()
            if obj:
                print("医院请求登录")
                # obj = obj.filter(password=password)
                if not check_password(password, obj.password):
                    # 密码错误
                    return render(request, 'commons/login.html', {"status": False, "error": "用户名或密码错误"})
                else:
                    # 用户名和密码都正确，允许登录
                    response = set_user_info(request, status, username)
                    return response
            else:
                print("不是医院，开始验证是否是管理员")
                obj = HospitalAdmin.objects.filter(username=username).first()
                if not obj:
                    # 医院和管理中都找不到，说明没有注册
                    info = {
                        "status": False,
                        "error": "该用户尚未自注册"
                    }
                    return render(request, "commons/login.html", info)
                if check_password(password, obj.password):
                    """密码验证通过，说明是管理员"""
                    status = "0"  # 让0代表管理员
                    response = set_user_info(request, status, username)
                    return response
                else:
                    print("用户名或密码错误")
                    info = {
                        "status": False,
                        "error": "用户名或密码错误"
                    }
                    response = render(request, 'commons/login.html', info)
                    return response
        elif status == "2":
            print("医生登录")
            obj = Doctor.objects.filter(username=username).first()
            if not obj:
                # 用户未注册
                info = {
                    "status": False,
                    "error": "该用户尚未注册"
                }
                return render(request, "commons/login.html", info)
            # 用户名存在，验证密码
            if check_password(password, obj.password):
                print("用户名和密码都正确，允许登录")
                response = set_user_info(request, status, username)
                return response
            else:
                print("密码错误")
                info = {
                    "status": False,
                    "error": "密码错误"
                }
                return render(request, 'commons/login.html', info)
        elif status == "3":
            print("患者登录")
            obj = Patient.objects.filter(username=username).first()
            if not obj:
                # 用户未注册
                info = {
                    "status": False,
                    "error": "该用户尚未注册"
                }
                return render(request, 'commons/login.html', info)
            # 用户名存在，验证密码
            if check_password(password, obj.password):
                print("用户名和密码都正确，允许登录")
                response = set_user_info(request, status, username)
                return response
            else:
                print("密码错误")
                info = {
                    "status": False,
                    "error": "密码错误"
                }
                return render(request, 'commons/login.html', info)
        else:
            print("未知用户类型错误")
            INFO["status"] = "0"
            info = {
                "status": False,
                "error": "未知用户类型错误"
            }
            response = render(request, "commons/login.html", info)
            return response
    except Exception as e:
        print("登录过程中，服务器出错：", e)
        info = {
            "status": False,
            "error": "服务器响应失败"
        }
        return render(request, "commons/login.html", info)
