from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'onlinecourse'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    path(route='', view=views.CourseListView.as_view(), name='index'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    # ex: /onlinecourse/5/
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    # ex: /enroll/5/
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),

    # <HINT> Create a route for submit view
    path('submit/<int:course_id>/', views.submit_request, name='submit'),

    # <HINT> Create a route for show_exam_result view
    path('submission/<int:pk>/', views.show_results, name='submission')

 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
