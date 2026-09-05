export type Student = {
  name: string;
  grade: number;
  level: number;
  progress: number;
  points: number;
  rank: number;
  streak: number;
  correctAnswers: number;
  wrongAnswers: number;
};

export type Mission = {
  subject: string;
  topic: string;
  questions: number;
  points: number;
};

export type Subject = {
  slug: string;
  title: string;
  subtitle: string;
  progress: number;
  icon: string;
};

export type LeaderboardRow = {
  rank: number;
  name: string;
  level: number;
  points: number;
};

export type Question = {
  id: number;
  subject: string;
  topic: string;
  text: string;
  options: string[];
  correctAnswer: number;
};

export const student: Student = {
  name: "علی",
  grade: 6,
  level: 7,
  progress: 72,
  points: 840,
  rank: 12,
  streak: 5,
  correctAnswers: 34,
  wrongAnswers: 8,
};

export const mission: Mission = {
  subject: "ریاضی",
  topic: "کسرها",
  questions: 10,
  points: 50,
};

export const subjects: Subject[] = [
  {
    slug: "math",
    title: "ریاضی",
    subtitle: "تمرین‌های منتخب",
    progress: 68,
    icon: "➗",
  },
  {
    slug: "science",
    title: "علوم",
    subtitle: "یادگیری و تمرین",
    progress: 52,
    icon: "🔬",
  },
  {
    slug: "persian",
    title: "فارسی",
    subtitle: "مرور و تمرین",
    progress: 81,
    icon: "📖",
  },
  {
    slug: "social",
    title: "مطالعات اجتماعی",
    subtitle: "جامعه و ایران",
    progress: 46,
    icon: "🌍",
  },
];

export const leaderboard: LeaderboardRow[] = [
  {
    rank: 10,
    name: "محمد",
    level: 8,
    points: 910,
  },
  {
    rank: 11,
    name: "سارا",
    level: 8,
    points: 875,
  },
  {
    rank: 12,
    name: "علی",
    level: 7,
    points: 840,
  },
  {
    rank: 13,
    name: "نگار",
    level: 7,
    points: 820,
  },
  {
    rank: 14,
    name: "پارسا",
    level: 7,
    points: 795,
  },
];

export const questions: Question[] = [
  {
    id: 1,
    subject: "math",
    topic: "کسرها",
    text: "کدام کسر با ۱/۲ برابر است؟",
    options: ["۲/۳", "۳/۶", "۴/۶", "۲/۵"],
    correctAnswer: 1,
  },
  {
    id: 2,
    subject: "math",
    topic: "کسرها",
    text: "حاصل ۱/۴ + ۲/۴ کدام است؟",
    options: ["۱/۲", "۳/۴", "۲/۸", "۴/۴"],
    correctAnswer: 1,
  },
  {
    id: 3,
    subject: "math",
    topic: "اعداد",
    text: "کدام عدد بر ۳ بخش‌پذیر است؟",
    options: ["۲۵", "۳۴", "۴۲", "۵۵"],
    correctAnswer: 2,
  },
  {
    id: 4,
    subject: "science",
    topic: "بدن انسان",
    text: "کدام اندام وظیفه پمپاژ خون را بر عهده دارد؟",
    options: ["ریه", "قلب", "مغز", "معده"],
    correctAnswer: 1,
  },
  {
    id: 5,
    subject: "science",
    topic: "گیاهان",
    text: "گیاهان بیشتر غذای خود را در کدام قسمت تولید می‌کنند؟",
    options: ["ریشه", "ساقه", "برگ", "گل"],
    correctAnswer: 2,
  },
  {
    id: 6,
    subject: "science",
    topic: "زمین",
    text: "آب در دمای معمولی در چه حالتی قرار دارد؟",
    options: ["جامد", "مایع", "گاز", "پلاسما"],
    correctAnswer: 1,
  },
  {
    id: 7,
    subject: "persian",
    topic: "واژه‌ها",
    text: "کدام گزینه مترادف «شجاع» است؟",
    options: ["ترسو", "دلیر", "آرام", "خسته"],
    correctAnswer: 1,
  },
  {
    id: 8,
    subject: "persian",
    topic: "ادبیات",
    text: "کدام گزینه یک اسم است؟",
    options: ["دویدن", "زیبا", "کتاب", "آرام"],
    correctAnswer: 2,
  },
  {
    id: 9,
    subject: "persian",
    topic: "دستور زبان",
    text: "در جمله «علی کتاب را خواند»، فاعل کدام است؟",
    options: ["علی", "کتاب", "را", "خواند"],
    correctAnswer: 0,
  },
  {
    id: 10,
    subject: "social",
    topic: "ایران",
    text: "پایتخت ایران کدام شهر است؟",
    options: ["مشهد", "اصفهان", "تهران", "شیراز"],
    correctAnswer: 2,
  },
  {
    id: 11,
    subject: "social",
    topic: "جغرافیا",
    text: "کدام مورد یکی از قاره‌های جهان است؟",
    options: ["خزر", "آسیا", "البرز", "نیل"],
    correctAnswer: 1,
  },
  {
    id: 12,
    subject: "social",
    topic: "جامعه",
    text: "کدام مورد برای زندگی اجتماعی اهمیت بیشتری دارد؟",
    options: ["همکاری", "بی‌نظمی", "بی‌توجهی", "انزوا"],
    correctAnswer: 0,
  },
];

export function getSubjectQuestions(subjectSlug: string): Question[] {
  return questions.filter(
    (question) => question.subject === subjectSlug
  );
}

export function getSubject(
  subjectSlug: string
): Subject | undefined {
  return subjects.find(
    (subject) => subject.slug === subjectSlug
  );
}