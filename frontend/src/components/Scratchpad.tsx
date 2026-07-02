"use client";

export function Scratchpad({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="panel p-4 space-y-2">
      <div className="flex items-center justify-between gap-3">
        <p className="eyebrow">scratchpad</p>
        <span className="text-xs mono text-muted">
          pseudocode / notes · optional · analyzed with your answer
        </span>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        rows={6}
        spellCheck={false}
        placeholder={"# jot pseudocode here (optional)\n# seen = {}\n# for i, n in enumerate(nums):\n#   if target - n in seen: return [seen[target-n], i]"}
        className="w-full rounded-lg p-3 text-sm mono"
        style={{ minHeight: 130, lineHeight: 1.6 }}
      />
    </div>
  );
}
