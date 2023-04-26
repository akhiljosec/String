from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .context_processors import subjects



USER_TYPES = (
    ('student', 'Student'),
    ('instructor', 'Instructor'),
    ('creator', 'Creator'),
)

SUBJECTS = []

for subject in subjects:
    SUBJECTS.append((f'{subject}', f'{subject}'))

SUBJECTS = tuple(SUBJECTS)



class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    subject = models.CharField(max_length=100, choices=SUBJECTS, null=True, blank=True)
    phone = models.CharField(max_length=12, unique=True)
    profile_pic = models.ImageField(upload_to="profile_pic")
    followers = models.IntegerField(null=True, blank=True)



class Message_Room(models.Model):
    room_name = models.CharField(max_length=100)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1_set')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2_set')



class Message(models.Model):
    message = models.TextField()
    message_room = models.ForeignKey(Message_Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)



class Friend(models.Model):
    requested_user = models.ForeignKey(User, related_name='requested_user', on_delete=models.CASCADE)
    received_user = models.ForeignKey(User, related_name='received_user', on_delete=models.CASCADE)
    requested = models.CharField(max_length=10, null=True, blank=True)
    accepted = models.CharField(max_length=10, default='no')
    friends = models.CharField(max_length=10, default='no')



class Course(models.Model):
    COURSE_TYPES = []

    for subject in subjects:
        COURSE_TYPES.append((f'{subject}', f'{subject}'))

    COURSE_TYPES = tuple(COURSE_TYPES)

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    course_type = models.CharField(max_length=100, choices=COURSE_TYPES)
    course_name = models.CharField(max_length=100)
    course_details = models.TextField(max_length=1000)
    course_poster = models.ImageField(upload_to="posters")
    likes = models.IntegerField(null=True, blank=True)



    def get_next_instructor(self, last_course_room_instructor=None):
        course_instructors = Instructor.objects.filter(course_id=self.id).order_by('joined_date')
        current_instructor_index = list(course_instructors).index(last_course_room_instructor) if last_course_room_instructor is not None else -1
        next_course_instructor = course_instructors[current_instructor_index+1] if current_instructor_index+1 < len(course_instructors) else course_instructors[0]
        return next_course_instructor



    def add_student(self, student):
        course_rooms = self.course_room_set.all().order_by('number')
        last_course_room = course_rooms.last()
        # max_capacity = Course_Room.max_capacity
        max_capacity = 2

        if last_course_room and last_course_room.enrollment_set.count() < max_capacity:
            Enrollment.objects.create(
                    course=self,
                    student=student,
                    course_room=last_course_room,
                    instructor=last_course_room.instructor
                )
        else:
            instructor = self.get_next_instructor(last_course_room.instructor) if last_course_room else self.get_next_instructor()
            course_room_count = Course_Room.objects.filter(course=self).count()+1
            new_course_room = Course_Room.objects.create(
                    number = len(course_rooms)+1,
                    instructor = instructor,
                    course = self,
                    instructor_profile = instructor.user,
                    course_room_count = course_room_count,
                )
            Enrollment.objects.create(
                    course=self,
                    student=student,
                    course_room=new_course_room,
                    instructor=new_course_room.instructor
                )
            course_rooms = self.course_room_set.all().order_by('number')

        return course_rooms

    def total_enrollments(self):
        return self.enrollment_set.count()



class Course_Contents(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    video = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=10000, null=True, blank=True)



class Instructor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(auto_now_add=True)



class Course_Room(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    number = models.IntegerField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    max_capacity = models.IntegerField(default=50)
    enrolled = models.IntegerField(null=True, blank=True)
    instructor_profile = models.ForeignKey(User, on_delete=models.CASCADE)
    course_room_count = models.IntegerField()



class Instructions(models.Model):
    course_room = models.ForeignKey(Course_Room, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    instruction = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, choices=SUBJECTS, null=True, blank=True)
    post_heading = models.TextField()
    post = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(null=True, blank=True)




class Comment(models.Model):
    course_room = models.ForeignKey(Course_Room, null=True, blank=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)



class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_room = models.ForeignKey(Course_Room, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)



class Course_Reviews(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_review = models.TextField()
    course_rating = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])



class Courses_Joined(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_room = models.ForeignKey(Course_Room, on_delete=models.CASCADE)



class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    # course = models.ForeignKey(Course, on_delete=models.CASCADE)