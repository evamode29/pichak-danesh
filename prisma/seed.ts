import "dotenv/config";

import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";
import { PrismaClient } from "../lib/generated/prisma/client";

const databaseUrl =
  process.env.DATABASE_URL ?? "file:./dev.db";

const adapter = new PrismaBetterSqlite3({
  url: databaseUrl,
});

const prisma = new PrismaClient({
  adapter,
});

async function main() {
  const student = await prisma.student.upsert({
    where: {
      mobile: "09120000000",
    },

    update: {
      name: "دانش‌آموز نمونه",
      grade: 6,
    },

    create: {
      name: "دانش‌آموز نمونه",
      mobile: "09120000000",
      grade: 6,

      points: 840,
      correctAnswers: 34,
      wrongAnswers: 8,
      answeredQuestions: 42,

      level: 7,
      streak: 5,
    },
  });

  console.log("");
  console.log("=================================");
  console.log("دانش‌آموز با موفقیت ثبت شد");
  console.log("=================================");
  console.log("ID:", student.id);
  console.log("نام:", student.name);
  console.log("موبایل:", student.mobile);
  console.log("پایه:", student.grade);
  console.log("امتیاز:", student.points);
  console.log("=================================");
}

main()
  .catch((error) => {
    console.error("خطا:", error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });