"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/ui/logo";

export default function LoginPage() {
  const router = useRouter();

  const [mobile, setMobile] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"mobile" | "otp">("mobile");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function sendOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setMessage("");

    const normalizedMobile = mobile
      .replace(/\s/g, "")
      .replace(/-/g, "");

    if (!/^09\d{9}$/.test(normalizedMobile)) {
      setError("شماره موبایل معتبر نیست.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("/api/auth/send-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mobile: normalizedMobile,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        setError(data.message || "ارسال کد انجام نشد.");
        return;
      }

      setMobile(normalizedMobile);
      setStep("otp");
      setMessage("کد تأیید برای شما ارسال شد.");
    } catch {
      setError("خطا در ارتباط با سرور.");
    } finally {
      setLoading(false);
    }
  }

  async function verifyOtp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setMessage("");

    const normalizedCode = code.replace(/\D/g, "");

    if (!/^\d{6}$/.test(normalizedCode)) {
      setError("کد تأیید باید ۶ رقم باشد.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mobile,
          code: normalizedCode,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        setError(data.message || "کد تأیید اشتباه است.");
        return;
      }

      setMessage("ورود با موفقیت انجام شد.");

      router.push("/student");
      router.refresh();
    } catch {
      setError("خطا در ارتباط با سرور.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="card w-full max-w-md p-7">
        <Logo />

        <h1 className="mt-8 text-2xl font-black">
          ورود به پیچک دانش
        </h1>

        <p className="mt-2 text-sm leading-7 text-[var(--muted)]">
          برای ورود به حساب دانش‌آموزی، شماره موبایل خود را وارد کنید.
        </p>

        {step === "mobile" ? (
          <form onSubmit={sendOtp}>
            <label
              htmlFor="mobile"
              className="mt-7 block text-sm font-bold"
            >
              شماره موبایل
            </label>

            <input
              id="mobile"
              name="mobile"
              type="tel"
              inputMode="numeric"
              dir="ltr"
              autoComplete="tel"
              value={mobile}
              onChange={(event) => setMobile(event.target.value)}
              placeholder="09120000000"
              disabled={loading}
              className="mt-2 w-full rounded-2xl border border-[var(--border)] bg-white px-4 py-3.5 text-left outline-none transition focus:border-green-500"
            />

            {error && (
              <p className="mt-3 rounded-xl bg-red-50 px-4 py-3 text-sm font-bold text-red-600">
                {error}
              </p>
            )}

            {message && (
              <p className="mt-3 rounded-xl bg-green-50 px-4 py-3 text-sm font-bold text-green-700">
                {message}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-4 w-full rounded-2xl bg-green-600 px-4 py-3.5 font-bold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "در حال ارسال..." : "دریافت کد تأیید"}
            </button>
          </form>
        ) : (
          <form onSubmit={verifyOtp}>
            <label
              htmlFor="code"
              className="mt-7 block text-sm font-bold"
            >
              کد تأیید
            </label>

            <input
              id="code"
              name="code"
              type="text"
              inputMode="numeric"
              dir="ltr"
              autoComplete="one-time-code"
              maxLength={6}
              value={code}
              onChange={(event) =>
                setCode(event.target.value.replace(/\D/g, ""))
              }
              placeholder="123456"
              disabled={loading}
              autoFocus
              className="mt-2 w-full rounded-2xl border border-[var(--border)] bg-white px-4 py-3.5 text-center text-xl font-black tracking-[0.4em] outline-none transition focus:border-green-500"
            />

            {message && (
              <p className="mt-3 rounded-xl bg-green-50 px-4 py-3 text-sm font-bold text-green-700">
                {message}
              </p>
            )}

            {error && (
              <p className="mt-3 rounded-xl bg-red-50 px-4 py-3 text-sm font-bold text-red-600">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || code.length !== 6}
              className="mt-4 w-full rounded-2xl bg-green-600 px-4 py-3.5 font-bold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "در حال بررسی..." : "تأیید و ورود"}
            </button>

            <button
              type="button"
              onClick={() => {
                setStep("mobile");
                setCode("");
                setError("");
                setMessage("");
              }}
              className="mt-3 w-full rounded-2xl border border-[var(--border)] px-4 py-3.5 text-sm font-bold"
            >
              تغییر شماره موبایل
            </button>
          </form>
        )}

        <Link
          href="/"
          className="mt-5 block text-center text-sm font-bold text-green-700"
        >
          بازگشت به صفحه اصلی
        </Link>
      </div>
    </main>
  );
}