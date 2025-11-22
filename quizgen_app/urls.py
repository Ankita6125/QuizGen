from django.urls import path
from . import views
from .services.quiz_api import chat_response
urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    # add new pattern with count
    path("start/<int:category_id>/<int:subcategory_id>/<str:level>/<int:count>/", views.generate_quiz_view, name="generate_quiz"),
    path("quiz/<int:quiz_id>/", views.quiz_view, name="quiz"),
    path("history/", views.history_view, name="history"),
    path("quiz/play/", views.quiz_play_view, name="quiz_play"),
    path("quiz/get/<int:index>/", views.get_question_view, name="get_question"),
    path("quiz/submit/", views.submit_quiz_view, name="submit_quiz"),
    path("categories/", views.categories_view, name="categories"),
   #  path("performance/", views.performance_view, name="performance"),
    path("profile/", views.profile_view, name="profile"),
    path("chat/", chat_response, name="chat_response"),


]
