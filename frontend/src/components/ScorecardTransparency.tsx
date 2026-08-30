import type { Scorecard } from "@/lib/types";

export function ScorecardTransparency({ scorecard }: { scorecard: Scorecard }) {
  const definitions = scorecard.dimension_definitions ?? [];
  const sources = scorecard.sources ?? [];

  return (
    <div className="space-y-4 text-left">
      <details className="group border-y-2 py-3" style={{ borderColor: "var(--border)" }}>
        <summary className="cursor-pointer select-none font-semibold">
          How this was graded
          <span className="ml-2 text-xs text-muted group-open:hidden">＋</span>
          <span className="ml-2 hidden text-xs text-muted group-open:inline">−</span>
        </summary>
        <dl className="mt-3 grid gap-3 sm:grid-cols-2">
          {definitions.map((definition) => (
            <div key={definition.name}>
              <dt className="text-sm font-semibold">{definition.name}</dt>
              <dd className="mt-0.5 text-xs leading-relaxed text-muted">
                {definition.description}
              </dd>
            </div>
          ))}
        </dl>
      </details>

      {sources.length > 0 ? (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-muted">
            Sources used to grade
          </span>
          {sources.map((source) => {
            const className =
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors hover:bg-[var(--surface-2)]";
            const tooltip = source.snippet || source.title;
            return source.url ? (
              <a
                key={source.id}
                className={className}
                href={source.url}
                target="_blank"
                rel="noreferrer"
                title={tooltip}
              >
                {source.title}
              </a>
            ) : (
              <span key={source.id} className={className} title={tooltip}>
                {source.title}
              </span>
            );
          })}
        </div>
      ) : (
        <p className="text-xs text-muted">Graded from rubric only.</p>
      )}
    </div>
  );
}
