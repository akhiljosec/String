from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    # path('movie_add/', views.movie_add, name='movie_add'),
    # path('movie_details/<int:id>/', views.movie_details, name='movie_details'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('course_room/<int:c_id>/', views.course_room, name='course_room'),
    path('course_room_discuss/<int:c_id>', views.course_room_discuss, name='course_room_discuss'),
    path('course_room_discussion_room/<int:discussion_id>/', views.course_room_discussion_room, name='course_room_discussion_room'),
    path('discussion_room/<int:discussion_id>/', views.discussion_room, name='discussion_room'),
    path('post/', views.post, name='post'),
    path('post_room/<int:p_id>/', views.post_room, name='post_room'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user_list/', views.user_list, name='user_list'),
    path('profile/<str:uname>', views.profile, name='profile'),
    path('message/<str:message_room_name>/', views.message, name='message'),
    path('friends/', views.friends, name='friends'),
    path('users_course_rooms/', views.users_course_rooms, name='users_course_rooms'),
    path('sent_friend_request/<str:receiver_username>/', views.sent_friend_request, name='sent_friend_request'),
    path('accept_friend_request/<str:requested_username>/', views.accept_friend_request, name='accept_friend_request'),
    path('unfriend/<str:friend>/', views.unfriend, name='unfriend'),
    path('message_box/', views.message_box, name='message_box'),
    path('friend_requests/', views.friend_requests, name='friend_requests'),
    path('create_course/', views.create_course, name='create_course'),
    path('update_course/<int:c_id>', views.update_course, name='update_course'),
    path('course_details/<int:c_id>', views.course_details, name='course_details'),
    path('join_course/<int:c_id>', views.join_course, name='join_course'),
    path('add_instructors/<int:c_id>/', views.add_instructors, name='add_instructors'),
    path('search_results/', views.search_results, name='search_results'),
    # path('profile/', views.profile, name='profile'),
    # path('movie_review/<int:id>/', views.movie_review, name='movie_review')
]

