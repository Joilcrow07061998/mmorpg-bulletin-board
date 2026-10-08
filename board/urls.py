from django.urls import path
from . import views
from .views import accept_response, delete_response

app_name = 'board'



urlpatterns = [
    path('', views.PostList.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('post/create/', views.PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/update/', views.PostUpdate.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name='post_delete'),
    path('post/<int:pk>/response/create/', views.ResponseCreate.as_view(), name='response_create'),
    path('responses/', views.ResponseList.as_view(), name='user_responses'),
    path('response/<int:pk>/', accept_response, name='accept_response'),
    path('response/<int:pk>/delete/', delete_response, name='delete_response'),
    path('account/verify/', views.VerifyCodeView.as_view(), name='verify_code'),

]