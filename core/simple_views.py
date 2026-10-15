from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from core.models import ClassRoom, UserProfile
from core.permissions import is_teacher, is_admin
from exams.models import PlacementAttempt, PlacementTest
from students.models import StudentProfile


IQ_TEST_TITLE = "آزمون هوش تصویری پیچک دانش"
IQ_QUESTIONS = [
    {"id":"q1","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="دایره، مربع، دایره، مربع، جای خالی"><circle cx="45" cy="45" r="20" fill="#15966d"/><rect x="100" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><circle cx="195" cy="45" r="20" fill="#15966d"/><rect x="250" y="25" width="40" height="40" rx="5" fill="#f2b84b"/><text x="360" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دایره سبز"),("B","مربع زرد"),("C","مثلث آبی"),("D","ستاره قرمز")],"answer":"A"},
    {"id":"q2","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک نقطه، دو نقطه، سه نقطه، جای خالی"><g fill="#536fe5"><circle cx="45" cy="45" r="7"/><circle cx="130" cy="35" r="7"/><circle cx="130" cy="55" r="7"/><circle cx="215" cy="30" r="7"/><circle cx="215" cy="45" r="7"/><circle cx="215" cy="60" r="7"/></g><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","یک نقطه"),("B","دو نقطه"),("C","چهار نقطه"),("D","شش نقطه")],"answer":"C"},
    {"id":"q3","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مثلث رو به بالا، مثلث رو به پایین، مثلث رو به بالا، جای خالی"><polygon points="45,18 20,65 70,65" fill="#f2b84b"/><polygon points="130,68 105,21 155,21" fill="#15966d"/><polygon points="215,18 190,65 240,65" fill="#f2b84b"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مثلث زرد رو به بالا"),("B","مثلث سبز رو به پایین"),("C","دایره سبز"),("D","مربع زرد")],"answer":"B"},
    {"id":"q4","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="مربع کوچک، مربع بزرگ، مربع کوچک، جای خالی"><rect x="27" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><rect x="105" y="12" width="66" height="66" rx="5" fill="#9b70d6"/><rect x="202" y="27" width="36" height="36" rx="4" fill="#9b70d6"/><text x="320" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","مربع کوچک"),("B","مربع بزرگ"),("C","دایره بزرگ"),("D","مثلث کوچک")],"answer":"B"},
    {"id":"q5","visual":'<svg viewBox="0 0 420 90" role="img" aria-label="یک ستاره، دو ستاره، سه ستاره، جای خالی"><g fill="#f2b84b" font-size="30" text-anchor="middle"><text x="45" y="56">★</text><text x="125" y="56">★</text><text x="153" y="56">★</text><text x="215" y="56">★</text><text x="243" y="56">★</text><text x="271" y="56">★</text></g><text x="350" y="56" font-size="34" fill="#53615b" text-anchor="middle">؟</text></svg>',"options":[("A","دو ستاره"),("B","سه ستاره"),("C","چهار ستاره"),("D","پنج ستاره")],"answer":"D"},
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
    attempts = PlacementAttempt.objects.filter(test__title=IQ_TEST_TITLE).select_related("student__user").order_by("-completed_at")[:30]
    return render(request, "simple/teacher.html", {
        "students": students,
        "student_count": StudentProfile.objects.count(),
        "attempts": attempts,
        "classrooms": ClassRoom.objects.filter(is_active=True).order_by("name")[:30],
    })
