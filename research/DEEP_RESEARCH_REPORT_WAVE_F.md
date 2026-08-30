# Wave F — Optional deep spaces — Deep Research Report

**Date:** 2026-08-30 · **Classification:** breadth-first · **Workers:** 5 (+ lead browser sweep) · **Sources:** see §7  
**ROOT:** `/Users/shar/Documents/GitHub/CodeEcho`  
**Also:** archived stale `nextsteps.md` → `research/archive/nextsteps-2026-08-28.md`; slim `nextsteps.md` + `research/IMPLEMENTATION.md`

## 1. Bottom line

Optional deep spaces reinforce—not rewrite—the 00c backlog. Among **Hello Interview, interviewing.io, Final Round AI, Yoodli, and Exponent** public try paths, **no scorecard or transcript appears without signup** [S1][S2][S3][S4][S5][S29] (Pramp / Interview Warmup try UI not fetched this wave). A labeled no-mic sample remains a wedge. ESL measurement, if done, is an **offline** Fair-Speech/Artie + mixed-effects protocol—not production labeling [S16][S17][S7]. Guest+audio security maps to a short **ASVS L1 + audio/PII L2** control set [S18][S9][S19]. Recruiter analytics on Hobby is **path-only Vercel Web Analytics** (50k/mo; custom events Pro) [S11]; do **not** enable session replay (ICO statistical exception; PostHog DOM risk) [S20][S21]. Homepage/scorecard/recorder acceptance criteria are category 27 [S13][S14][S15][S22][S23].

## 2. Key findings

| # | Finding | Confidence | Sources |
|---|---------|-----------|---------|
| 1 | HI Bitly, i.io AI, FRAI `/try` CTAs, Yoodli Start roleplaying, HI Behavioral Start Practice end at auth/signup — no public scorecard | high | [S1][S2][S3][S4][S5] |
| 2 | Shared pattern: free CTA → signup; feedback promised; mic/cold-start not observable without a session. Public chrome without login includes HI catalog/picker **and** FRAI `/try` format list | high | note 23 P1–P5 |
| 3 | No NIST *accent-fairness* standard (OpenASR ≠ that [S30]); process: NIST MEASURE 2.11 + IEEE 7003 abstract/scope | high | [S6][S24][S30] |
| 4 | Offline protocol: Fair-Speech/Artie + Liu Poisson + speaker-avg (Herron); interpret A/B/C layers | medium — synthesis | [S16][S17][S7][S8]; note 24 F8 |
| 5 | ASVS: upload L1; authz every endpoint; CSP/CORS; STT spend caps; private signed URLs (prefer TTL ≪ 3600s example) | high | [S9][S25][S19][S26][S10] |
| 6 | Hobby analytics = Vercel path views only (50k; no custom events) | high | [S11] |
| 7 | Spec: real sample + scent CTA; score visible + ≤2 disclosure levels; priming before GUM; Blob review | high | [S13][S22][S14][S15][S23] |

## 3. Detailed breakdown

### 3.1 Competitive live UI (cat 23)

Marketing pages promise reports/breakdowns [S3][S29][note 23 P2]; try CTAs land on **Sign In / Create account** for HI, interviewing.io, FRAI, and Yoodli [S1][S2][S3][S4][S5]. Lead browser confirmed Yoodli → `/signup` and HI Behavioral **Start Practice** → login. Without login: HI catalogs/pickers **and** FRAI `/try` format list (still no session/scorecard). Implication: CodeEcho guest sample without signup is unusual in this fetched set.

### 3.2 ESL measurement (cat 24)

Prefer public corpora + mixed-effects models [S16][S17][S7]. Do not equate gold WPM/pause L2≠L1 with detector bias (layer B). Filler detectors couple to ASR; no published filler-F1×L2 table. Fair-Speech Whisper “L2 better” conflicts with most L2 studies and is ethnicity-confounded [S8] — no universal multiplier.

### 3.3 Threat model / ASVS (cat 25)

One DFD + STRIDE [S27]; implement File Upload, REST/API, Frontend, and Data Protection controls [S9][S25][S19][S28]. Supabase documents a 3600s signed-URL example — prefer shorter TTL for audio [S10]. UUID object names are fine only if an opaque guest token authorizes access.

### 3.4 Product analytics (cat 26)

Vercel Web Analytics is cookieless; Hobby is page views only [S11][S12]. Encode funnel as routes. Never log audio/transcript/tokens (product rule from note 26 F8, aligned with cat 18). Session replay fails the ICO statistical exception for individual recordings [S20]; PostHog replay defaults can expose page text [S21].

### 3.5 Design spec (cat 27)

NN/g: real content samples + CTA scent [S13]. Progressive disclosure: ≤2 levels; keep score on primary surface [S22]. GOV.UK Details for secondary text [S14]. MDN: do not open with hung `getUserMedia` [S15]; MediaRecorder review is app Blob state after assembly [S23]. Full checklist in category 27. “Labeled Sample” chrome is also cat-12 policy, not only NN/g.

## 4. Conflicts and open questions

| Question | Position A | Position B | Better supported |
|----------|-----------|-----------|------------------|
| L1 vs L2 WER direction | Fair-Speech Whisper: L2 lower WER | Most L2 studies: L2 worse | Neither universal — Herron confounders [S8] |
| FRAI free General/Mock | `/try` FREE badges | Homepage “no free trial” for live (note 14) | Both may be true for different products; in-app unread |
| Consent-free analytics | Vendor “no banner” claims | CNIL/ICO conditional exemptions | Regulators — vendor counsel is [marketing] |

Unresolved: post-signup competitor UI; IEEE 3198 metric PDF; W3C APG Disclosure (403); Umami Cloud quotas; GA4 exemption unread; Pramp/Warmup try UI.

## 5. Implications

1. **Do not reorder 00c #1–4** — Wave F strengthens sample scorecard and guest try.
2. **Optional later:** offline Fair-Speech/Artie audit; ASVS checklist as PR acceptance for guest/audio; Vercel Analytics when routes exist.
3. **Category 27** is the UI acceptance bar for homepage/scorecard/recorder PRs.
4. Stale root `nextsteps.md` is archived; use `IMPLEMENTATION.md` + INDEX.

## 6. Category artifacts

| # | File |
|---|------|
| 00d | [`categories/00d-wave-f-roadmap.md`](./categories/00d-wave-f-roadmap.md) |
| 23 | [`categories/23-competitive-live.md`](./categories/23-competitive-live.md) |
| 24 | [`categories/24-esl-measurement.md`](./categories/24-esl-measurement.md) |
| 25 | [`categories/25-threat-model-asvs.md`](./categories/25-threat-model-asvs.md) |
| 26 | [`categories/26-product-analytics.md`](./categories/26-product-analytics.md) |
| 27 | [`categories/27-design-spec-synthesis.md`](./categories/27-design-spec-synthesis.md) |

## 7. Sources

| id | url | title | tier | used for |
|----|-----|-------|------|----------|
| S1 | https://www.hellointerview.com/practice/system-design/bitly | HI Bitly → Sign In | primary | finding 1 |
| S2 | https://start.interviewing.io/login?nextPath=%2Finterview-ai | i.io AI → login | primary | finding 1 |
| S3 | https://www.finalroundai.com/sign-up | FRAI signup after /try | primary | finding 1 |
| S4 | https://app.yoodli.ai/signup | Yoodli Start roleplaying dest | primary | finding 1 |
| S5 | https://www.hellointerview.com/login?callback_url=%2Fpractice%2Fbehavioral | HI Behavioral Start Practice | primary | finding 1 |
| S6 | https://airc.nist.gov/airmf-resources/playbook/measure/ | NIST AI RMF Measure | primary | finding 3 |
| S7 | https://arxiv.org/html/2109.09061 | Liu et al. ASR fairness model | primary | finding 4 |
| S8 | https://arxiv.org/html/2605.10615 | Herron et al. benchmarking | primary | findings 4; §4 |
| S9 | https://asvs.dev/v5.0.0/V5-File-Handling/ | ASVS 5.0 File Handling | primary | finding 5 upload |
| S10 | https://supabase.com/docs/guides/storage/serving/downloads | Supabase signed downloads | primary | finding 5 TTL |
| S11 | https://vercel.com/docs/analytics/limits-and-pricing | Vercel Analytics limits | primary | finding 6 |
| S12 | https://vercel.com/docs/analytics/privacy-policy | Vercel Analytics privacy | primary | §3.4 cookieless |
| S13 | https://www.nngroup.com/articles/homepage-design-principles/ | NN/g homepage principles | primary | finding 7 |
| S14 | https://design-system.service.gov.uk/components/details/ | GOV.UK Details | primary | finding 7 |
| S15 | https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia | MDN getUserMedia | primary | finding 7 priming |
| S16 | https://arxiv.org/html/2408.12734 | Fair-Speech — Veliche et al. | primary | finding 4 |
| S17 | https://aclanthology.org/2020.lrec-1.796/ | Artie Bias Corpus | primary | finding 4 |
| S18 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x03-What-is-the-ASVS.md | What is the ASVS | primary | §1 L1/L2 bar |
| S19 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x12-V3-Web-Frontend-Security.md | ASVS V3 Frontend | primary | finding 5 CSP/CORS |
| S20 | https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/what-are-the-exceptions/ | ICO PECR exceptions | primary | no replay |
| S21 | https://posthog.com/docs/session-replay/privacy | PostHog replay privacy | primary | no replay |
| S22 | https://www.nngroup.com/articles/progressive-disclosure/ | NN/g Progressive Disclosure | primary | finding 7 ≤2 levels |
| S23 | https://developer.mozilla.org/en-US/docs/Web/API/MediaStream_Recording_API | MDN MediaStream Recording | primary | finding 7 Blob review |
| S24 | https://standards.ieee.org/ieee/7003/11357/ | IEEE 7003-2024 (abstract) | primary | finding 3 hedge |
| S25 | https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html | REST Security CS | primary | finding 5 authz |
| S26 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x11-V2-Validation-and-Business-Logic.md | ASVS V2 Validation | primary | finding 5 STT caps |
| S27 | https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html | Threat Modeling CS | primary | §3.3 DFD/STRIDE |
| S28 | https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0/5.0/en/0x23-V14-Data-Protection.md | ASVS V14 Data Protection | primary | §3.3 |
| S29 | https://www.tryexponent.com/ | Exponent homepage | primary | §1 named set; marketing feedback |
| S30 | https://www.nist.gov/itl/iad/mltg/openasr-challenge | NIST OpenASR Challenge | primary | finding 3 OpenASR ≠ accent fairness |

Worker notes retain full tables (23–27).

## 8. Method and audit

- Plan: `research/PLAN.md` (= `PLAN_WAVE_F.md`)
- Worker notes: `research/notes/23`–`27` (retained)
- Lead Needs-browser sweep: Yoodli signup href + HI Behavioral Start Practice → login; W3C APG still 403
- Second research wave: **skipped** (no answer-changing gap left in public sources)
- Citation audit (first pass): 38 supported / 5 weak / 2 unsupported / 10 miscited / 4 drift — fixes applied
- Citation audit (re-run): 58 supported / 3 weak / 0 unsupported / 0 miscited / 2 drift — nits fixed (Exponent, OpenASR, marketing vs auth cites; TTL hedge; 00d scope)
- Known gaps: post-login competitor UI; IEEE 3198 PDF; Pramp/Warmup; GA4
- Archive: `research/archive/nextsteps-2026-08-28.md`
