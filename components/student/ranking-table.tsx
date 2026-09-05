"use client";

import { useEffect, useMemo, useState } from "react";
import type { LeaderboardRow } from "@/lib/mock-data";

type RankingTableProps = {
  rows: LeaderboardRow[];
  studentName: string;
  studentLevel: number;
  initialPoints: number;
};

type StoredStats = {
  points: number;
  correctAnswers: number;
  wrongAnswers: number;
  answeredQuestions: number;
};

const STORAGE_KEY = "pichak-student-stats";

export function RankingTable({
  rows,
  studentName,
  studentLevel,
  initialPoints,
}: RankingTableProps) {
  const [studentPoints, setStudentPoints] =
    useState(initialPoints);

  useEffect(() => {
    function loadPoints() {
      const saved = localStorage.getItem(STORAGE_KEY);

      if (!saved) {
        setStudentPoints(initialPoints);
        return;
      }

      try {
        const stats =
          JSON.parse(saved) as Partial<StoredStats>;

        if (typeof stats.points === "number") {
          setStudentPoints(stats.points);
        } else {
          setStudentPoints(initialPoints);
        }
      } catch {
        setStudentPoints(initialPoints);
      }
    }

    loadPoints();

    window.addEventListener(
      "pichak-stats-updated",
      loadPoints
    );

    window.addEventListener(
      "storage",
      loadPoints
    );

    return () => {
      window.removeEventListener(
        "pichak-stats-updated",
        loadPoints
      );

      window.removeEventListener(
        "storage",
        loadPoints
      );
    };
  }, [initialPoints]);

  const rankingRows = useMemo(() => {
    const otherRows = rows.filter(
      (row) => row.name !== studentName
    );

    const allRows: LeaderboardRow[] = [
      ...otherRows,

      {
        rank: 0,
        name: studentName,
        level: studentLevel,
        points: studentPoints,
      },
    ];

    return allRows
      .sort((a, b) => {
        // اول امتیاز بیشتر
        if (b.points !== a.points) {
          return b.points - a.points;
        }

        // در صورت مساوی بودن امتیاز،
        // سطح بالاتر اول باشد
        if (b.level !== a.level) {
          return b.level - a.level;
        }

        // در صورت برابری کامل
        return a.name.localeCompare(b.name);
      })
      .map((row, index) => ({
        ...row,
        rank: index + 1,
      }));
  }, [
    rows,
    studentName,
    studentLevel,
    studentPoints,
  ]);

  const visibleRows = rankingRows.slice(0, 10);

  const studentRank =
    rankingRows.find(
      (row) => row.name === studentName
    )?.rank ?? 0;

  return (
    <div className="card overflow-hidden">

      {/* =========================
          رتبه فعلی دانش‌آموز
      ========================= */}
      <div className="border-b border-[var(--border)] bg-[var(--brand-soft)] px-5 py-4">
        <div className="flex items-center justify-between gap-4">

          <div>
            <p className="text-sm font-bold text-[var(--brand)]">
              رتبه شما
            </p>

            <p className="mt-1 text-xs text-[var(--muted)]">
              با گرفتن امتیاز بیشتر، رتبه‌ات بالاتر می‌رود.
            </p>
          </div>

          <div className="text-left">
            <div className="text-2xl font-black text-[var(--brand)]">
              {studentRank.toLocaleString("fa-IR")}
            </div>

            <div className="text-xs font-bold text-[var(--muted)]">
              رتبه
            </div>
          </div>

        </div>
      </div>


      {/* =========================
          لیست رتبه‌ها
      ========================= */}
      <div className="divide-y divide-[var(--border)]">

        {visibleRows.map((row) => {
          const isCurrentStudent =
            row.name === studentName;

          return (
            <div
              key={`${row.name}-${row.rank}`}
              className={`flex items-center gap-4 p-4 transition ${
                isCurrentStudent
                  ? "bg-green-50"
                  : "bg-white"
              }`}
            >

              {/* رتبه */}
              <div
                className={`grid size-9 shrink-0 place-items-center rounded-full text-sm font-black ${
                  row.rank === 1
                    ? "bg-yellow-100 text-yellow-700"
                    : row.rank === 2
                      ? "bg-gray-100 text-gray-700"
                      : row.rank === 3
                        ? "bg-orange-100 text-orange-700"
                        : "bg-green-50 text-green-700"
                }`}
              >
                {row.rank.toLocaleString("fa-IR")}
              </div>


              {/* آواتار */}
              <div className="grid size-10 shrink-0 place-items-center rounded-full bg-green-100 font-bold text-green-700">
                {row.name.slice(0, 1)}
              </div>


              {/* نام و سطح */}
              <div className="min-w-0 flex-1">

                <div className="flex items-center gap-2">

                  <div className="truncate font-bold">
                    {row.name}
                  </div>

                  {isCurrentStudent && (
                    <span className="shrink-0 rounded-full bg-green-200 px-2 py-0.5 text-[10px] font-black text-green-800">
                      شما
                    </span>
                  )}

                </div>

                <div className="mt-1 text-xs text-[var(--muted)]">
                  سطح{" "}
                  {row.level.toLocaleString("fa-IR")}
                </div>

              </div>


              {/* امتیاز */}
              <span className="shrink-0 text-sm font-black">
                {row.points.toLocaleString("fa-IR")} امتیاز
              </span>

            </div>
          );
        })}

      </div>

    </div>
  );
}