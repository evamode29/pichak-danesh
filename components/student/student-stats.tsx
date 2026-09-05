"use client";

import { useEffect, useState } from "react";

export type StudentStatsData = {
  points: number;
  correctAnswers: number;
  wrongAnswers: number;
  answeredQuestions: number;
};

export type StudentStatsProps = {
  initialStats: StudentStatsData;
};

export function StudentStats({
  initialStats,
}: StudentStatsProps) {
  const [stats, setStats] = useState<StudentStatsData>(initialStats);

  useEffect(() => {
    const saved = localStorage.getItem("pichak-student-stats");

    if (!saved) return;

    try {
      const parsed = JSON.parse(saved) as Partial<StudentStatsData>;

      setStats({
        points: parsed.points ?? initialStats.points,
        correctAnswers:
          parsed.correctAnswers ?? initialStats.correctAnswers,
        wrongAnswers:
          parsed.wrongAnswers ?? initialStats.wrongAnswers,
        answeredQuestions:
          parsed.answeredQuestions ?? initialStats.answeredQuestions,
      });
    } catch {
      localStorage.removeItem("pichak-student-stats");
    }
  }, [initialStats]);

  const totalAnswers =
    stats.correctAnswers + stats.wrongAnswers;

  const progress =
    totalAnswers === 0
      ? 0
      : Math.round(
          (stats.correctAnswers / totalAnswers) * 100
        );

  return (
    <section
      aria-label="وضعیت آموزشی دانش‌آموز"
      className="grid grid-cols-2 gap-3 sm:grid-cols-4"
    >
      <Stat
        label="امتیاز"
        value={stats.points.toLocaleString("fa-IR")}
        icon="🏆"
      />

      <Stat
        label="پاسخ صحیح"
        value={stats.correctAnswers.toLocaleString("fa-IR")}
        icon="✅"
      />

      <Stat
        label="پاسخ غلط"
        value={stats.wrongAnswers.toLocaleString("fa-IR")}
        icon="❌"
      />

      <Stat
        label="درصد موفقیت"
        value={`${progress.toLocaleString("fa-IR")}٪`}
        icon="📈"
      />
    </section>
  );
}

function Stat({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: string;
}) {
  return (
    <article className="card p-4">
      <div className="flex items-center justify-between gap-2">
        <span
          className="text-lg"
          aria-hidden="true"
        >
          {icon}
        </span>

        <span className="text-xs text-[var(--muted)]">
          {label}
        </span>
      </div>

      <div className="mt-3 text-xl font-black">
        {value}
      </div>
    </article>
  );
}