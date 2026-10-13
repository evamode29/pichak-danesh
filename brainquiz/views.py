import time
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from students.models import StudentProfile
from .models import BrainQuizAttempt

QUESTIONS = [
("کدام شکل بعدی است؟", "🔴  🔵  🔴  🔵  ؟", ["🔴", "🟡", "🔺", "🟦"], 0),
("الگو را کامل کن", "▲  ▲  ●  ▲  ▲  ●  ؟", ["▲", "●", "■", "◆"], 0),
("شکل متفاوت را پیدا کن", "●  ●  ●  ■", ["●", "■", "◆", "▲"], 1),
("کدام گزینه ادامه الگوست؟", "🟢  🟢  🟡  🟢  🟢  🟡  ؟", ["🟢", "🟡", "🔵", "🔴"], 0),
("جای خالی را پر کن", "▲  ■  ▲  ■  ▲  ؟", ["▲", "■", "●", "◆"], 1),
("کدام شکل با بقیه فرق دارد؟", "◆  ◆  ◆  ○", ["◆", "○", "□", "△"], 1),
("دنباله را ادامه بده", "🔺  🔻  🔺  🔻  ؟", ["🔺", "🔻", "🟦", "🟢"], 0),
("کدام شکل بعدی می‌آید؟", "●  ●  ■  ●  ●  ■  ؟", ["●", "■", "▲", "◆"], 0),
("شکل متفاوت کدام است؟", "▲  ▲  ▲  ◆", ["▲", "◆", "●", "■"], 1),
("الگو را کامل کن", "★  ☆  ★  ☆  ؟", ["★", "☆", "●", "▲"], 0),
("کدام گزینه ادامه الگوست؟", "🟥  🟨  🟦  🟥  🟨  ؟", ["🟥", "🟨", "🟦", "🟩"], 2),
("شکل متفاوت را پیدا کن", "○  ○  ○  △", ["○", "△", "□", "◇"], 1),
("جای خالی چیست؟", "■  □  ■  □  ؟", ["■", "□", "●", "▲"], 0),
("دنباله را ادامه بده", "▲  ●  ●  ▲  ●  ●  ؟", ["▲", "●", "■", "◆"], 0),
("کدام یکی متفاوت است؟", "🟣  🟣  🟣  🟠", ["🟣", "🟠", "🔵", "🟢"], 1),
("الگو را ادامه بده", "◆  ◇  ◆  ◇  ؟", ["◆", "◇", "○", "□"], 0),
("کدام شکل بعدی است؟", "🔵  🔵  🔴  🔵  🔵  🔴  ؟", ["🔵", "🔴", "🟡", "🟢"], 0),
("شکل متفاوت را مشخص کن", "□  □  □  ○", ["□", "○", "◇", "△"], 1),
("دنباله را کامل کن", "▲  ■  ●  ▲  ■  ؟", ["▲", "■", "●", "◆"], 2),
("آخرین الگو کدام است؟", "🌙  ⭐  🌙  ⭐  ؟", ["🌙", "⭐", "☀️", "☁️"], 0),
]

@login_required(login_url="login")
def start(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("teacher-dashboard" if request.user.is_staff else "dashboard")
    return render(request, "brainquiz/start.html", {"student": student, "latest": student.brain_quiz_attempts.first(), "question_count": len(QUESTIONS), "duration_minutes": 15})

@login_required(login_url="login")
def play(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("login")
    if request.method == "POST":
        answers, correct = {}, 0
        for index, item in enumerate(QUESTIONS):
            selected = request.POST.get(f"q{index}", "")
            if selected.isdigit() and 0 <= int(selected) < 4:
                answers[str(index)] = int(selected)
                correct += int(int(selected) == item[3])
        started = request.session.pop("brainquiz_started", int(time.time()))
        duration = max(0, min(900, int(time.time()) - int(started)))
        attempt = BrainQuizAttempt.objects.create(student=student, score=round(correct * 100 / len(QUESTIONS)), correct_answers=correct, total_questions=len(QUESTIONS), duration_seconds=duration, answers=answers)
        return redirect("brainquiz:result", attempt_id=attempt.id)
    request.session["brainquiz_started"] = int(time.time())
    questions = [{"index": i, "text": item[0], "visual": item[1], "options": list(enumerate(item[2]))} for i, item in enumerate(QUESTIONS)]
    return render(request, "brainquiz/play.html", {"questions": questions, "duration_seconds": 900})

@login_required(login_url="login")
def result(request, attempt_id):
    student = getattr(request.user, "student_profile", None)
    if not student:
        return redirect("login")
    attempt = get_object_or_404(BrainQuizAttempt, pk=attempt_id, student=student)
    return render(request, "brainquiz/result.html", {"attempt": attempt})
