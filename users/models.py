from django.db import models


class Doctor(models.Model):
    # 医生
    hid = models.IntegerField(null=False)  # 医生所属医院的id
    username = models.CharField(max_length=50, null=False, unique=True)  # 手机号码, 作为用户名登录
    password = models.CharField(max_length=100, null=False)  # 密码
    gender = models.CharField(max_length=10, null=False)  # 性别
    age = models.IntegerField(null=False)  # 年纪
    position = models.CharField(default="", max_length=50)
    email = models.CharField(max_length=50, null=False)  # 邮箱
    name = models.CharField(max_length=50, null=False)  # 用户的真实姓名，允许为空
    details = models.TextField(null=True)  # 详细描述

    class Meta:
        db_table = 'doctor'


class Patient(models.Model):
    # 普通用户/患者
    id = models.AutoField(primary_key=True)  # 主键、自增
    username = models.CharField(max_length=50, unique=True)  # 手机号,登录名
    password = models.CharField(max_length=100)  # 密码
    gender = models.CharField(max_length=20, null=False)  # 性别
    email = models.CharField(max_length=50, default="null")  # 邮箱
    name = models.CharField(max_length=50, default="null")  # 真实姓名
    age = models.IntegerField(null=False)  # 年龄
    details = models.TextField(null=True)

    class Meta:
        db_table = "patient"


class PatientFile(models.Model):
    # 普通用户上传的图片
    pid = models.IntegerField()  # 该值就是用户的id，所属关系
    number = models.CharField(max_length=50, default="0")  # 图片编号，利用hash得到
    img_user = models.CharField(max_length=50, default="")  # 图片中的患者的名字，和当前登录者可能不是同一个人，所以另建一个字段
    filename = models.CharField(max_length=50)  # 文件名
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间
    upload_to = models.CharField(max_length=100)  # 图片上传路径
    result_to = models.CharField(max_length=100, default="")  # 图片保存路径
    confirm_del = models.IntegerField(default=0)  # 默认为0,说明并没有被放入回收站
    details = models.TextField(default="")  # 默认为空

    class Meta:
        db_table = "user_file"


