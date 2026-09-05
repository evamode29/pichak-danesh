"use client";

import { useMemo, useState } from "react";
import type {
  Question,
  Subject,
} from "@/lib/mock-data";

type PracticeViewProps = {
  subject: Subject;
  questions: Question[];
  studentMobile: string;
};

export function PracticeView({
  subject,
  questions,
  studentMobile,
}: PracticeViewProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const [selectedAnswer, setSelectedAnswer] =
    useState<number | null>(null);

  const [isFinished, setIsFinished] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [sessionCorrect, setSessionCorrect] =
    useState(0);

  const [sessionWrong, setSessionWrong] =
    useState(0);

  const currentQuestion = questions[currentIndex];

  const isAnswered = selectedAnswer !== null;

  const isCorrect =
    isAnswered &&
    selectedAnswer === currentQuestion?.correctAnswer;

  const progress = useMemo(() => {
    if (questions.length === 0) {
      return 0;
    }

    const answeredCount =
      currentIndex + (isAnswered ? 1 : 0);

    return Math.round(
      (answeredCount / questions.length) * 100
    );
  }, [
    currentIndex,
    isAnswered,
    questions.length,
  ]);

  async function savePracticeResult(
    correct: number,
    wrong: number
  ) {
    const totalQuestions = correct + wrong;

    if (totalQuestions === 0) {
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      const response = await fetch(
        "/api/practice/complete",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mobile: studentMobile,
            subjectSlug: subject.slug,
            subjectTitle: subject.title,
            totalQuestions,
            correctAnswers: correct,
            wrongAnswers: wrong,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.message ||
            "ذخیره نتیجه تمرین ناموفق بود."
        );
      }

      console.log(
        "Practice result saved:",
        data.data
      );

      setIsFinished(true);
    } catch (error) {
      console.error(
        "SAVE_PRACTICE_RESULT_ERROR:",
        error
      );

      setSaveError(
        error instanceof Error
          ? error.message
          : "ذخیره نتیجه تمرین ناموفق بود."
      );
    } finally {
      setIsSaving(false);
    }
  }

  function handleAnswer(answerIndex: number) {
    if (isAnswered || !currentQuestion || isSaving) {
      return;
    }

    setSelectedAnswer(answerIndex);

    const correct =
      answerIndex === currentQuestion.correctAnswer;

    if (correct) {
      setSessionCorrect(
        (value) => value + 1
      );
    } else {
      setSessionWrong(
        (value) => value + 1
      );
    }
  }

  async function handleNext() {
    if (!isAnswered || isSaving) {
      return;
    }

    const nextCorrect =
      sessionCorrect +
      (isCorrect ? 1 : 0);

    const nextWrong =
      sessionWrong +
      (isCorrect ? 0 : 1);

    /*
     * اگر سؤال آخر است:
     * ابتدا آمار نهایی جلسه را در state قرار می‌دهیم
     * سپس همان آمار را برای ذخیره به API می‌فرستیم.
     */
    if (
      currentIndex ===
      questions.length - 1
    ) {
      setSessionCorrect(nextCorrect);
      setSessionWrong(nextWrong);

      await savePracticeResult(
        nextCorrect,
        nextWrong
      );

      return;
    }

    setSessionCorrect(nextCorrect);
    setSessionWrong(nextWrong);

    setCurrentIndex(
      (value) => value + 1
    );

    setSelectedAnswer(null);
  }

  function restart() {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setIsFinished(false);
    setIsSaving(false);
    setSaveError(null);
    setSessionCorrect(0);
    setSessionWrong(0);
  }

  if (!currentQuestion) {
    return (
      <section className="card p-8 text-center">
        <div className="text-4xl">
          📚
        </div>

        <h2 className="mt-4 text-xl font-black">
          سؤالی برای این تمرین وجود ندارد.
        </h2>
      </section>
    );
  }

  if (isFinished) {
    const totalQuestions =
      sessionCorrect + sessionWrong;

    const sessionPoints =
      sessionCorrect * 10;

    const sessionProgress =
      totalQuestions === 0
        ? 0
        : Math.round(
            (sessionCorrect /
              totalQuestions) *
              100
          );

    return (
      <section className="card overflow-hidden">
        <div className="bg-[var(--brand-soft)] p-7 text-center sm:p-10">
          <div className="text-5xl">
            🎉
          </div>

          <h2 className="mt-4 text-2xl font-black">
            تمرین تمام شد!
          </h2>

          <p className="mt-2 text-sm text-[var(--muted)]">
            عملکردت در تمرین {subject.title}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 p-5 sm:grid-cols-4 sm:p-7">
          <ResultCard
            label="درست"
            value={sessionCorrect}
            icon="✅"
          />

          <ResultCard
            label="غلط"
            value={sessionWrong}
            icon="❌"
          />

          <ResultCard
            label="درصد"
            value={sessionProgress}
            suffix="٪"
            icon="📈"
          />

          <ResultCard
            label="امتیاز"
            value={sessionPoints}
            icon="🏆"
          />
        </div>

        <div className="px-5 pb-5 sm:px-7 sm:pb-7">
          <div className="rounded-2xl bg-green-50 p-5 text-center">
            <div className="text-sm text-green-700">
              نتیجه تمرین
            </div>

            <div className="mt-2 text-3xl font-black text-green-800">
              {sessionProgress.toLocaleString(
                "fa-IR"
              )}
              ٪
            </div>

            <p className="mt-2 text-sm text-green-700">
              {sessionCorrect.toLocaleString(
                "fa-IR"
              )}{" "}
              پاسخ صحیح از{" "}
              {totalQuestions.toLocaleString(
                "fa-IR"
              )}{" "}
              سؤال
            </p>

            <p className="mt-2 text-sm font-bold text-green-800">
              +
              {sessionPoints.toLocaleString(
                "fa-IR"
              )}{" "}
              امتیاز
            </p>

            <p className="mt-3 text-xs font-bold text-green-700">
              ✓ نتیجه در حساب دانش‌آموز ذخیره شد
            </p>
          </div>

          {saveError && (
            <div className="mt-4 rounded-2xl bg-red-50 p-4 text-sm font-bold text-red-700">
              {saveError}
            </div>
          )}

          <button
            type="button"
            onClick={restart}
            className="mt-5 w-full rounded-xl bg-[var(--brand)] px-5 py-3.5 font-bold text-white transition hover:bg-[var(--brand-dark)]"
          >
            شروع دوباره تمرین
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="card overflow-hidden">
      <div className="border-b border-[var(--border)] p-5 sm:p-7">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-bold text-[var(--brand)]">
              سؤال{" "}
              {(currentIndex + 1).toLocaleString(
                "fa-IR"
              )}{" "}
              از{" "}
              {questions.length.toLocaleString(
                "fa-IR"
              )}
            </p>

            <p className="mt-1 text-xs text-[var(--muted)]">
              {progress.toLocaleString(
                "fa-IR"
              )}
              ٪ تکمیل شده
            </p>
          </div>

          <div
            className="text-sm font-black"
            aria-label={`پیشرفت ${progress} درصد`}
          >
            {progress.toLocaleString(
              "fa-IR"
            )}
            ٪
          </div>
        </div>

        <div className="mt-4 h-3 overflow-hidden rounded-full bg-green-50">
          <div
            className="h-full rounded-full bg-[var(--brand)] transition-all duration-300"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>
      </div>

      <div className="p-5 sm:p-7">
        <span className="inline-flex rounded-full bg-green-50 px-3 py-1.5 text-xs font-bold text-green-700">
          {currentQuestion.topic}
        </span>

        <h2 className="mt-5 text-xl font-black leading-9 sm:text-2xl">
          {currentQuestion.text}
        </h2>

        <div
          className="mt-6 grid gap-3"
          role="radiogroup"
          aria-label="گزینه‌های پاسخ"
        >
          {currentQuestion.options.map(
            (option, index) => {
              const correct =
                index ===
                currentQuestion.correctAnswer;

              const selected =
                index === selectedAnswer;

              let className =
                "border-[var(--border)] bg-white hover:border-green-300 hover:bg-green-50";

              if (isAnswered && correct) {
                className =
                  "border-green-500 bg-green-50 text-green-800";
              } else if (
                isAnswered &&
                selected &&
                !correct
              ) {
                className =
                  "border-red-400 bg-red-50 text-red-800";
              }

              return (
                <button
                  key={`${currentQuestion.id}-${index}`}
                  type="button"
                  role="radio"
                  aria-checked={selected}
                  disabled={
                    isAnswered || isSaving
                  }
                  onClick={() =>
                    handleAnswer(index)
                  }
                  className={`flex min-h-14 items-center gap-3 rounded-2xl border p-4 text-right font-bold transition ${className}`}
                >
                  <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-gray-100 text-sm">
                    {String.fromCharCode(
                      1575 + index
                    )}
                  </span>

                  <span className="flex-1">
                    {option}
                  </span>

                  {isAnswered &&
                    correct && (
                      <span
                        aria-label="پاسخ صحیح"
                        className="text-green-700"
                      >
                        ✓
                      </span>
                    )}

                  {isAnswered &&
                    selected &&
                    !correct && (
                      <span
                        aria-label="پاسخ غلط"
                        className="text-red-700"
                      >
                        ✕
                      </span>
                    )}
                </button>
              );
            }
          )}
        </div>

        {isAnswered && (
          <div
            className={`mt-5 rounded-2xl p-4 ${
              isCorrect
                ? "bg-green-50 text-green-800"
                : "bg-red-50 text-red-800"
            }`}
            role="status"
          >
            <div className="font-black">
              {isCorrect
                ? "آفرین! پاسخ درست بود 🎉"
                : "این پاسخ درست نبود."}
            </div>

            {!isCorrect && (
              <p className="mt-2 text-sm leading-7">
                پاسخ درست:
                <strong className="mr-1">
                  {
                    currentQuestion.options[
                      currentQuestion.correctAnswer
                    ]
                  }
                </strong>
              </p>
            )}

            {isCorrect && (
              <p className="mt-2 text-sm">
                +۱۰ امتیاز به امتیازت اضافه می‌شود.
              </p>
            )}
          </div>
        )}

        {saveError && (
          <div className="mt-4 rounded-2xl bg-red-50 p-4 text-sm font-bold text-red-700">
            {saveError}
          </div>
        )}

        {isAnswered && (
          <button
            type="button"
            onClick={handleNext}
            disabled={isSaving}
            className="mt-5 w-full rounded-xl bg-[var(--brand)] px-5 py-3.5 font-bold text-white transition hover:bg-[var(--brand-dark)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSaving
              ? "در حال ذخیره نتیجه..."
              : currentIndex ===
                  questions.length - 1
                ? "مشاهده نتیجه"
                : "سؤال بعدی"}
          </button>
        )}
      </div>
    </section>
  );
}

function ResultCard({
  label,
  value,
  icon,
  suffix = "",
}: {
  label: string;
  value: number;
  icon: string;
  suffix?: string;
}) {
  return (
    <div className="rounded-2xl border border-[var(--border)] p-4 text-center">
      <div
        className="text-xl"
        aria-hidden="true"
      >
        {icon}
      </div>

      <div className="mt-2 text-xl font-black">
        {value.toLocaleString("fa-IR")}
        {suffix}
      </div>

      <div className="mt-1 text-xs text-[var(--muted)]">
        {label}
      </div>
    </div>
  );
}