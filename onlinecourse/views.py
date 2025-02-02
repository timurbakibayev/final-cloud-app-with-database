from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
# <HINT> Import any new Models here
from .models import Course, Enrollment, Submission, Question, Choice
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def index(request: HttpRequest) -> HttpResponse:
    return redirect("onlinecourse:index")


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def submit_request(request, course_id) -> HttpResponse:
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course, mode="honor")
    submission = Submission()
    submission.enrollment = enrollment
    submission.save()
    questions = Question.objects.filter(lesson__course=course)
    for question in questions:
        for choice in question.choice_set.all():
            if int(request.POST.get(f"choice_{choice.id}", "-1")) == choice.id:
                submission.choices.add(choice)

    return HttpResponseRedirect(reverse(viewname='onlinecourse:submission', args=(submission.id,)))


def show_results(request: HttpRequest, pk: int) -> HttpResponse:
    submission = get_object_or_404(Submission, pk=pk)
    enrollment = submission.enrollment
    course = enrollment.course
    questions = Question.objects.filter(lesson__course=course)
    submission_choices = submission.choices.all()
    selected_ids = [choice.id for choice in submission_choices]
    correct = 0
    for question in questions:
        question.correct = question.is_get_score(selected_ids)
        question.choices = list(question.choice_set.all())
        for choice in question.choices:
            choice.guessed = choice.is_correct == (choice.id in selected_ids)

        if question.correct:
            correct += 1
    grade = int(correct / len(questions) * 1000)/10

    return render(
        request=request,
        template_name='onlinecourse/exam_result_bootstrap.html',
        context={
            "submission": submission,
            "enrollment": enrollment,
            "course": course,
            "questions": questions,
            "grade": grade,
        }
    )


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# <HINT> Create an exam result view to check if learner passed exam and show their question results and result for each question,
# you may implement it based on the following logic:
        # Get course and submission based on their ids
        # Get the selected choice ids from the submission record
        # For each selected choice, check if it is a correct answer or not
        # Calculate the total score
#def show_exam_result(request, course_id, submission_id):



