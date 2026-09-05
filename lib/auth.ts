import { cookies } from "next/headers";
import { createHmac, randomInt, timingSafeEqual } from "crypto";

const OTP_COOKIE = "pichak_otp";
const SESSION_COOKIE = "pichak_student";

const OTP_EXPIRE_SECONDS = 120;
const SESSION_EXPIRE_SECONDS = 60 * 60 * 24 * 30;

function getSecret() {
  return (
    process.env.AUTH_SECRET ||
    "pichak-danesh-development-secret-change-me"
  );
}

/* تبدیل اعداد فارسی و عربی به انگلیسی */
function toEnglishDigits(value: string) {
  return value
    .replace(/[۰-۹]/g, (digit) =>
      String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit))
    )
    .replace(/[٠-٩]/g, (digit) =>
      String("٠١٢٣٤٥٦٧٨٩".indexOf(digit))
    );
}

function sign(value: string) {
  return createHmac("sha256", getSecret())
    .update(value)
    .digest("hex");
}

function safeCompare(a: string, b: string) {
  const aBuffer = Buffer.from(a);
  const bBuffer = Buffer.from(b);

  if (aBuffer.length !== bBuffer.length) {
    return false;
  }

  return timingSafeEqual(aBuffer, bBuffer);
}

function normalizeMobile(mobile: string) {
  let value = toEnglishDigits(mobile);

  value = value
    .trim()
    .replace(/\s+/g, "")
    .replace(/-/g, "");

  if (value.startsWith("+98")) {
    value = "0" + value.slice(3);
  }

  if (value.startsWith("0098")) {
    value = "0" + value.slice(4);
  }

  if (!/^09\d{9}$/.test(value)) {
    return null;
  }

  return value;
}

export function normalizeStudentMobile(mobile: string) {
  return normalizeMobile(mobile);
}

export function generateOtp() {
  return randomInt(100000, 1000000).toString();
}

export async function saveOtp(
  mobile: string,
  code: string
) {
  const cookieStore = await cookies();

  const normalizedMobile = normalizeMobile(mobile);
  const normalizedCode = toEnglishDigits(code);

  if (!normalizedMobile) {
    throw new Error("Invalid mobile number.");
  }

  if (!/^\d{6}$/.test(normalizedCode)) {
    throw new Error("Invalid OTP code.");
  }

  const expiresAt =
    Date.now() + OTP_EXPIRE_SECONDS * 1000;

  const payload =
    `${normalizedMobile}|${normalizedCode}|${expiresAt}`;

  const signature = sign(payload);

  const token =
    `${payload}|${signature}`;

  cookieStore.set(OTP_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: OTP_EXPIRE_SECONDS,
  });

  console.log(
    `[Pichak Danesh OTP] ${normalizedMobile}: ${normalizedCode}`
  );
}

export async function verifyOtp(
  mobile: string,
  code: string
) {
  const cookieStore = await cookies();

  const token =
    cookieStore.get(OTP_COOKIE)?.value;

  if (!token) {
    console.log("[Pichak Danesh OTP] Cookie not found.");
    return false;
  }

  const parts = token.split("|");

  if (parts.length !== 4) {
    console.log("[Pichak Danesh OTP] Invalid cookie format.");
    return false;
  }

  const [
    savedMobile,
    savedCode,
    expiresAtString,
    signature,
  ] = parts;

  const normalizedMobile =
    normalizeMobile(mobile);

  const normalizedCode =
    toEnglishDigits(code)
      .trim()
      .replace(/\s/g, "");

  if (!normalizedMobile) {
    return false;
  }

  if (!/^\d{6}$/.test(normalizedCode)) {
    return false;
  }

  const expiresAt =
    Number(expiresAtString);

  if (!Number.isFinite(expiresAt)) {
    return false;
  }

  if (Date.now() > expiresAt) {
    console.log("[Pichak Danesh OTP] OTP expired.");
    cookieStore.delete(OTP_COOKIE);
    return false;
  }

  if (savedMobile !== normalizedMobile) {
    console.log(
      "[Pichak Danesh OTP] Mobile mismatch."
    );
    return false;
  }

  if (!safeCompare(savedCode, normalizedCode)) {
    console.log(
      `[Pichak Danesh OTP] Code mismatch. Saved: ${savedCode}, Received: ${normalizedCode}`
    );
    return false;
  }

  const payload =
    `${savedMobile}|${savedCode}|${expiresAtString}`;

  if (!safeCompare(sign(payload), signature)) {
    console.log(
      "[Pichak Danesh OTP] Signature mismatch."
    );
    return false;
  }

  cookieStore.delete(OTP_COOKIE);

  console.log(
    `[Pichak Danesh OTP] Verified successfully for ${normalizedMobile}`
  );

  return true;
}

export async function createStudentSession(
  mobile: string
) {
  const cookieStore = await cookies();

  const normalizedMobile =
    normalizeMobile(mobile);

  if (!normalizedMobile) {
    throw new Error("Invalid mobile number.");
  }

  const createdAt = Date.now();

  const payload =
    `${normalizedMobile}|${createdAt}`;

  const signature = sign(payload);

  const token =
    `${payload}|${signature}`;

  cookieStore.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_EXPIRE_SECONDS,
  });
}

export async function getStudentMobile() {
  const cookieStore = await cookies();

  const token =
    cookieStore.get(SESSION_COOKIE)?.value;

  if (!token) {
    return null;
  }

  const parts = token.split("|");

  if (parts.length !== 3) {
    return null;
  }

  const [
    mobile,
    createdAtString,
    signature,
  ] = parts;

  const normalizedMobile =
    normalizeMobile(mobile);

  if (!normalizedMobile) {
    return null;
  }

  const payload =
    `${normalizedMobile}|${createdAtString}`;

  if (!safeCompare(sign(payload), signature)) {
    return null;
  }

  const createdAt =
    Number(createdAtString);

  if (!Number.isFinite(createdAt)) {
    return null;
  }

  if (
    Date.now() - createdAt >
    SESSION_EXPIRE_SECONDS * 1000
  ) {
    cookieStore.delete(SESSION_COOKIE);
    return null;
  }

  return normalizedMobile;
}

export async function logoutStudent() {
  const cookieStore = await cookies();

  cookieStore.delete(SESSION_COOKIE);
}