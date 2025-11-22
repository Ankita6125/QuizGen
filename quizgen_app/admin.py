from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User, Category, SubCategory, Quiz, Question, QuizHistory


# ---------------- User Admin ---------------- #
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ["email", "is_admin", "is_active"]
    list_filter = ["is_admin", "is_active"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Permissions", {"fields": ["is_admin", "is_active"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []


# ---------------- Quiz System Admin ---------------- #
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "created_at"]
    search_fields = ["name", "category__name"]
    list_filter = ["category"]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "subcategory", "created_at"]
    search_fields = ["title", "subcategory__name"]
    list_filter = ["subcategory__category"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "quiz", "correct_answer", "created_at"]
    search_fields = ["text", "quiz__title"]
    list_filter = ["quiz"]


@admin.register(QuizHistory)
class QuizHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "quiz", "score", "completed_at"]
    search_fields = ["user__email", "quiz__title"]
    list_filter = ["quiz", "user"]


# ---------------- Register Custom User ---------------- #
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
