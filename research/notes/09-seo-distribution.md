# 09 — Free SEO / link-preview / distribution for a recruiter-facing demo

**Worker:** research-worker · **Budget used:** 20/12 (cap 20) · **Date:** 2026-08-30

## Findings

- **OG required four (in `<head>`, RDFa):** `og:title`, `og:type`, `og:image`, `og:url` (canonical ID). Optional but recommended: `og:description` (1–2 sentences), `og:site_name`, `og:locale` (default `en_US`). If `og:image` is set, spec says you **should** set `og:image:alt` (what is *in* the image, not a caption). First of multiple `og:image` tags wins on conflict. Homepage type: `website`. [S1]

- **LinkedIn share cards are OG + image size.** Official Help: required `og:title`, `og:image`, `og:description`, `og:url`. Image max **5 MB**; min **1200×627**; recommended ratio **1.91:1**. Images **<401 px wide display as a thumbnail**. If specs are met but the image is missing, LinkedIn says the crawler may be blocked or the file may be in a protected directory. Help last updated “2 years ago” as of fetch. [S2]

- **X/Twitter Cards: Next.js still emits `twitter:*`; first-party spec is gone.** Next.js `twitter` field writes `twitter:card` (docs example: `summary_large_image`), title, description, image. Metadata export is **Server Components only** so tags land in the **initial HTML** (required: social bots are HTML-limited; Next.js keeps metadata blocking for e.g. `facebookexternalhit`). [S10] Official Cards markup URL now serves a generic X Developer hub with **no Cards specification**. [S11] Do not treat blog “twitter:card has no OG fallback” claims as primary.

- **Google title link ≠ your `<title>` alone.** Sources include `<title>`, visible main title/`<h1>`, **`og:title`**, prominent text, on/off-page anchors, `WebSite` structured data. Recrawl: “a few days to a few weeks.” Practices: descriptive concise `<title>` (avoid “Home”); no keyword stuffing; unique per page; brand the home page; site name + `-`/`:`/`|` on inner pages; one clear main heading. No hard char cap; title link **truncated to device width**. Last updated 2025-12-10. [S3]

- **Google snippet: page content first; meta description is a hint.** Google “may also use” `<meta name="description">` when it is a better summary. Unique per page; home page can use a site-level pitch. No length limit; snippet truncated to device width. Keyword-string descriptions less likely to be shown. Last updated 2026-04-20. [S4]

- **Canonical is optional; self-referential is recommended.** Signal strength: redirects > `rel="canonical"` > sitemap inclusion (weak). None required — Google will pick a URL. Reasons to set one: preferred URL in results, consolidate links, simpler metrics, less crawl waste. Best practices: self-canonical on the preferred URL; do not contradict sitemap vs `rel=canonical`; do not use robots.txt for canonicalization; put canonical in **HTML source**, not JS-only. Prefers HTTPS over HTTP. Last updated 2025-12-10 (page date on sibling Search Central docs). [S8]

- **Sitemap is optional for a small, well-linked site; still useful if the site is new and barely linked.** You **might not need** one if ≤ **~500** index-worthy pages, all reachable from the home page, and you do not need video/image/news rich results. You **might need** one if the site is **new and has few external links** (crawlers discover via already-crawled pages). Submit is a hint, not a crawl guarantee (from Search Central sitemap intro). Last updated 2025-12-10. [S5] Next.js: `app/sitemap.ts` or `sitemap.xml`; `robots.ts` can emit `Sitemap:`. [S9][S12]

- **GitHub README is the first visitor surface.** Typical contents: what it does, why useful, how to get started, where to get help, who maintains. Also listed with license, citation file, contributing, code of conduct. If multiple READMEs: `.github` > root > `docs`. Truncated past **500 KiB**. Keep README to get-started; longer docs → wiki. Auto Outline from headings; relative in-repo links over absolute. [S6]

- **Repo About + topics + social preview are the other skim/share surfaces.** Topics: purpose/subject/language; max **20**; lowercase, numbers, hyphens; ≤50 chars; appear on the repo main page and are searchable; GitHub may suggest topics on public repos. [S7] Custom social preview: until you upload one, shares show **basic repo info + owner avatar**. Upload PNG/JPG/GIF **<1 MB**; recommend ≥640×320, **1280×640 for best display**; solid background safer than transparency. Image only shared from a **public** repo. [S13]

- **CodeEcho live URL already ships recruiter-grade OG (verified 2026-08-30, `LinkedInBot` HTML).** `<title>` + meta description; all four OG required + `site_name`/`locale`/`image:width/height/alt`; `twitter:card=summary_large_image`. `og:image` = `https://trycodeecho.vercel.app/og-home.png?v=85f23f1b` (absolute HTTPS). PNG **200 OK**, `content-length` **208244** (~203 KB, ≪5 MB), declared **1200×630** (meets LinkedIn 1200×627). SHA query on the image URL matches the layout comment about cache-busting. **Missing vs docs:** no `rel=canonical`; `/sitemap.xml` **404**; `/robots.txt` **404** (HTML 404, `noindex`). `og:image:alt` is `"CodeEcho"`, not a description of the screenshot. [S14][S10][S1][S2]

- **CodeEcho GitHub skim/share is weaker than the live site.** REST API 2026-08-30: `homepage` = `https://trycodeecho.vercel.app`; description set (two-axis scoring); **`topics: []`**; **`license: None`**; 0 stars / 0 forks. Repo OG uses GitHub’s auto image `opengraph.githubassets.com/…/CodeEcho` at **1200×600** — **below LinkedIn’s 1200×627 minimum**. Sharing the **repo** URL on LinkedIn is a different (weaker) card than sharing the **demo** URL. README has live link + what/why, then **Stack + env-var tables** before Features; unfinished v2 items (“Cringe Reel”) sit in the first-screen Features list; no “where to get help” / “who maintains”; no license. [S15][S16][S6][S2][S13]

- **Highest-leverage free wins (synthesis of the above, not a new source):** (1) Put the **demo URL** on resume/LinkedIn, not only the repo — live OG already works. (2) GitHub: LICENSE + 3–8 topics + custom social preview **≥1200×627** (ideally 1280×640). (3) README: first screen = one-sentence what + live link + screenshot/GIF + how to try; move Stanford/UIT env internals and v2 checkboxes down or to `ARCHITECTURE.md`. (4) Site: self-referential `alternates.canonical`; optional one-URL `sitemap.ts` + `robots.ts` **because the site is new and barely linked** [S5], not because sitemaps rank. (5) Align `<title>`/`og:title` with the visible H1 so Google is less likely to rewrite [S3]. Skip a blog and paid ads.

## Conflicts and uncertainty

- Official GitHub docs do **not** quantify a “~90s skim.” That number is career-blog territory (worker 05 / Landed); this note uses GitHub’s own “first item a visitor will see” list only.
- X Cards first-party markup is **absent** [S11]; Next.js still documents `twitter` tags [S10]. Fallback-to-OG behavior is widely claimed in secondary posts; not reconfirmed on an official X page.
- LinkedIn Help image rules vs GitHub default OG **1200×600**: conflict only if the **repo** URL is the share target. [S2] vs [S16]
- Sitemap: Google says a small internally linked site may skip one [S5]; the same page says a **new, few-backlink** site may need one. CodeEcho is both small *and* new (0 stars). Treat a one-URL sitemap as cheap insurance, not a ranking lever.
- Canonical: Google says you will “likely do just fine” without one [S8]; still recommends self-canonical. Vercel preview-URL duplicates were **not** researched on Vercel docs (out of remaining budget).
- `og:image:alt="CodeEcho"` vs OG “should specify og:image:alt” describing image contents [S1] — present but weak.
- Title “get the offer” vs homepage visible pitch (“Answer real interview questions…”) — rewrite risk [S3], not proven.
- LinkedIn Post Inspector / Facebook Sharing Debugger: not on the Help page fetched; not cited as required.
- UI composition of `og-home.png` is worker 06. Auth is worker 10.

## Quotes

> "The four required properties for every page are: og:title, og:type, og:image, og:url" [S1]

> "If the page specifies an og:image it should specify og:image:alt." [S1]

> "Minimum image dimensions: 1200 (w) x 627 (h) pixels" [S2]

> "You might not need a sitemap if: Your site is \"small\". By small, we mean about 500 pages" [S5]

> "A README is often the first item a visitor will see when visiting your repository." [S6]

> "Until you add an image, repository links expand to show basic information" [S13]

> "Do include a rel=\"canonical\" link on the canonical page itself" [S8]

> "metadata must be resolved on the server before the page component is rendered" [S10]

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://ogp.me/ | The Open Graph protocol | unknown | primary | Spec; required + optional + image:alt |
| S2 | https://www.linkedin.com/help/linkedin/answer/a521928 | Make your website shareable on LinkedIn | unknown (“2 years ago”) | primary | Official Help; [stale] possible |
| S3 | https://developers.google.com/search/docs/appearance/title-link | Influencing title links in Google Search | 2025-12-10 | primary | Search Central |
| S4 | https://developers.google.com/search/docs/appearance/snippet | How to write meta descriptions | 2026-04-20 | primary | Search Central |
| S5 | https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview | What is a sitemap | 2025-12-10 | primary | Need / not-need rules |
| S6 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes | About the repository README file | unknown | primary | GitHub Docs |
| S7 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics | Classifying your repository with topics | unknown | primary | GitHub Docs |
| S8 | https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls | How to specify a canonical URL | unknown (fetched 2026-08-30) | primary | Search Central |
| S9 | https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap | Metadata Files: sitemap.xml | 2026-08-25 | primary | Next.js |
| S10 | https://nextjs.org/docs/app/api-reference/functions/generate-metadata | Functions: generateMetadata | unknown (fetched 2026-08-30) | primary | Metadata API; twitter; streaming bots |
| S11 | https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/markup | X Developer Platform (Cards URL) | unknown | primary | Cards markup gone; hub only |
| S12 | https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots | Metadata Files: robots.txt | 2026-05-01 | primary | Next.js |
| S13 | https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview | Customizing your repository's social media preview | unknown | primary | GitHub Docs |
| S14 | https://trycodeecho.vercel.app/ | CodeEcho production HTML (LinkedInBot) | 2026-08-30 | primary | Live tags + og-home.png 200; sitemap/robots 404 |
| S15 | https://api.github.com/repos/shardulmarathe/CodeEcho | GitHub REST repo object | 2026-08-30 | primary | description, homepage, topics=[], license=None |
| S16 | https://github.com/shardulmarathe/CodeEcho | CodeEcho GitHub HTML (facebookexternalhit) | 2026-08-30 | primary | Auto OG 1200×600 |

## Needs-browser

- `https://trycodeecho.vercel.app/` — fetch.py exit 2 (thin/JS body). Raw HTML via curl as LinkedInBot was enough for meta; OG *composition* not visually inspected (worker 06).

## Searched

Open Graph protocol, Next.js metadata API, Google title description sitemap, GitHub about repository README, Twitter X cards documentation, Google Search Central title link, GitHub customize repository topics, LinkedIn Open Graph share, X Twitter cards official docs, GitHub social media preview
