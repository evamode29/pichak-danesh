import json
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ImageField as DjangoImageField
from django.shortcuts import redirect, render
from django.utils import timezone
from openpyxl import load_workbook

from core.permissions import is_admin, is_teacher
from exams.models import (
    BankQuestion, PlacementQuestion, PlacementTest, QuestionCategory,
    TestBankQuestion,
)


SUBJECT_ALIASES = {
    "math": "math", "ریاضی": "math",
    "science": "science", "علوم": "science",
    "persian": "persian", "فارسی": "persian",
    "social": "social", "مطالعات اجتماعی": "social",
}
HEADER_ALIASES = {
    "درس": "subject", "subject": "subject",
    "پایه": "grade", "grade": "grade",
    "فصل": "chapter", "chapter": "chapter",
    "مبحث": "topic", "مبحث های چندگانه": "topic", "مبحث‌های چندگانه": "topic",
    "topic": "topic", "topics": "topic",
    "زیرمبحث": "subtopic", "زیرمبحث ها": "subtopic", "زیرمبحث‌ها": "subtopic",
    "subtopic": "subtopic", "subtopics": "subtopic",
    "متن سوال": "text", "متن سؤال": "text", "question": "text", "text": "text",
    "گزینه ۱": "option_a", "گزینه اول": "option_a", "option a": "option_a", "option_a": "option_a",
    "گزینه ۲": "option_b", "گزینه دوم": "option_b", "option b": "option_b", "option_b": "option_b",
    "گزینه ۳": "option_c", "گزینه سوم": "option_c", "option c": "option_c", "option_c": "option_c",
    "گزینه ۴": "option_d", "گزینه چهارم": "option_d", "option d": "option_d", "option_d": "option_d",
    "پاسخ صحیح": "correct", "پاسخ درست": "correct", "correct": "correct", "correct_option": "correct",
    "درجه سختی": "difficulty", "سختی": "difficulty", "difficulty": "difficulty",
    "توضیح پاسخ": "explanation", "توضیح": "explanation", "explanation": "explanation",
}


def _can_use_bank(user):
    return bool(user.is_authenticated and (is_teacher(user) or is_admin(user) or user.is_superuser))


def _cell_text(value):
    return "" if value is None else str(value).strip()



def _duplicate_question(row):
    return BankQuestion.objects.filter(
        subject=row["subject"], grade=row["grade"], text=row["text"],
        option_a=row["option_a"], option_b=row["option_b"],
        option_c=row["option_c"], option_d=row["option_d"],
        correct_option=row["correct"],
    ).exists()

def _category(subject, grade, name, parent=None):
    if not name:
        return None
    obj, _ = QuestionCategory.objects.get_or_create(
        subject=subject, grade=grade, parent=parent, name=name,
        defaults={"is_active": True},
    )
    return obj


def _attach_categories(question, row):
    chapter = _category(row["subject"], row["grade"], row.get("chapter", ""))
    topic_names = [x.strip() for x in row.get("topic", "").replace("،", ",").split(",") if x.strip()]
    subtopic_names = [x.strip() for x in row.get("subtopic", "").replace("،", ",").split(",") if x.strip()]
    parents = []
    if topic_names:
        for name in topic_names:
            parents.append(_category(row["subject"], row["grade"], name, chapter))
    elif chapter:
        parents = [chapter]
    if subtopic_names:
        for name in subtopic_names:
            for parent in parents or [chapter]:
                _category(row["subject"], row["grade"], name, parent)
    categories = []
    if chapter:
        categories.append(chapter)
    categories.extend([x for x in parents if x])
    for parent in parents:
        if parent:
            categories.extend(parent.children.filter(is_active=True))
    if categories:
        question.categories.add(*categories)


def _validate_row(raw, row_number):
    errors = []
    subject_raw = raw.get("subject", "").strip().lower()
    subject = SUBJECT_ALIASES.get(subject_raw)
    if not subject:
        errors.append("درس باید یکی از ریاضی، علوم، فارسی یا مطالعات اجتماعی باشد.")
    try:
        grade = int(raw.get("grade") or 6)
        if not 1 <= grade <= 12:
            raise ValueError
    except (TypeError, ValueError):
        grade = 6
        errors.append("پایه باید عددی بین ۱ تا ۱۲ باشد.")
    text = raw.get("text", "").strip()
    options = [raw.get(f"option_{letter}", "").strip() for letter in "abcd"]
    if not text:
        errors.append("متن سؤال خالی است.")
    if any(not value for value in options):
        errors.append("هر چهار گزینه باید تکمیل شوند.")
    correct = raw.get("correct", "").strip().upper()
    if correct in ("1", "۱"):
        correct = "A"
    elif correct in ("2", "۲"):
        correct = "B"
    elif correct in ("3", "۳"):
        correct = "C"
    elif correct in ("4", "۴"):
        correct = "D"
    if correct not in ("A", "B", "C", "D"):
        errors.append("پاسخ صحیح باید A تا D یا ۱ تا ۴ باشد.")
    try:
        difficulty = int(raw.get("difficulty") or 2)
        if not 1 <= difficulty <= 5:
            raise ValueError
    except (TypeError, ValueError):
        difficulty = 2
        errors.append("درجه سختی باید عددی بین ۱ تا ۵ باشد.")
    return {
        "row": row_number, "subject": subject or "math", "grade": grade,
        "chapter": raw.get("chapter", "").strip(),
        "topic": raw.get("topic", "").strip(),
        "subtopic": raw.get("subtopic", "").strip(),
        "text": text, "option_a": options[0], "option_b": options[1],
        "option_c": options[2], "option_d": options[3],
        "correct": correct, "difficulty": difficulty,
        "explanation": raw.get("explanation", "").strip(),
        "errors": errors,
    }


@login_required(login_url="login")
def teacher_question_bank(request):
    if not _can_use_bank(request.user):
        return redirect("simple-student")

    error = None
    message = None
    preview = request.session.get("question_bank_preview", [])
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_question":
            row = _validate_row({
                "subject": request.POST.get("subject", "math"),
                "grade": request.POST.get("grade", "6"),
                "chapter": request.POST.get("chapter", ""),
                "topic": request.POST.get("topic", ""),
                "subtopic": request.POST.get("subtopic", ""),
                "text": request.POST.get("text", ""),
                "option_a": request.POST.get("option_a", ""),
                "option_b": request.POST.get("option_b", ""),
                "option_c": request.POST.get("option_c", ""),
                "option_d": request.POST.get("option_d", ""),
                "correct": request.POST.get("correct", ""),
                "difficulty": request.POST.get("difficulty", "2"),
                "explanation": request.POST.get("explanation", ""),
            }, 1)
            uploads = {
                "question_image": request.FILES.get("question_image"),
                "option_a_image": request.FILES.get("option_a_image"),
                "option_b_image": request.FILES.get("option_b_image"),
                "option_c_image": request.FILES.get("option_c_image"),
                "option_d_image": request.FILES.get("option_d_image"),
            }
            if row["errors"]:
                error = " ".join(row["errors"])
            else:
                try:
                    for upload in uploads.values():
                        if upload:
                            if upload.size > 5 * 1024 * 1024:
                                raise ValidationError("حجم هر تصویر نباید بیشتر از ۵ مگابایت باشد.")
                            DjangoImageField().clean(upload)
                            upload.seek(0)
                except ValidationError as exc:
                    error = " ".join(exc.messages)
                if not error and _duplicate_question(row):
                    error = "این سؤال با همین متن، گزینه‌ها و پاسخ صحیح از قبل در بانک وجود دارد."
                if not error:
                    question = BankQuestion.objects.create(
                        subject=row["subject"], grade=row["grade"], text=row["text"],
                        option_a=row["option_a"], option_a_image=uploads["option_a_image"],
                        option_b=row["option_b"], option_b_image=uploads["option_b_image"],
                        option_c=row["option_c"], option_c_image=uploads["option_c_image"],
                        option_d=row["option_d"], option_d_image=uploads["option_d_image"],
                        question_image=uploads["question_image"],
                        correct_option=row["correct"], difficulty=row["difficulty"],
                        explanation=row["explanation"], created_by=request.user,
                    )
                    _attach_categories(question, row)
                    message = "سؤال با موفقیت به بانک افزوده شد."

        elif action == "preview_excel":
            upload = request.FILES.get("workbook")
            if not upload or not upload.name.lower().endswith((".xlsx", ".xlsm")):
                error = "فایل اکسل معتبر با پسوند xlsx انتخاب کن."
            elif upload.size > 5 * 1024 * 1024:
                error = "حجم فایل اکسل نباید بیشتر از ۵ مگابایت باشد."
            else:
                try:
                    workbook = load_workbook(BytesIO(upload.read()), read_only=True, data_only=True)
                    sheet = workbook["سوال‌ها"] if "سوال‌ها" in workbook.sheetnames else workbook.active
                    iterator = sheet.iter_rows(values_only=True)
                    headers = next(iterator, ())
                    mapped = {}
                    for index, value in enumerate(headers):
                        key = _cell_text(value).lower().replace("\u200c", " ")
                        if key in HEADER_ALIASES:
                            mapped[HEADER_ALIASES[key]] = index
                    required = {"subject", "text", "option_a", "option_b", "option_c", "option_d", "correct"}
                    if not required.issubset(mapped):
                        error = "ستون‌های ضروری فایل پیدا نشد. از قالب اکسل بانک سؤال پیچک دانش استفاده کن."
                    else:
                        rows = []
                        for row_number, values in enumerate(iterator, start=2):
                            if not any(value is not None and _cell_text(value) for value in values):
                                continue
                            raw = {key: _cell_text(values[index]) if index < len(values) else "" for key, index in mapped.items()}
                            rows.append(_validate_row(raw, row_number))
                            if len(rows) > 500:
                                error = "در هر نوبت حداکثر ۵۰۰ سؤال وارد کن."
                                break
                        if not error and not rows:
                            error = "در برگه انتخاب‌شده هیچ سؤالی پیدا نشد."
                        if not error:
                            request.session["question_bank_preview"] = rows
                            request.session.modified = True
                            preview = rows
                            message = f"پیش‌نمایش {len(rows)} سؤال آماده شد؛ هنوز چیزی در بانک ثبت نشده است."
                    workbook.close()
                except Exception:
                    error = "خواندن فایل ممکن نشد. فایل را با فرمت xlsx ذخیره و دوباره انتخاب کن."

        elif action == "confirm_import":
            rows = request.session.get("question_bank_preview", [])
            invalid = [row for row in rows if row.get("errors")]
            if not rows:
                error = "ابتدا فایل اکسل را بارگذاری و پیش‌نمایش کن."
            elif invalid:
                error = "ابتدا خطاهای ردیف‌های مشخص‌شده را در اکسل اصلاح کن."
            else:
                imported_count = 0
                skipped_count = 0
                with transaction.atomic():
                    for row in rows:
                        if _duplicate_question(row):
                            skipped_count += 1
                            continue
                        question = BankQuestion.objects.create(
                            subject=row["subject"], grade=row["grade"], text=row["text"],
                            option_a=row["option_a"], option_b=row["option_b"],
                            option_c=row["option_c"], option_d=row["option_d"],
                            correct_option=row["correct"], difficulty=row["difficulty"],
                            explanation=row["explanation"], created_by=request.user,
                        )
                        _attach_categories(question, row)
                        imported_count += 1
                del request.session["question_bank_preview"]
                preview = []
                message = f"{imported_count} سؤال وارد شد؛ {skipped_count} سؤال تکراری نادیده گرفته شد."

        elif action == "clear_preview":
            request.session.pop("question_bank_preview", None)
            preview = []
            message = "پیش‌نمایش پاک شد."

    questions = BankQuestion.objects.prefetch_related("categories").order_by("-created_at")[:100]
    return render(request, "simple/question_bank.html", {
        "questions": questions, "preview": preview,
        "preview_error_count": sum(bool(row.get("errors")) for row in preview),
        "message": message, "error": error,
    })
