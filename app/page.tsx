import Link from "next/link";
import { FeatureCard } from "@/components/ui/feature-card";
import { Logo } from "@/components/ui/logo";

const features = [
  {
    icon: "📚",
    title: "یادگیری",
    description: "درس‌ها و مسیرهای آموزشی ساده و هدفمند برای پیشرفت واقعی."
  },
  {
    icon: "🏆",
    title: "رقابت",
    description: "با امتیاز و رتبه، انگیزه بیشتری برای ادامه مسیر داشته باش."
  },
  {
    icon: "🌱",
    title: "رشد",
    description: "پیشرفتت را ببین و هر روز یک قدم از دیروز جلوتر برو."
  }
];

export default function HomePage() {
  return (
    <main>
      <header className="border-b border-[var(--border)] bg-white/90 backdrop-blur">
        <div className="container-page flex h-18 items-center justify-between gap-4">
          <Logo />
          <nav aria-label="منوی اصلی" className="hidden items-center gap-7 text-sm text-[var(--muted)] md:flex">
            <Link className="transition hover:text-[var(--brand)]" href="#features">ویژگی‌ها</Link>
            <Link className="transition hover:text-[var(--brand)]" href="#about">درباره پیچک دانش</Link>
          </nav>
          <Link
            href="/login"
            className="rounded-xl border border-[var(--border)] bg-white px-4 py-2.5 text-sm font-bold text-[var(--ink)] shadow-sm transition hover:border-green-200 hover:text-[var(--brand)]"
          >
            ورود
          </Link>
        </div>
      </header>

      <section className="brand-gradient overflow-hidden">
        <div className="container-page grid min-h-[620px] items-center gap-12 py-16 lg:grid-cols-[1.15fr_.85fr] lg:py-24">
          <div>
            <span className="inline-flex rounded-full border border-green-200 bg-white px-4 py-2 text-sm font-bold text-green-700 shadow-sm">
              پلتفرم رشد دانش‌آموزان
            </span>

            <h1 className="mt-7 max-w-3xl text-4xl font-black leading-[1.35] tracking-tight sm:text-5xl lg:text-6xl">
              یاد بگیر، رشد کن،
              <span className="block text-[var(--brand)]">بالاتر برو.</span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-8 text-[var(--muted)] sm:text-lg">
              پیچک دانش یک مسیر ساده و دانش‌آموزمحور برای یادگیری، تمرین و رقابت است؛
              جایی که پیشرفت تو فقط یک عدد نیست، بلکه یک مسیر قابل مشاهده است.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/student"
                className="inline-flex items-center justify-center rounded-2xl bg-[var(--brand)] px-6 py-3.5 font-bold text-white shadow-lg shadow-green-900/10 transition hover:bg-[var(--brand-dark)]"
              >
                شروع یادگیری
              </Link>
              <Link
                href="#features"
                className="inline-flex items-center justify-center rounded-2xl border border-[var(--border)] bg-white px-6 py-3.5 font-bold text-[var(--ink)] transition hover:border-green-200"
              >
                بیشتر بدانید
              </Link>
            </div>
          </div>

          <div aria-hidden="true" className="relative mx-auto w-full max-w-md">
            <div className="absolute -inset-8 rounded-full bg-green-100/60 blur-3xl" />
            <div className="relative rounded-[32px] border border-green-100 bg-white p-5 shadow-2xl shadow-green-950/10">
              <div className="rounded-3xl bg-[var(--brand-soft)] p-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-green-800">داشبورد دانش‌آموز</span>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-green-700">فعال</span>
                </div>
                <div className="mt-7">
                  <div className="text-3xl font-black text-green-900">Level 7</div>
                  <div className="mt-2 text-sm text-green-700">840 امتیاز</div>
                </div>
                <div className="mt-7 h-3 overflow-hidden rounded-full bg-white">
                  <div className="h-full w-[72%] rounded-full bg-green-500" />
                </div>
                <div className="mt-3 flex justify-between text-xs text-green-700">
                  <span>پیشرفت مسیر</span>
                  <span>72٪</span>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-[var(--border)] p-4">
                  <div className="text-xl">🏆</div>
                  <div className="mt-2 text-xs text-[var(--muted)]">رتبه</div>
                  <div className="mt-1 font-black">12</div>
                </div>
                <div className="rounded-2xl border border-[var(--border)] p-4">
                  <div className="text-xl">🔥</div>
                  <div className="mt-2 text-xs text-[var(--muted)]">فعالیت پیوسته</div>
                  <div className="mt-1 font-black">5 روز</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="container-page py-20">
        <div className="max-w-2xl">
          <p className="font-bold text-[var(--brand)]">سه پایه اصلی</p>
          <h2 className="mt-2 text-3xl font-black">یادگیری که به رشد تبدیل می‌شود.</h2>
        </div>
        <div className="mt-9 grid gap-5 md:grid-cols-3">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </section>

      <section id="about" className="container-page pb-20">
        <div className="card grid gap-8 p-7 md:grid-cols-[1fr_auto] md:items-center md:p-10">
          <div>
            <p className="font-bold text-[var(--brand)]">درباره پیچک دانش</p>
            <h2 className="mt-2 text-2xl font-black">یک مسیر روشن برای بهتر شدن.</h2>
            <p className="mt-4 max-w-3xl leading-8 text-[var(--muted)]">
              پیچک دانش در نسخه اولیه خود روی ساخت یک تجربه آموزشی مدرن تمرکز دارد؛
              تجربه‌ای که یادگیری، تمرین، آزمون، امتیاز و پیشرفت را در یک مسیر منسجم کنار هم قرار می‌دهد.
            </p>
          </div>
          <Link href="/student" className="rounded-2xl bg-green-50 px-5 py-3 text-center font-bold text-green-700 hover:bg-green-100">
            مشاهده داشبورد
          </Link>
        </div>
      </section>

      <footer className="border-t border-[var(--border)] bg-white">
        <div className="container-page flex flex-col gap-3 py-8 text-sm text-[var(--muted)] sm:flex-row sm:items-center sm:justify-between">
          <Logo />
          <p>© 2026 پیچک دانش — نسخه 0.2</p>
        </div>
      </footer>
    </main>
  );
}
