from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Avg, Count, F, Sum, Max
from django.db.models.functions import Coalesce
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import Category, Quiz, SubCategory, QuizHistory, UserAnswer
from .services.quiz_api import generate_quiz_questions
import random
from django.db import transaction
from django.db.models import F, ExpressionWrapper, DurationField, Avg, Max
from datetime import timedelta
from django.core.paginator import Paginator

# ---------------- QUIZ GENERATION ----------------


@login_required
def generate_quiz_view(request, category_id, subcategory_id, level, count):
    category = get_object_or_404(Category, id=category_id)
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    # AI se questions lao
    questions = generate_quiz_questions(
        category.name,
        subcategory.name,
        num_questions=count,
        difficulty=level
    )

    # ---------------------- FIXED SHUFFLE ----------------------
    for q in questions:
        # Original correct answer text
        correct_text = q["options"][q["answer"]]

        # Option texts ko shuffle karo
        values = list(q["options"].values())
        random.shuffle(values)

        # Map shuffled values back to fixed labels A,B,C,D
        q["options"] = {label: text for label, text in zip(["A","B","C","D"], values)}

        # Update correct answer label
        for label, text in q["options"].items():
            if text == correct_text:
                q["answer"] = label
                break
    # ---------------------- FIXED SHUFFLE END ----------------------

    with transaction.atomic():
        # Quiz create karo
        quiz = Quiz.objects.create(
            title=f"AI Quiz - {subcategory.name} ({level})",
            subcategory=subcategory,
            category=category,
            description=f"AI generated quiz in {subcategory.name}",
            difficulty=level,
        )

        # History create karo
        history = QuizHistory.objects.create(
            user=request.user,
            quiz=quiz,
            total_questions=count,
            started_at=timezone.now(),
        )

    # Session me store karo
    request.session["current_quiz"] = questions
    request.session["quiz_meta"] = {"history_id": history.id}

    return redirect("quiz_play")



@login_required
def quiz_play_view(request):
    questions = request.session.get("current_quiz", [])
    return render(request, "quiz_play.html", {"total": len(questions)})


@login_required
def get_question_view(request, index):
    questions = request.session.get("current_quiz", [])
    if 0 <= index < len(questions):
        return JsonResponse(questions[index], safe=False)
    return JsonResponse({"error": "Invalid question index"}, status=400)


# ---------------- AUTH ----------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- DASHBOARD ---------------------

@login_required
def dashboard_view(request):
    user = request.user

    # ---- Categories for quick-start dropdown ----
    categories = Category.objects.prefetch_related("subcategories").all()

    # ---- Base queryset for user's quiz histories ----
    user_hist_qs = QuizHistory.objects.filter(user=user).exclude(completed_at__isnull=True)

    # ---- Aggregate stats ----
    total_quizzes = user_hist_qs.count()
    stats = user_hist_qs.aggregate(avg_score=Avg("score"), best_score=Max("score"))
    avg_score = stats["avg_score"] or 0
    best_score = stats["best_score"] or 0

    # ---- Recent history (limit 5 for dashboard) ----
    recent_history = user_hist_qs.order_by("-completed_at")[:5]
    # Add status color for template
    for h in recent_history:
        if h.score >= 80:
            h.status_color = "bg-green-100 text-green-700"
        elif h.score >= 50:
            h.status_color = "bg-yellow-100 text-yellow-700"
        else:
            h.status_color = "bg-red-100 text-red-700"

    # ---- Streak calculation ----
    streak_days = 0
    last_date = None
    for h in user_hist_qs.order_by("-completed_at"):
        d = h.completed_at.date()
        if last_date is None:
            streak_days = 1
            last_date = d
        elif (last_date - d).days == 1:
            streak_days += 1
            last_date = d
        elif last_date == d:
            continue
        else:
            break

    # ---- Category performance for dashboard cards ----
    category_performance_qs = (
        user_hist_qs
        .values("quiz__category__id", "quiz__category__name")
        .annotate(avg_score=Avg("score"), quizzes=Count("id"))
        .order_by("-quizzes")
    )

    colors = ["card-color-1","card-color-2","card-color-3","card-color-4","card-color-5","card-color-6"]
    final_category_performance = []
    for i, c in enumerate(category_performance_qs):
        avg = c.get("avg_score") or 0
        status = "Strong" if avg >= 85 else "Good" if avg >= 70 else "Needs Work"
        final_category_performance.append({
            "id": c["quiz__category__id"],
            "name": c["quiz__category__name"],
            "score": round(avg, 2),
            "quizzes": c["quizzes"],
            "status": status,
            "color_class": colors[i % len(colors)]
        })

    # ---- Badges ----
    badges = []
    if total_quizzes >= 1:
        badges.append({"icon": "⭐", "name": "First Quiz", "description": "Completed your first quiz"})
    if best_score >= 90:
        badges.append({"icon": "🏆", "name": "High Scorer", "description": "Scored above 90%"})
    if streak_days >= 3:
        badges.append({"icon": "🔥", "name": "Streak Master", "description": f"{streak_days}-day streak"})

    # ---- User attempts per category ----
    user_attempts_per_category = (
        user_hist_qs
        .values("quiz__category__id")
        .annotate(attempts=Count("id"))
    )
    attempts_dict = {item["quiz__category__id"]: item["attempts"] for item in user_attempts_per_category}

    # ---- Performance over time (last 7 attempts) ----
    perf = list(user_hist_qs.order_by("-started_at")[:7])  # list conversion
    perf.reverse()  # now oldest to newest
    performance_labels = [h.started_at.strftime("%d %b") if h.started_at else "N/A" for h in perf]
    performance_scores = [h.score for h in perf]


    # ---- Category-wise performance for charts ----
    cat_data = (
        user_hist_qs.values("quiz__category__name")
        .annotate(avg_score=Avg("score"))
        .order_by("quiz__category__name")
    )
    category_labels = [c["quiz__category__name"] for c in cat_data]
    category_scores = [round(c["avg_score"], 2) for c in cat_data]

    # ---- Strongest & weakest subject ----
    if cat_data:
        strongest = max(cat_data, key=lambda x: x["avg_score"])
        weakest = min(cat_data, key=lambda x: x["avg_score"])
        strongest_subject = strongest["quiz__category__name"]
        strongest_score = round(strongest["avg_score"], 2)
        weak_subject = weakest["quiz__category__name"]
    else:
        strongest_subject = weak_subject = "N/A"
        strongest_score = 0

    # ---- Accuracy rate & Avg time per question ----
    total_correct = user_hist_qs.aggregate(total=Sum("correct_answers"))["total"] or 0
    total_questions = user_hist_qs.aggregate(total=Sum("total_questions"))["total"] or 1
    accuracy_rate = round((total_correct / total_questions) * 100, 2)

    # Avg time per question
    duration_data = user_hist_qs.annotate(
        duration=ExpressionWrapper(F('completed_at') - F('started_at'), output_field=DurationField())
    ).aggregate(avg_duration=Avg('duration'))['avg_duration']
    if duration_data:
        avg_time_per_question = round(duration_data.total_seconds() / total_questions, 2)
    else:
        avg_time_per_question = None

    # ---- Optional improvement (dynamic or fallback) ----
    accuracy_improvement = 0  # compute dynamically if needed

    # ---- Final context ----
    context = {
        "categories": categories,
        "recent_history": recent_history,
        "total_quizzes": total_quizzes,
        "avg_score": round(avg_score, 2),
        "best_score": best_score,
        "streak_days": streak_days,
        "category_performance": final_category_performance,
        "badges": badges,
        "attempts_dict": attempts_dict,
        "performance_labels": performance_labels,
        "performance_scores": performance_scores,
        "category_labels": category_labels,
        "category_scores": category_scores,
        "accuracy_rate": accuracy_rate,
        "accuracy_improvement": accuracy_improvement,
        "avg_time_per_question": avg_time_per_question,
        "strongest_subject": strongest_subject,
        "strongest_score": strongest_score,
        "weak_subject": weak_subject,
    }

    return render(request, "dashboard.html", context)






@login_required
def categories_view(request):
    """
    Show categories page with selection of category/subcategory/difficulty
    """
    categories = Category.objects.prefetch_related("subcategories").all()
    return render(request, "categories.html", {"categories": categories})


@login_required
def start_quiz(request, cat, sub, level, count):
    """
    Redirects to generate_quiz_view with parameters.
    """
    return generate_quiz_view(request, category_id=cat, subcategory_id=sub, level=level, count=count)


@login_required
def history_view(request):
    # Base queryset
    history_list = QuizHistory.objects.filter(user=request.user).order_by("-completed_at")
    
    # Paginator
    paginator = Paginator(history_list, 10)
    page_number = request.GET.get("page")
    history = paginator.get_page(page_number)
    
    # Dropdown data
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    
    return render(request, "history.html", {
        "history": history,
        "categories": categories,
        "subcategories": subcategories,
    })


def quiz_view(request, quiz_id):
    return HttpResponse(f"Quiz Page - quiz id: {quiz_id}")


# ---------------- SUBMIT QUIZ ----------------
@login_required
def submit_quiz_view(request):
    if request.method == "POST":
        questions = request.session.get("current_quiz", [])
        quiz_meta = request.session.get("quiz_meta", {})

        if not quiz_meta:
            return redirect("dashboard")

        history_id = quiz_meta.get("history_id")
        history = get_object_or_404(QuizHistory, id=history_id, user=request.user)

        # Calculate result
        total = len(questions)
        correct = 0
        user_answers = request.POST

        results = []  # 👈 yeh add karo

        for i, q in enumerate(questions):
            user_ans = user_answers.get(str(i))
            is_correct = (user_ans == q["answer"])
            if is_correct:
                correct += 1

            results.append({
                "question": q["question"],
                "options": q["options"],
                "user": user_ans,
                "correct": q["answer"],
                "is_correct": is_correct,
            })

        score = round((correct / total) * 100, 2)

        # Update history
        history.correct_answers = correct
        history.score = score
        history.completed_at = timezone.now()
        history.save()

        # Clear session
        request.session.pop("current_quiz", None)
        request.session.pop("quiz_meta", None)

        return render(request, "quiz_result.html", {
            "score": score,
            "correct": correct,
            "total": total,
            "results": results,  # 👈 ab template me milega
        })

    return redirect("dashboard")



@login_required
def profile_view(request):
    user = request.user
    user_hist_qs = QuizHistory.objects.filter(user=user).exclude(completed_at__isnull=True)

    # Stats
    total_quizzes = user_hist_qs.count()
    avg_score = user_hist_qs.aggregate(Avg("score"))["score__avg"] or 0
    best_score = user_hist_qs.aggregate(Max("score"))["score__max"] or 0

    # Accuracy
    total_correct = user_hist_qs.aggregate(Sum("correct_answers"))["correct_answers__sum"] or 0
    total_questions = user_hist_qs.aggregate(Sum("total_questions"))["total_questions__sum"] or 1
    accuracy_rate = round((total_correct / total_questions) * 100, 2) if total_questions else 0

    # Streak Days (unique consecutive days)
    streak_days = 0
    last_date = None
    for h in user_hist_qs.order_by("-completed_at"):
        d = h.completed_at.date()
        if last_date is None:
            streak_days = 1
            last_date = d
        elif (last_date - d).days == 1:
            streak_days += 1
            last_date = d
        elif last_date == d:
            continue
        else:
            break

    # Strongest subject
    strongest_subject = None
    if user_hist_qs.exists():
        cat_data = (
            user_hist_qs.values("quiz__category__name")
            .annotate(avg_score=Avg("score"))
            .order_by("-avg_score")
        )
        strongest_subject = cat_data[0]["quiz__category__name"] if cat_data else None
    
    # New metrics for badges
   
    categories_attempted = user_hist_qs.values('quiz__category').distinct().count()
    difficult_quizzes_completed = user_hist_qs.filter(quiz__difficulty__gte=4).count()
    # Badges
    badges = []
    if total_quizzes >= 1:
        badges.append({"icon": "⭐", "name": "First Quiz", "description": "Completed your first quiz"})
    if best_score >= 90:
        badges.append({"icon": "🏆", "name": "High Scorer", "description": "Scored above 90%"})
    if avg_score >= 70:
        badges.append({"icon": "🎯", "name": "Consistent", "description": "Maintained 70%+ average"})
    if streak_days >= 3:
        badges.append({"icon": "🔥", "name": "Streak Master", "description": f"{streak_days}-day streak"})
    
    if best_score == 100:
        badges.append({"icon": "🥇", "name": "Perfect Score", "description": "Achieved 100% on a quiz"})
    if categories_attempted >= 3:
        badges.append({"icon": "🧭", "name": "Quiz Explorer", "description": f"Attempted quizzes in {categories_attempted} categories"})
    if difficult_quizzes_completed >= 1:
        badges.append({"icon": "🏔️", "name": "Challenger", "description": "Completed a difficult quiz"})


    # Recent Activity (last 5 quizzes)
    recent_history = user_hist_qs.order_by("-completed_at")[:5]

    context = {
        "user": user,
        "avatar": user.profile.avatar.url if hasattr(user, "profile") and user.profile.avatar else "/static/default-avatar.png",
        "name": user.profile.full_name if hasattr(user, "profile") and user.profile.full_name else user.email.split("@")[0],
        "email": user.email,
        "avg_score": round(avg_score, 2),
        "best_score": best_score,
        "attempted": total_quizzes,
        "accuracy_rate": accuracy_rate,
        "streak_days": streak_days,
        "strongest_subject": strongest_subject or "N/A",
        "badges": badges,
        "recent_history": recent_history,
    }
    return render(request, "profile.html", context)



