import Link from "next/link";
import type { Subject } from "@/lib/mock-data";

export function SubjectCard({
  subject
}: {
  subject: Subject;
}) {
  return (
    <Link
      href={`/student/practice/${subject.slug}`}
      className="group block rounded-2xl border border-[var(--border)] bg-white p-4 transition hover:-translate-y-0.5 hover:border-green-300 hover:shadow-lg hover:shadow-green-950/5"
    >
      <div className="flex items-center gap-3">
        <span
          className="grid size-11 place-items-center rounded-xl bg-green-50 text-xl"
          aria-hidden="true"
        >
          {subject.icon}
        </span>

        <div className="min-w-0 flex-1">
          <h3 className="font-black">
            {subject.title}
          </h3>

          <p className="mt-1 text-xs text-[var(--muted)]">
            {subject.subtitle}
          </p>
        </div>

        <span className="text-xs font-black text-green-700">
          {subject.progress}٪
        </span>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-100">
        <div
          className="h-full rounded-full bg-green-500"
          style={{
            width: `${subject.progress}%`
          }}
        />
      </div>

      <div className="mt-3 text-xs font-bold text-green-700 opacity-0 transition group-hover:opacity-100">
        شروع تمرین ←
      </div>
    </Link>
  );
}