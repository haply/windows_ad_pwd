# -*- coding: utf-8 -*-
from flask import Flask,redirect,url_for
from flask import render_template,request
from ad.update_user import *
from itsdangerous import URLSafeSerializer
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from threading import Thread
from sms_send import *
app = Flask(__name__,static_url_path='')
app.config['SECRET_KEY']=SECRET_KEY
app.config['MAIL_DEBUG'] = False
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_SERVER'] = mailserver
app.config['MAIL_PORT']=mail_port
app.config['MAIL_USE_SSL']=mail_use_ssl
app.config['MAIL_USE_TLS']=mail_use_tls
app.config['MAIL_USERNAME']=mail_username
app.config['MAIL_PASSWORD']=mail_password
app.config['MAIL_DEFAULT_SENDER']=mail_username
mail=Mail(app)
from flask_redis import FlaskRedis
redis_store=FlaskRedis(app)
CSRFProtect(app)
user_keys = URLSafeSerializer(KEY)
def send_async_email(app,msg):
    with app.app_context():
         mail.send(msg)
def msg_mail(user,user_mail,url):
    msg=Message(subject="重置您的密码",
                  recipients=[user_mail]) 
    msg.body = 'send by live400'
    msg.html = '<b>'+user+'</b> 您好!   <br></br>点击以下链接重置您的密码:<a href="'+url+'"/>点击密码重置</a><br></br>如果您没有请求修改密码，请忽略该邮件.'
    thread = Thread(target=send_async_email,args=[app,msg])
    thread.start()
    return '<h1> 发送成功 </h1>'
              
@app.route('/',methods=['GET','POST'])
def mod_password():
    if request.method=="POST":
        username=request.form.get('login')
        oldpassword=request.form.get('oldpassword')
        newpassword=request.form.get('newpassword')
        confirmpassword=request.form.get('confirmpassword')
        if (not username or not oldpassword or  not newpassword or not confirmpassword ):
            return render_template('index.html', pass_status="请输入用户名和密码", alert_status="alert-danger")
        if ( newpassword != confirmpassword ):
            return render_template('index.html',pass_status="密码不一致",alert_status="alert-danger")
        if (newpassword == oldpassword):
            return render_template('index.html', pass_status="您的新密码与旧密码相同",alert_status="alert-danger")
        user_status=check_user(username,oldpassword)
        if not user_status:
            return render_template('index.html', pass_status="密码错误",alert_status="alert-danger")

        user_dn=get_type(cn=username)[0]
        if (user_dn == "not found" ):
            return render_template('index.html', pass_status="用户名或密码错误", alert_status="alert-danger")

        update_status=update_password(user_dn,newpassword)
        if not update_status:
            return render_template('index.html', pass_status="修改失败请联系管理员",alert_status="alert-danger")
        if  update_status:
            return render_template('index.html', pass_status="密码修改成功",alert_status="alert-success",hidden_status="hidden")

    else:
        return render_template('index.html',pass_status="修改您的密码",alert_status="alert-success")
@app.route('/mail/',methods=['GET','POST'])
def mail_password():
    if request.method=="POST":
        username=request.form.get('login')
        mail=request.form.get('mail')
        user_dns = get_type(cn=username)
        user_dn=user_dns[0]
        user_mail=user_dns[1]
        if (user_dn == "not found" or mail != user_mail):
            return render_template('mail.html', mail_status="用户名或邮件地址错误", alert_status="alert-danger",hidden_status="none")
        else:
            user_key = user_keys.dumps(str(username))
            user_token= user_keys.dumps(str(user_key))
            redis_store[user_token]=username
            redis_store.expire(user_token, 3600)
            url=domain+"/mail/"+user_token
            msg_mail(username,mail,url)
            return render_template('mail.html', mail_status="重置邮件已发送",alert_status="alert-success",hidden_status="hidden")
    else:
        return render_template('mail.html',alert_status="alert-success",mail_status="邮件发送密码重置链接")
@app.route('/mail/<mailtoken>',methods=['GET','POST'])
def modify_mail_password(mailtoken):
        def get_user(mailtoken):
            try:
                user = redis_store.get(mailtoken).decode()
                return user
            except:
                return "not found"
        if request.method == "POST":
            mailtoken = request.form.get('mailtoken')
            user=request.form.get('login')
            newpassword = request.form.get('newpassword')
            confirmpassword = request.form.get('confirmpassword')
            if (newpassword != confirmpassword):
                return render_template('modify_mail.html',pass_status="输入的密码不同",mailtoken=mailtoken,alert_status="alert-success",user=user)
            user = get_user(mailtoken)
            if (user == "not found"):
                return redirect('/mail/')
            else:
                user_dn = get_type(cn=user)[0]
                update_status = update_password(user_dn, newpassword)
                if not update_status:
                    return render_template('modify_mail.html', pass_status="修改失败请联系管理员", alert_status="alert-danger",user=user)
                if update_status:
                    redis_store.delete(mailtoken)
                    return render_template('modify_mail.html', pass_status="密码修改成功", alert_status="alert-success",hidden_status="hidden")
                return render_template('modify_mail.html', mailtoken=mailtoken,alert_status="alert-success",user=user)
        else:
            if request.method=="GET":
                user = get_user(mailtoken)
                if (user == "not found"):
                    return render_template('modify_mail.html', pass_status="连接失效请重新生成", alert_status="alert-success",
                                           hidden_status="hidden")
                else:
                    return render_template('modify_mail.html', mailtoken=mailtoken,pass_status="输入新的密码", alert_status="alert-success",user=user)
                return redirect('/mail/')


@app.route('/sms/',methods=['GET','POST'])
def sms_password():
    if request.method=="POST":
        username=request.form.get('login')
        try:
            tel=get_type(cn=username)
            tel_number=tel[2]
            user=tel[3]
            list = tel_number[3:8]
            Phone_Number=tel_number.replace(list,"*****")
            user_key=user_keys.dumps(str(user))

            if ( tel != "not found"):
                return render_template('get_sms.html',user_key=user_key,Phone_Number=Phone_Number,user=user,pass_status="确认用户信息是否正确，点击发送获取短信",alert_status="alert-success")
            else:
                return render_template('sms.html', pass_status="未发现手机号1", alert_status="alert-danger")
        except:
            return render_template('sms.html',pass_status="系统异常请联系管理员",alert_status="alert-danger")

        return render_template('sms.html',pass_status="获取短信验证码", alert_status="alert-success")
    else:

        return render_template('sms.html',pass_status="获取短信验证码",alert_status="alert-success")
@app.route("/sms/<op>",methods=['GET', 'POST'])
def sms_op(op):
    if  (op=="get_sms_code"):
        if request.method=="POST":
            user_token=request.form.get('user')

            try:
                user=user_keys.loads(user_token)

            except:
                return render_template('get_sms_code.html')
            code=get_sms_token()
            redis_store[code] = str(user)
            redis_store.expire(code,3600)
            tel=get_type(cn=user)
            tel_number=tel[2]
            send_to_tel(tel_number,code) 
            return  render_template('get_sms_code.html')

        if request.method=="GET":
            return redirect('/sms/')
    elif (op == "get_modify_pass"):
        if request.method=="POST":
            smstoken=request.form.get('smstoken')
            def get_user(smstoken):
                try:
                    user=redis_store.get(smstoken).decode()
                    return user
                except:
                    return "not found"
            user=get_user(smstoken)
            if (user == "not found"):
                return render_template('get_sms_code.html')
            else:
                return render_template('modify_sms.html', pass_status="请输入新的密码",smstoken=smstoken,alert_status="alert-success",user=user)

        else:
            return redirect('/sms/')
    elif (op == "modify_pass"):
        if request.method == "POST":
            smstoken = request.form.get('smstoken')
            user=request.form.get('login')
            newpassword = request.form.get('newpassword')
            confirmpassword = request.form.get('confirmpassword')
            if (newpassword != confirmpassword):
                return render_template('modify_sms.html',pass_status="两次密码不同",smstoken=smstoken,alert_status="alert-success",user=user)

            def get_user(smstoken):
                try:
                    user = redis_store.get(smstoken).decode()
                    return user
                except:
                    return "not found"
            user = get_user(smstoken)
            if (user == "not found"):
                return redirect('/sms/')
            else:
                user_dn = get_type(cn=user)[0]
                update_status = update_password(user_dn, newpassword)
                if not update_status:
                    return render_template('index.html', pass_status="修改失败请联系管理员", alert_status="alert-danger")
                if update_status:
                    redis_store.delete(smstoken)
                    return render_template('modify_sms.html', pass_status="密码修改成功", alert_status="alert-success",hidden_status="hidden")
                return render_template('modify_sms.html', smstoken=smstoken,alert_status="alert-success",user=user)
        else:
            return redirect('/sms/')
    else:
        return redirect('/sms/')
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True
        )
