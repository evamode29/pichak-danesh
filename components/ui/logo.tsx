import Link from "next/link";

export function Logo() {
  return (
    <Link
      href="/"
      className="inline-flex items-center gap-2.5"
      aria-label="پیچک دانش"
    >
      <span className="grid size-10 place-items-center rounded-2xl bg-green-600 text-xl text-white shadow-sm">
        🌱
      </span>

      <span className="text-lg font-black tracking-tight">
        پیچک دانش
      </span>
    </Link>
  );
}