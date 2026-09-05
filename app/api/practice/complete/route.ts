import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

type CompletePracticeBody = {
  mobile: string;
  subjectSlug: string;
  subjectTitle: string;
  totalQuestions: number;
  correctAnswers: number;
  wrongAnswers: number;
};

export async function POST(request: Request) {
  try {
    const body =
      (await request.json()) as CompletePracticeBody;

    const {
      mobile,
      subjectSlug,
      subjectTitle,
      totalQuestions,
      correctAnswers,
      wrongAnswers,
    } = body;

    if (
      !mobile ||
      !subjectSlug ||
      !subjectTitle ||
      !Number.isInteger(totalQuestions) ||
      !Number.isInteger(correctAnswers) ||
      !Number.isInteger(wrongAnswers)
    ) {
      return NextResponse.json(
        {
          success: false,
          message: "اطلاعات تمرین ناقص است.",
        },
        { status: 400 }
      );
    }

    if (
      totalQuestions <= 0 ||
      correctAnswers < 0 ||
      wrongAnswers < 0 ||
      correctAnswers + wrongAnswers !== totalQuestions
    ) {
      return NextResponse.json(
        {
          success: false,
          message: "اطلاعات پاسخ‌ها معتبر نیست.",
        },
        { status: 400 }
      );
    }

    const progress = Math.round(
      (correctAnswers / totalQuestions) * 100
    );

    const points = correctAnswers * 10;

    const student = await prisma.student.findUnique({
      where: {
        mobile,
      },
    });

    if (!student) {
      return NextResponse.json(
        {
          success: false,
          message: "دانش‌آموز پیدا نشد.",
        },
        { status: 404 }
      );
    }

    const result = await prisma.$transaction(async (tx) => {
      const attempt =
        await tx.practiceAttempt.create({
          data: {
            studentId: student.id,
            subjectSlug,
            subjectTitle,
            totalQuestions,
            correctAnswers,
            wrongAnswers,
            progress,
            points,
          },
        });

      const updatedStudent =
        await tx.student.update({
          where: {
            id: student.id,
          },
          data: {
            points: {
              increment: points,
            },

            correctAnswers: {
              increment: correctAnswers,
            },

            wrongAnswers: {
              increment: wrongAnswers,
            },

            answeredQuestions: {
              increment: totalQuestions,
            },
          },
        });

      return {
        attempt,
        student: updatedStudent,
      };
    });

    return NextResponse.json({
      success: true,
      message: "نتیجه تمرین با موفقیت ذخیره شد.",
      data: {
        attemptId: result.attempt.id,
        points: result.attempt.points,
        progress: result.attempt.progress,
        student: {
          id: result.student.id,
          name: result.student.name,
          mobile: result.student.mobile,
          points: result.student.points,
          correctAnswers:
            result.student.correctAnswers,
          wrongAnswers:
            result.student.wrongAnswers,
          answeredQuestions:
            result.student.answeredQuestions,
        },
      },
    });
  } catch (error) {
    console.error(
      "PRACTICE_COMPLETE_ERROR:",
      error
    );

    return NextResponse.json(
      {
        success: false,
        message: "خطایی هنگام ذخیره نتیجه رخ داد.",
      },
      { status: 500 }
    );
  }
}