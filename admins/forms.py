from django import forms


class StatusForm(forms.Form):
    status = forms.IntegerField(widget=forms.Select)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    status = forms.IntegerField(widget=forms.Select)


class SignForm_H(forms.Form):
    username = forms.CharField()  # 医院 医生 用户
    password = forms.CharField()
    level = forms.CharField()
    address = forms.CharField()


class SignForm_D(forms.Form):
    details = forms.CharField(widget=forms.Textarea)
    email = forms.CharField()
    username = forms.CharField()  # 医院 医生 用户
    truename = forms.CharField()  # 医生用户
    password1 = forms.CharField()
    position = forms.CharField()
    fromwhere = forms.CharField()
    dsex = forms.CharField(widget=forms.RadioSelect)
    age = forms.IntegerField()
    phone = forms.CharField()


class SignForm_P(forms.Form):
    details = forms.CharField(widget=forms.Textarea)
    email = forms.CharField()
    username = forms.CharField()  # 医院 医生 用户
    truename = forms.CharField()  # 医生用户
    password2 = forms.CharField()
    address = forms.CharField()
    psex = forms.CharField(widget=forms.RadioSelect)
    age = forms.IntegerField()
    phone = forms.CharField()