import { NextResponse } from "next/server";
import {
  generateOtp,
  normalizeStudentMobile,
  saveOtp,
} from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const mobile = normalizeStudentMobile(
      String(body.mobile ?? "")
    );

    if (!mobile) {
      return NextResponse.json(
        {
          success: false,
          message: "شماره موبایل معتبر نیست.",
        },
        { status: 400 }
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
            "این شماره موبایل هنوز در سامانه ثبت نشده است.",
        },
        { status: 404 }
      );
    }

    const otp = generateOtp();

    await saveOtp(mobile, otp);

    console.log(
      `[Pichak Danesh OTP] ${mobile}: ${otp}`
    );

    return NextResponse.json({
      success: true,
      message:
        "کد ورود با موفقیت ایجاد شد.",
      devOtp:
        process.env.NODE_ENV === "development"
          ? otp
          : undefined,
    });
  } catch (error) {
    console.error(
      "POST /api/auth/send-otp error:",
      error
    );

    return NextResponse.json(
      {
        success: false,
        message:
          "خطا در ارسال کد ورود.",
      },
      { status: 500 }
    );
  }
}