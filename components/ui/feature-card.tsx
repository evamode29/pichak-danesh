type FeatureCardProps = {
  icon: string;
  title: string;
  description: string;
};

export function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <article className="card p-6 transition hover:-translate-y-1 hover:shadow-lg">
      <div className="grid size-12 place-items-center rounded-2xl bg-green-50 text-2xl" aria-hidden="true">
        {icon}
      </div>
      <h3 className="mt-5 text-lg font-black">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-[var(--muted)]">{description}</p>
    </article>
  );
}
