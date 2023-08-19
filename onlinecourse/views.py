import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Course, Enrollment, Lesson, Question, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html", context)
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except Exception:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context["message"] = "User already exists."
            return render(request, "onlinecourse/user_registration_bootstrap.html", context)


def login_request(request):
    context = {}
    if request.method != "POST":
        return render(request, "onlinecourse/user_login_bootstrap.html", context)
    username = request.POST["username"]
    password = request.POST["psw"]
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("onlinecourse:index")
    else:
        context["message"] = "Invalid username or password."
        return render(request, "onlinecourse/user_login_bootstrap.html", context)


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


class CourseListView(generic.ListView):
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by("-total_enrollment")[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "onlinecourse/course_detail_bootstrap.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        lessons = Lesson.objects.filter(course=self.object)
        questions = Question.objects.filter(lesson__in=lessons)
        context = {"course": self.object, "lessons": lessons, "questions": questions}
        return render(request, self.template_name, context)


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode="honor")
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname="onlinecourse:course_details", args=(course.id,)))


def submit(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, pk=course_id)
        user = request.user
        enrollment = Enrollment.objects.get(user=user, course=course)
        submission = Submission.objects.create(enrollment=enrollment)
        submitted_answers = extract_answers(request)
        for answer_id in submitted_answers:
            choice = Choice.objects.get(id=answer_id)
            submission.choices.add(choice)
        return redirect("onlinecourse:show_exam_result", course_id=course.id, submission_id=submission.id)


def extract_answers(request):
    return [int(request.POST[key]) for key in request.POST if key.startswith("choice")]


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_choices = submission.choices.all()
    all_correct = all(choice.is_correct for choice in selected_choices)
    total_score = 100 if all_correct else 0
    
    selected_choices_with_status = [
        {"choice": choice, "selected": choice.is_correct} for choice in selected_choices
    ]
    
    context = {
        "course": course,
        "selected_choices_with_status": selected_choices_with_status,
        "total_score": total_score
    }
    return render(request, "onlinecourse/exam_result_bootstrap.html", context)
