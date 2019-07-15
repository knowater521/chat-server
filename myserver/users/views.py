from django.shortcuts import render
from django.http import HttpResponse
import json
from users.models import Users,Friends,Off_msg,Make_friends_requests
from django.contrib.sessions.backends.db import SessionStore
# Create your views here.
def get_ip(request): 
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ""
    if x_forwarded_for: 
        ip = x_forwarded_for.split(',')[0] #所以这里是真实的ip 
    else: 
        ip = request.META.get('REMOTE_ADDR') #这里获得代理ip return ip
    return ip

def save_file(request):
    '''
    @description: 尝试文件上传API，保存文件，写入数据库（上传文件服务器重命名为服务名的名称，在数据库写入文件路径）
    @param {type} 
    @return: 
    '''  
    if request.method == "POST":
        f = request.FILES.get("uploadfile")
        print(f.name)
        fobj = open("test","wb+")
        for chunk in f.chunks():
            print(chunk)
            fobj.write(chunk)
        msg = {"status":True,"msg":"文件以接收"}
        fobj.close()
    else:
        msg = {"status":False,"msg":"请求方法错误"}  
    return HttpResponse(json.dumps(msg))

def query_file(request):
    '''
    @description: 尝试从服务器下载文件
    @param {type} 
    @return: 
    '''   
    f = open("test","rb")
    return HttpResponse(f.read()) 

def index(request):
    '''
    @description: 测试新的功能函数session的不再浏览器记录的情况,API视图函数中使用session会话机制编程
    @param {type} 
    @return: 
    '''
    if not request.session.session_key: # 初始requests.post()并不会像浏览器那样生成session_key,自己生成一个session_key
        request.session.create()

    name = "xxxx"
    password = "xxxxx"
    if request.method=="GET":
        msg = {"status":False,"msg":"请求方法不对"}
        msg = json.dumps(msg)
        return HttpResponse(msg)

    elif request.method=="POST":
        u=request.POST.get("username")
        p=request.POST.get("password")

        if u==name and p==password:
            #生成随机字符串
            #写到用户浏览器cookie
            #保存到session
            #在随机字符串对应的字典中设置相关内容
            request.session["username"]= u #上面的4步就设置完了
            request.session["is_login"]=True

            session_key = request.session.session_key

            msg = {"status":True,"msg":"登录成功","session_id":session_key}
            return HttpResponse(json.dumps(msg))
        else:
            msg = {"status":False,"msg":"账号密码错误"}
            return HttpResponse(json.dumps(msg))
    
    # return HttpResponse(sdata,content_type="application/json")
    # return HttpResponse(sdata)

def check_session(request):
    '''
    @description: 测试从requests.post中抽取session_key值进行用户身份的处理
    @param {type} {"msg":{......},"session_id":xxxxx}
    @return: 
    '''    
    if request.method =="POST":
        session_id = request.POST.get("session_id","")

        if request.session.exists(session_id):
            print("存在该session_key")
            s = SessionStore(session_key=session_id)
            print(s.keys())
            print(s.values())
            request.session.delete(session_id) # 清除该会话记录不能用s.clear()
            msg = {"status":True,"msg":"会话识别正确"}
        else:
            print("非法用户登陆")
            msg = {"status":False,"msg":"会话不存在"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def login(request):
    '''
    @description: 验证登录，记录client的IP，设置在线状态，分配访问cookie（ip地址确定每个请求）
    @param {type} post: {msg:{"user_email":email,"password":password}
    @return:{"status":True|False,"msg":"详细的错误消息","session_id":session_id} 只有正确登录才会有session_id字段
    '''

    # 交互信息的格式控制与变量命名规则
    # if request.method == "POST":
    #     msg = request.POST.get('msg','')
    #     data = json.loads(msg) # data永远是从msg交互消息中复原的msg数据字典对象，msg是要发送的交互信息
    #     print(data['email'],data['password'])
    #     msg = {"status":False,"email":data["email"],"password":data["password"]}
    # else:
    #     msg = {"status":False}
    # return HttpResponse(json.dumps(msg))
    if not request.session.session_key:
        request.session.create()

    if request.method == "POST":
        msg = request.POST.get("msg",'')
        data = json.loads(msg)
        email_msg = data['user_email']
        password_msg = data['password']

        user_ip = get_ip(request)
        
        # TODO 异常退出处理
        try:
            user = Users.objects.get(email=email_msg) # user.password
            user_entry_set = Users.objects.filter(ip_address=user_ip)
            user_entry_only_set = Users.objects.filter(email=email_msg,is_online=1) # 同一IP,账号不能两次登录

            print("login email:",email_msg,"debug:",len(user_entry_only_set),len(user_entry_set))
            if len(user_entry_only_set)>0:
                msg = {"status":False,"msg":"该用户已登录，不能重复登录"}
            elif len(user_entry_set)>0:
                msg ={"status":False,"msg":"同一ip不能同时登录两个账号"}
            else:
                if user.password == password_msg:
                    # 处理登录状态的设置，记录信息
                    user.ip_address = user_ip
                    user.is_online = 1
                    user.save()
                    # TODO 正确登录则设置session_ID中email字段标识一个用户
                    request.session["email"] = email_msg
                    request.session["is_login"] = True
                    session_id = request.session.session_key

                    msg = {"status":True,"msg":"登录成功","session_id":session_id}    
                else:
                    msg = {"status":False,"msg":"密码账号错误"}
        except Users.DoesNotExist:
            msg = {"status":False,"msg":"连接数据库失败"}
    else:
        msg = {'status':False,"msg":"网络错误"}
    return HttpResponse(json.dumps(msg))

def logout(request):
    '''
    @description: post请求都可以了
    @param {type} POST {"session_id":session_id}
    @return: {"status":True|False,"msg":"详细的错误消息"}
    '''
    if request.method == "POST":
        # msg = request.POST.get("msg",'')
        # TODO 获取session_id进行会话身份识别
        session_id = request.POST.get("session_id",'')
        # data = json.loads(msg)
        # user_email = data["user_email"]
        # session_id = data["session_id"] 

        # TODO 检验session_id是否存在存在化话记录
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            if s["is_login"]: # 和下面的重复了,没关系
                user_email = s["email"]
                print("logout: ",user_email)
                try:
                    user = Users.objects.get(email=user_email)
                    if user.is_online == 1:
                        user.is_online = 0
                        user.ip_address = ""
                        user.save()

                        # TODO 清除该条session记录
                        request.session.delete(session_id)
                        msg = {"status":True,"msg":"退出登录成功"}
                    else:
                        msg = {"status":False,"msg":"用户已经退出登录"}
                except:
                    msg = {"status":False,"msg":"数据库不存在该用户"}
            else:
                msg = {"status":False,"msg":"该用户已下线"} 
        else:
            msg = {"status":False,"msg":"非法用户登录"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    msg = json.dumps(msg)
    return HttpResponse(msg)

def register(request):
    '''
    @description: 支持客户端的注册功能
    @param {type} post:{"msg":{"user_email":xxx,"password":xxxx,"public_key":xxxx,"confirm_password":xxxxx}}
    @return: {"status":True|False,"msg":"详细的消息"}，如{"status":True,"msg":"注册成功"}
    '''
    if request.method=="POST":
        msg = request.POST.get("msg",'') # {"type":xxx,"msg":{xxx}}
        data = json.loads(msg)
        email_m = data["user_email"]
        password_m = data["password"]
        confirm_password = data["confirm_password"]
        public_key_m = data["public_key"]

        if email_m == "" or password_m == "" or confirm_password=="":
            msg = {"status":False,"msg":"账号不可以为空"}
        else:
            try:
                same_email_user = Users.objects.filter(email=email_m)
                if same_email_user:
                    msg = {"status":False,"msg":"该邮箱已经注册"}
                else:
                    if password_m == confirm_password:
                        new_user = Users.objects.create()
                        new_user.password = password_m
                        new_user.email = email_m
                        new_user.public_key = public_key_m

                        new_user.save()
                        msg = {"status":True,"msg":"注册成功"}
                    else:
                        msg = {"status":False,"msg":"两次密码不符合"}
            except:
                msg = {"status":False,"msg":"网络出错"}
    else:
        msg = {"status":False,"msg":"网络出错"}

    return HttpResponse(json.dumps(msg))

def friends(request):
    '''
    @description: 响应在线client的好友列表，返回好友列表（以状态位标志online是否在线），列表的组织形式：
    @param {type} requests.POST(url,data={"session_id"=xxxx"})
    @return: {"status":True,"msg":{[{"friend_email":xxxx,"online":0|1},{"friend_email":xxxx,"online":0|1},{......}]}} online = 1 表示该好友在线或者 {"status":False,"msg":错误提示} {"email":xxxx}为一个好友信息的返回
    '''
    if request.method == 'POST':
        # user_ip = get_ip(request)
        session_id = request.POST.get("session_id","")
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
            try:
                friends_list = [] # "msg":[{"user_id":email},...]
                user = Users.objects.get(email=user_email)
                friends_set = Friends.objects.filter(user_id=user_email) # 返回好友集合
                for friend in friends_set:
                    friend_on_line = Users.objects.get(email=friend.friend_id)
                    if friend_on_line.is_online == 1:
                        friends_list.append({"friend_email":friend.friend_id,"online":1}) # 返回好友的id(email)
                    else:
                        friends_list.append({"friend_email":friend.friend_id,"online":0})
                msg = {"status":True,"msg":friends_list}
            except Users.DoesNotExist:
                msg={"status":False,"msg":"连接数据库失败"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

# def friends_on(request):
#     '''
#     @description: 在线client获取在线好友列表，返回在线好友列表
#     @param {type} 任意post,即requests.post(url)
#     @return:  {"status":True,"msg":{[{"email":xxxx},{"email":xxxx},{......}]}} 或者 {"status":False,"msg":错误提示} {"email":xxxx}为一个在线好友信息的返回
#     '''
#     if request.method == 'POST':
#         user_ip = get_ip(request)
#         try:
#             friends_list = [] # "msg":[{"user_id":email},...]
#             user = Users.objects.get(ip_address=user_ip)
#             user_email = user.email
#             friends_set = Friends.objects.filter(user_id=user_email) # 返回好友集合,is_online
#             for friend in friends_set:
#                 try:
#                     friend_on_line = Users.objects.get(email=friend.friend_id)
#                     if friend_on_line.is_online == 1:
#                         friends_list.append({"email":friend.friend_id}) # 好友列表的子集
#                 except Users.DoesNotExist:
#                     pass
#             msg = {"status":True,"msg":friends_list}
#         except Users.DoesNotExist:
#             msg={"status":False,"msg":"连接数据库失败"}
#     else:
#         msg = {"status":False,"msg":"网络错误"}
#     return HttpResponse(json.dumps(msg))

def friends_info(request):
    '''
    @description: 响应客户端的请求，返回在线好友的ip,public_key(根据请求参数的好友的email) 
    @param {type} POST，{"msg":{"friend_email":xxxxx},"session_id":xxxxx}
    @return: {"status":True,"online":True|False,"msg":{"user_ip":user.ip_address,"user_public_key":user.public_key}} 或者 ｛"status":False,"msg":xxxxx｝,详细的错误信息
    '''
    if request.method=="POST": # 请求带有对方的email就是主键
        msg = request.POST.get("msg","")
        session_id = request.POST.get("session_id","")
        data = json.loads(msg)
        friend_email = data["friend_email"] # 一次请求一个friend的在线信息，包括ip,public,online

        if request.session.exists(session_id):
            try:
                user = Users.objects.get(email=friend_email)
                if user.is_online==1:
                    msg = {"status":True,"friend_email":friend_email,"online":True,"msg":{"user_ip":user.ip_address,"user_public_key":user.public_key}}
                else:
                    msg = {"status":True,"friend_email":friend_email,"online":False,"msg":{"user_ip":"请求好友不在线","user_public_key":user.public_key}}
            except Users.DoesNotExist:
                msg = {"status":False,"msg":"不存在该用户"}
        else:
            msg={"status":False,"msg":"非法用户请求"}

    else:
        msg={"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def query_user_by_email(request):
    '''
    @description: client添加好友输入email进行系统用户查询（添加好友前的好友信息查询，即用户是否存在）
    @param {type} POST,{"msg":{"user_email":xxxx},"session_id":xxxxxx}
    @return: {"status":True,"msg":{"user_email":user.email}} 或者 查询用户不存在的 msg={"status":False,"msg":"查询好友不存在"} False中有其他的错误信息提示或者是好友不存在
    ''' 
    if request.method=="POST":
        msg = request.POST.get("msg","")
        session_id = request.POST.get("session_id","")
        data = json.loads(msg)
        user_email=data["user_email"]
        if request.session.exists(session_id):
            try:
                user = Users.objects.get(email=user_email)
                msg = {"status":True,"msg":{"user_email":user.email}}
            except Users.DoesNotExist:
                msg={"status":False,"msg":"查询用户不存在"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg ={"status":False,"msg":"请求方法错误"}   
    return HttpResponse(json.dumps(msg))
def make_friends_requests(request):
    '''
    @description: 好友申请表  即提交好友申请的处理
    @param {type} POST {"msg":{"user_email":xxxxx},"session_id":xxxxxx} xxxx为用户的邮箱
    @return: msg = {"status":True,"msg":"好友申请成功"} 或者 msg = {"status":False,"msg":xxx}的详细错误提示
    '''
    # TODO 修改重复添加好友
    if request.method=="POST":
        msg = request.POST.get('msg','')
        session_id = request.POST.get("session_id","")
        data = json.loads(msg)
        # user_ip = get_ip(request) #添加者
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
            try:
                user = Users.objects.get(email=user_email)
                # user_email = user.email
                friend_email = data["user_email"] # 被添加者
                if user_email == friend_email:
                    msg = {"status":False,"msg":"不能添加自己为好友"}
                else:
                    make_friends_request_entry_set = Make_friends_requests.objects.filter(from_id=user_email,to_id=friend_email,handled=0) # 不能重复添加
                    make_friends_request_from_friends_set = Make_friends_requests.objects.filter(from_id=user_email,to_id=friend_email,handled=1,result=1) # 已经是好友不能再添加，1是同意，2是拒绝
                    print("login email:",user_email,"debug:",len(make_friends_request_from_friends_set),len(make_friends_request_entry_set))
                    if len(make_friends_request_entry_set)>0:
                        msg = {"status":False,"msg":"重复添加好友"}
                    elif len(make_friends_request_from_friends_set)>0:
                        msg = {"status":False,"msg":"已经是好友不能重复添加"}
                    else:
                        new_entry = Make_friends_requests.objects.create()
                        new_entry.from_id = user_email
                        new_entry.to_id = friend_email
                        new_entry.handled = 0
                        new_entry.save()

                        friend = Users.objects.get(email=friend_email) # 用户表的被申请人的申请状态修改
                        friend.have_friends_requests+=1
                        friend.save()
                        msg = {"status":True,"msg":"好友申请成功"}

            except Exception as e:
                msg = {"status":False,"msg":"连接数据库失败"+str(e)}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))
def query_make_friends_requests(request):
    '''
    @description: 被申请加为好友的对方登录查询好友申请记录，返回好友申请列表
    @param {type} POST,{"session_id":xxxx}
    @return: {"status":True,"msg":[{"from_user_email":xxxx},{"from_user_email":xxxx},{"from_user_email":xxxx},......]}或者{"status":False,"msg":"没有好友申请"}
    '''
    if request.method =="POST":
        session_id = request.POST.get("session_id","")
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
        # user_ip = get_ip(request)
            user = Users.objects.get(email=user_email)
            if user.have_friends_requests:
                query_set = Make_friends_requests.objects.filter(to_id=user_email,handled=0) # 被申请人且未处理的好友申请记录列表返回
                query_list = []
                for query_entry in query_set:
                    from_user_email = query_entry.from_id
                    query_list.append({"from_user_email":from_user_email})
                msg = {"status":True,"msg":query_list}
            else:
                msg = {"status":False,"msg":"没有好友申请"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def query_make_friends_requests_response(request):
    '''
    @description: 返回自己的好友申请记录的对方处理状态,[{"to_id":to_user_email,"result":1|2|3},{...},....],其中to_user_email是自己申请谁为好友，1，2，3分别代表为｛未处理，已同意，已拒绝｝
    @param {type} POST {"session_id":session_id}
    @return: {"status":True|False,"msg":[{"to_id":to_user_email,"result":1|2|3},{...},....]}
    '''    
    if request.method == "POST":
        session_id = request.POST.get("session_id")
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s['email']
            res_make_friend_requests_set = Make_friends_requests.objects.filter(from_id=user_email).order_by('-add_time')
            msg_list = []
            for res_make_friend_requests_entry in res_make_friend_requests_set:
                if res_make_friend_requests_entry.handled == 0:
                    msg_list.append({"to_id":res_make_friend_requests_entry.to_id,"result":1})
                else:
                    if res_make_friend_requests_entry.result == 1:
                        msg_list.append({"to_id":res_make_friend_requests_entry.to_id,"result":2})
                    else:
                        msg_list.append({"to_id":res_make_friend_requests_entry.to_id,"result":3})
            msg = {"status":True,"msg":msg_list}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def respose_make_friends(request):
    '''
    @description: 被申请加为好友的client响应是否同意添加好友，用户表的被申请人的申请状态修改 与 申请表的修改
    @param {type} POST:{"session_id":xxx,"msg":{"type":True|False,"friend_email":xxxx}} 是否(typ=True|False)同意email为friend_id的人加为好友
    @return: {"status":True,"msg":"添加成功"} 或者 {"status":True,"msg":"拒绝添加好友"}  
    '''
    if request.method=="POST":
        msg = request.POST.get("msg","")
        session_id = request.POST.get("session_id","")
        data = json.loads(msg)

        # user_ip = get_ip(request)
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
            user = Users.objects.get(email=user_email) # 只有在线才能响应添加好友
            friend_email = data["friend_email"] # 发起好友申请的用户id

            make_friends_request_entry = Make_friends_requests.objects.get(from_id=friend_email,to_id=user_email,handled=0)

            if data["type"]: # type=1是同意添加好友
                new_entry = Friends.objects.create() # Friends表的记录添加

                new_entry.user_id = user_email # 两边添加
                new_entry.friend_id = friend_email
                new_entry.save()

                new_entry = Friends.objects.create() # 要重新删除一次
                new_entry.user_id = friend_email
                new_entry.friend_id = user_email
                new_entry.save()

                user.have_friends_requests -= 1 # 一次同意一个好友
                user.save()

                make_friends_request_entry.handled = 1
                make_friends_request_entry.result = 1
                make_friends_request_entry.save()
                msg = {"status":True,"msg":"添加成功"}
            else:
                # 如果是多个的好友请求 怎么处理 通过计数器了
                user.have_friends_requests -= 1 # 一次处理一个好友
                user.save()

                make_friends_request_entry.handled = 1
                make_friends_request_entry.result = 2 # 拒绝添加为好友
                make_friends_request_entry.save()
                msg = {"status":True,"msg":"拒绝添加好友"}  
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def del_friends(request):
    '''
    @description: 响应删除好友，同时删除双方的表friends
    @param {type} POST:{"session_id":xxx,msg":{"friend_email":xxxx}} 请求一次删除email为friend_id的好友
    @return:  {"status":True,"msg":"删除成功"} or msg = {"status":False,"msg":"不存在该好友"} or {"status":False,"msg":"网络错误"}
    '''
    if request.method=="POST":
        session_id = request.POST.get("session_id","")
        # user_ip = get_ip(request)
        if request.session.exists(session_id):
            s = SessionStore(session_key=session_id)
            user_email = s["email"]

            user = Users.objects.get(email=user_email) # 获取到当前client的记录

            msg = request.POST.get("msg",'') # 获取到client发来的消息,如要删除那个好友
            data = json.loads(msg) # {"friend_email":....} 要删除的好友id
            friend_email = data["friend_email"]
            try:
                friend_entry = Friends.objects.get(user_id=user_email,friend_id=friend_email)
                friend_entry.delete()
                friend_entry = Friends.objects.get(friend_id=user_email,user_id=friend_email)
                friend_entry.delete()
                msg = {"status":True,"msg":"删除成功"}
            except Friends.DoesNotExist:
                msg = {"status":False,"msg":"不存在该好友"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def save_off_message(request):
    '''
    @description: 保存客户端发来的离线消息，一条一条保存
    @param {type} post={"session_id":session_id,"from_email":xxx,"to_email":xxxx,"msg_enc":xxxx}
    @return: {"status":True,"msg":"保存成功"} or {"status":False,"msg":"网络错误"}
    '''
    if request.method=="POST":
        session_id = request.POST.get("session_id","")
        if request.session.exists(session_id):
            # user_ip = get_ip(request)
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
            user = Users.objects.get(email=user_email) # 获取到发送者的id记录，作为from _id
            msg = request.POST.get("msg",'')
            data = json.loads(msg)
            to_id = data["to_email"]
            msg_enc = data["msg_enc"]


            to_user = Users.objects.get(email=to_id)
            # 保存离线消息到数据库
            new_entry = Off_msg.objects.create()
            new_entry.from_id=user_email
            new_entry.to_id = to_id
            new_entry.msg_enc=msg_enc
            new_entry.save()

            to_user.have_off_msg=1 # 设置对方有离线消息
            to_user.save()
            msg = {"status":True,"msg":"保存成功"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg={"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))
def query_off_msg(request):
    '''
    @description: client知道存在离线消息，用户查询 离线消息集合 的转发
    @param {type} {"session_id":session_id}
    @return: {"status":True,"public_key":xxx，msg":[ {"msg_enc":xxxxxx},  {"msg_enc":xxxxx}...]}
    '''
    if request.method=="POST":
        session_id = request.POST.get("session_id","")
        if request.session.exists(session_id):

            # user_ip = get_ip(request)
            s = SessionStore(session_key=session_id)
            user_email = s["email"]
            user = Users.objects.get(email=user_email)
            user_to_id = user_email
            

            # off_msg_set = Off_msg.objects.filter(to_id=user_to_id,is_read=0)
            off_msg_set = Off_msg.objects.filter(to_id=user_to_id)
            off_msg_list=[]
            for off_msg_entry in off_msg_set:
                msg_entry = {"msg_enc":off_msg_entry.msg_enc}
                off_msg_entry.is_read = 1
                off_msg_entry.save()
                off_msg_list.append(msg_entry)
            user.have_off_msg = 0
            user.save()
            msg = {"status":True,"msg":off_msg_list}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))

def is_have_off_message(request):
    '''
    @description: 返回当前client是否有离线消息
    @param POST,{"session_id":xxxxx}
    @return: {"status":True,"msg":"有新的离线消息"} or  {"status":False,"msg":"网络错误"}
    '''
    if request.method=="POST":
        session_id = request.POST.get("session_id","")
        if request.session.exists(session_id):
            # user_ip=get_ip(request)
            s = SessionStore(session_key=session_id)
            user_email = s['email']
            user = Users.objects.get(email=user_email)
            if user.have_off_msg:
                msg={"status":True,"msg":"有新的离线消息"}
            else:
                msg={"status":False,"msg":"没有新的离线消息"}
        else:
            msg = {"status":False,"msg":"非法用户请求"}
    else:
        msg = {"status":False,"msg":"请求方法错误"}
    return HttpResponse(json.dumps(msg))
