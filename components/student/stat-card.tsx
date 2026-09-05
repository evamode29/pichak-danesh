type StatCardProps = {
  label: string;
  value: string;
  icon: string;
};

export function StatCard({ label, value, icon }: StatCardProps) {
  return (
    <article className="card p-4">
      <div className="flex items-center justify-between gap-2">
        <span className="text-lg" aria-hidden="true">{icon}</span>
        <span className="text-xs text-[var(--muted)]">{label}</span>
      </div>
      <div className="mt-3 text-xl font-black">{value}</div>
    </article>
  );
}
