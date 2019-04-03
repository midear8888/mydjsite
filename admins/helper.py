from mydjsite.public_helper import *
import os
from django.shortcuts import HttpResponse, redirect
import json


"""
所有用户，登录成功之后，都会有以下四个标记来验明身份
user_status: 用户类型,(0是管理员， 1是医院， 2是医生，3是普通用户)
username: 用户名（手机号），用作表查询的依据
user_type: 用户类型，和user_status所不同的是，标记是（医院是"Hospital", 管理员是"Admin", 医生是"Doctor", 普通用户是"User"）
"""

BASE_DIR = os.getcwd()
INFO = {
    "head_title": "心电图管理仓库",
}


def admin_auth(func):
    """用来装饰，验证用户是不是医院"""
    def inner(request, *args, **kwargs):
        v = request.COOKIES.get("status")
        hospt_id = hospital_id(request)
        try:
            hospital = Hospital.objects.filter(id=hospt_id).first().h_name  # 医院名
            INFO['hospital'] = hospital
        except Exception as er:
            print("没有获取到医院名: ", er)
        if v == "1" or v == "0":  # 保证只能是医院或者管理员可以登陆
            return func(request, *args, **kwargs)
        return render(request, 'commons/login.html')
    return inner


def all_admins(request):
    """得到所有的管理员对象"""
    hospt_id = hospital_id(request)
    obj = HospitalAdmin.objects.filter(hid=hospt_id)
    return obj


def all_doctor(request):
    """得到所有的医生对象"""
    hospt_id = hospital_id(request)
    obj = Doctor.objects.filter(hid=hospt_id)
    return obj


def list_admin_handle(request):
    """获取管理列表的post处理函数, 只能是后台人员能调用"""
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    try:
        admins = all_admins(request)
        INFO["admins"] = admins
        return render(request, 'admins/listadmin.html', INFO)
    except Exception as er:
        print("获取管理员列表失败: ", er)
        return render(request, 'admins/listadmin.html', INFO)


def add_admin_handle(request):
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    hospt_id = hospital_id(request)
    username = request.POST.get("phone")  # 用户名，也就是手机号
    password = request.POST.get("password1")  # 密码，前端的name属性里就是password1
    position = request.POST.get("position")  # 职位
    truename = request.POST.get("truename")  # 真实姓名
    gender = request.POST.get("dsex")  # 性别
    age = request.POST.get('age')  # 年龄
    email = request.POST.get("email")  # 邮箱
    details = request.POST.get("details")  # 描述
    obj = HospitalAdmin.objects.filter(username=username)  # filter获取的是一个列表
    try:
        if not obj:
            print("该用户名未被注册过")
            info = {
                "hid": hospt_id,  # 医院id
                "username": username,  # 用户名
                "password": password,   # 用户密码
                "position": position,   # 管理员职位
                "name": truename,  # 管理员真实姓名
                "gender": gender,
                "age": age,
                "email": email,
                "details": details
            }
            HospitalAdmin.objects.create(**info)  # 增加管理员
            admins = all_admins(request)
            INFO["status"] = 1
            INFO["admins"] = admins
            return render(request, 'admins/listadmin.html', INFO)
        else:
            print("该用户已经存在")
            INFO["status"] = 0  # 表示用户名被占用
            INFO["add_error"] = "该用户已经存在"
            return render(request, 'admins/listadmin.html', INFO)
    except Exception as er:
        print("添加管理员失败：", er)
        return render(request, 'admins/index.html', INFO)


def list_doctor_handle(request):
    """该医院的医生列表"""
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    doctors = all_doctor(request)
    INFO['doctors'] = doctors
    return render(request, 'admins/listdoctor.html', INFO)


def add_doctor_handle(request):
    """增加医生"""
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    username = request.POST.get("phone")
    password = request.POST.get("password1")
    name = request.POST.get("truename")
    gender = request.POST.get("dsex")
    age = request.POST.get("age")
    email = request.POST.get("email")
    details = request.POST.get("details")
    obj = Doctor.objects.filter(username=username)
    try:
        if not obj:
            """说明该用户或者该手机号未被占用"""
            hospt_id = hospital_id(request)
            info = {
                "hid": hospt_id,
                "username": username,
                "password": password,
                "name": name,
                "gender": gender,
                "age": age,
                "email": email,
                "details": details,
            }
            Doctor.objects.create(**info)  # 增加数据
            INFO["add_error"] = ""
            INFO["status"] = 1  # 表示添加成功
            INFO["doctors"] = all_doctor(request)  # 因为返回的是一个管理员列表，所以要将数据传过去
            return render(request, 'admins/listdoctor.html', INFO)
        else:
            """说明用户名已经被占用，不允许再增加"""
            INFO["add_error"] = "用户名已经被占用"
            INFO["status"] = 0
            return render(request, 'admins/adddoctor.html', INFO)
    except Exception as er:
        print("增加医生出错>>", er)
        INFO["add_error"] = "增加医生失败"
        return render(request, 'admins/index.html', INFO)


def ecg_img_handle(request):
    """图示展示医院图片"""
    user_info = get_truename(request)
    truename = user_info.get("truename")
    hospt_id = hospital_id(request)  # 医院id
    ecg_obj = HospitalFile.objects.filter(hid=hospt_id, confirm_del=0)  # list
    results, page_range = get_page(request, ecg_obj, 9)  # 分页，最多显示9条数据
    data = {
        "status": True,
        "results": results,  # 图片的对象列表
        "truename": truename,
        "page_range": page_range,
        "hospital": Hospital.objects.filter(id=hospt_id).first().h_name  # 医院名
    }
    return render(request, 'admins/listecg_img.html', data)


def ecg_tb_handle(request):
    """get请求触发的操作，列表展示医院图库"""
    user_info = get_truename(request)
    INFO["truename"] = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    hospt_id = hospital_id(request)
    ecg = HospitalFile.objects.filter(hid=hospt_id, confirm_del=0)  # 以医院的id去查找与之有关的所有图片
    data = []
    for img in ecg:
        try:
            u_id = img.owner_id  # 图片上传者id
            doctor_obj = Doctor.objects.filter(id=u_id).first()  # 利用用户id找到他的信息
            user_name = doctor_obj.name  # 上传者真实姓名
            user_phone = doctor_obj.username  # 利用用户id他的联系电话（用户名）
        except Exception as err:
            user_name, user_phone = "", ""
            print("查找用户id出错：", err)
        data.append({"filename": img.filename,
                     "number": img.number,
                     "user": user_name,
                     "phone": user_phone,
                     "upload_time": img.upload_time  # 上传时间
                     })
    print(data)
    INFO['ecg_list'] = data
    return render(request, 'admins/listecg_table.html', INFO)


def img_tb_base(pic_obj, command, pic_number):
    if command == "delete":
        try:
            print("用户要删除")
            try:
                # 由于第一次的删除只是让如回收站，所以这儿不将文件删除
                HospitalFile.objects.filter(number=pic_number).update(confirm_del=1)  # 修改值，表示该图片被删除，在回收站可被回收
            except Exception as er:
                # 不知道为什么，这一步老是会被连续请求两次，导致第二次删除时，文件已经不存在了，所以索性用异常处理来忽略
                print("删除图片出错：", er)
            return HttpResponse(json.dumps({"status": True, "result": "成功删除了图片"}))
        except Exception as err:
            print("请求删除失败：", err)
            return HttpResponse(json.dumps({"status": False, "result": "删除失败"}))
    if command == "show":
        try:
            print("用户要查看")
            # pic_path = pic_obj.result_to  # 经过处理的图片路径,由于还未经处理，所以为空，那么就先用下面的原图代替
            pic_path = pic_obj.upload_to
            details = pic_obj.details
            img_user = pic_obj.img_user  # 图片中患者的名字
            data = {
                "img_user": img_user,
                "pic_path": pic_path,
                "details": details
            }
            return HttpResponse(json.dumps({"status": True, "result": data}))
        except Exception as er:
            print("用户请求查看图片详情失败: ", er)
            return HttpResponse(json.dumps({"status": False, "result": "未找到相关的信息"}))
    print("出现未知错误, 用户既不是要显示图片，也不是要删除图片")
    return HttpResponse(json.dumps({"status": False, "result": None}))  # 可能是程序出错，导致接收到的命令既不是delete，也不是show。


def img_tb_post_handle(request):
    """控制用户post请求历史记录。即可能是要查看图片详情，也可能是要删除某张图片"""
    pic_number = request.POST.get("pic_number")  # 返回图片的编号
    command = request.POST.get("command")  # 根据这个结果来判断是要显示还是删除图片
    print("command, pic_number: ", command, pic_number)
    pic_obj = HospitalFile.objects.filter(number=pic_number).first()
    response = img_tb_base(pic_obj, command, pic_number)
    return response


def del_admin(request):
    username = request.POST.get("username")  # str,
    try:
        obj = HospitalAdmin.objects.filter(username=username).first()
        print(obj)
        # obj.delete()  # 删除该用户
        return HttpResponse(json.dumps({"status": 1}))
    except Exception as err:
        print("删除管理员失败: ", err)
        return HttpResponse(json.dumps({"status": 0}))


def del_doctor(request):
    username = request.POST.get("username")  # str
    try:
        obj = Doctor.objects.filter(username=username).first()
        print(obj)
        # obj.delete()  # 删除该用户
        return HttpResponse(json.dumps({"status": 1}))
    except Exception as err:
        print("删除医生失败: ", err)
        return HttpResponse(json.dumps({"status": 0}))


def get_recycle_info(request):
    """get请求回收站，将回收站的信息返回给用户"""
    try:
        hospt_id = hospital_id(request)
        obj_list = HospitalFile.objects.filter(hid=hospt_id, confirm_del=1)  # 找到该医院在回收站中的图片
        data = []
        for obj in obj_list:
                user_id = obj.owner_id  # 获取所属者id
                user_obj = Doctor.objects.filter(id=user_id).first()  # 获取用户对象
                data.append({
                    "filename": obj.filename,  # 文件名
                    "number": obj.number,  # 图片编号
                    "upload_time": obj.upload_time,  # 上传时间
                    "img_user": user_obj.name,  # 所属者真实姓名
                    "phone": user_obj.username,  # 所属者号码
                })
        INFO['recycles'] = data
        return render(request, 'admins/recycle.html', INFO)
    except Exception as er:
        print("请求回收站失败: ", er)
        return render(request, 'admins/index.html')


def recycle_handle(request):
    """处理回收站的信息（恢复还是删除）"""
    response = request.POST.get("handle")  # 判断用户是要删除还是恢复
    pic_number = request.POST.get("pic_number")  # 因为只有后台有回收站功能，所以，回收的都在HospitalFile里
    if response == "delete":
        print("用户要删除文件")
        try:
            obj = HospitalFile.objects.filter(number=pic_number).first()  # 用first方法，如果获取不到值，则为None，而不是报错
            upload_to = BASE_DIR + obj.upload_to  # 原图的绝对路径
            result_to = BASE_DIR + obj.result_to  # 处理后的图片绝对路径
            print("原图的绝对路径upload_to: ", upload_to)
            if os.path.isfile(upload_to):
                os.remove(upload_to)
                print("删除了原图")
            if os.path.isfile(result_to):
                os.remove(result_to)
                print("删除了处理的图")
            obj.delete()  # 删除数据库中的相应的内容
        except Exception as er:
            print("删除图片失败: ", er)
    elif response == "restore":
        print("用户要恢复图片")
        try:
            HospitalFile.objects.filter(number=pic_number).update(confirm_del=0)
        except Exception as err:
            print("恢复图片失败", err)
    else:
        print("没有获取到pic_number: ", pic_number)
    return render(request, 'admins/recycle.html', INFO)


