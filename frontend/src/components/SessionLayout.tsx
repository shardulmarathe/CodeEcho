"use client";

// Two-column session shell: a narrow left rail (question-type controls) and a larger
// right column (the generated question + the recorder pinned at its bottom). Stacks on
// small screens. Purely presentational, callers pass the pieces.

export function SessionLayout({
  left,
  right,
}: {
  left: React.ReactNode;
  right: React.ReactNode;
}) {
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(260px,330px)_1fr] items-start">
      <aside className="lg:sticky lg:top-6">{left}</aside>
      <section className="flex min-h-[60vh] flex-col gap-5">{right}</section>
    </div>
  );
}
