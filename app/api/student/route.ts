import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  try {
    const student = await prisma.student.findUnique({
      where: {
        mobile: "09120000000",
      },
      include: {
        practiceAttempts: {
          orderBy: {
            createdAt: "desc",
          },
          take: 20,
        },
      },
    });

    if (!student) {
      return NextResponse.json(
        {
          success: false,
          message: "دانش‌آموز پیدا نشد",
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      student,
    });
  } catch (error) {
    console.error("GET /api/student error:", error);

    return NextResponse.json(
      {
        success: false,
        message: "خطا در دریافت اطلاعات دانش‌آموز",
      },
      { status: 500 }
    );
  }
}