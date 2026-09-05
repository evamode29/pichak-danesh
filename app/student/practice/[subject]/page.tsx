import Link from "next/link";
import { notFound } from "next/navigation";
import { PracticeView } from "@/components/student/practice-view";
import {
  getSubject,
  getSubjectQuestions,
} from "@/lib/mock-data";

type PracticePageProps = {
  params: Promise<{
    subject: string;
  }>;
};

export default async function PracticePage({
  params,
}: PracticePageProps) {
  const { subject: subjectSlug } = await params;

  const subject = getSubject(subjectSlug);

  if (!subject) {
    notFound();
  }

  const subjectQuestions = getSubjectQuestions(subjectSlug);

  return (
    <main className="min-h-screen">
      <header className="border-b border-[var(--border)] bg-white">
        <div className="container-page flex min-h-18 items-center justify-between gap-4">
          <div>
            <Link
              href="/student"
              className="text-sm font-bold text-[var(--muted)] transition hover:text-[var(--brand)]"
            >
              ← بازگشت به داشبورد
            </Link>

            <h1 className="mt-1 text-lg font-black">
              تمرین {subject.title}
            </h1>
          </div>

          <div
            className="grid size-11 place-items-center rounded-xl bg-green-50 text-xl"
            aria-hidden="true"
          >
            {subject.icon}
          </div>
        </div>
      </header>

      <div className="container-page py-7 sm:py-10">
        <div className="mx-auto max-w-2xl">
          <div className="mb-6">
            <p className="text-sm font-bold text-[var(--brand)]">
              تمرین آموزشی
            </p>

            <h2 className="mt-2 text-2xl font-black sm:text-3xl">
              {subject.title}
            </h2>

            <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
              به سؤال‌ها پاسخ بده و برای هر پاسخ صحیح ۱۰ امتیاز بگیر.
            </p>
          </div>

          {subjectQuestions.length > 0 ? (
            <PracticeView
              subject={subject}
              questions={subjectQuestions}
              studentMobile="09120000000"
            />
          ) : (
            <div className="card p-8 text-center">
              <div className="text-4xl">📚</div>

              <h2 className="mt-4 text-xl font-black">
                هنوز سؤالی برای این درس وجود ندارد.
              </h2>

              <Link
                href="/student"
                className="mt-6 inline-flex rounded-xl bg-[var(--brand)] px-5 py-3 font-bold text-white"
              >
                بازگشت به داشبورد
              </Link>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}