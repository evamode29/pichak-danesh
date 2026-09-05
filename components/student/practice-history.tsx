type PracticeHistoryItem = {
  id: string;
  subjectSlug: string;
  subjectTitle: string;
  totalQuestions: number;
  correctAnswers: number;
  wrongAnswers: number;
  progress: number;
  points: number;
  createdAt: string;
};

type PracticeHistoryProps = {
  initialHistory: PracticeHistoryItem[];
};

export function PracticeHistory({
  initialHistory,
}: PracticeHistoryProps) {
  if (initialHistory.length === 0) {
    return (
      <div className="card p-6 text-center">
        <div className="text-4xl">📚</div>

        <h3 className="mt-3 font-black">
          هنوز تمرینی ثبت نشده است
        </h3>

        <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
          اولین تمرینت را انجام بده تا نتیجه آن اینجا نمایش داده شود.
        </p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <div className="divide-y divide-[var(--border)]">
        {initialHistory.map((item) => (
          <PracticeHistoryRow
            key={item.id}
            item={item}
          />
        ))}
      </div>
    </div>
  );
}

function PracticeHistoryRow({
  item,
}: {
  item: PracticeHistoryItem;
}) {
  const date = new Date(item.createdAt);

  const dateText = date.toLocaleDateString("fa-IR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const timeText = date.toLocaleTimeString("fa-IR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <article className="p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        {/* آیکون */}
        <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-green-50 text-xl">
          📖
        </div>

        {/* اطلاعات تمرین */}
        <div className="min-w-0 flex-1">
          <div className="font-black">
            {item.subjectTitle}
          </div>

          <div className="mt-1 text-xs text-[var(--muted)]">
            {dateText} — ساعت {timeText}
          </div>

          <div className="mt-1 text-xs text-[var(--muted)]">
            {item.totalQuestions.toLocaleString("fa-IR")} سؤال
          </div>
        </div>

        {/* آمار */}
        <div className="grid grid-cols-3 gap-2 sm:min-w-64">
          <HistoryStat
            label="صحیح"
            value={item.correctAnswers}
            className="text-green-700"
          />

          <HistoryStat
            label="غلط"
            value={item.wrongAnswers}
            className="text-red-600"
          />

          <HistoryStat
            label="درصد"
            value={`${item.progress.toLocaleString("fa-IR")}٪`}
            className="text-[var(--brand)]"
          />
        </div>

        {/* امتیاز */}
        <div className="rounded-xl bg-green-50 px-4 py-3 text-center">
          <div className="text-xs text-green-700">
            امتیاز
          </div>

          <div className="mt-1 font-black text-green-800">
            +
            {item.points.toLocaleString("fa-IR")}
          </div>
        </div>
      </div>
    </article>
  );
}

function HistoryStat({
  label,
  value,
  className = "",
}: {
  label: string;
  value: number | string;
  className?: string;
}) {
  return (
    <div className="rounded-xl bg-gray-50 px-3 py-2 text-center">
      <div
        className={`text-sm font-black ${className}`}
      >
        {typeof value === "number"
          ? value.toLocaleString("fa-IR")
          : value}
      </div>

      <div className="mt-1 text-[10px] text-[var(--muted)]">
        {label}
      </div>
    </div>
  );
}