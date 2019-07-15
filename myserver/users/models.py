from django.db import models

# Create your models here.
class Users(models.Model):
    '''
    @description: 以用户的userid为标识一个用户
    @param {type} 
    @return: 
    '''
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    public_key = models.TextField()

    ip_address = models.CharField(max_length=20,null=True)
    is_online = models.IntegerField(default=0) # 记录登录状态
    have_off_msg = models.IntegerField(default=0)
    have_friends_requests = models.IntegerField(default=0)

    def __str__(self):
        return self.email

class Friends(models.Model):
    '''
    @description: 当一个client删除一个好友时，两个记录要删除,
    @param {type} 
    @return: 
    '''
    user_id = models.EmailField() # 以email作为id
    friend_id = models.EmailField()

    def __str__(self):
        return self.user_id

class Make_friends_requests(models.Model):
    '''
    @description: 好友申请
    @param {type} 
    @return: 
    '''
    from_id = models.EmailField() # 以email作为id
    to_id = models.EmailField() # 以email作为id
    handled = models.IntegerField(default=0) # 默认是未查看未处理
    result = models.IntegerField(default=0)
    add_time = models.DateField(auto_now=True)

    def __str__(self):
        return "make_friend_requests"

class Off_msg(models.Model):
    '''
    @description: 暂时不支持多个离线会话（即可能会有多个ks会话秘钥，后面测试得写，改进是存普通消息时候带上key_msg保存在那个id了）
    @param {type} 
    @return: 
    '''

    from_id = models.EmailField() # 以email作为id
    to_id = models.EmailField() # 以email作为id
    msg_enc = models.TextField() # 包含了消息与消息的解密秘钥
    is_read = models.IntegerField(default=0) # 默认是未查看未处理
    msg_time = models.DateField(auto_now=True)

    def __str__(self):
        return "off_msg"
