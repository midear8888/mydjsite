from django.db import models


class Hospital(models.Model):
    # 医院注册时，注册的人要设置登录密码和相关的信息。该用户就是该医院的超级管理员
    id = models.AutoField(primary_key=True)  # 主键、自增
    name = models.CharField(max_length=50, null=False, unique=True)  # 医院名
    address = models.CharField(max_length=255, null=False)  # 医院地址
    username = models.CharField(max_length=20, null=False, unique=True)  # 把用户的手机号码作为登录密码
    password = models.CharField(max_length=100, null=False)  # 登录密码

    class Meta:
        db_table = 'hospital'


class HospitalAdmin(models.Model):
    # 医院的普通管理员
    hid = models.IntegerField(null=False)  # 管理员所属医院的id
    username = models.CharField(max_length=50, null=False, unique=True)  # 手机号码，作为用户名登录
    password = models.CharField(max_length=100, null=False)  # 密码
    position = models.CharField(max_length=50, null=False)  # 职位
    gender = models.CharField(max_length=10, null=False)  # 性别
    age = models.IntegerField(null=False)  # 年纪
    email = models.CharField(max_length=50, null=False)  # 邮箱
    name = models.CharField(max_length=50, null=False)  # 用户的真实姓名
    details = models.TextField()  # 详细描述

    class Meta:
        db_table = "hospital_admin"


class HospitalFile(models.Model):
    # 医院的相册仓库
    hid = models.IntegerField()  # 该值就是该医院的id,表示所属关系
    owner_id = models.IntegerField(null=False)  # 所属者（图片上传者）他的id
    number = models.CharField(max_length=50, default="0")  # 图片编号，利用hash得到
    filename = models.CharField(max_length=50)  # 文件名
    upload_to = models.CharField(max_length=100)  # 图片上传路径
    data = models.CharField(max_length=100, default="")  # 数据路径
    result_to = models.CharField(max_length=100, default="")  # 处理后的图片存储路径，因为一开始上传后，并没有立刻开始处理，所以这个值无法写入，所以必须要可以为空，
    img_user = models.CharField(max_length=50, default="")  # 图片中的患者的名字，和当前登录者可能不是同一个人，所以另建一个字段
    upload_time = models.DateTimeField(auto_now_add=True)  # 上传时间
    confirm_del = models.IntegerField(default=0)  # 默认为0,说明并没有真的删除
    details = models.TextField(default="")  # 默认为空

    class Meta:
        db_table = "hospital_file"

