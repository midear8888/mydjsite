from mydjsite.public_helper import *
import os
from django.shortcuts import HttpResponse, redirect
import json


"""
所有用户，登录成功之后，都会有以下四个标记来验明身份
user_status: 用户类型,(0是管理员， 1是医院， 2是医生，3是普通用户)
username: 用户名（手机号），用作表查询的依据
user_type: 用户类型，和user_status所不同的是，标记是（医院是"Hospital", 管理员是"Admin", 医生是"Doctor", 普通用户是"Patient"）
"""

BASE_DIR = os.getcwd()
INFO = {
    "head_title": "心电图管理仓库",
}


def admin_auth(func):
    """用来装饰，验证用户是不是医院"""
    def inner(request, *args, **kwargs):
        v = request.COOKIES.get("status")
        print(request.session.get('admin'))
        print("status:", v)
        try:
            is_login = request.session.get('admin').get('is_login')  # 获取登录状态
            print("is_login:", is_login)
            if is_login and v == "1" or v == "0":  # 保证只能是医院或者管理员可以访问
                print("返回")
                return func(request, *args, **kwargs)
            return redirect('/admins/login/')  # 重定向
        except Exception as err:
            print("后台用户尚未登录：", err)
            return redirect('/admins/login/')  # 重定向
    return inner


def all_username():
    """得到后台所有人员的手机号，用户在修改管理员时，验证修改的手机号是否已经存在"""
    phones = []
    hospital_phones = Hospital.objects.all()
    for phone in hospital_phones:
        phones.append(phone.username)   # 所有医院的账号
    admin_phones = HospitalAdmin.objects.all()
    for phone in admin_phones:
        phones.append(phone.username)  # 所有管理员的账号
    return phones


def hospital_info(request):
    """得到医院id和所有的管理员对象"""
    try:
        hospital_id = request.session.get('admin').get('hospital_id')  # 医院id
        admins_obj = HospitalAdmin.objects.filter(hid=hospital_id)  # 获取该医院的所有管理员对象
        # print("hospital_info返回：", {"hospital_id": hospital_id, "admins": admins_obj})
        return {"hospital_id": hospital_id, "admins": admins_obj}
    except Exception as er:
        print("获取医院id和管理员对象失败：", er)
        return {"hospital_id": None, "admins": None}


def all_doctor(request):
    """得到该医院下的所有的医生对象"""
    hospital_id = request.session.get('admin').get('hospital_id')  # 得到医院id
    obj = Doctor.objects.filter(hid=hospital_id)
    return obj


def edit_admin_handle(request):
    """编辑管理员信息,只有医院有这个权限"""
    try:
        uid = int(request.POST.get("id"))  # 该id就是要修改的管理员的id,因为该获取到的值是一个字符串，但是用id查数据表时，这个id得是一个整型，所以这儿要先转化为整数
    except Exception as er:
        print("医生要修改管理员的资料，但是未获取到管理员的id：", er)
        return HttpResponse(json.dumps({"status": False, "edit_error": "未获取到改管理员id"}))
    # print(uid)
    name = request.POST.get("name")
    username = request.POST.get("phone")  # 用户名
    password = request.POST.get("pwd")
    position = request.POST.get('position')  # 职位
    email = request.POST.get("email")
    details = request.POST.get("details")
    data = {}
    phones = all_username()  # 获取后台所有人员的账号
    if name:
        data["name"] = name  # 姓名
    if username:
        data["username"] = username  # 修改用户名
    if password:
        data["password"] = make_password(password)  # 加密密码
    if position:
        data["position"] = position  # 职位
    if email:
        data["email"] = email  # 修改邮箱
    if details:
        data["details"] = details
    print(data)
    status = request.COOKIES.get('status')
    try:
        old_username = HospitalAdmin.objects.filter(id=uid).first().username
        phones.remove(old_username)  # 排除当前的账号
        if username in phones:
            # 判断用户修改的这个账号是否是别人的账号，如果是，则报错
            """该用户名已经存在，不允许这样修改资料"""
            print("无法修改账号为已经别人的账号")
            results = {
                "status": False,
                "edit_error": "该用户名已经存在",
                "user_type": status
            }
            return HttpResponse(json.dumps(results))
        else:
            print("修改管理员资料")
            HospitalAdmin.objects.filter(id=uid).update(**data)  # 修改信息
            results = {
                "status": True,
                "edit_error": None,  # 医院编辑管理员信息的错误信息，因为没错，所以为None
                "user_type": status
            }
            return HttpResponse(json.dumps(results))
    except Exception as er:
        print("编辑管理员信息失败：", er)
        results = {
            "status": False,
            "edit_error": "服务器响应失败",
            "user_type": status
        }
    return HttpResponse(json.dumps(results))


def list_admin_handle(request):
    """获取管理列表的post处理函数, 只能是后台人员能调用"""
    status = request.COOKIES.get('status')
    info = get_truename(request, status)
    data = hospital_info(request)  # 返回的是一个字典，能获取hospital_id, admins_obj
    results = {
        "hospital": info.get('hospital'),
        "truename": info.get('truename'),
        "user_type": request.COOKIES.get('status')
    }
    try:
        results['admins'] = data.get('admins')
        # print(results)
        return render(request, 'admins/listadmin.html', results)
    except Exception as er:
        print("获取管理员列表失败: ", er)
        return render(request, 'admins/listadmin.html', results)


def add_admin_handle(request):
    """只有医院等增加管理员，所以该方法只能是医院使用,并且user_id就是医院的id"""
    user_id = request.session.get('admin').get('user_id')  # 当前是医院，所以user_id就是hospital_id
    status = request.COOKIES.get('status')
    username = request.POST.get("phone")  # 用户名，也就是手机号
    password = request.POST.get("password1")  # 密码，前端的name属性里就是password1
    position = request.POST.get("position")  # 职位
    truename = request.POST.get("truename")  # 真实姓名
    gender = request.POST.get("dsex")  # 性别
    age = request.POST.get('age')  # 年龄
    email = request.POST.get("email")  # 邮箱
    details = request.POST.get("details")  # 描述
    obj = HospitalAdmin.objects.filter(username=username).first()  # 检查该用户是否已经存在
    hospital = Hospital.objects.filter(id=user_id).first().name  # 医院名
    data = {
        "truename": hospital,  # 该用户是医院，所以真实姓名就是医院
        "user_type": status,
        "hospital": hospital
    }
    try:
        if not obj:
            print("要添加的管理员未被注册过")
            info = {
                "hid": user_id,  # 医院id
                "username": username,  # 用户名
                "password": make_password(password),   # 加密密码
                "position": position,   # 管理员职位
                "name": truename,  # 管理员真实姓名
                "gender": gender,
                "age": age,
                "email": email,
                "details": details
            }
            HospitalAdmin.objects.create(**info)  # 增加管理员
            data["admins"] = hospital_info(request).get('admins')  # 在添加成功之后，重新获取一下管理员列表，这样保证在前端显示的是新的
            data["status"] = True
            data["add_success"] = "添加成功"
            return render(request, 'admins/listadmin.html', data)
        else:
            print("该用户已经存在")
            data["status"] = False
            data["add_error"] = "该用户已经存在"
            return render(request, 'admins/addadmin.html', data)
    except Exception as er:
        print("添加管理员失败：", er)
        return redirect('/index/')


def list_doctor_handle(request):
    """该医院的医生列表"""
    status = request.COOKIES.get('status')
    user_info = get_truename(request, status)  # 用户信息
    doctors = all_doctor(request)  # 所有医生对象的一个列表
    results = {
        "truename": user_info.get('truename'),
        "hospital": user_info.get('hospital'),  # 这个地方为什么不用session获取医院名，因为医院名存在了数据库中，这样可以少读取一次数据库
        "user_type": status,
        "doctors": doctors
    }
    return render(request, 'admins/listdoctor.html', results)


def add_doctor_handle(request):
    """增加医生"""
    status = request.COOKIES.get('status')  # 用户类型（医院或者管理员）
    user_info = get_truename(request, status)
    username = request.POST.get("phone")
    password = request.POST.get("password1")
    name = request.POST.get("truename")
    gender = request.POST.get("dsex")
    age = request.POST.get("age")
    email = request.POST.get("email")
    details = request.POST.get("details")
    position = request.POST.get('position')
    obj = Doctor.objects.filter(username=username)
    hospital_id = hospital_info(request).get('hospital_id')
    hospital = Hospital.objects.filter(id=hospital_id).first().name  # 医院名
    data = {
        "user_type": status,
        "truename": user_info.get('truename'),
        "hospital": hospital
    }
    try:
        if not obj:
            """说明该用户或者该手机号未被占用"""
            hospital = user_info.get('hospital')  # 获取医院名
            hospital_obj = Hospital.objects.filter(name=hospital).first()
            info = {
                "hid": hospital_obj.id,  # 所属医院的id
                "username": username,
                "password": make_password(password),  # 使用加密的密码
                "name": name,
                "gender": gender,  # 性别
                "age": age,
                "email": email,
                "position": position,  # 职位
                "details": details,
            }
            Doctor.objects.create(**info)  # 增加数据
            data["doctor"] = all_doctor(request)
            # data["add_error"] = ""  # 添加成功，则没有错误返回给用户
            data["status"] = True
            data["add_true"] = "添加医生成功"
            # return render(request, 'admins/listdoctor.html', data)
            return redirect('/admins/listdoctor/')  # 重定向
        else:
            """说明用户名已经被占用，不允许再增加"""
            data["status"] = False
            data["add_error"] = "用户名已经被占用"
            return render(request, 'admins/adddoctor.html', data)
    except Exception as er:
        print("增加医生出错>>", er)
        data["add_error"] = "增加医生失败"
        data["status"] = False
        data["doctor"] = all_doctor(request)
        return render(request, 'admins/index.html', data)


def edit_doctor_handle(request):
    """编辑医生,医院和管理员都有权限"""
    try:
        uid = int(request.POST.get("id"))  # 这个id是要编辑的那个人的id
    except Exception as er:
        print("未获取到要修改的管理员的id，无法修改他的资料: ", er)
        return HttpResponse(json.dumps({"status": False, "edit_error": "未获取管理员id，无法修改他的资料"}))
    name = request.POST.get("name")
    username = request.POST.get("phone")
    password = request.POST.get("pwd")
    position = request.POST.get('position')
    email = request.POST.get("email")
    details = request.POST.get("details")
    status = request.COOKIES.get('flag')
    data = {}
    if name:
        data["name"] = name  # 姓名
    if username:
        data["username"] = username  # 修改用户名
    if password:
        data["password"] = make_password(password)  # 加密密码
    if position:
        data["position"] = position  # 职位
    if email:
        data["email"] = email  # 修改邮箱
    if details:
        data["details"] = details
    print(data)
    users_obj = Doctor.objects.all()  # 得到所有人的账号
    phones = []
    for user in users_obj:
        phones.append(user.username)
    try:
        old_username = Doctor.objects.filter(id=uid).first().username
        phones.remove(old_username)  # 排除当前的账号
        if username in phones:
            # 判断用户修改的这个账号是否是别人的账号，如果是，则报错
            """该用户名已经存在，不允许这样修改资料"""
            print("无法修改账号为已经别人的账号")
            results = {
                "status": False,
                "edit_error": "该用户名已经存在",
                "user_type": status
            }
            return HttpResponse(json.dumps(results))
        else:
            print("修改医生资料")
            Doctor.objects.filter(id=uid).update(**data)  # 修改信息
            results = {
                "status": True,
                "edit_error": None,  # 医院编辑管理员信息的错误信息，因为没错，所以为None
                "user_type": status
            }
            return HttpResponse(json.dumps(results))
    except Exception as er:
        print("编辑医生信息失败：", er)
        results = {
            "status": False,
            "edit_error": "服务器响应失败",
            "user_type": request.COOKIES.get("status")
        }
    return HttpResponse(json.dumps(results))


def modify_get_handle(request):
    status = request.COOKIES.get("status")
    user_info = get_truename(request, status)  # 用户信息（真实姓名和医院名）
    hospital_id = request.session.get('admin').get('hospital_id')
    hospital = Hospital.objects.filter(id=hospital_id).first().name  # 医院名
    hospital = hospital  # 医院名
    data = {
        "user_type": status,
        "truename": user_info.get('truename'),
        "hospital": hospital
    }
    if status == "1":
        """医院修改自己的资料"""
        try:
            obj = Hospital.objects.filter(name=hospital).first()  # 获取该医院的对象
            data["results"] = obj
        except Exception as er:
            print("医生查看edit.html失败", er)
            data["results"] = None
    else:
        """管理员修改自己的资料"""
        try:
            user_id = request.session.get('admin').get('user_id')
            obj = HospitalAdmin.objects.filter(id=user_id).first()  # 该管理员对象
            data["results"] = obj
        except Exception as er:
            print("管理员查看edit.html失败", er)
            data["results"] = None
    return render(request, 'admins/modify.html', data)


def modify_post_handle(request):
    """医院或者管理员修改自己的信息"""
    status = request.COOKIES.get("status")
    user_id = request.session.get('admin').get('user_id')  # 当前登录的用户的id
    phones = all_username()  # 所有后台人员的账号
    if status == "1":
        print("医院提交修改资料表单")
        name = request.POST.get("name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        address = request.POST.get("address")
        form = {}
        if name:
            form["name"] = name
        if username:
            form["username"] = username
        if password:
            form["password"] = make_password(password)  # 加密密码
        if address:
            form["address"] = address
        print("form>>", form)
        try:
            if form.get('username') in phones:
                """用户名已经存在，不允许这样修改"""
                results = {
                    "status": False,
                    "modify_error": "用户名已经存在，修改失败",
                    "truename": get_truename(request, status).get('truename'),
                    "hospital": get_truename(request, status).get('hospital')
                }
                return HttpResponse(json.dumps(results))
            Hospital.objects.filter(id=user_id).update(**form)  # 修改成功之后，再次获取医院名和用户真实姓名
            info = get_truename(request, status)  # 获取后台人员的医院或者真实姓名
            results = {
                "status": True,
                "truename": info.get('truename'),
                "hospital": info.get('hospital')
            }
            print(results)
        except Exception as er:
            print(er)
            info = get_truename(request, status)  # 获取后台人员的医院或者真实姓名
            results = {
                "status": False,
                "modify_error": "资料修改失败",
                "truename": info.get('truename'),
                "hospital": info.get('hospital')
            }
            print(results)
        return HttpResponse(json.dumps(results))
        # return render(request, 'admins/modify.html', results)
    if status == "0":
        print("管理员提交修改资料表单")
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        age = request.POST.get('age')
        details = request.POST.get('details')
        form = {}
        if name:
            form["name"] = name
        if username:
            form["username"] = username
        if password:
            form["password"] = make_password(password)
        if email:
            form["email"] = email
        if age:
            form["age"] = age
        if details:
            form["details"] = details
        print("form: ", form)
        try:
            if form.get('username') in phones:
                """该用户已经存在，修改失败"""
                results = {
                    "status": False,
                    "modify_error": "用户名已经存在，修改失败",
                    "truename": get_truename(request, status).get('truename'),
                    "hospital": get_truename(request, status).get('hospital')
                }
                return HttpResponse(json.dumps(results))
            HospitalAdmin.objects.filter(id=user_id).update(**form)
            info = get_truename(request, status)  # 获取后台人员的医院或者真实姓名
            results = {
                "status": True,
                "truename": info.get('truename'),
                "hospital": info.get('hospital')
            }
            if username:
                results["username"] = username  # 提示前端，修改cookies
        except Exception as er:
            print("管理员修改信息失败", er)
            info = get_truename(request, status)  # 获取后台人员的医院或者真实姓名
            results = {
                "status": False,
                "modify_error": "资料修改失败",
                "truename": info.get('truename'),
                "hospital": info.get('hospital')
            }
        # return render(request, 'admins/modify.html', results)
        return HttpResponse(json.dumps(results))


def ecg_img_handle(request):
    """图示展示医院图片"""
    status = request.COOKIES.get('status')
    user_info = get_truename(request, status)
    truename = user_info.get("truename")  # 用户真实姓名
    hospital = user_info.get('hospital')  # 医院名
    hospt_id = request.session.get('admin').get('hospital_id')  # 医院id
    data = {
        "truename": truename,
        "hospital": hospital,  # 医院名
        "user_type": request.COOKIES.get("status")
    }
    try:
        ecg_obj = HospitalFile.objects.filter(hid=hospt_id, confirm_del=0)  # 该医院的所有图片的对象的一个列表
        result = []
        for ecg in ecg_obj:
            owner_obj = Doctor.objects.filter(id=ecg.owner_id).first()  # 该图片上传者的对象
            result.append({
                "upload_time": ecg.upload_time,  # 上传时间
                "owner": owner_obj.name,  # 医生
                "position": owner_obj.position,  # 图片所属医生的职位
                "details": ecg.details,  # 图片描述
                "number": ecg.number,  # 图片编号
                "upload_to": ecg.upload_to  # 图片路径
            })
        results, page_range = get_page(request, result, 9)  # 分页，最多显示9条数据
        data["status"] = True
        data["results"] = results
        data["page_range"] = page_range
        return render(request, 'admins/listecg_img.html', data)
    except Exception as er:
        print("用户请求图表展示图片失败：", er)
        data["status"] = False
        return render(request, 'admins/listecg_img.html', data)


def ecg_tb_handle(request):
    """get请求触发的操作，列表展示医院图库"""
    status = request.COOKIES.get('status')
    user_info = get_truename(request, status)
    hospital_id = request.session.get('admin').get('hospital_id')  # 医院id
    hospital = Hospital.objects.filter(id=hospital_id).first().name  # 医院名
    pic_list = HospitalFile.objects.filter(hid=hospital_id, confirm_del=0)  # 以医院的id去查找与之有关的所有图片,confirm_del=0表示不在回收站中的图片
    data = []
    for ecg in pic_list:
        try:
            owner_id = ecg.owner_id  # 上传该图片的用户的id
            obj = Doctor.objects.filter(id=owner_id).first()
            name = obj.name  # 上传该图片的用户的姓名
            phone = obj.username  # 上传该图片的用户的用户名（手机号）
            position = obj.position
            result = {
                "phone": phone,
                "name": name,
                "upload_time": ecg.upload_time,
                "upload_to": ecg.upload_to,
                "result_to": ecg.result_to,
                "filename": ecg.filename,
                "number": ecg.number,
                "img_user": ecg.img_user,
                "details": ecg.details,
                "position": position,
                "truename": user_info.get('truename'),
                "user_type": status,
                "hospital": hospital,
            }
            data.append(result)
        except Exception as er:
            print("这儿出错：", er)
            pass
    results = {
        "ecg_list": data,
        "truename": user_info.get('truename'),
        "user_type": status,
        "hospital": hospital,
    }
    return render(request, 'admins/listecg_table.html', results)


def img_tb_post_handle(request):
    """控制用户post请求历史记录。可能是要删除某张图片"""
    pic_number = request.POST.get("pic_number")  # 返回图片的编号
    command = request.POST.get("command")  # 根据这个结果来判断是要显示还是删除图片
    print("command, pic_number: ", command, pic_number)
    status = request.COOKIES.get('status')
    if command == "delete":
        try:
            print("用户要删除")
            try:
                # 由于第一次的删除只是让如回收站，所以这儿不将文件删除
                HospitalFile.objects.filter(number=pic_number).update(confirm_del=1)  # 修改值，表示该图片被删除，在回收站可被回收
            except Exception as er:
                # 不知道为什么，这一步老是会被连续请求两次，导致第二次删除时，文件已经不存在了，所以索性用异常处理来忽略
                print("删除图片出错：", er)
            return HttpResponse(json.dumps({"status": True, "result": "成功删除了图片", "user_type": status}))
        except Exception as err:
            print("请求删除失败：", err)
            return HttpResponse(json.dumps({"status": False, "result": "删除失败", "user_type": status}))
    return HttpResponse(json.dumps({"status": False, "result": "未知类型的请求", "user_type": status}))


def del_admin(request):
    try:
        uid = int(request.POST.get("id"))  # 要删除的管理员的id
    except Exception as err:
        print("未获取到管理员的id，无法删除失败： ", err)
        return HttpResponse(json.dumps({"status": False, "del_error": "未获取到该管理员的id，删除失败"}))
    try:
        obj = HospitalAdmin.objects.filter(id=uid).first()
        obj.delete()  # 删除该用户
        return HttpResponse(json.dumps({"status": True}))
    except Exception as err:
        print("删除管理员失败: ", err)
        return HttpResponse(json.dumps({"status": False, "del_error": "该用户不存在"}))


def del_doctor(request):
    try:
        uid = int(request.POST.get("id"))  # 要删除的医生的id
    except Exception as err:
        print("未获取到医生的id，无法删除失败： ", err)
        return HttpResponse(json.dumps({"status": False, "del_error": "未获取到该医生的id，删除失败"}))
    try:
        obj = Doctor.objects.filter(id=uid).first()
        obj.delete()  # 删除该用户
        return HttpResponse(json.dumps({"status": True}))
    except Exception as err:
        print("删除医生失败: ", err)
        return HttpResponse(json.dumps({"status": False, "del_error": "该用户不存在"}))


def get_recycle_info(request):
    """get请求回收站，将回收站的信息返回给用户"""
    status = request.COOKIES.get('status')
    user_info = get_truename(request, status)
    result = {
        "truename": user_info.get('truename'),  # 真实姓名
        "hospital": user_info.get('hospital'),  # 医院名
        "user_type": status  # 用户类型
    }
    try:
        hospt_id = hospital_info(request).get('hospital_id')  # 医院id
        obj_list = HospitalFile.objects.filter(hid=hospt_id, confirm_del=1)  # 找到该医院在回收站中的图片
        data = []
        for obj in obj_list:
            owner = Doctor.objects.filter(id=obj.owner_id).first()  # 上传该照片的医生的对象
            data.append(
                {"number": obj.number,
                 "filename": obj.filename,
                 "upload_time": obj.upload_time,
                 "position": owner.position,  # 上传该图片的医生的职位
                 "owner": owner.name,  # 上传该图片的医生的名字
                 "phone": owner.username,
                 "details": obj.details,
                 "upload_to": obj.upload_to  # 图片路径
                 }
            )
        results, page_range = get_page(request, data, 9)  # 数字代表每页做多显示多少
        result["results"] = results
        result["page_range"] = page_range
        print(result.get('pic_list'))
        return render(request, 'admins/recycle.html', result)
    except Exception as er:
        print("请求回收站失败: ", er)
        return render(request, 'admins/index.html', result)


def recycle_handle(request):
    """处理回收站的信息（恢复还是删除）"""
    status = request.COOKIES.get('status')
    user_info = get_truename(request, status)
    response = request.POST.get("handle")  # 判断用户是要删除还是恢复
    pic_number = request.POST.get("pic_number")  # 因为只有后台有回收站功能，所以，回收的都在HospitalFile里
    results = {
        "user_type": status,
        "truename": user_info.get('truename'),
        "hospital": user_info.get('hospital')
    }
    if response == "delete":
        print("用户要删除文件")
        try:
            obj = HospitalFile.objects.filter(number=pic_number).first()  # 用first方法，如果获取不到值，则为None，而不是报错
            upload_to = BASE_DIR + obj.upload_to  # 原图的绝对路径
            result_to = BASE_DIR + obj.result_to  # 处理后的图片绝对路径
            if os.path.isfile(upload_to):
                os.remove(upload_to)
                print("删除了原图")
            if os.path.isfile(result_to):
                os.remove(result_to)
                print("删除了处理的图")
            obj.delete()  # 删除数据库中的相应的内容
            results["status"] = True
        except Exception as er:
            print("删除图片失败: ", er)
            results["status"] = False
            results["error"] = er  # 错误信息
    elif response == "restore":
        print("用户要恢复图片")
        try:
            HospitalFile.objects.filter(number=pic_number).update(confirm_del=0)  # 让confirm_del=0表示移出回收站
            results["status"] = True
        except Exception as err:
            print("恢复图片失败", err)
            results["status"] = False
            results["error"] = err
    else:
        print("未知请求类型：", response)
        results["status"] = False
        results["error"] = "未知的请求类型"
    return render(request, 'admins/recycle.html', results)


