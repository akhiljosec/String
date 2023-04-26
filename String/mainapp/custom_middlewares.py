from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve
from .models import Course_Room, Enrollment, Instructor
from shopapp.models import Cart


class UserRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.view_for_creator = ['create_course', 'update_course']
        self.view_for_student = ['join_course']
        self.view_for_message = ['message']
        self.view_for_course_room = ['course_room', 'course_room_discuss', 'course_room_discussion_room']
        self.view_for_sell = ['shop_sell']
        self.view_for_cart_and_bank = ['shop_cart', 'bank_account']
        self.view_for_payment = ['make_payment']
        # One-time configuration and initialization.


    def __call__(self, request):
        # Code to be executed for each request before


        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # if view_func.__name__ in ["create_course", "join_course", "delete", "movie_add",'Movies']:
        #     if request.user.is_authenticated and request.user.profile.user_type == 'creator':
        #         pass
        #     else:
        #         messages.info(request, "You must have a creator account to access it")
        #         return redirect("join_course")

        view_func, args, kwargs = resolve(request.path_info)

        if view_func.__name__ in self.view_for_creator:
            if request.user.profile.user_type == 'student':
                messages.info(request, "You must have a creator account to access it")
                return redirect("/")
            elif request.user.profile.user_type == 'instructor':
                messages.info(request, "You must have a creator account to access it")
                return redirect("/")


        if view_func.__name__ in self.view_for_student:
            if request.user.profile.user_type == 'creator':
                messages.info(request, "You must have a student account to access it")
                return redirect("/")
            elif request.user.profile.user_type == 'instructor':
                messages.info(request, "You must have a student account to access it")
                return redirect("/")


        if view_func.__name__ in self.view_for_message:
            message_room_value = kwargs.get('message_room_name')

            message_room_value = message_room_value.split("_")

            if request.user.is_authenticated and request.user.username not in message_room_value[:2]:
                messages.info(request, "You cannot access to other users message rooms")
                return redirect("/")



        if view_func.__name__ in self.view_for_course_room:
            course_room_id = kwargs.get('c_id')
            print(course_room_id)
            course_room = Course_Room.objects.get(id=course_room_id)
            user_in_course_room = True if Enrollment.objects.filter(course_room=course_room, student=request.user).count() > 0 else False
            instructor_of_course_room = True if Course_Room.objects.filter(id=course_room_id, instructor_profile=request.user).count() > 0 else False
            if not user_in_course_room and not instructor_of_course_room:
                messages.info(request, "You cannot enter this Course Room")
                return redirect("/")


        if view_func.__name__ in self.view_for_sell:
            if not request.user.is_authenticated:
                messages.info(request, "You must login to sell your product")
                return redirect("/shop")


        if view_func.__name__ in self.view_for_cart_and_bank:
            u_name = kwargs.get('u_name')
            if not request.user.is_authenticated and not u_name == request.user.username:
                messages.info(request, "You must login to access cart or bank account")
                return redirect("/shop")


        if view_func.__name__ in self.view_for_payment:
            cart_id = kwargs.get('cart_id')
            cart = Cart(user=request.user)
            if not request.user.is_authenticated and not cart_id == cart.id:
                messages.info(request, "This is not your Cart")
                return redirect("/shop")