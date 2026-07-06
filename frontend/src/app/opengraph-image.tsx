import { ImageResponse } from "next/og";

// Coded OpenGraph card — rendered from the values below, never a screenshot,
// so it stays in sync with the live site with zero manual updates.
export const alt = "CodeEcho — practice explaining, get the offer";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const TITLE = "CodeEcho";
const TAGLINE = "Practice explaining. Get the offer.";
const SUB = "Answer real SWE interview questions out loud — scored on your reasoning and your delivery.";

// Full glyph set so Google's font subsetting includes every character we render.
const GLYPHS =
  " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?/&()@·—–";

// satori only supports ttf/otf/woff (not woff2); requesting without a browser
// UA makes Google serve truetype. Falls back to the built-in font on failure.
async function loadFont(family: string, weight: number, text: string): Promise<ArrayBuffer | null> {
  try {
    const url = `https://fonts.googleapis.com/css2?family=${family.replace(/ /g, "+")}:wght@${weight}&text=${encodeURIComponent(text)}`;
    const css = await (await fetch(url)).text();
    const src = css.match(/src:\s*url\(([^)]+)\)\s*format\('(?:opentype|truetype)'\)/);
    if (!src) return null;
    const res = await fetch(src[1]);
    if (!res.ok) return null;
    return await res.arrayBuffer();
  } catch {
    return null;
  }
}

export default async function Image() {
  const [kalam, grotesk] = await Promise.all([
    loadFont("Kalam", 700, GLYPHS),
    loadFont("Space Grotesk", 500, GLYPHS),
  ]);

  const fonts = [
    ...(kalam ? [{ name: "Kalam", data: kalam, weight: 700 as const, style: "normal" as const }] : []),
    ...(grotesk ? [{ name: "Grotesk", data: grotesk, weight: 500 as const, style: "normal" as const }] : []),
  ];

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          padding: 56,
          background:
            "radial-gradient(1100px 560px at 82% -12%, rgba(234,179,8,0.16), transparent 60%), #f6f3ea",
        }}
      >
        {/* sketch card with hard offset shadow */}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            background: "#fffdf6",
            border: "3px solid #1b1b1b",
            borderRadius: 20,
            boxShadow: "12px 12px 0 #1b1b1b",
            padding: "56px 60px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div
                style={{
                  display: "flex", alignItems: "center", justifyContent: "center",
                  width: 56, height: 56, borderRadius: 14, background: "#1b1b1b", color: "#f9f6ee",
                  fontFamily: "Kalam", fontSize: 34,
                }}
              >
                C
              </div>
              <div style={{ fontFamily: "Grotesk", fontSize: 22, letterSpacing: 5, color: "#6f6a5f", textTransform: "uppercase", display: "flex" }}>
                Interview Practice
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, background: "#eab308", border: "2px solid #1b1b1b", borderRadius: 999, padding: "8px 18px", fontFamily: "Grotesk", fontSize: 22, color: "#1b1b1b" }}>
              spoken · scored
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            <div style={{ fontFamily: "Kalam", fontSize: 132, lineHeight: 0.95, color: "#1b1b1b", display: "flex" }}>
              {TITLE}
            </div>
            <div style={{ fontFamily: "Grotesk", fontSize: 44, color: "#1b1b1b", display: "flex" }}>
              {TAGLINE}
            </div>
          </div>

          <div style={{ fontFamily: "Grotesk", fontSize: 27, color: "#6f6a5f", maxWidth: 900, lineHeight: 1.35, display: "flex" }}>
            {SUB}
          </div>
        </div>
      </div>
    ),
    { ...size, fonts: fonts.length ? fonts : undefined },
  );
}
