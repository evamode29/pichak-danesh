import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "پیچک دانش | یاد بگیر، رشد کن، بالاتر برو",
  description:
    "پلتفرم آموزشی دانش‌آموزان پیچک دانش",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}