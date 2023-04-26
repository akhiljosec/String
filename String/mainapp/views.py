from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib import auth
from .models import Profile, Friend, Courses_Joined, Enrollment, Course, Course_Contents, Course_Room, Like, Instructor, Instructions, Comment, Reply, Post, Message, Message_Room
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from .context_processors import subjects
import re
from django.core.paginator import Paginator

# Create your views here.



def home(request):
    courses = Course.objects.all()
    courses_sort = dict()
    for subject in subjects:
        courses_sort[subject] = Course.objects.filter(course_type=subject)

    courses_sort = dict(sorted(courses_sort.items(), key=lambda x: len(x[1]), reverse=True))

    return render(request, 'mainapp/home.html', {'courses':courses, 'courses_sort':courses_sort})


# def home(request):
#     courses_sort = dict()
#     for subject in subjects:
#         courses_sort[subject] = Course.objects.filter(course_type=subject)
#     print(courses)
#     return render(request, 'home.html', {'courses':courses, 'courses_sort':courses_sort})


def signup(request):
    if request.method == "POST":
        user_type = request.POST['user_type']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        pnum = request.POST['pnum']
        subject = request.POST.get('subject')
        pro_pic = request.FILES['pro_pic']
        if User.objects.filter(username=username).exists():
            messages.info(request,"Username already exist")
        else:
            data = User.objects.create_user(username=username, email=email, password=password)
            user = Profile(user_type=user_type, user_id=data, phone=pnum, profile_pic=pro_pic, subject=subject)
            data.save()
            user.save()
    return render(request, 'signup.html', {'subjects':subjects})


def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.info(request,"Username or Password is wrong")
    return render(request, 'signin.html')


def signout(request):
    logout(request)
    return redirect("/")


def dashboard(request):
    if request.user.is_authenticated and request.user.profile.user_type == 'student':
        courses_enrolled = Enrollment.objects.filter(student=request.user)
        friends = Friend.objects.filter(Q(received_user=request.user, accepted='yes') | Q(requested_user=request.user, accepted='yes'))
        other_users = list()
        for friend in friends:
            other_user = friend.requested_user if friend.received_user == request.user else friend.received_user
            other_users.append(other_user)
        return render(request, 'student_dashboard.html', {'courses_enrolled':courses_enrolled, 'other_users':other_users})

    if request.user.is_authenticated and request.user.profile.user_type == 'instructor':
        return render(request, 'instructor_dashboard.html')

    if request.user.is_authenticated and request.user.profile.user_type == 'creator':
        return render(request, 'creator_dashboard.html')



def profile(request, uname):
    profile_info = User.objects.get(username=uname)
    if request.user.is_authenticated:
        followers = Like.objects.filter(profile=profile_info).count() if Like.objects.filter(profile=profile_info.profile).count() < 0 else None
        user_is_follower = True if Like.objects.filter(profile=profile_info.profile, user=request.user).count() > 0 else False
        if Friend.objects.filter(Q(requested_user=request.user, received_user=profile_info) | Q(requested_user=profile_info, received_user=request.user)):
            friend = Friend.objects.get(Q(requested_user=request.user, received_user=profile_info) | Q(requested_user=profile_info, received_user=request.user)) if Friend.objects.get(Q(requested_user=request.user, received_user=profile_info) | Q(requested_user=profile_info, received_user=request.user)) else 0
        else:
            friend = None
        users = [request.user.username, uname]
        users.sort()
        message_room_name = f"{users[0]}_{users[1]}_message_room"

        if request.method == 'POST' and 'follow_submit_button' in request.POST:
            user = request.user
            profile = profile_info.profile
            Like.objects.create(user=user, profile=profile)
            profile.followers = Like.objects.filter(profile=profile).count()
            profile.save()

        if request.method == 'POST' and 'unfollow_submit_button' in request.POST:
            user = request.user
            profile = profile_info.profile
            Like.objects.get(user=user, profile=profile).delete()
            profile.followers = Like.objects.filter(profile=profile).count()
            profile.save()
        return render(request, 'profile.html', {'pinfo':profile_info, 'message_room_name':message_room_name, 'friend':friend, 'followers':followers, 'user_is_follower':user_is_follower})
    else:
        return render(request, 'profile.html', {'pinfo': profile_info})



def users_course_rooms(request):
    enrollments = Enrollment.objects.filter(Q(student=request.user))
    course_rooms = Course_Room.objects.filter(Q(instructor_profile=request.user)).order_by('course')
    return render(request, 'users_course_rooms.html', {'enrollments':enrollments, 'course_rooms':course_rooms})



def message(request, message_room_name):
    if Message_Room.objects.filter(room_name=message_room_name):
        message_room = Message_Room.objects.get(room_name=message_room_name)
        room_messages = Message.objects.filter(message_room=message_room)
        for message in room_messages:
            message.message = dehasher(message.message)
    else:
        other_user = message_room_name.split("_")[1] if request.user.username == message_room_name.split("_")[0] else message_room_name.split("_")[0]
        other_user = User.objects.get(username=other_user)
        Message_Room.objects.create(
            room_name=message_room_name,
            user1=request.user,
            user2=other_user,
        )
        message_room = Message_Room.objects.get(room_name=message_room_name)
        room_messages = Message.objects.filter(message_room=message_room)


    if request.method == 'POST':
        message = request.POST['message']
        message = hasher(message)

        user = request.user
        # Message_Room.objects.create(
        #     message_room=message_room,
        #     user1 = users[0],
        #     user2 = users[1],
        # )
        Message.objects.create(
            user=user,
            message=message,
            message_room=message_room,
        )
    return render(request, 'message.html', {'message_room':message_room, 'room_messages':room_messages})




def message_box(request):
    message_rooms = Message_Room.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    other_user = list()
    for room in message_rooms:
        other_user.append(room.user1 if request.user == room.user2 else room.user2)
    message_rooms = tuple(zip(message_rooms, other_user))
    return render(request, 'message_box.html', {'message_rooms':message_rooms, 'other_user':other_user})



def sent_friend_request(request, receiver_username):
    other_user = User.objects.get(username=receiver_username)
    if request.method == 'POST':
        sent_request = request.POST['sent_request']
        if Friend.objects.filter(Q(requested_user=request.user, received_user=other_user) | Q(requested_user=other_user, received_user=request.user)):
            friend = Friend.objects.get(Q(requested_user=request.user, received_user=other_user) | Q(requested_user=other_user, received_user=request.user))
            print("Dinka Dinka", sent_request)
            friend.requested = sent_request
            friend.save()
        else:
            friend = Friend(requested_user=request.user, received_user=other_user, requested=sent_request)
            friend.save()
        return redirect('/')
    return render(request, 'sent_friend_request.html', {'receiver_username':receiver_username})


def accept_friend_request(request, requested_username):
    other_user = User.objects.get(username=requested_username)
    if request.method == 'POST':
        accept_request = request.POST['accept_request']
        friend = Friend.objects.get(Q(requested_user=other_user, received_user=request.user))
        if accept_request == 'yes':
            friend.friends = 'yes'
        friend.accepted=accept_request
        friend.save()
        return redirect('/')
    return render(request, 'accept_friend_request.html', {'requested_username':requested_username})


def unfriend(request, friend):
    other_user = User.objects.get(username=friend)
    if request.method == 'POST':
        unfriend = request.POST['unfriend']
        print(Friend.objects.get(Q(requested_user=other_user, received_user=request.user) | Q(requested_user=request.user, received_user=other_user)))
        friend = Friend.objects.get(Q(requested_user=other_user, received_user=request.user) | Q(requested_user=request.user, received_user=other_user))
        if unfriend == 'yes':
            friend.friends = 'no'
            friend.accepted ='no'
        friend.save()
        return redirect('/')
    return render(request, 'unfriend.html', {'friend':friend})



def friends(request):
    friends = Friend.objects.filter(Q(received_user=request.user, accepted='yes') | Q(requested_user=request.user, accepted='yes'))
    other_users = list()
    for friend in friends:
        other_user = friend.requested_user if friend.received_user == request.user else friend.received_user
        other_users.append(other_user)
    friend_list = list(zip(friends, other_users))
    return render(request, 'friends.html', {'friend_list':friend_list, 'other_users':other_users})



def friend_requests(request):
    # f_requests = Friend.objects.filter(Q(received_user=request.user)) if Friend.objects.filter(Q(received_user=request.user)) else 'No Requests'
    f_requests = Friend.objects.filter(Q(received_user=request.user, accepted='no'))
    # if request.method == 'POST':
    #     sent_request = request.POST['sent_request']
    #     if Friend.objects.filter(Q(requested_user=request.user, received_user=other_user) | Q(requested_user=other_user, received_user=request.user)):
    #         friend = Friend.objects.get(Q(requested_user=request.user, received_user=other_user) | Q(requested_user=other_user, received_user=request.user))
    #         print("Dinka Dinka", sent_request)
    #         friend.requested = sent_request
    #         friend.save()
    #     else:
    #         friend = Friend(requested_user=request.user, received_user=other_user, requested=sent_request)
    #         friend.save()
    #     return redirect('/')
    return render(request, 'friend_requests.html', {'f_requests':f_requests})



def create_course(request):
    if request.user.profile.user_type == 'creator' and request.method == 'POST':
        course_type = request.POST['course_type']
        course_name = request.POST['course_name']
        course_details = request.POST['course_details']
        course_poster = request.FILES['course_poster']
        page_count = request.POST['page_count']
        course_register = Course(creator_id=request.user.id, course_type=course_type, course_name=course_name, course_details=course_details, course_poster=course_poster)
        course_register.save()
        if page_count:
            for i in range(1, int(page_count)+1):
                video = f'{request.POST[f"video{i}"]}'[32:]
                description = f'{request.POST[f"description{i}"]}'
                Course_Contents(course=course_register, page_number=i, video=video, description=description).save()
        # course_room_register = Course_Room(course=Course.id, number=1, instructor=course_register.course_instructors.all()[0])
        # course_room_register.save()
        return redirect("/")
    return render(request, 'create_course.html', {'subjects':subjects})



def update_course(request, c_id):
    course = Course.objects.get(id=c_id)
    course_contents = Course_Contents.objects.filter(course=course).order_by('page_number')
    # videos = getattr(course, 'course_videos')
    # video_links = videos.replace("[", "").replace("]", "").replace("'", "").replace(", ", ",")
    # video_links = video_links.split(",")
    # link_count = len(video_links)
    # print(video_links)


    if request.method == 'POST':
        course_name = request.POST['course_name']
        course_details = request.POST['course_details']
        course_poster = request.FILES['course_poster']
        video_count = int(request.POST['video_count']) + int(request.POST['link_count'])
        course_videos = []
        for i in range(1, int(video_count) + 1):
            video = f'{request.POST[f"video{i}"]}'
            course_videos.append(video[32:])
        course_videos = str(course_videos)
        course.course_name = course_name
        course.course_details = course_details
        course.course_videos = course_videos
        course.course_poster = course_poster
        course.save()
    if link_count == 1 and len(video_links[0]) < 10:
        return render(request, 'update_course.html', {'course': course, 'video_links': None, 'link_count': 0})
    return render(request, 'update_course.html', {'course':course, 'course_contents':course_contents, 'video_links':video_links, 'link_count':link_count})



def course_details(request, c_id):
    course = Course.objects.get(id=c_id)
    total_enrollments = course.total_enrollments()
    course_instructors = Instructor.objects.filter(course_id=c_id)
    users_in_course = Enrollment.objects.filter(course_id=c_id)
    users_in_course = [enroll.student for enroll in users_in_course]
    total_enrollments = course.total_enrollments()
    course_rooms = Course_Room.objects.filter(course_id=c_id)

    for course_room in course_rooms:
        course_room.enrolled = course_room.enrollment_set.count()

    if request.method == 'POST' and 'like_submit_button' in request.POST:
        user = request.user
        course = course
        Like.objects.create(user=user, course=course)
        course.likes = Like.objects.filter(course=course).count()
        course.save()


    if request.method == 'POST' and 'unlike_submit_button' in request.POST:
        user = request.user
        course = course
        Like.objects.get(user=user, course=course).delete()
        course.likes = Like.objects.filter(course=course).count()
        course.save()

    if request.user.is_authenticated:
        user_liked_course = True if Like.objects.filter(course=course, user=request.user).count() > 0 else False
        if request.user in users_in_course:
            enrollment = Enrollment.objects.get(course_id=c_id, student_id=request.user.id)
            # courses_joined = Courses_Joined.objects.filter(course_id=c_id, student_id=request.user.id)
            return render(request, 'course_details.html',
                          {'course': course, 'enrollment': enrollment, 'user_liked_course':user_liked_course, 'total_enrollments': total_enrollments, 'users_in_course': users_in_course, 'course_instructors': course_instructors, 'course_rooms':course_rooms})



    return render(request, 'course_details.html', {'course':course, 'total_enrollments':total_enrollments, 'users_in_course':users_in_course, 'course_rooms':course_rooms, 'course_instructors': course_instructors})






def course_room(request, c_id):
    users_in_course = Enrollment.objects.filter(course_room_id=c_id)
    users_in_course = [enroll.student for enroll in users_in_course]
    course_room = Course_Room.objects.get(id=c_id)
    course = course_room.course
    course_contents = Course_Contents.objects.filter(course=course)
    instructions = Instructions.objects.filter(course_room=course_room) if Instructions.objects.filter(course_room=course_room).count() > 0 else None
    # # course_videos = Course.course_videos
    # # video_links = re.findall(r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=)?([^\s]+)', course_videos)
    # # video_links = list(map(str, video_links))
    # videos = getattr(course, 'course_videos')
    # only_links = videos.replace("[", "").replace("]", "").replace("'", "").replace(", ", ",")
    # only_links = only_links.split(",")
    # only_links = list(filter(lambda x: len(x)==11, only_links))
    # # video_links = re.findall(r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/(?:watch\?v=)?([^\s]+)', videos)

    p = Paginator(course_contents, 1)
    page = request.GET.get('page')
    contents = p.get_page(page)

    if request.method == 'POST' and request.user.profile.user_type == 'instructor':
        instruction = request.POST['instruction']
        Instructions(instructor=request.user, course_room=course_room, instruction=instruction).save()

    return render(request, 'course_room.html', {'course':course, 'instructions':instructions, 'contents':contents, 'course_room':course_room, 'users_in_course':users_in_course})




def course_room_discuss(request, c_id):
    course_room = Course_Room.objects.get(id=c_id)
    # comments = Comment.objects.filter(id=c_id).order_by('created_at')
    comments = Comment.objects.filter(course_room=course_room)

    for comment in comments:
        comment.comment = dehasher(comment.comment)


    if request.method == 'POST' and request.POST['comment']:
        user = request.user
        comment = request.POST['comment']
        if comment == "":
            messages.info(request, 'No Comment added')
            return render(request, 'course_room_discuss.html', {'comments':comments, 'course_room':course_room})
        comment = hasher(comment)
        Comment.objects.create(
            user=user,
            comment=comment,
            course_room=course_room,
        )
        # commented = Comment(user=user, comment=comment, course_room=course_room)
        # commented.save()
    return render(request, 'course_room_discuss.html', {'comments':comments, 'course_room':course_room})



def course_room_discussion_room(request, discussion_id):
    comment = Comment.objects.get(Q(id=discussion_id))
    comment.comment = dehasher(comment.comment)
    replies = Reply.objects.filter(Q(parent_comment=comment))
    for reply in replies:
        reply.reply = dehasher(reply.reply)

    if request.method == 'POST' and request.POST['reply']:
        user = request.user
        reply = request.POST['reply']
        reply = hasher(reply)
        replied = Reply(user=user, reply=reply, parent_comment=comment)
        replied.save()
    return render(request, 'course_room_discussion_room.html', {'comment':comment, 'replies':replies})




def discussion_room(request, discussion_id):
    comment = Comment.objects.get(Q(id=discussion_id))
    comment.comment = dehasher(comment.comment)
    replies = Reply.objects.filter(Q(parent_comment=comment))
    for reply in replies:
        reply.reply = dehasher(reply.reply)

    if request.method == 'POST' and 'reply_button' in request.POST:
        user = request.user
        reply = request.POST['reply']
        reply = hasher(reply)
        replied = Reply(user=user, reply=reply, parent_comment=comment)
        replied.save()
    return render(request, 'discussion_room.html', {'comment':comment, 'replies':replies})



def post(request):
    posts = Post.objects.all().order_by('-likes')
    if request.user.is_authenticated:
        # print("sdfjhskjghkhsdfg", Like.objects.filter(user=request.user).count())
        likes = Like.objects.filter(user=request.user) if Like.objects.filter(user=request.user).count() > 0 else list()
        liked_posts = [like.post.id for like in likes if like.post]
        # if likes is not None:
        #     for like in likes:
        #         liked_posts.append(like.post.id)
    # comments = Comment.objects.filter(id=c_id).order_by('created_at')
    # comments = Comment.objects.filter(post=).order_by('created_at')
    if request.method == 'POST' and 'post_submit_button' in request.POST and request.user.is_authenticated:
        user = request.user
        post = request.POST['post']
        post_heading = request.POST['post_heading']
        subject = request.POST['subject']
        Post.objects.create(
            user=user,
            post_heading=post_heading,
            post=post,
            subject=subject,
        )

    if request.method == 'POST' and 'like_submit_button' in request.POST and request.user.is_authenticated:
        user = request.user
        id = request.POST['post']
        post = Post.objects.get(id=id)
        Like.objects.create(user=user, post=post)
        post.likes = Like.objects.filter(post=post).count()
        post.save()


    if request.method == 'POST' and 'unlike_submit_button' in request.POST and request.user.is_authenticated:
        user = request.user
        id = request.POST['post']
        post = Post.objects.get(id=id)
        Like.objects.get(user=user, post=post).delete()
        post.likes = Like.objects.filter(post=post).count()
        post.save()

    # if request.method == 'POST' and request.POST['reply']:
    #     user = request.user
    #     comment = request.POST['reply']
    #     comment_id = request.POST['comment_id']
    #     replied = Reply(user=user, comment=comment, course_room_id=c_id)
    #     replied.save()
    if request.user.is_authenticated:
        return render(request, 'post.html', {'posts':posts, 'subjects':subjects, 'liked_posts':liked_posts})
    return render(request, 'post.html', {'posts': posts, 'subjects': subjects})



def post_room(request, p_id):
    post = Post.objects.get(Q(id=p_id))
    comments = Comment.objects.filter(post=post)
    for comment in comments:
        comment.comment = dehasher(comment.comment)

    if request.method == 'POST' and request.POST['comment']:
        user = request.user
        comment = request.POST['comment']
        if comment == "":
            messages.info(request, 'No Comment added')
            return render(request, 'post_room.html', {'comments': comments, 'post': post})
        comment = hasher(comment)
        Comment.objects.create(
            user=user,
            comment=comment,
            post=post,
        )
        # commented = Comment(user=user, comment=comment, course_room=course_room)
        # commented.save()
    return render(request, 'post_room.html', {'comments':comments, 'post':post})



def add_instructors(request, c_id):
    course = Course.objects.get(id=c_id)
    instructors = Profile.objects.filter(subject=course.course_type)
    course_instructors = Instructor.objects.filter(course_id=c_id)
    course_instructors = [profile.user for profile in course_instructors]
    instructors = [profile.user_id for profile in instructors if profile.user_id not in course_instructors]
    # print(course_instructors)
    # print(instructors)
    # print(c_id)
    if request.method == 'POST':
        instructor = request.POST['instructor']
        Instructor(user_id=instructor, course_id=course.id).save()

    return render(request, 'add_instructors.html', {'course':course, 'instructors':instructors})



def join_course(request, c_id):
    course = Course.objects.get(id=c_id)
    total_enrollments = course.total_enrollments()
    users_in_course = Enrollment.objects.filter(course_id=c_id)
    users_in_course = [enroll.student for enroll in users_in_course]

    if request.method == 'POST' and request.POST['confirm_join'] == 'yes' and request.user not in users_in_course:
        user = request.user
        course.add_student(user)
        enrollment = Enrollment.objects.get(course=course, student=user)
        if enrollment:
            return redirect('/')

        enrollment = Enrollment.objects.create(course=course, student=user)
        enrollment.save()
        joined = Courses_Joined(course=course, student=user, course_room=enrollment.course_room)
        joined.save()
        # url = reverse('course_room', args=[c_id])
        # return redirect(url)
        # return redirect('course_room', args=[enrollment.course_room_id])
        return render('/')

    return render(request, 'join_course.html', {'course':course, 'total_enrollments':total_enrollments})



def enroll_course(request, c_id):
    course = Course.objects.get(id=c_id)



def user_list(request):
    user_list = User.objects.all()
    courses = Course.objects.all()
    return render(request, 'user_list.html', {'users':user_list, 'courses':courses})



def search_results(request):
    query = None
    if 'q' in request.GET:
        query = request.GET.get('q')
        courses = Course.objects.all().filter(Q(course_name__icontains=query) | Q(course_type__icontains=query))
        instructors = User.objects.all().filter(Q(username__icontains=query))
        return render(request, 'search_results.html', {'query' : query, 'courses' : courses, 'instructors' : instructors})



def comments(request, id):
    if request.method == 'POST':
        user = request.user
        content = request.POST['content']
        course_room_id = request.POST['course_room_id']
        comment = Comment.objects.create(
            content=content,
            course_room_id=course_room_id,
            user=user,
        )
        messages.success(request, 'Comment Added Successfully')
        if section[:2] == 'cr':
            return render('course_room', id=section)



def hasher(text):
    text = text[-1::-1]
    text = list(text)
    text = list(map(ord, text))
    text = list(map(lambda x:.5*x, text))
    text = list(map(str, text))
    text = "$".join(text)
    return text


def dehasher(text):
    text = text.split("$")
    text = list(map(float, text))
    text = list(map(lambda x:2*x, text))
    text = list(map(int, text))
    text = list(map(chr, text))
    text = "".join(text)
    text = text[-1::-1]
    return text