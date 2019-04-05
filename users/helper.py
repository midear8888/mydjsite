from django.shortcuts import HttpResponse, render_to_response, redirect
from django.core.mail import send_mail
from mydjsite.settings import EMAIL_FROM
from mydjsite.public_helper import *
import os
import time
import json

"""
所有用户，登录成功之后，都会有以下四个标记来验明身份
status: 用户类型,(0是管理员， 1是医院， 2是医生，3是普通用户)
username: 用户名（手机号），用作表查询的依据
user_type: 用户类型，和status所不同的是，标记是（医院是"Hospital", 管理员是"Admin", 医生是"Doctor", 普通用户是"User"）
"""


BASE_DIR = os.getcwd()
INFO = {
    "head_title": "心电图管理仓库",
}


def user_auth(func):
    """用来装饰，在每一个类之上，用于验证用户是否已经登录过，并且还判断用户类型"""

    def inner(request, *args, **kwargs):
        v = request.COOKIES.get('status')
        if v == "2" or v == "3":
            # 是医院或者患者
            return func(request, *args, **kwargs)
        return render(request, 'commons/login.html')
    return inner


def get_truename(request):
    """得到普通用户的真实姓名"""
    username = request.COOKIES.get("username")
    status = request.COOKIES.get("status")
    true_name = "Personal"
    try:
        if status == "2":
            # 医生
            obj = Doctor.objects.filter(username=username).first()
            true_name = obj.name  # 真实姓名
        if status == "3":
            # 患者
            obj = Patient.objects.filter(username=username).first()
            true_name = obj.name  # 真实姓名
        if true_name:
            return true_name
        return true_name
    except Exception as er:
        print("获取用户真名失败：", er)
        return true_name


def gallery_handle(request):
    """画廊处理函数; 医生看到的是医院的库，患者看到的是自己的库"""
    user_info = get_truename(request)
    truename = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    status = request.COOKIES.get("status")
    try:
        if status == "2":
            # 医生
            hospt_id = hospital_id(request)  # 该医生的医院id
            ecg_obj = HospitalFile.objects.filter(hid=hospt_id)  # list，该医院的所有ecg图片
        else:
            # 患者
            username = request.COOKIES.get("username")  # 用户名
            user_id = Patient.objects.filter(username=username).first().id  # 该患者的id
            ecg_obj = PatientFile.objects.filter(pid=user_id)  # list, 患者的所有ecg图片
        results, page_range = get_page(request, ecg_obj, 9)  # 最多显示9张图
        response = {
            "results": results,
            "page_range": page_range,
            "truename": truename,
            "status": True

        }
        print(INFO.get("truename"))
        return render(request, 'users/gallery.html', response)
    except Exception as err:
        print("用户获取画廊信息失败: ", err)
        response = {
            "status": False,
            "truename": truename
        }
        return render(request, 'users/gallery.html', response)


def history_get_handle(request):
    """控制get历史记录显示"""
    user_info = get_truename(request)
    truename = user_info.get("truename")  # 将用户真名信息放入INFO，然后返回
    user_status = request.COOKIES.get("status")
    username = request.COOKIES.get("username")  # 用户名
    data = []
    if user_status == "2":
        # 医生
        print("显示医生的上传历史")
        obj = Doctor.objects.filter(username=username).first()  # 获取用户对象
        user_id = obj.id  # 用户id
        pic_obj = HospitalFile.objects.filter(owner_id=user_id)  # 获取该医生上传的所有图片对象
        for pic in pic_obj:
            filename = pic.filename  # 文件名
            pic_id = pic.number  # 图片编号
            upload_time = pic.upload_time  # 图片上传时间
            details = pic.details

            if len(details) > 15:
                details = details[0:15]+"..."  # 如果长度太大，那么就剪掉一些
            data.append({"filename": filename,  # 文件名
                         "pic_number": pic_id,  # 图片编号
                         "time": upload_time,  # 上传时间
                         "details": details  # 图片描述
                         })
    elif user_status == "3":
        # 患者
        print("显示患者的上传历史")
        obj = Patient.objects.filter(username=username).first()
        user_id = obj.id  # 用户id
        pic_obj = PatientFile.objects.filter(pid=user_id)  # 得到图片库中该用户的所有图片,list
        for pic in pic_obj:
            filename = pic.filename  # 文件名
            pic_id = pic.number  # 图片编号
            upload_time = pic.upload_time  # 图片上传时间
            details = pic.details
            if len(details) > 15:
                details = details[0:15]+"..."  # 如果长度太大，那么就剪掉一些
            data.append({"filename": filename,  # 文件名
                         "pic_number": pic_id,  # 图片编号
                         "time": upload_time,  # 上传时间
                         "details": details  # 图片描述
                         })
    results, page_range = get_page(request, data, 10)  # 最多显示10条数据
    response = {
        "truename": truename,
        "results": results,
        "page_range": page_range,
        "status": True
    }
    return render_to_response('users/history.html', response)


def history_base(pic_obj, command, pic_number, status):
    if command == "delete":
        try:
            print("用户要删除")
            upload_to = BASE_DIR + pic_obj.upload_to  # 原图的绝对路径
            result_to = BASE_DIR + pic_obj.result_to  # 处理后的图片绝对路径
            print("原图的绝对路径upload_to: ", upload_to)
            try:
                if os.path.isfile(upload_to):
                    os.remove(upload_to)
                    print("删除了原图")
                if os.path.isfile(result_to):
                    os.remove(result_to)
                    print("删除了处理的图")
            except Exception as er:
                # 不知道为什么，这一步老是会被连续请求两次，导致第二次删除时，文件已经不存在了，所以索性用异常处理来忽略
                print("删除图片出错：", er)
            if status == "2":
                HospitalFile.objects.filter(number=pic_number).delete()
                print("删除了数据库中相应的内容")
            if status == "3":
                PatientFile.objects.filter(number=pic_number).delete()
                print("删除了数据库中相应的内容")
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
    return HttpResponse(json.dumps({"status": False, "result": None}))  # 可能是程序出错，导致接收到的命令既不是delete，也不是show。


def history_post_handle(request):
    """控制用户post请求历史记录。即可能是要查看图片详情，也可能是要删除某张图片"""
    pic_number = request.POST.get("pic_number")  # 返回图片的编号
    command = request.POST.get("command")  # 根据这个结果来判断是要显示还是删除图片
    status = request.COOKIES.get("status")
    print("command, pic_number: ", command, pic_number)
    if status == "2":
        pic_obj = HospitalFile.objects.filter(number=pic_number).first()  # 获取该图片编号的对象[0]
        response = history_base(pic_obj, command, pic_number, status)
        return response
    if status == "3":
        pic_obj = PatientFile.objects.filter(number=pic_number).first()
        response = history_base(pic_obj, command, pic_number, status)
        return response


def upload_handle(request):
    """接收第一步的操作，并存储上传的原图，并返回路径，在用户界面显示"""
    file_obj = request.FILES.get("avatar")  # 把文件下载来
    if file_obj:
        username = request.COOKIES.get("username")  # 登录者的用户名
        now_time = time.time()
        file_number = username + str(now_time) + file_obj.name  # 用户名+当前时间+文件名
        number = str(hash(file_number))[1:]  # 上传文件的编号，因为有时候结果中会含有负号，所以不管是否有负号，统一去掉第一个字符
        print("hash的结果为：", hash(file_number), type(number), number)
        status = request.COOKIES.get("status")  # 判断登录的用户类型
        if status == "2":
            # 医生
            try:
                obj = Doctor.objects.filter(username=username).first()  # 根据用户名找到他所在的医院id
                hospt_id = obj.hid  # 得到医院id
                user_id = obj.id  # 得到用户id
                info = {
                    "hid": hospt_id,  # 医生上传的图片，归医院所有，该hid就是医院的id
                    "owner_id": user_id,  # 上传者id
                    "number": number,  # 图片编号
                    "filename": file_obj.name,
                    "upload_to": r"/media/upload/"+number,  # 只记录相对路径就可以
                    "img_user": "",   # 图片患者姓名
                    "details": ""  # 图片详细信息
                }
                HospitalFile.objects.create(**info)  # 存入数据
                save_path = os.path.join(BASE_DIR, r'media/upload/'+number)
                with open(save_path, "wb") as f:    # 在数据存入数据库成功后再写入文件，避免中途出错，致使两个地方的数据不一致
                    for block in file_obj.chunks():
                        f.write(block)  # 分块写入文件
            except Exception as er:
                print("医生上传文件失败: ", er)
                return HttpResponse(json.dumps({"status": 0}))  # 表示失败
        if status == "3":
            # 患者
            try:
                obj = Patient.objects.filter(username=username).first()
                user_id = obj.id  # 用户id
                info = {
                    "pid": user_id,
                    "number": number,
                    "filename": file_obj.name,
                    "upload_to": r'/media/upload/'+number,
                    "upload_time": time.ctime(),
                    "img_user": "",
                    "details": ""
                }
                PatientFile.objects.create(**info)  # 存入数据
                save_path = os.path.join(BASE_DIR, r'media/upload/' + number)
                with open(save_path, "wb") as f:  # 在数据存入数据库成功后再写入文件，避免中途出错，致使两个地方的数据不一致
                    for block in file_obj.chunks():
                        f.write(block)  # 分块写入文件
            except Exception as err:
                print("患者上传文件失败: ", err)
                return HttpResponse(json.dumps({"status": 0}))  # 表示失败
        print("给用户返回原图路径：", r'/media/upload/'+number)
        return HttpResponse(json.dumps({"status": 1, "result": r'/media/upload/' + number}))
    else:
        return HttpResponse(json.dumps({"status": 0}))


def process_handle(request):
    """处理图片，并返回处理后的图片的路径"""
    img_user = request.POST.get("img_user")  # 图片中患者的姓名
    img_details = request.POST.get("img_details")  # 图片描述
    img_path = request.POST.get("img_path")  # 原图地址
    print("查看结果：", img_user, img_path, img_details)
    if not img_user:
        img_user = ""
    if not img_details:
        img_details = ""
    if not img_path:
        img_path = ""
    # 上面三个if判断是防止有些数据没有获取到，即值为None，存入数据库出错
    status = request.COOKIES.get("status")
    info = {
        "img_user": img_user,
        "details": img_details
    }
    try:
        if status == "2":
            HospitalFile.objects.filter(upload_to=img_path).update(**info)
            # 为什么不是用.first()获取到一个值，然后在进行upload呢？原因请对比数据库命令: upload HospitalFile set **info where upload_to=img_path
            print("数据库更新成功")
        if status == "3":
            PatientFile.objects.filter(upload_to=img_path).update(**info)
            # obj.update(**info)
            print("数据库更新成功")
        print("img_path: ", img_path)
        if img_path:
            print("原图路径存在: ", img_path)
            """这儿调用程序并返回处理后的图片, 处理后的图片理应是已经保存了，所以算法函数应该还要返回相应的路径，文件名等信息"""
            img = r"\media\result\599307627"
            return HttpResponse(json.dumps({"status": 1, "result": img}))
        else:
            return HttpResponse(json.dumps({"status": 0, "result": "原图路径丢失"}))
    except Exception as er:
        print("查看结果图失败：", er)
        return HttpResponse(json.dumps({"status": 0, "result": "查看结果失败"}))


def contact_handle(request):
    """控制邮件的发送"""
    name = request.POST.get("name")  # 用户姓名, 邮件标题就是这个
    email = request.POST.get("email")  # 用户的邮箱
    # subject = request.POST.get("subject")  # 这个是干嘛的？邮件类型？
    message = request.POST.get("message")  # 邮件内容
    try:
        print(type(EMAIL_FROM), EMAIL_FROM)
        send_status = send_mail(name, message, email, [EMAIL_FROM])  # EMAIL_FROM是你的QQ邮箱
        if send_status:
            print("发送成功了")
            data = {
                "send_status": 1,
                "result": "发送成功！"
            }
            return HttpResponse(json.dumps(data))
    except Exception as err:
        print("用户发送邮件失败: ", err)
        INFO["send_status"] = "发送失败"
        data = {
            "send_status": 0,
            "result": err  # 将错误信息返回给用户
        }
        return HttpResponse(json.dumps(data))


def get_userinfo(request):
    """用户get请求用户中心，要将用户信息返回"""
    user_info = get_truename(request)
    username = request.COOKIES.get("username")
    status = request.COOKIES.get("status")
    if status == "2":
        # 医生
        obj = Doctor.objects.filter(username=username).first()  # 获取用户对象
    else:
        # 患者
        obj = Patient.objects.filter(username=username).first()  # 获取用户对象
    data = {
        "truename": obj.name,  # 真实姓名
        "gender": obj.gender,
        "age": obj.age,
        "phone": obj.username,  # 手机号
        "details": obj.details,  # 自我描述
        "email": obj.email  # 邮箱
    }
    return render(request, 'users/user_center.html', {"data": data, "truename": user_info.get("truename")})
    # 为了统一，这儿的truename单独分开来用。因为每一页的前端都是这样用的{{ truename }}


def post_userinfo(request):
    """用户请求修改个人资料"""
    name = request.POST.get("name")
    age = request.POST.get("age")
    username = request.POST.get("phone")
    pwd = request.POST.get("password")
    email = request.POST.get("email")
    details = request.POST.get("details")
    data = {}
    if name:
        data["name"] = name
    if age:
        data["age"] = age
    if username:
        data["username"] = username
    if pwd:
        data["password"] = pwd
    if email:
        data["email"] = email
    if details:
        data["details"] = details
    status = request.COOKIES.get("status")
    current_user = request.COOKIES.get("username")
    try:
        if status == "2":
            # 医生
            Doctor.objects.filter(username=current_user).update(**data)
        if status == "3":
            # 患者
            Patient.objects.filter(username=current_user).update(**data)
        return redirect('user_center')  # 重定向
    except Exception as er:
        print("用户修改资料出错：", er)
        return redirect('user_center')










