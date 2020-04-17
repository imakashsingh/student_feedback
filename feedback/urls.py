from django.urls import path
from feedback.feedback_views.viewss import *

urlpatterns = [
    path('givefeedback/', SubmitFeedbackView.as_view(),name="getform"),
    path('analyse/',PerformAnalysis.as_view(),name="analyse"),
    path('login/',LoginView.as_view(),name="login"),
    path('index/',LandingPage.as_view(),name="index"),
    path('adminop/',AdminOptions.as_view(),name="adminop"),
    path('subjects/',Subjects.as_view(),name="subjects"),
    path('subjects/add',SubjectOperations.as_view(),name="add_subject"),
    path('subjects/<str:sub>/edit',SubjectOperations.as_view(),name="edit_subject"),
    path('subjects/<str:sub>/delete',SubjectOperations.as_view(),name="delete_subject"),
    path('subjects/deleteall',SubjectOperations.as_view(),name="delete_all"),
    path('sessionstarted',LandingPage.as_view(),name="session_started"),
    path('loginppage/',LoginView.as_view(),name = "login"),
    path('logoutppage/',logout_func,name = "logout"),
    path('loginerror/',LoginError.as_view(),name="loginerror"),
]