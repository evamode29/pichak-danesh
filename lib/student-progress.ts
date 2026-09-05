export type StudentProgressStats = {
  points: number;
  correctAnswers: number;
  wrongAnswers: number;
  answeredQuestions: number;
};

export const STORAGE_KEY = "pichak-student-stats";

export const DEFAULT_STATS: StudentProgressStats = {
  points: 840,
  correctAnswers: 34,
  wrongAnswers: 8,
  answeredQuestions: 42,
};

export function getLevelFromPoints(points: number): number {
  return Math.max(1, Math.floor(points / 200) + 3);
}

export function getLevelProgress(points: number) {
  const level = getLevelFromPoints(points);

  const currentLevelStart =
    Math.max(0, (level - 3) * 200);

  const nextLevelStart =
    (level - 2) * 200;

  const levelRange =
    nextLevelStart - currentLevelStart;

  const earnedInLevel =
    points - currentLevelStart;

  const progress =
    levelRange <= 0
      ? 100
      : Math.min(
          100,
          Math.max(
            0,
            Math.round(
              (earnedInLevel / levelRange) * 100
            )
          )
        );

  return {
    level,
    currentLevelStart,
    nextLevelStart,
    earnedInLevel,
    levelRange,
    progress,
    remaining: Math.max(
      0,
      nextLevelStart - points
    ),
  };
}