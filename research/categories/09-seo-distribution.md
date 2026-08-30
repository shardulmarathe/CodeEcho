# Category 09 — SEO / distribution / link previews

**Evidence:** [`../notes/09-seo-distribution.md`](../notes/09-seo-distribution.md)  
**Audience:** recruiter via resume / LinkedIn / GitHub skim  
**Live check:** `trycodeecho.vercel.app` already has OG+Twitter large image; sitemap/robots 404; GitHub `license: None`, `topics: []`

## Bottom line

OG cards already work. Free wins are **LICENSE + topics + custom GitHub social preview (≥1200×627)**, a **recruiter-first README**, and **self-canonical + optional one-URL sitemap/robots** because the site is new and thinly linked [S1][S2][S5][S6][S13][S14][S15].

## Key evidence

- LinkedIn: OG title/image/description/url; image min 1200×627, max 5 MB [S2]
- OG: add `og:image:alt` that describes the image (not just product name) [S1]
- Google: unique title + meta description; self-canonical recommended; sitemap useful when new/few links [S3][S4][S5][S8]
- Next.js Metadata API / `sitemap.ts` / `robots.ts` are the free implementation path [S9][S10][S12]
- GitHub README = first visitor surface; keep get-started + pitch above the fold [S6]
- Repo API: homepage set; empty topics; no license; auto social 1200×600 below LinkedIn min height [S15][S16]

## Recommended CodeEcho actions

1. Add a LICENSE file; set GitHub topics (`interview-prep`, `nextjs`, `fastapi`, …).
2. Upload custom repo social preview ≥1200×627.
3. Rewrite README top: pitch + live demo link + screenshot; push env/setup below.
4. Add `metadataBase` + canonical; `app/sitemap.ts` + `robots.ts` for the demo URL.
5. Improve `og:image:alt`; keep sharing the **demo** URL on resume/LinkedIn.

## Sources (note-local)

See note `09` Sources S1–S16 (ogp.me, LinkedIn Help, Search Central, Next.js, GitHub docs, live fetches).
