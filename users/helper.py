from django.shortcuts import HttpResponse, render_to_response, redirect
from django.core.mail import send_mail
from mydjsite.settings import EMAIL_FROM
from mydjsite.public_helper import *
from mydjsite.imgdeal import *
import os
import time
import json
import re
import cv2
from django.contrib.auth.decorators import login_required

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
    """用来装饰，在每一个类之上，用于验证用户是否已经登录过，
    并且还判断用户类型
    """
    def inner(request, *args, **kwargs):
        v = request.COOKIES.get('flag')
        try:
            is_login = request.session.get('user').get('is_login')  # 查看登录状态
            print("is_login: ", is_login)
            print("v: ", v)
            if is_login and v == "2" or v == "3":
                # 前台，所以只允许医生和患者登录
                return func(request, *args, **kwargs)
            return render(request, 'commons/login.html', {"status": False, "error": "请先登录"})
        except Exception as er:
            print("抛出异常用户尚未登录: ", er)
            return render(request, 'commons/login.html', {"status": False, "error": "请先登录"})
    return inner


def all_username():
    """得到前台所有人员的手机号，用户在修改资料时，验证修改的手机号是否已经存在"""
    phones = []
    hospital_phones = Doctor.objects.all()
    for phone in hospital_phones:
        phones.append(phone.username)  # 所有医生的账号
    admin_phones = Patient.objects.all()
    for phone in admin_phones:
        phones.append(phone.username)  # 所有患者的账号
    return phones


def gallery_handle(request):
    """画廊处理函数; 医生看到的是医院的库，患者看到的是自己的库"""
    flag = request.COOKIES.get('flag')
    user_info = get_truename(request, flag)
    truename = user_info.get('truename')  # 将用户真名信息放入INFO，然后返回
    user_id = request.session.get('user').get('user_id')  # 用户id
    try:
        if flag == "2":
            # 医生
            hospt_id = Doctor.objects.filter(id=user_id).first().hid  # 该医生的医院id
            ecg_obj = HospitalFile.objects.filter(hid=hospt_id)  # list，该医院的所有ecg图片
        else:
            # 患者
            ecg_obj = PatientFile.objects.filter(pid=user_id)  # list, 患者的所有ecg图片
        results, page_range, page_data = get_page(request, ecg_obj, 6)
        response = {
            "results": results,
            "page_range": page_range,
            "truename": truename,
            "status": True
        }
        response.update(page_data)
        return render(request, 'users/gallery.html', response)
    except Exception as err:
        print("用户获取画廊信息失败: ", err)
        response = {
            "status": False,
            "truename": truename,
            "results": None
        }
        return render(request, 'users/gallery.html', response)


def history_get_handle(request):
    """控制get历史记录显示"""
    flag = request.COOKIES.get('flag')
    user_info = get_truename(request, flag)
    truename = user_info.get('truename')  # 获取用户真实姓名
    user_id = request.session.get('user').get('user_id')  # 用户id
    position = None
    if flag == "2":
        # 医生
        print("显示医生的上传历史")
        pic_obj = HospitalFile.objects.filter(owner_id=user_id)  # 该医生上传的所有图片对象
        data = pic_obj
        user_obj = Doctor.objects.filter(id=user_id).first()  # 用户对象
        position = user_obj.position
    else:
        # 患者
        print("显示患者的上传历史")
        pic_obj = PatientFile.objects.filter(pid=user_id)  # 得到图片库中该用户的所有图片,list
        data = pic_obj
    results, page_range, page_data = get_page(request, data, 2)
    info = {
        "truename": truename,
        "results": results,
        "page_range": page_range,
        "page_data": page_data,
        "status": True,
        "user_type": request.COOKIES.get('flag'),
        "position": position  # 职位，只有医生有这个字段，患者的没有
    }
    info.update(page_data)
    print(info)
    print("result:", info.get('results'))
    print("pagerange:", info.get('page_range'))
    print("page_data:", info.get('page_data'))
    return render(request, 'users/history.html', info)


def history_base(pic_obj, command, pic_number, flag):
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
            if flag == "2":
                HospitalFile.objects.filter(number=pic_number).delete()
                print("删除了数据库中相应的内容")
            if flag == "3":
                PatientFile.objects.filter(number=pic_number).delete()
                print("删除了数据库中相应的内容")
            return HttpResponse(json.dumps({"status": True, "result": "成功删除了图片"}))
        except Exception as err:
            print("请求删除失败：", err)
            return HttpResponse(json.dumps({"status": False, "result": "删除失败"}))
    return HttpResponse(json.dumps({"status": False, "result": None}))  # 可能是程序出错，导致接收到的命令既不是delete，也不是show。


def history_post_handle(request):
    """控制用户post请求历史记录"""
    pic_number = request.POST.get("pic_number")  # 返回图片的编号
    command = request.POST.get("command")  # 根据这个结果来判断是要显示还是删除图片
    flag = request.COOKIES.get("flag")
    print("command, pic_number: ", command, pic_number)
    if flag == "2":
        pic_obj = HospitalFile.objects.filter(number=pic_number).first()  # 获取该图片编号的对象[0]
        response = history_base(pic_obj, command, pic_number, flag)
        return response
    if flag == "3":
        pic_obj = PatientFile.objects.filter(number=pic_number).first()
        response = history_base(pic_obj, command, pic_number, flag)
        return response


def upload_handle(request):
    img_user = request.POST.get("username")  # 图片中患者的姓名
    img_details = request.POST.get("details")  # 图片描述
    file_obj = request.FILES.get("avatar")
    print("用户名{}，详情{}，文件名{}".format(img_user, img_details, file_obj.name))
    if file_obj:
        # username = request.COOKIES.get("username")  # 登录者的用户名
        user_id = request.session.get('user').get('user_id')  # 用户id
        now_time = time.time()
        flag = request.COOKIES.get("flag")  # 判断登录的用户类型
        if flag == "2":
            # 医生
            try:
                obj = Doctor.objects.filter(id=user_id).first()
                username = obj.username
                file_number = username + str(now_time) + file_obj.name
                number = str(hash(file_number))[1:]
                print("hash的结果为：", hash(file_number), type(number), number)
                hospt_id = obj.hid  # 得到医院id
                try:
                    hz = re.compile('.*(\..*)').findall(file_obj.name)[0]  # 获取文件的后缀名
                    filename = number+hz
                except Exception as er:
                    print("获取文件名{}的后缀失败{} ".format(file_obj.name, er))
                    filename = number+'.jpg'
                info = {
                    "hid": hospt_id,  # 医院的id
                    "owner_id": user_id,
                    "number": number,
                    "filename": file_obj.name,
                    "upload_to": r"/media/upload/"+filename,
                    "img_user": img_user,
                    "details": img_details,
                    "result_to": "",
                    "data": ""
                }
                HospitalFile.objects.create(**info)  # 存入数据
                save_path = os.path.join(BASE_DIR, r'media/upload/'+filename)
                with open(save_path, "wb") as f:    # 数据存入数据库成功后再写入文件
                    for block in file_obj.chunks():
                        f.write(block)  # 分块写入文件

                # 图片校正
                readpath = save_path.replace('\\', '/')
                img = cv2.imread(readpath)
                print(readpath)
                # cv2.imshow("origin", img)
                houghimg = hough(img)
                cv2.imwrite(readpath, houghimg)

                return HttpResponse(json.dumps({"upload_status": True, "result": r'/media/upload/'+filename}))
            except Exception as er:
                print("医生上传文件失败: ", er)
                return HttpResponse(json.dumps({"upload_status": False, "upload_error": er}))  # 表示失败
        if flag == "3":
            # 患者
            try:
                obj = Patient.objects.filter(id=user_id).first()
                username = obj.username  # 获取用户名
                file_number = username + str(now_time) + file_obj.name  # 文件的初始编号，用户名+当前时间+文件名
                number = str(hash(file_number))[1:]  # 上传文件的编号，因为有时候结果中会含有负号，所以不管是否有负号，统一去掉第一个字符
                print("hash的结果为：", hash(file_number), type(number), number)
                try:
                    hz = re.compile('.*(\..*)').findall(file_obj.name)[0]  # 获取文件的后缀名
                    filename = number + hz
                except Exception as er:
                    print("获取文件名{}的后缀失败{} ".format(file_obj.name, er))
                    filename = number + '.jpg'  # 默认转化为jpg
                info = {
                    "pid": user_id,
                    "number": number,
                    "filename": file_obj.name,
                    "upload_to": r'/media/upload/'+filename,
                    "img_user": username,
                    "details": img_details,
                    "result_to": "1",
                    "data": "2"
                }
                PatientFile.objects.create(**info)  # 存入数据
                save_path = os.path.join(BASE_DIR, r'media/upload/' + filename)
                with open(save_path, "wb") as f:  # 在数据存入数据库成功后再写入文件，避免中途出错，致使两个地方的数据不一致
                    for block in file_obj.chunks():
                        f.write(block)  # 分块写入文件

                # 图片校正
                readpath = save_path.replace('\\', '/')
                img = cv2.imread(readpath)
                print(readpath)
                # cv2.imshow("origin", img)
                houghimg = hough(img)
                houghimg = resize(houghimg)
                cv2.imwrite(readpath, houghimg)

                return HttpResponse(json.dumps({"upload_status": True, "result": r'/media/upload/'+filename}))
            except Exception as err:
                print("患者上传文件失败: ", err)
                return HttpResponse(json.dumps({"upload_status": False}))  # 表示失败
        return HttpResponse(json.dumps({"upload_status": False, "upload_error": "未知用户类型错误"}))
    else:
        print("上传图片不能为空")
        return HttpResponse(json.dumps({"upload_status": False, "upload_error": "上传图片不能为空"}))
    # return HttpResponse(json.dumps({"upload_status": False, "upload_error": "上传图片不能为空"}))


def process_handle(request):
    """处理图片，并返回处理后的图片的路径"""
    img_path = request.POST.get("img_path")  # 原图地址
    flag = request.COOKIES.get('flag')
    print("查看结果：", img_path, flag)
    try:
        if img_path:
            print("原图路径存在: ", img_path)
            # 路径
            # filename = re.search('\d+', img_path)[0]  # 图片名
            filename = img_path[12:]  # 图片名
            # print("filename", filename)
            result_to = r'media/result/' + filename  # 结果路径
            origin_path = os.path.join(BASE_DIR, img_path[1:])  # 图片绝对路径
            print("filename:{}\norigin_path:{}\nresult:{}".format(filename, origin_path, result_to))
            origin_path = origin_path.replace('\\', '/')
            print("newpath", origin_path)

            # 图像处理
            img = cv2.imread(origin_path)
            result, datas = start(img)

            # 数据写入文件
            # data_file = re.search('\d+', img_path)[0]
            data_file = img_path[12:-4]
            print("文件名", data_file)
            data_path = os.path.join(BASE_DIR, r'media/data/'+data_file+'.csv')
            data_path = data_path.replace('\\', '/')
            print("数据保存路径", data_path)
            with open(data_path, "w") as f:
                for data in datas:
                    f.write(str(data[0][0]))
                    f.write(',')
                    f.write(str(data[0][1]))
                    f.write('\n')

            # 结果图片保存
            result_path = os.path.join(BASE_DIR, r'media/result/'+data_file+'.jpg')
            result_path = result_path.replace('\\', '/')
            print("图片保存路径", result_path)
            cv2.imwrite(result_path, result)
            data_to = r'media/data/'+data_file+'.csv'
            print("data_to", data_to)

            # 数据库存储
            print("result_to", result_to)
            info = {"result_to": result_to,
                    "data": data_to}
            # print("info:", info)
            # 数据库更新
            upload_path = r'/media/upload/'+filename
            if flag == "2":
                obj = HospitalFile.objects.filter(upload_to=upload_path)
                print("img_path:{}\nobj:\n{}".format(upload_path, obj))
                HospitalFile.objects.filter(upload_to=upload_path).update(**info)
                print("数据库更新成功")
            if flag == "3":
                PatientFile.objects.filter(upload_to=upload_path).update(**info)
                # obj.update(**info)
                print("数据库更新成功")
            # print("img_path: ", img_path)
            if os.path.isfile(origin_path):
                os.remove(origin_path)
                print("删除了临时图片存放")
            else:
                print("图不存在")
            return HttpResponse(json.dumps({"process_status": True, "result": result_to}))
        else:
            return HttpResponse(json.dumps({"process_status": False, "process_error": "原图路径丢失"}))
    except Exception as er:
        print("查看结果图失败：", er)
        return HttpResponse(json.dumps({"process_status": False, "process_error": "查看结果失败"}))


def contact_handle(request):
    """控制邮件的发送,用户是ajax提交的"""
    name = request.POST.get("name")  # 用户姓名, 邮件标题就是这个
    email = request.POST.get("email")  # 用户的邮箱
    # subject = request.POST.get("subject")  # 这个是干嘛的？邮件类型？
    message = request.POST.get("message")  # 邮件内容
    try:
        # print(type(EMAIL_FROM), EMAIL_FROM)
        send_status = send_mail(name, message, email, [EMAIL_FROM])  # EMAIL_FROM是你的QQ邮箱
        if send_status:
            print("发送成功了")
            data = {
                "send_status": True,
                "result": "发送成功！"
            }
            return HttpResponse(json.dumps(data))
    except Exception as err:
        print("用户发送邮件失败: ", err)
        data = {
            "send_status": False,
            "result": err  # 将错误信息返回给用户
        }
        return HttpResponse(json.dumps(data))


def get_userinfo(request):
    """用户get请求用户中心，要将用户信息返回"""
    user_id = request.session.get('user').get('user_id')
    flag = request.COOKIES.get("flag")
    if flag == "2":
        # 医生
        obj = Doctor.objects.filter(id=user_id).first()  # 获取用户对象
    else:
        # 患者
        obj = Patient.objects.filter(id=user_id).first()  # 获取用户对象
    return obj  # 之所以不直接用render返回，是因为用户修改资料后，render之后页面也要显示用户的信息，所以就把这个data作为一个值传过去
    # return render(request, 'users/user_center.html', data)
    # 为了统一，这儿的truename单独分开来用。因为每一页的前端都是这样用的{{ truename }}


def post_userinfo(request):
    """用户修改个人资料"""
    name = request.POST.get("name")
    age = request.POST.get("age")
    username = request.POST.get("phone")
    pwd = request.POST.get("password")
    email = request.POST.get("email")
    details = request.POST.get("details")
    data = {}
    print("name:", name)
    print("age:", age)
    print("username:", username)
    print("pwd:", pwd)
    print("email:", email)
    print("details:", details)
    if name:
        data["name"] = name
    if age:
        data["age"] = age
    if username:
        data["username"] = username
        phones = all_username()
        user_obj = get_userinfo(request)  # 得到当前用户的信息
        phones.remove(user_obj.username)  # 排除自己的账号，与其他账号做对比
        if username in phones:
            print("用户将自己的用户名修改为别人的用户名，冲突了，返回错误信息")
            info = {
                "status": False,
                "data": user_obj,
                "truename": user_obj.name,
                "results": '修改失败：因为账号{}已经存在'.format(username)
            }
            return render(request, 'users/user_center.html', info)
    if pwd:
        data["password"] = make_password(pwd)  # 加密密码
    if email:
        data["email"] = email
    if details:
        data["details"] = details
    flag = request.COOKIES.get("flag")
    user_id = request.session.get('user').get('user_id')  # 获取用户id
    try:
        if data:
            if flag == "2":
                # 医生
                Doctor.objects.filter(id=user_id).update(**data)
            else:
                # 患者
                Patient.objects.filter(id=user_id).update(**data)
            user_obj = get_userinfo(request)  # 要在修改之后重新获取用户信息
            info = {
                "status": True,
                "results": "修改成功！",
                "data": user_obj,
                "truename": user_obj.name  # 用户真实姓名
            }
            return render(request, 'users/user_center.html', info)
            # return HttpResponse(json.dumps({"status": True, "result": "成功"}))
        else:
            user_obj = get_userinfo(request)
            info = {
                "status": False,
                "results": "不能提交空表单",
                "truename": user_obj.name,
                "data": user_obj
            }
            return render(request, 'users/user_center.html', info)
    except Exception as er:
        print("用户修改资料出错：", er)
        user_obj = get_userinfo(request)
        info = {
            "status": False,
            "results": "修改失败：{}".format(er),
            "data": user_obj,
            "truename": user_obj.name
        }
        return render(request, 'users/user_center.html', info)
        # return HttpResponse(json.dumps({"status": False, "result": er}))









