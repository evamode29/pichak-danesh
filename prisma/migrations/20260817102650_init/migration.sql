-- CreateTable
CREATE TABLE "Student" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "mobile" TEXT NOT NULL,
    "grade" INTEGER NOT NULL DEFAULT 6,
    "points" INTEGER NOT NULL DEFAULT 840,
    "correctAnswers" INTEGER NOT NULL DEFAULT 34,
    "wrongAnswers" INTEGER NOT NULL DEFAULT 8,
    "answeredQuestions" INTEGER NOT NULL DEFAULT 42,
    "level" INTEGER NOT NULL DEFAULT 7,
    "streak" INTEGER NOT NULL DEFAULT 5,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "PracticeAttempt" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "studentId" INTEGER NOT NULL,
    "subjectSlug" TEXT NOT NULL,
    "subjectTitle" TEXT NOT NULL,
    "totalQuestions" INTEGER NOT NULL,
    "correctAnswers" INTEGER NOT NULL,
    "wrongAnswers" INTEGER NOT NULL,
    "progress" INTEGER NOT NULL,
    "points" INTEGER NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "PracticeAttempt_studentId_fkey" FOREIGN KEY ("studentId") REFERENCES "Student" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "Student_mobile_key" ON "Student"("mobile");

-- CreateIndex
CREATE INDEX "Student_points_idx" ON "Student"("points");

-- CreateIndex
CREATE INDEX "PracticeAttempt_studentId_idx" ON "PracticeAttempt"("studentId");

-- CreateIndex
CREATE INDEX "PracticeAttempt_createdAt_idx" ON "PracticeAttempt"("createdAt");
