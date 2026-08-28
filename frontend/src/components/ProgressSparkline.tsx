"use client";

/** Tiny SVG trend line. No chart library — stroke follows the sketch ink. */
export function ProgressSparkline({
  values,
  color = "var(--echo)",
}: {
  values: number[];
  color?: string;
}) {
  const w = 160;
  const h = 44;
  const pad = 4;

  if (values.length === 0) {
    return (
      <div className="flex items-center" style={{ height: h }}>
        <p className="text-xs text-muted">No points yet</p>
      </div>
    );
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min;
  const coords = values.map((v, i) => {
    const x = values.length === 1 ? w / 2 : pad + (i / (values.length - 1)) * (w - pad * 2);
    const y = span === 0 ? h / 2 : pad + (1 - (v - min) / span) * (h - pad * 2);
    return { x, y };
  });
  const line = coords.map((p) => `${p.x},${p.y}`).join(" ");
  const area = `${pad},${h - pad} ${line} ${w - pad},${h - pad}`;
  const last = coords[coords.length - 1];

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      width="100%"
      height={h}
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      {values.length > 1 && (
        <polygon points={area} fill={color} opacity={0.08} />
      )}
      <polyline
        points={line}
        fill="none"
        stroke={color}
        strokeWidth={2.2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx={last.x} cy={last.y} r={3.2} fill={color} />
    </svg>
  );
}
