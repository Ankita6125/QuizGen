import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%6+rb1$-se&z=aola42w6c3tt$tr@a@fm0*^copph@%6fxki-c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'quizgen_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quizgen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR /"templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'quizgen.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'quizgen_app.User'

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"   # dashboard/homepage
LOGOUT_REDIRECT_URL = "login"



load_dotenv()  # load .env file

QUIZ_API_KEY = os.getenv("OPENROUTER_API_KEY")

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# ---------------- Jazzmin Settings ---------------- #

# ---------------- Jazzmin Settings ---------------- #
def get_user_avatar(user):
    try:
        return user.profile.avatar.url
    except:
        return "/static/images/default-avatar.png"


JAZZMIN_SETTINGS = {
    "site_title": "QuizGen Admin",
    "site_header": "Admin",
    "site_brand": "Quiz",
    "welcome_sign": "Welcome to the CareerQuiz Admin Panel",
    "copyright": "infosys",
    
    # Searchable models
    "search_model": ["quizgen_app.User"],

    # User menu links
    "usermenu_links": [
        {"model": "quizgen_app.User"}
    ],

    "use_google_fonts_cdn": True,

    # Logos (from static folder)
    "site_logo_classes": "img-circle",
    "site_logo": "images/quiz.png",
    "login_logo": "images/quiz.png",
    "login_logo_dark": "images/quiz.png",
    "custom_css": "admin/css/custom.css",

    # User avatar callable
    "user_avatar": get_user_avatar,

    # FontAwesome icons for each model
    "icons": {
        "quizgen_app.User": "fas fa-user-circle",
        "quizgen_app.Profile": "fas fa-id-badge",
        "quizgen_app.Category": "fas fa-briefcase",
        "quizgen_app.SubCategory": "fas fa-exchange-alt",
        "quizgen_app.Quiz": "fas fa-book",
        "quizgen_app.Question": "fas fa-brain",
        "quizgen_app.QuizHistory": "fas fa-lightbulb",
        "quizgen_app.UserAnswer": "fas fa-trophy",
    },

    # Sidebar order
    "order_with_respect_to": [
        "quizgen_app.User",
        "quizgen_app.Profile",
        "quizgen_app.Category",
        "quizgen_app.SubCategory",
        "quizgen_app.Quiz",
        "quizgen_app.Question",
        "quizgen_app.QuizHistory",
        "quizgen_app.UserAnswer",
    ],
}

# ------------------ Jazzmin UI Tweaks ------------------ #
JAZZMIN_UI_TWEAKS = {
    "theme": "cerulean",
    "dark_mode_theme": "darkly",
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
}

# ------------------ Jazzmin Dashboard ------------------ #
JAZZMIN_DASHBOARD = {
    "widgets": [
        # 🔹 Quick Stats Cards
        {
            "type": "stats",
            "title": "Quick Stats",
            "stats": [
                {"label": "Users", "model": "quizgen_app.User", "aggregate": "count", "icon": "fas fa-users", "class": "bg-primary"},
                {"label": "Quizzes", "model": "quizgen_app.Quiz", "aggregate": "count", "icon": "fas fa-book", "class": "bg-success"},
                {"label": "Questions", "model": "quizgen_app.Question", "aggregate": "count", "icon": "fas fa-brain", "class": "bg-info"},
                {"label": "Played", "model": "quizgen_app.QuizHistory", "aggregate": "count", "icon": "fas fa-history", "class": "bg-danger"},
            ],
        },
        # 🔹 Line Chart for Quiz History
        {
            "type": "chart",
            "title": "Quizzes Played Over Time",
            "model": "quizgen_app.QuizHistory",
            "chart": "line",
            "options": {
                "x_field": "completed_at",
                "y_field": "id",
                "aggregate": "count",
            },
        },
        # 🔹 Models List Section
        {
            "type": "model_list",
            "title": "QuizGen Models",
            "models": [
                "quizgen_app.User",
                "quizgen_app.Profile",
                "quizgen_app.Category",
                "quizgen_app.SubCategory",
                "quizgen_app.Quiz",
                "quizgen_app.Question",
                "quizgen_app.QuizHistory",
                "quizgen_app.UserAnswer",
            ],
        },
    ]
}
