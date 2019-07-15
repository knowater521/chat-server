# coding:utf-8
from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('register/',views.register,name="register"),
    path('friends/',views.friends,name="friends"),
    #path('friends_on/',views.friends_on,name="friends_on"),
    path('friends_info/',views.friends_info,name="friends_info"),
    path('make_friends_requests/',views.make_friends_requests,name="make_friends_requests"),
    path('respose_make_friends/',views.respose_make_friends,name="response_make_friends"),
    path('query_make_friends_res/',views.query_make_friends_requests_response,name="query_make_friends_res"),
    path('del_friends/',views.del_friends,name="del_friends"),
    path('save_off_msg/',views.save_off_message,name="save_off_message"),
    path('query_off_msg/',views.query_off_msg,name="query_off_message"),
    path('query_user_by_email/',views.query_user_by_email,name="query_user_by_email"),
    path('query_make_friends_requests/',views.query_make_friends_requests,name="query_make_friends_requests"),
    path('is_have_off_message/',views.is_have_off_message,name="is_have_off_message"),
    # 测试函数用
    #path('index/',views.index,name="index"),
    #path('check_session',views.check_session,name="check_session"),
    path('save_file/',views.save_file,name="save_file"),
    path('query_file/',views.query_file,name="query_file"),
]