import Link from "next/link";
import { Logo } from "@/components/ui/logo";

type DashboardHeaderProps = {
  studentName: string;
};

export function DashboardHeader({
  studentName
}: DashboardHeaderProps) {
  return (
    <header className="border-b border-[var(--border)] bg-white">
      <div className="container-page flex min-h-18 items-center justify-between gap-4">
        <Logo />

        <div className="flex items-center gap-3">
          <span className="hidden text-sm text-[var(--muted)] sm:inline">
            سلام {studentName}
          </span>

          <span className="hidden rounded-full bg-green-50 px-3 py-1.5 text-xs font-bold text-green-700 sm:inline">
            پایه ششم
          </span>

          <Link
            href="/"
            className="rounded-xl border border-[var(--border)] px-3 py-2 text-xs font-bold transition hover:border-green-200 hover:text-green-700"
          >
            خروج
          </Link>
        </div>
      </div>
    </header>
  );
}