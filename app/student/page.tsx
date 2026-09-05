import { DashboardHeader } from "@/components/student/dashboard-header";
import { MissionCard } from "@/components/student/mission-card";
import { PracticeHistory } from "@/components/student/practice-history";
import { RankingTable } from "@/components/student/ranking-table";
import { StudentStats } from "@/components/student/student-stats";
import { SubjectCard } from "@/components/student/subject-card";

import {
  mission,
  subjects,
  leaderboard,
} from "@/lib/mock-data";

import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export default async function StudentDashboardPage() {
  const student = await prisma.student.findUnique({
    where: {
      mobile: "09120000000",
    },
    include: {
      practiceAttempts: {
        orderBy: {
          createdAt: "desc",
        },
        take: 20,
      },
    },
  });

  if (!student) {
    return (
      <main className="min-h-screen">
        <div className="container-page py-10">
          <div className="card p-6 text-center">
            <h1 className="text-xl font-black">
              دانش‌آموز پیدا نشد
            </h1>

            <p className="mt-2 text-sm text-[var(--muted)]">
              اطلاعات دانش‌آموز در پایگاه داده وجود ندارد.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const progress =
    student.answeredQuestions > 0
      ? Math.round(
          (student.correctAnswers / student.answeredQuestions) * 100
        )
      : 0;

  /*
   * تاریخچه تمرین‌ها را از Prisma به فرم مورد نیاز
   * کامپوننت PracticeHistory تبدیل می‌کنیم.
   */
  const practiceHistory = student.practiceAttempts.map((attempt) => ({
    id: String(attempt.id),
    subjectSlug: attempt.subjectSlug,
    subjectTitle: attempt.subjectTitle,
    totalQuestions: attempt.totalQuestions,
    correctAnswers: attempt.correctAnswers,
    wrongAnswers: attempt.wrongAnswers,
    progress: attempt.progress,
    points: attempt.points,
    createdAt: attempt.createdAt.toISOString(),
  }));

  return (
    <main className="min-h-screen">
      <DashboardHeader studentName={student.name} />

      <div className="container-page py-7 sm:py-10">

        {/* خوش‌آمدگویی */}
        <section aria-labelledby="welcome-title">
          <p className="text-sm font-bold text-[var(--brand)]">
            داشبورد دانش‌آموز
          </p>

          <h1
            id="welcome-title"
            className="mt-2 text-2xl font-black sm:text-3xl"
          >
            سلام {student.name} 👋
          </h1>

          <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
            پایه {student.grade} — آماده‌ای امروز هم یک قدم جلوتر بروی؟
          </p>
        </section>

        {/* آمار دانش‌آموز */}
        <section className="mt-6">
          <StudentStats
            initialStats={{
              points: student.points,
              correctAnswers: student.correctAnswers,
              wrongAnswers: student.wrongAnswers,
              answeredQuestions: student.answeredQuestions,
            }}
          />
        </section>

        {/* پیشرفت کلی */}
        <section
          className="mt-6 card p-5 sm:p-7"
          aria-labelledby="progress-title"
        >
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2
                id="progress-title"
                className="font-black"
              >
                پیشرفت کلی
              </h2>

              <p className="mt-1 text-xs text-[var(--muted)]">
                مسیر یادگیری پایه {student.grade}
              </p>
            </div>

            <span className="font-black text-green-700">
              {progress.toLocaleString("fa-IR")}٪
            </span>
          </div>

          <div className="mt-5 h-3 overflow-hidden rounded-full bg-green-50">
            <div
              className="h-full rounded-full bg-green-500 transition-all"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>
        </section>

        {/* مأموریت امروز */}
        <section
          className="mt-8"
          aria-labelledby="mission-title"
        >
          <div className="mb-3 flex items-center justify-between">
            <h2
              id="mission-title"
              className="text-xl font-black"
            >
              مأموریت امروز
            </h2>

            <span className="text-xs font-bold text-[var(--muted)]">
              پیشنهاد شده
            </span>
          </div>

          <MissionCard mission={mission} />
        </section>

        {/* درس‌ها */}
        <section
          className="mt-8"
          aria-labelledby="subjects-title"
        >
          <div className="mb-3">
            <p className="text-sm font-bold text-[var(--brand)]">
              درس‌ها
            </p>

            <h2
              id="subjects-title"
              className="mt-1 text-xl font-black"
            >
              ادامه یادگیری
            </h2>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {subjects.map((subject) => (
              <SubjectCard
                key={subject.slug}
                subject={subject}
              />
            ))}
          </div>
        </section>

        {/* آخرین تمرین‌ها */}
        <section
          className="mt-8"
          aria-labelledby="history-title"
        >
          <div className="mb-3 flex items-end justify-between">
            <div>
              <p className="text-sm font-bold text-[var(--brand)]">
                فعالیت‌های اخیر
              </p>

              <h2
                id="history-title"
                className="mt-1 text-xl font-black"
              >
                آخرین تمرین‌ها
              </h2>
            </div>

            <span className="text-xs text-[var(--muted)]">
              {student.practiceAttempts.length.toLocaleString("fa-IR")} تمرین
            </span>
          </div>

          <PracticeHistory
            initialHistory={practiceHistory}
          />
        </section>

        {/* جدول برترین‌ها */}
        <section
          className="mt-8"
          aria-labelledby="leaderboard-title"
        >
          <div className="mb-3 flex items-end justify-between">
            <div>
              <p className="text-sm font-bold text-[var(--brand)]">
                رقابت دوستانه
              </p>

              <h2
                id="leaderboard-title"
                className="mt-1 text-xl font-black"
              >
                جدول برترین‌ها
              </h2>
            </div>

            <span className="text-xs text-[var(--muted)]">
              زنده
            </span>
          </div>

          <RankingTable
            rows={leaderboard}
            studentName={student.name}
            studentLevel={student.level}
            initialPoints={student.points}
          />
        </section>

      </div>
    </main>
  );
}