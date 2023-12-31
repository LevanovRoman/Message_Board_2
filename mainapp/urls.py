from django.urls import path, include

from .views import *

urlpatterns = [
    path('', main_view, name='main'),
    path('login/', login_view, name='login'),
    path('otp/', otp_view, name='otp'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('comments/', CommentsPage.as_view(), name='comments'),
    path('post/create/', CreatePost.as_view(), name='create_post'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('post/update/<slug:slug>/', UpdatePost.as_view(), name='update_post'),
    path('news/delete/<slug:slug>/', DeletePost.as_view(), name='delete_post'),
    path('category/<slug:category_slug>/', CategoryPostList.as_view(), name='category'),
    path('subscr/<slug:slug>/', subscr, name='subscr'),
    path('comm_add/<slug:slug>/', comm_add, name='comm_add'),
    path('comm_delete/<slug:slug>/', comm_delete, name='comm_delete'),
]