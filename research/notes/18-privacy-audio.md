# Note — Privacy / disclosure for interview audio + transcripts

**Worker:** 18 · **Date:** 2026-08-30 · **Scope:** High-level privacy-notice, retention, deletion UX, and free-tier storage disclosure for a portfolio voice-interview demo (Supabase private bucket + signed URLs; guests + accounts). [not legal advice]. Not guest-token crypto (22). Not exploit/PoC.

**Recommendation (evidence-weighted):** [not legal advice] Before Record: who you are; audio **and** transcript stored; why (practice/grade); finite keep-or-review; named processors; how to delete. ICO: raw audio is personal data, not biometric unless you extract voice to ID the speaker. FTC: voice *recordings* are “biometric information”; staff also flag transcripts. Name a clock (EDPB: a delete button ≠ a retention policy). Private bucket + short-lived signed URLs; say a leaked link lasts until expiry; guests ≠ accounts. Delete must hit audio + transcript + live DBs (backups “beyond use”).

## Findings

- **F1. ICO: meeting audio is personal data even without a name; it is not biometric unless you technically process the voice to identify the speaker.** Example: employer can identify a staff member from a meeting recording → personal information; “this doesn’t make the audio recording biometric data, as it doesn’t result from specific technical processing of the staff member’s characteristics (ie their voice).” Buying a voice-recognition transcriber that *enrols* attendees, extracts features, stores templates, and attributes speech → all those stages are biometric data; if the purpose is unique identification, also special-category. A “recording of someone talking” is listed as a biometric *sample* only in the capture/enrolment path. Guidance banner: under review after the Data (Use and Access) Act. **S1** primary. [not legal advice]

- **F2. ICO storage limitation: no fixed statutory period; you justify length from purpose; document periods; erase or anonymise when done; allow early delete.** Art. 5(1)(e): keep identifiable form “no longer than is necessary for the purposes.” “You cannot keep it for longer than you actually need it.” UK GDPR “does not set specific time limits.” Need a policy with standard periods “wherever possible”; “flexible enough to allow for early deletion.” Review at end of period; automated flag/delete “particularly useful if you hold many records of the same type.” Do not keep “indefinitely ‘just in case’.” Individuals “have a right to erasure if you no longer need the data.” Small org / occasional low-risk: documented policy optional, but still must regularly review and delete/anonymise. Done with data: erase **or** anonymise. Offline archive is still processing (SAR still applies). “Deletion” of electronic data = put **beyond use**; also remove from backups. Pseudonymised (key-coded) data usually still identifiable. **S2** primary. [not legal advice]

- **F3. ICO “always tell” list for notices (voice apps inherit this; not a special voice statute).** When collecting from the person: name + contact; purposes (each one); lawful basis; retention period *or* the criteria used to decide; rights (access, rectification, erasure, restriction, objection, portability — only those that actually apply); right to object “explicitly… clearly and separately”; right to complain (UK: ICO + contact); plus if applicable: DPO/rep, legitimate interests, named or specific recipient *categories* (includes processors), international transfers + safeguards, withdraw-consent (as easy as give), statutory/contractual must-provide, solely-automated decisions with legal/similarly significant effects. SME shortlist: types of data, why, basis, who shared with, how long then “getting rid of it securely,” rights, how to complain. Simple language. **S3, S4** primary. [not legal advice]

- **F4. ICO presentation pattern: layered + just-in-time; don’t bury unexpected uses.** People skip long T&Cs. Required qualities: concise, transparent, intelligible, easy to access, clear/plain language. Use layered notices + headings; “Don’t hide information… clearly bring to people’s attention any uses of data that may be unexpected.” Links must land on the relevant privacy text, not a homepage hunt. Just-in-time notices should also link to fuller policy (user-testing example). Provide at collection time (S3). Tailor copy for different audiences (guests vs accounts). **S5** primary.

- **F5. Erasure UX (ICO): in-product delete is the pattern; backups “beyond use”; tell people what actually happens.** Art. 17 applies if (among others) data no longer needed, consent withdrawn, or unlawful. Not absolute (legal obligation, legal claims, etc.). Request can be verbal or written to any contact; respond within one month. If shared, inform recipients unless impossible/disproportionate. “You must be absolutely clear with individuals as to what will happen to their data when their erasure request is fulfilled, including in respect of backup systems.” Live delete can be instant; backups may persist until overwrite — put them “beyond use,” do not use for any other purpose. Have “appropriate methods” to erase. **S6** primary. [not legal advice]

- **F6. FTC 2023: voice *recordings* are “biometric information”; leftover transcripts + hollow delete are the enforcement pattern.** Policy PDF (18 May 2023): biometric information includes “recordings of an individual’s … voice” and “data derived from such … recordings, to the extent that it would be reasonably possible to identify the person.” Example given is photo + faceprint, not “transcript.” Statement “does not confer any rights” / does not bind the public. Deception: false statements *or* half-truths (name some uses, omit material ones). Collection not “reasonably avoidable” if not “clearly and conspicuously disclosed.” Factors: assess harms first; fix known risks / limit access; no surreptitious/unexpected collection; oversee vendors; train staff; ongoing monitoring. Indefinite keep / no business need called out as increasing harm. **S7, S7a** primary. Staff blog (31 May 2023) Alexa: stores “an audio file and a text transcript”; delete UI left transcripts elsewhere; ~30k employees had voice access without need; staff sentence: recordings “and transcripts of recordings” fall in the May statement. Product: delete audio **and** transcript copies; don’t promise “delete anytime” unless true; don’t keep “just because.” Under-13/COPPA extra — skip unless you collect kids. **S8** primary.

- **F7. Supabase official: public bucket URL is world-readable; private = signed URL or authenticated GET.** Public: `…/storage/v1/object/public/[bucket]/[asset]`. Private: no public URL; access by (1) time-limited signed URL “on the Server, for example with Edge Functions,” or (2) GET `…/object/authenticated/…` + user Authorization. `createSignedUrl(path, expiresInSeconds)` example 3600s. Signed with a **dedicated storage key**, not Auth JWT — survives JWT rotation; valid until expiry; revoke = contact support (no self-serve revoke on this page). Disclose: private bucket; short-lived playback links; a leaked link works until expiry. **S9** primary [vendor].

- **F8. ICO delivery pattern for a recorder: just-in-time at the mic + short top layer + dashboard delete.** Same medium as collection (web form → JIT). Retailer example: JIT on email = purpose; prominent link = courier recipient + “keep it for two years.” Layered: short notice (who / what / why) + expand or one link to detail. Top layer must early-warn uses that are “unexpected, objectionable, or significantly affect them” — storing voice + sending to an STT vendor belongs here. Dashboard: withdraw consent as easily as given; exercise objection/access/portability. Icons optional. **S10** primary.

- **F9. Supabase RLS default-deny; service role bypasses all of it.** No uploads without RLS on `storage.objects`. Patterns: restrict `bucket_id`; per-user folder = first path segment = JWT `sub`; owner `SELECT`. Service key “entirely bypass[es] RLS” — “should not share the service key publicly.” Disclose named processor + that operators with the service role can read objects; guests vs `authenticated` policies differ. **S11** primary [vendor].

- **F10. Chrome web prompt has no site purpose string — you must explain in-page before `getUserMedia`.** Official Help: site dialog is “Allow while visiting the site,” “Allow this time,” or “Never allow.” Granted: “Sites can start to record when you’re on the site” (not other tabs/apps). Recovery: Site settings → Microphone → remove exception. No field for custom “why.” Apple `NSMicrophoneUsageDescription` / AVFoundation pages were JS-walled (Needs-browser). For a web demo, ICO JIT (F8) is the analog of a native purpose string. **S12** primary.

- **F11. EDPB VVA guidelines (adopted 7 Jul 2021): voice carries content + speaker meta; a delete button does not replace a retention clock.** “Voice data is inherently biometric personal data”; Art. 6 + Art. 9 if processed to uniquely identify or it is special-category. Controllers should ask: must you store all recordings *and* transcriptions? once you have the transcript, why keep the audio? for how long per purpose? Those answers “should be part of the information available to the data subjects.” Default indefinite keep of snippets/transcripts “goes against the storage limitation principle”; giving users a delete control “does not remove” the duty to define and enforce retention. Design delete in-device **and** remote stores; mistaken capture → delete immediately. Self-service delete/dashboard recommended. VVA-specific (wake word, multi-user) but retention/notice questions transfer. Body read from adopted v2.0 PDF extract; official PDF not HTML. **S13** primary. [not legal advice]

## Conflicts and uncertainty

- **Voice = biometric?** ICO **S1**: raw meeting audio = personal data, **not** biometric unless you technically process the voice to identify the speaker (enrolment / templates / attribution). FTC **S7a**: voice *recordings* are listed as biometric information; *derived* data if reasonably identifying. FTC staff **S8** adds “transcripts of recordings.” EDPB **S13**: “voice data is inherently biometric”; Art. 9 only when used to uniquely identify or already special-category. Do not blend. Trust copy: “we store your recording and transcript as sensitive personal data” is safer than “this is / isn’t GDPR special-category.” [not legal advice]
- ICO **S3** still says “outside the EU” / “complain to a supervisory authority” in places — UK-GDPR page is under review after the Data (Use and Access) Act (banner on S1–S6, S10).
- No official “X days for interview practice audio” — purpose-led only (S2, S13).
- Apple native purpose-string pages unread (JS wall). Illinois BIPA / state biometric statutes unread (FTC PDF footnotes only).
- Guest vs account retention: no regulator example; ICO says tailor notices per audience (S5).
- Worker 22 owns guest-token attacks — not researched.

## Quotes

- “this doesn’t make the audio recording biometric data, as it doesn’t result from specific technical processing” **S1**
- “you cannot keep it for longer than you actually need it” **S2**
- “If you don’t have a specific retention period then you need to tell people the criteria” **S3**
- “Consent must be as easy to withdraw as it is to give” **S3**
- “put the backup data ‘beyond use’, even if it cannot be immediately overwritten” **S6**
- “recordings of an individual’s facial features, iris or retina, finger or handprints, voice” **S7a**
- “voice recordings – and transcripts of recordings – fall within” **S8**
- “Signed URLs remain valid until their expiry time regardless of any Auth key changes” **S9**
- “the top layer should always give people prominent, early warning” **S10**
- “Service keys entirely bypass RLS policies” **S11**
- “Sites can start to record when you're on the site” **S12**
- “Providing data subjects with means to delete their personal data does not remove” **S13**

## Sources

| id | url | title | published | tier | note |
|----|-----|-------|-----------|------|------|
| S1 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/biometric-data-guidance-biometric-recognition/biometric-recognition/ | Biometric recognition \| ICO | unknown (fetched 2026-08-30) | primary | Under review (DUAA); meeting-audio vs speaker-ID |
| S2 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/ | Principle (e): Storage limitation \| ICO | unknown | primary | Art. 5(1)(e); no fixed periods; beyond use |
| S3 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/the-right-to-be-informed/what-privacy-information-should-we-provide/ | What privacy information should we provide? \| ICO | unknown | primary | Always-list; retention or criteria |
| S4 | https://ico.org.uk/for-organisations/advice-for-small-organisations/privacy-notices-and-cookies/how-to-write-a-privacy-notice-and-what-goes-in-it/ | How to write a privacy notice \| ICO | unknown | primary | SME shortlist; simple language |
| S5 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/the-right-to-be-informed/how-should-we-draft-our-privacy-information/ | How should we draft our privacy information? \| ICO | unknown | primary | Unexpected uses; test; tailor audience |
| S6 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/individual-rights/right-to-erasure/ | Right to erasure \| ICO | unknown | primary | Art. 17; 1 month; backups |
| S7 | https://www.ftc.gov/news-events/news/press-releases/2023/05/ftc-warns-about-misuses-biometric-information-harm-consumers | FTC Warns About Misuses of Biometric Information | 2023-05-18 | primary | Press; unfairness factors |
| S7a | https://www.ftc.gov/system/files/ftc_gov/pdf/p225402biometricpolicystatement.pdf | FTC Policy Statement on Biometric Information | 2023-05-18 | primary | Voice recordings listed; derived data; fetch.py exit 3 / browser 403; body from official-PDF extract |
| S8 | https://www.ftc.gov/business-guidance/blog/2023/05/out-mouths-babes-ftc-says-amazon-kept-kids-alexa-voice-data-forever-even-after-parents-ordered | FTC: Amazon kept kids’ Alexa voice data | 2023-05-31 | primary | Audio+transcript; hollow delete; staff restates S7a |
| S9 | https://supabase.com/docs/guides/storage/serving/downloads | Serving assets from Storage \| Supabase | 2026-08-28 | primary | Private vs public; signed URL; [vendor] |
| S10 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/the-right-to-be-informed/what-methods-can-we-use-to-provide-privacy-information/ | What methods can we use to provide privacy information? \| ICO | unknown | primary | Layered / JIT / dashboard |
| S11 | https://supabase.com/docs/guides/storage/security/access-control | Storage Access Control \| Supabase | 2026-08-28 | primary | RLS default deny; service key; [vendor] |
| S12 | https://support.google.com/chrome/answer/2693767?hl=en | Use your camera and microphone in Chrome | unknown | primary | No custom purpose string |
| S13 | https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-022021-virtual-voice-assistants_en | Guidelines 02/2021 on virtual voice assistants \| EDPB | 2021-07-07 | primary | Landing official; body from adopted v2.0 PDF extract |

## Needs-browser

- https://www.ftc.gov/system/files/ftc_gov/pdf/p225402biometricpolicystatement.pdf — fetch.py exit 3; playwright-jobs HTTP 403. Body used from official-PDF text extract (S7a).
- https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription — fetch.py exit 2 (JS).
- https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media — fetch.py exit 2 (JS).
- https://www.edpb.europa.eu/system/files/2021-07/edpb_guidelines_202102_on_vva_v2.0_adopted_en.pdf — not fetched as HTML; quotes aligned to adopted v2.0 extract.
- https://ico.org.uk/for-organisations/advice-for-small-organisations/privacy-notices-and-cookies/where-do-i-put-my-privacy-notice/ — HTTP 404.

## Searched

- ICO voice recording privacy
- EDPB voice biometric data
- ICO storage limitation principle
- FTC biometric voice privacy
- ICO privacy notice what include
- Apple microphone purpose string
- Supabase storage signed URLs
- Google microphone permission message
- ICO right to erasure
- Apple write clear purpose strings
