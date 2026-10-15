from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.permissions import is_teacher, is_admin
from exams.models import PlacementAttempt, PlacementQuestion, PlacementTest
from students.models import StudentProfile


IQ_TEST_TITLE = "آزمون هوش تصویری پیچک دانش"
IQ_QUESTIONS = [
    {"id":"q1","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="دایره، مربع، دایره، مربع، جای خالی"><circle cx="45" cy="45" r="20" fill="#15966d"/><rect x="100" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><circle cx="195" cy="45" r="20" fill="#15966d"/><rect x="250" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><text x="360" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دایره سبز"),("B","مربع زرد"),("C","مثلث آبی"),("D","ستاره قرمز")],"answer":"A"},
    {"id":"q2","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک نقطه، دو نقطه، سه نقطه، جای خالی"><g fill="#536fe5"><circle cx="45" cy="45" r="7"/><circle cx="130" cy="35" r="7"/><circle cx="130" cy="55" r="7"/><circle cx="215" cy="30" r="7"/><circle cx="215" cy="45" r="7"/><circle cx="215" cy="60" r="7"/></g><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","یک نقطه"),("B","دو نقطه"),("C","چهار نقطه"),("D","شش نقطه")],"answer":"C"},
    {"id":"q3","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مثلث رو به بالا، مثلث رو به پایین، مثلث رو به بالا، جای خالی"><polygon points="45,18 20,65 70,65" fill="#f2b84b"/><polygon points="130,68 105,21 155,21" fill="#15966d"/><polygon points="215,18 190,65 240,65" fill="#f2b84b"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مثلث زرد رو به بالا"),("B","مثلث سبز رو به پایین"),("C","دایره سبز"),("D","مربع زرد")],"answer":"B"},
    {"id":"q4","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مربع کوچک، مربع بزرگ، مربع کوچک، جای خالی"><rect x="27" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><rect x="105" y="12" width="66" height="66" rx="5" fill="#9b70d6"/><rect x="202" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مربع کوچک"),("B","مربع بزرگ"),("C","دایره بزرگ"),("D","مثلث کوچک")],"answer":"B"},
    {"id":"q5","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک ستاره، دو ستاره، سه ستاره، جای خالی"><g fill="#f2b84b" font-size="30" text-anchor="middle"><text x="45" y="56">★</text><text x="125" y="56">★</text><text x="153" y="56">★</text><text x="215" y="56">★</text><text x="243" y="56">★</text><text x="271" y="56">★</text></g><text x="350" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دو ستاره"),("B","سه ستاره"),("C","چهار ستاره"),("D","پنج ستاره")],"answer":"C"},
]


def simple_home(request):
    if request.user.is_authenticated:
        if is_teacher(request.user) or is_admin(request.user):
            return redirect("simple-teacher")
        if hasattr(request.user, "student_profile"):
            return redirect("simple-student")
    return render(request, "simple/home.html")


@login_required(login_url="login")
def simple_student(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")
    attempts = PlacementAttempt.objects.filter(student=student).select_related("test")[:5]
    return render(request, "simple/student.html", {"student": student, "attempts": attempts})


@login_required(login_url="login")
def simple_iq_test(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")
    error = None
    if request.method == "POST":
        answers = {q["id"]: request.POST.get(q["id"], "") for q in IQ_QUESTIONS}
        if any(not value for value in answers.values()):
            error = "لطفاً برای هر پنج سؤال یک پاسخ انتخاب کن."
        else:
            correct = sum(answers[q["id"]] == q["answer"] for q in IQ_QUESTIONS)
            test, _ = PlacementTest.objects.get_or_create(
                title=IQ_TEST_TITLE,
                defaults={"grade": student.grade, "duration_minutes": 8, "is_active": True},
            )
            attempt = PlacementAttempt.objects.create(
                student=student,
                test=test,
                score=round(correct * 100 / len(IQ_QUESTIONS)),
                correct_answers=correct,
                total_questions=len(IQ_QUESTIONS),
                level=max(1, min(10, correct * 2)),
                completed_at=timezone.now(),
            )
            return render(request, "simple/result.html", {"attempt": attempt})
    return render(request, "simple/iq.html", {"questions": IQ_QUESTIONS, "error": error})


@login_required(login_url="login")
def simple_teacher(request):
    if not (is_teacher(request.user) or is_admin(request.user) or request.user.is_superuser):
        return redirect("simple-student")
    students = list(StudentProfile.objects.select_related("user", "classroom").order_by("user__first_name", "user__last_name")[:30])
    attempts = PlacementAttempt.objects.select_related("student__user", "test").order_by("-completed_at")[:30]
    return render(request, "simple/teacher.html", {
        "students": students,
        "student_count": StudentProfile.objects.count(),
        "attempts": attempts,
        "tests": PlacementTest.objects.prefetch_related("questions").order_by("-id")[:8],
    })


@login_required(login_url="login")
def teacher_test_manager(request):
    if not (is_teacher(request.user) or is_admin(request.user) or request.user.is_superuser):
        return redirect("simple-student")
    message = None
    error = None
    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "create_test":
            title = request.POST.get("title", "").strip()
            try:
                duration = int(request.POST.get("duration_minutes", "15"))
            except (TypeError, ValueError):
                duration = 15
            if not title:
                error = "عنوان آزمون را بنویس."
            elif not 1 <= duration <= 240:
                error = "زمان آزمون باید بین ۱ تا ۲۴۰ دقیقه باشد."
            else:
                test = PlacementTest.objects.create(title=title, grade=6, duration_minutes=duration, is_active=False)
                message = f"آزمون «{test.title}» ساخته شد. حالا سؤال اضافه کن."
        elif action == "add_question":
            test = get_object_or_404(PlacementTest, pk=request.POST.get("test_id"))
            question_text = request.POST.get("question_text", "").strip()
            options = [request.POST.get("option_" + letter.lower(), "").strip() for letter in "ABCD"]
            correct = request.POST.get("correct_option", "")
            if not question_text or any(not option for option in options):
                error = "متن سؤال و هر چهار گزینه را کامل کن."
            elif correct not in ("A", "B", "C", "D"):
                error = "گزینه درست را انتخاب کن."
            else:
                next_order = (test.questions.order_by("-order").values_list("order", flat=True).first() or 0) + 1
                PlacementQuestion.objects.create(test=test, text=question_text, option_a=options[0],
                    option_b=options[1], option_c=options[2], option_d=options[3],
                    correct_option=correct, order=next_order, is_active=True)
                message = "سؤال به آزمون اضافه شد."
        elif action == "toggle_test":
            test = get_object_or_404(PlacementTest, pk=request.POST.get("test_id"))
            if not test.is_active and not test.questions.filter(is_active=True).exists():
                error = "برای فعال‌کردن، ابتدا دست‌کم یک سؤال فعال اضافه کن."
            else:
                test.is_active = not test.is_active
                test.save(update_fields=["is_active"])
                message = "وضعیت آزمون تغییر کرد."
        elif action == "toggle_question":
            question = get_object_or_404(PlacementQuestion, pk=request.POST.get("question_id"))
            question.is_active = not question.is_active
            question.save(update_fields=["is_active"])
            message = "وضعیت سؤال تغییر کرد."
    tests = PlacementTest.objects.prefetch_related("questions").order_by("-id")
    return render(request, "simple/test_manager.html", {"tests": tests, "message": message, "error": error})


@login_required(login_url="login")
def student_test_list(request):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")
    tests = PlacementTest.objects.filter(is_active=True, questions__is_active=True).distinct().prefetch_related("questions").order_by("-id")
    return render(request, "simple/test_list.html", {"tests": tests})


@login_required(login_url="login")
def student_take_test(request, test_id):
    student = getattr(request.user, "student_profile", None)
    if student is None:
        return redirect("simple-teacher" if is_teacher(request.user) or is_admin(request.user) else "login")
    test = get_object_or_404(PlacementTest, pk=test_id, is_active=True)
    questions = list(test.questions.filter(is_active=True).order_by("order", "id"))
    if not questions:
        return redirect("student-test-list")
    error = None
    if request.method == "POST":
        answers = {str(q.id): request.POST.get("question_" + str(q.id), "") for q in questions}
        if any(value not in ("A", "B", "C", "D") for value in answers.values()):
            error = "لطفاً برای همه سؤال‌ها یک گزینه انتخاب کن."
        else:
            correct = sum(answers[str(q.id)] == q.correct_option for q in questions)
            attempt = PlacementAttempt.objects.create(student=student, test=test,
                score=round(correct * 100 / len(questions)), correct_answers=correct,
                total_questions=len(questions), level=max(1, min(10, round(correct * 10 / len(questions)))),
                completed_at=timezone.now())
            return render(request, "simple/result.html", {"attempt": attempt})
    return render(request, "simple/test_take.html", {"test": test, "questions": questions, "error": error})
