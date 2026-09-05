import { NextResponse } from "next/server";
import {
  createStudentSession,
  normalizeStudentMobile,
  verifyOtp,
} from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const mobile = normalizeStudentMobile(
      String(body.mobile ?? "")
    );

    const code = String(body.code ?? "").trim();

    if (!mobile) {
      return NextResponse.json(
        {
          success: false,
          message: "شماره موبایل معتبر نیست.",
        },
        { status: 400 }
      );
    }

    if (!/^\d{6}$/.test(code)) {
      return NextResponse.json(
        {
          success: false,
          message: "کد ورود باید ۶ رقمی باشد.",
        },
        { status: 400 }
      );
    }

    const isValid = await verifyOtp(
      mobile,
      code
    );

    if (!isValid) {
      return NextResponse.json(
        {
          success: false,
          message:
            "کد ورود اشتباه است یا منقضی شده.",
        },
        { status: 401 }
      );
    }

    const student = await prisma.student.findUnique({
      where: {
        mobile,
      },
    });

    if (!student) {
      return NextResponse.json(
        {
          success: false,
          message:
            "دانش‌آموزی با این شماره پیدا نشد.",
        },
        { status: 404 }
      );
    }

    await createStudentSession(mobile);

    return NextResponse.json({
      success: true,
      message: "ورود با موفقیت انجام شد.",
      student: {
        id: student.id,
        name: student.name,
        mobile: student.mobile,
        grade: student.grade,
      },
    });
  } catch (error) {
    console.error(
      "POST /api/auth/verify-otp error:",
      error
    );

    return NextResponse.json(
      {
        success: false,
        message:
          "خطا در تأیید کد ورود.",
      },
      { status: 500 }
    );
  }
}