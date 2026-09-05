import Link from "next/link";
import type { Mission } from "@/lib/mock-data";

export function MissionCard({
  mission
}: {
  mission: Mission;
}) {
  return (
    <article className="card overflow-hidden">
      <div className="bg-green-50 p-5 sm:p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-xs font-bold text-green-700">
              مأموریت پیشنهادی
            </span>

            <h3 className="mt-2 text-xl font-black">
              {mission.subject} — {mission.topic}
            </h3>
          </div>

          <span className="rounded-xl bg-white px-3 py-2 text-sm font-black text-green-700">
            +{mission.points}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between gap-4 p-5">
        <span className="text-sm text-[var(--muted)]">
          {mission.questions} سؤال
        </span>

        <Link
          href="/student/practice/math"
          className="rounded-xl bg-green-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-green-700"
        >
          شروع
        </Link>
      </div>
    </article>
  );
}