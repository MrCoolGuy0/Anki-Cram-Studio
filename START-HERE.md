# MAIN CRAM + ANKI CRAM 2.0.26 — shared Writing enumeration

Install Cram-Studio-v2.0.26.ankiaddon over Cram and restart Anki. Keep the full
Cram-Studio-Handoff-v2.0.26.zip for continuation. Package remains cram_studio.

Gemini, Groq and Grok share the same Writing prompt, decoder, grouping checks,
source formatting and input matching. Clear counted one-word lists such as
The five primary tastes are sweet, salty, sour, bitter, and umami now produce
five targets offline, including all five inside one cloze. A previous single-item
cache cannot override this clear structure. Complex prose/compounds still use
the shared semantic grouping process rather than blindly splitting punctuation.

The shared AI decoder accepts harmless case/spacing differences and empty
separator metadata while mapping targets back to the exact source. It still
rejects invented words, changed numbers, omitted answers and unknown connectors.
One-item and whole-list submissions, partial reveal, original commas/and/markup,
case/plural input tolerance, wrong-answer revision/reveal and explicit native
rating behavior are retained. Existing multiple-choice fixes are included.

314 short Python checks, the Node UI suite and focused actual Qt WebEngine
checks pass. Both MAIN/ANKI, light/dark and narrow/wide layouts show 0/5 -> 1/5
and reveal the exact source list. No live provider call or user collection was
used. See WRITING-PROVIDER-FIX.md for evidence and limits.

# Previous releases

# MAIN CRAM + ANKI CRAM 2.0.25 — shared AI choice rules

Install Cram-Studio-v2.0.25.ankiaddon over the current Cram add-on and restart
Anki. Keep Cram-Studio-Handoff-v2.0.25.zip for complete source continuation.

Groq now uses the complete Gemini choice-writing instructions, including the
same question-based difficulty and real related-but-wrong fallback rules. All
providers share new presentation rules so wrong choices do not expose the answer
by adding repeated category labels or differing in capitalization/naming style.
Groq keeps its additional semantic audit in the same request. Original answers,
shared case rendering, saved progress, customization and scheduling are retained.

Regenerate choices or Regenerate deck choices for existing affected sets. Saved
options are not silently changed mid-question. See CHOICE-FORMAT-FIX.md for the
implementation, short checks and limits. No live AI quality test was performed.

# Previous releases

# MAIN CRAM + ANKI CRAM 2.0.24 — distinct Groq choices and hover stability

Install Cram-Studio-v2.0.24.ankiaddon over the current Cram add-on, then restart
Anki. Keep the complete Cram-Studio-Handoff-v2.0.24.zip for exact continuation.
Previous features, prompts, providers, saved practice and customization remain.
Read DELIVERY-REQUIREMENTS.md before making future changes.

Groq now has a concise, provider-specific choice prompt and a required concept
and factual-contrast audit inside the same generation request. It must identify
what each option means, reject aliases/alternate correct answers, and replace
bad candidates before returning three distinct wrong options. Validation rejects
repeated canonical concepts and missing/invalid contrast metadata. Gemini's
original generation prompt, schema and temperature are unchanged; Grok also
retains its previous contract. Writing generation is unchanged for all providers.
There is no additional verification API call, hidden retry or model switch.
The response has more metadata, so equal API latency is not promised.

Shared context-specific guards now reject the reported IPv4 address-supply
synonyms, MTU/MTU-size alternatives, misleading MTU name changes and alternate
Copyright Act names in a Section 107/fair-use stem. These guards run on new
results, cached sets during preparation/attachment and the manual choice editor.
They are deliberately narrow, rather than a universal synonym dictionary.
Novel cases additionally rely on the AI's concept audit, which is not a proof
of factual correctness. Only the three option strings are saved, as before.

After installing, use Regenerate deck choices for the affected Groq decks to
replace old generated sets. Cache IDs and profile formats are unchanged: this
update does not erase valid Gemini choices or rewrite saved practice snapshots.
Recognized bad cached examples are rejected on fresh preparation; old attached
options stay fixed until an explicit regeneration replaces them.

The hover fix now covers choice text, panels and pseudo-element overlays in both
interfaces. ANKI CRAM also avoids reapplying its whole palette/images/sizing on
unrelated body-class changes. Genuine theme changes, customization and new card
roots still apply normally. Layout, colors, keyboard controls, random choice
positions and all scheduling rules remain intact.

302 short Python tests and the complete Node suite passed. Real Qt WebEngine
checks compare inherited-theme hover effects before/after, retain scroll and
picks, and verify theme/customization updates. Existing Space, revealed-mode
and Flashcard control regressions pass. All checks use synthetic cards, no live
AI keys or user collection. Windows OS and real Groq response quality were not
tested. See QUALITY-HOVER-FIX.md for evidence, limits and reproduction commands.

# Historical release notes

# MAIN CRAM + ANKI CRAM 2.0.23 — cloze answers stay filled on Space

Install the complete Cram-Studio-v2.0.23.ankiaddon over the existing Cram add-on,
then restart Anki. Keep Cram-Studio-Handoff-v2.0.23.zip for exact continuation.
All previous features, providers, saved practice and customization are included.
Read DELIVERY-REQUIREMENTS.md before making another update.

ANKI CRAM now keeps the existing Multiple Choice question, blank and choice
nodes when Anki replaces its answer view. Space requests native Show Answer once;
a delayed activation of the focused option cannot alter the selection while
that request is pending. Selected text remains visible before the response,
then every blank shows its correct answer, including wrong or incomplete attempts.
The next card starts fresh, and explicit regeneration still replaces its options.

The change is confined to ANKI CRAM's MCQ reveal presentation. Answer-side Space
and rating keys still use Anki's original callbacks. Flashcard flipping, Writing,
image occlusion and ordinary Anki review retain their existing behavior. MAIN
CRAM is covered by its existing shared UI checks; no MAIN runtime change is made
apart from the version label. No AI prompts, API requests, cache IDs, randomness,
card queues, scheduling, filtered-deck settings or stored profile formats change.

294 short Python tests and the full Node UI suite passed. Bounded real Qt
WebEngine checks cover the screenshot's three-blank pattern, mouse selection,
Space, a delayed focused-button activation, repeated mounts, explicit rating,
choice focus/hover, Flashcard Space and revealed mode transitions. Tests use
synthetic cards and no live API/user collection; Windows OS was not tested.
See CLOZE-SPACE-FIX.md for the scope, limits and test commands.

# Historical release notes

# MAIN CRAM + ANKI CRAM 2.0.22 — stable multiple-choice interaction

Install the full Cram-Studio-v2.0.22.ankiaddon over the existing Cram add-on,
then restart Anki. Keep Cram-Studio-Handoff-v2.0.22.zip separately for exact
continuation. This is the complete add-on, retaining Gemini, Groq, Grok (xAI),
Writing, flashcards, customizers, saved practice, filters and native scheduling.
Read DELIVERY-REQUIREMENTS.md for every future update.

Focusing/clicking an option for the current blank no longer resets the choices
pane’s scroll position or rewrites all blank contents. Moving to another blank
still pages to its choices normally. Both MAIN CRAM and ANKI CRAM are covered.

Repeated native shown-hook calls now retain the existing rendered card instead
of rebuilding it from an older pre-generation packet. Loaded choices, picks,
text zoom and scroll stay in place. One stable hook callback is installed per
Anki hook array. New card/epoch/side/DOM and explicit regeneration still redraw
when appropriate. Native choices opt out of inherited hover animations that can
fade or move their answer hit boxes; their configured colors remain intact.

The old broad AI validation error is replaced by specific reasons: repeated
correct answer, alias, repeated wrong option, empty/long option, wrong count or
invalid response fields. Validation rules and prompts are unchanged. Failed
batches never overwrite saved choices, create invented choices or silently spend
quota on automatic retries. The message does not echo provider JSON, note text,
keys or unexpected parser exception details. Create choices retries explicitly.

Answer positions are randomized by Cram locally using SystemRandom, independently
of the AI provider. The AI supplies three wrong choices; Cram adds the original
correct answer and shuffles the four. Repeated letters can occur naturally; the
add-on does not impose an A-B-C-D pattern or exact balancing. Attached choices
remain fixed during the question. No randomness or cache-ID change is introduced.

293 short Python tests and the complete Node UI suite passed. A real Qt WebEngine
regression reproduced and then verified the fix for focus/scroll jumps in both
interfaces, theme hover fading and stale native remount. Existing real Qt mode
transition checks passed for late/cached options, Writing, reveal and explicit
ratings. These tests used synthetic cards/responses on Linux, not a user’s
Windows installation or a live AI API. No long tests were run. See
CHOICE-STABILITY.md for exact before/after observations and commands.

# Historical release notes

# MAIN CRAM + ANKI CRAM 2.0.21 — Grok (xAI), Gemini and Groq

Install the complete Cram-Studio-v2.0.21.ankiaddon over the existing Cram add-on,
then restart Anki. Keep Cram-Studio-Handoff-v2.0.21.zip separately for exact
continuation. Both contain the complete current add-on, with previous features.
Read DELIVERY-REQUIREMENTS.md before making another update.

In MAIN CRAM open Settings → AI settings, or click AI settings in ANKI CRAM’s
start window. Select Grok (xAI), enter a model API key from https://console.x.ai/,
click Test connection, then Save. Grok defaults to grok-4.7. Refresh models lists
text model IDs available to your key; you can also enter one manually. Project
model access, quota and API credits are managed by xAI. A Cursor/agent credential
is not assumed to grant public model API access. Replace any key exposed in chat.

Choices, individual/deck regeneration and Writing answer grouping all use the
selected provider. The same question-based prompts, real related wrong terms,
alias exclusions and original-format checks apply in both Cram interfaces.
Grok uses the xAI Responses endpoint with JSON Schema, no tools and store:false.
This avoids creating a retrievable server-side conversation; it is not a promise
about all provider retention policies. No exposed key was used for validation.

Google Gemini, Groq and Grok have independent model settings, session keys,
environment variables and Windows DPAPI files. Existing Gemini and Groq model
and cache identifiers are unchanged; Grok choices use their own grok: namespace.
Switching providers does not delete old choices, history or saved MAIN sessions.
MAIN CRAM remains independent practice. ANKI CRAM still uses Anki’s queue and
explicit ratings, including filtered-deck rescheduling settings and Undo.

288 short Python checks, the complete Node UI suite and real Qt settings checks
passed using synthetic keys/responses. Checks cover both MAIN and native Grok
generation without unintended scheduling, three-provider key/cache isolation,
HTTP errors/credits, model lists, JSON/refusal handling and Writing grouping.
No live xAI/Gemini/Groq request, Windows OS run or user collection was used.
Live model availability, response quality, cost and latency are not measured.
No long tests were run. Other add-ons are unchanged and remain separate.

# Historical release notes

# MAIN CRAM + ANKI CRAM 2.0.20 — Gemini and Groq

Install Cram-Studio-v2.0.20.ankiaddon over the existing Cram add-on, then restart Anki.
This is the full add-on with previous features. Keep the separate matching
Cram-Studio-Handoff-v2.0.20.zip for continuation. Read DELIVERY-REQUIREMENTS.md.

In MAIN CRAM open Settings → AI settings. In ANKI CRAM’s start window click
AI settings. Select Google Gemini or Groq, paste that provider’s API key, choose
a model, click Test connection, then Save. Groq defaults to openai/gpt-oss-20b;
Refresh models or a manually entered text model ID can select another model.
Use the corresponding provider’s key: Gemini keys do not authenticate to Groq.

Choices, individual/deck regeneration and Writing answer grouping all use the
selected provider in both interfaces. The existing question-based difficulty,
real related wrong terms, alias exclusions and original-format grouping checks
are shared. The provider is never switched automatically after an error.

Your previous Gemini model/key/cache are retained. Windows stores each provider’s
key in its own DPAPI file. Other systems support separate session/environment
keys. Changing provider preserves both configurations; keys are never placed in
practice.json or these downloads. Switching back to Gemini reuses its old choices.
Groq choices have a provider-qualified cache namespace. Existing saved MAIN sessions
retain their snapshot; an already attached question is not silently reshuffled.
Writing grouping caches are provider-neutral because their validated output is
exact spans into the same source answer. See PROVIDERS.md for implementation notes.

Short validation: 277 Python checks, the existing Node UI suite and a real Qt
settings check passed using synthetic keys/replies. Included scheduling checks
retain the MAIN practice / native ANKI queue boundary. No live Groq/Gemini request,
Windows OS run or user collection was used; model access, live quality, quota and
latency still depend on your account/provider. No long tests were run.

# Historical release notes

# Separate full source delivery

Read DELIVERY-REQUIREMENTS.md first. The user requires a separate FULL installer
and matching FULL source ZIP for each updated add-on, every time. This ZIP
contains this add-on only. Existing runtime files and installer are unchanged.

# MAIN CRAM + ANKI CRAM 2.0.19

Install the full Cram-Studio-v2.0.19.ankiaddon over Cram and restart Anki.
Keep Cram-Studio-Handoff-v2.0.19.zip for exact continuation.

The supplied numeric timing log identifies the remaining delay:19 requests
averaged23.403 seconds; queue wait never exceeded0.51ms; saving averaged6.587ms
per batch. HTTP accounted for99.967% of recorded worker time. HTTP includes
connection/network/upload/server/download, so this does not isolate Google's
processing time or prove a rate limit. Older error statuses can include Pause.

Bulk deck regeneration and MAIN CRAM background choice preparation now overlap
at most two requests. The first waiting question is still generated first;
single-card regeneration, native ANKI CRAM per-card generation and Writing
keep their sequential request behavior. Each request still uses the existing
bounded batches and identical prompt/schema/model/generation settings. This
can improve bulk throughput; it does not make an individual response instant.

Every valid completed batch is saved, including results that finish out of
order after another batch fails or Pause is requested. Resume tracks exact
saved choice IDs, preventing skipped or repeated sets. No new requests launch
once cancellation/failure is known; already running replies are drained and
saved. On HTTP429 there is no hidden retry: completed work stays, and the next
Resume uses one request at a time for the rest of this profile session.

Dedicated workers and persistent connections remain independent of AnkiLink
and Anki's collection/general executors. API child workers share safe numeric
timing context. Overlapping HTTP durations may sum to more than wall time;
new logs mark api_parallelism and api_queue. Pause now has a separate cancelled
status. No study content/API key is logged or uploaded as telemetry.

The complete Python and Node UI regressions passed, plus targeted tests after
the final priority-batch quota guard. Tests exercise real bounded worker overlap, no more than two in flight,
priority first question, no extra requests after Pause, out-of-order failure
checkpoints, exact Resume IDs, quota fallback and synchronized timing records.
Choice/Writing generation method ASTs and all web UI assets match2.0.18.
No real Gemini key/request, user collection or end-to-end speedup was tested.
AnkiLink1.1.2, Study List0.6.17 and Study Sounds1.1.8 remain separate/unchanged.

# MAIN CRAM + ANKI CRAM 2.0.18

Install the full Cram-Studio-v2.0.18.ankiaddon over Cram and restart Anki.
Keep Cram-Studio-Handoff-v2.0.18.zip for exact continuation.

This restores2.0.16's dedicated Gemini workers after the requested2.0.17
rollback, then improves generation without weakening the AI instructions.

- Reuse a persistent HTTP connection per Gemini worker, across batches and new
  Gemini client instances. The former urllib opener closed every connection.
- Update MCQ questions from a copy of only their relevant cached choices,
  instead of copying unrelated cards and Writing plans from the whole profile.
- Whole-deck regeneration and background preparation use up to10 short-answer
  sets per request. The first waiting question remains a small priority batch;
  single-card regeneration and native per-card generation retain their prior
  small batches. Long answers reduce the batch size to protect output limits.

Requests remain sequential within each generation job. There are no hidden
retries, extra parallel batch requests, model switches or thinking changes.
Choice/Writing prompts, schema, validation, model selection and generation
settings are retained exactly. Existing saved choices, progress, layouts,
custom sizes/colors, native ratings/undo and filtered-deck behavior remain.

Validation:256 short Python checks passed in3.78 seconds, plus the complete
Node UI suite. Local HTTP, bounded batches, cancellation/resume and selective
cache tests passed. Interface assets match2.0.16 byte-for-byte.

Transport keeps API keys in request headers only, blocks cookies/machine auth,
rejects redirects/unexpected origins, bounds reads and preserves quota/errors.
Profile shutdown closes connections off the UI thread. Numeric-only local
queue/request/cache timing records from2.0.16 are retained. No real user key,
collection or Gemini request was used for validation; real Google latency and
the user's total speedup are not measured here.

# Continue version 2.0.16

Preserve cram_studio identity and the entire existing UI/features. A possible
regeneration regression after2.0.15 was reproduced: generation waits behind
other add-ons when Anki's shared non-collection workers are occupied. Use
network_jobs.run_network for all six network-only jobs, never TaskManager's
collection or shared general executor. Actual collection QueryOps stay on Anki.
NetworkJobs owns three workers per profile; close_network is called during
profile close and does not join running requests on the UI thread. UI
completions still use taskman.run_on_main, with closed-profile guards. The
LiveReviewer network_runner argument is only a dependency-injection seam;
production defaults to the same dedicated runner.

Local bounded numeric-only timing records distinguish queue wait, request/
decode/cache-save totals and complete worker time. File failures are nonfatal,
keys/prompts/answers/errors/URLs are never logged, and no telemetry is uploaded.
The full Gemini wire payload, prompts and validation are preserved, verified
against2.0.15. Do not weaken choice quality to hide latency. Real user/API timing
remains unknown until observed. All247 Python checks and full UI checks passed.
Deliver the full2.0.16 installer and its exact matching source handoff together.

# Continue version 2.0.15

Continue the exact cram_studio source. Six network/cache-only TaskManager jobs
now pass uses_collection=False; retain this flag. Do not apply it to collection
queries. The prior UI and scheduling audit missed the default collection
executor on direct run_in_background calls; this release corrects that issue.
Tests/test_background_jobs.py fails with the old default and passes with the
fix, including a held-generation/next-card queue case. All242 Python checks and
the complete UI suite passed. Source, full installer and UI from2.0.14 remain
intact apart from worker assignments, version metadata and documentation.
No new scheduling, interface or AI-generation behavior is introduced.

# Continue version 2.0.14

Use this exact source/package cram_studio and full matching installer. This
patch changes MAIN CRAM home markup/styles and catalog filtered metadata only.
Do not recreate the study UI or change any existing capabilities. Latest-two
saved practice cards expand/search without deleting progress. Full deck names
and IDs stay in stored sessions; concise names are display only. Standalone
filtered roots have their own visual section; actual hierarchy is untouched.

Current checks: complete Node UI suite, 240 short Python tests, native catalog
metadata, light/dark/narrow QtWebEngine rendering. See the performance audit.
The following historical notes remain part of the same continuation.

# MAIN CRAM + ANKI CRAM 2.0.13

Install Cram-Studio-v2.0.13.ankiaddon over the existing Cram add-on and restart Anki.
Keep Cram-Studio-Handoff-v2.0.13.zip for exact continuation of this source/UI.

Answers containing an image automatically use a flashcard for that question in
both MAIN CRAM and ANKI CRAM, including when Multiple Choice or Writing was
selected. The original image and accompanying caption are retained. An image
hidden inside the active cloze is now a valid answer slot instead of being
silently dropped or exposed on the question side. Other cloze ordinals remain
visible as context, as before. Image Occlusion keeps its existing masked UI.

ANKI CRAM now renders these supported image answers in its normal compiled
flashcard rather than the native-card fallback. Space reveals/flips repeatedly;
it never auto-rates. Again/Hard/Good/Easy remain native Anki controls. The selected
study mode is preserved, so the next supported text question uses that mode.
MAIN CRAM keeps its separate practice recall controls and saved progress. No
OCR or Gemini generation is requested for the visual answer. Existing behavior
for image answers with captions is retained; image-only cloze support is new.

Checks: 103 short Python tests passed in 1.3 seconds, including new image-answer
cases plus content, native-review boundary, filtered rescheduling on/off,
progress and MAIN parity regressions. Full Node DOM suite and JS syntax checks
passed. New DOM cases exercise original image rendering, no Writing/MCQ UI,
repeated flips, reveal exactly once and persistent native rating controls.
Native controller checks trip on any replacement scheduler/queue access.
No live Windows Anki collection, live Gemini request or long tests were run.
No CSS, appearance/customization, other add-ons or scheduler code was changed.

Continue this exact source under package cram_studio. Preserve profile/cache/
sessions/appearance and all earlier features. Deliver the complete installer
and exact matching source handoff together for every future update. Latest
Library identities are retained for installer and handoff; prior release
instructions below apply only to their named versions.

Historical release notes follow.

# MAIN CRAM + ANKI CRAM 2.0.12

Install Cram-Studio-v2.0.12.ankiaddon over the existing add-on, then restart Anki.
Also install Study List 0.6.16 for the matching Study List button styling.

Fixes the overview buttons flickering/pulsating together. Previously both
observers insisted on the position immediately after Description, moving each
other indefinitely. The stable order is native controls, Study List (when
present), ANKI CRAM. Neither add-on moves or restyles native controls. Cram adds
one ANKI CRAM button; no MAIN CRAM block, new bar or global button CSS is added.

The new button matches the native control's computed border corners, colors,
font and padding, including themes styled by IDs/structural selectors. It
stretches with the existing control row instead of centering as a short pill.
Only this added button has movement/hover animations disabled. Attribute writes
are guarded so both observers settle. Native styles and dark-mode updates are
retained. Study List remains a separate add-on.

Bounded real Qt WebEngine checks reproduce 35 mutations in 700 ms with
2.0.11/0.6.15, versus zero after settling with these updates. Regular, filtered
and finished/no-cards-due layouts retain native HTML/heights, match corners and
height, keep hover bounds stable, dispatch each click once, refresh colors for
dark mode and recover a themed control-row redraw without duplicates. This is
a synthetic theme fixture, not a live run of the user's Windows theme.

All quiz behavior, Writing border, scheduling boundaries, progress and saved
appearance from 2.0.11 are retained. No scheduler/reviewer implementation is
changed. Keep Cram-Studio-Handoff-v2.0.12.zip for exact continuation.

Historical release notes below apply to their named versions.

# Continue Cram Studio 2.0.11

The user rejected2.0.10's two-button deck entry wrapper and visible native bottom
links. Continue the exact source/UI; only ONE added ANKI CRAM button is allowed
in the regular/filtered/finished overview controls. No new MAIN CRAM entry/bar,
no resizing/restyling other buttons, no redesign. Keep every practice fix in2.0.10.

entry.js now inserts one bare button after Description/Empty/Options, copies the
reference class/inline style to that new button only, and never wraps the row.
It reports duplicated in-page overview controls to Python. __init__.py removes
its own native bottom links; overview_controls temporarily hides only the
redundant overview bottomWeb and restores its prior visible state on departure.
An already hidden theme bar is never forced visible. Original standard review
ratings remain native. Study List0.6.15 checks bar visibility after300/1200ms and
continues its own fallback; no Study List files were changed. Entry is overview
only (not the top deckBrowser), with no added context-menu ANKI entry. Existing
Tools/native shortcuts and original MAIN context menu stay. writing.css scopes
a full explicit border and response-pane padding to MAIN's Writing control.

231 fast Python checks, full Node suite and updated test_main_parity_qt.py pass.
Real WebEngine tests use synthetic notes/controller fixtures. Original overview
buttons preserve exact HTML/heights; exactly one new button/no wrapper; adverse
disabled-border rules; existing restart/Writing/IO controls. No real user data,
Windows Anki/Rust or Gemini API calls. Do not claim the user's entire theme was
run here; only representative equivalent layouts and protected node geometry.

Deliver full installer plus matching source handoff; preserve package/cache/
profile/session identities. Study List, Study Sounds and AnkiLink stay separate.
Library installer identity libfile_bf06728858748191a6434c01246d2905 (before this
release version44), handoff libfile_b24f0c73e4b481919f9cd80a85e8b294 (version45).
Historical notes below are retained but their deck-entry UI is superseded.

# Continue Cram Studio 2.0.10

Continue this exact source/UI as an update of package cram_studio. Every release
must include the full .ankiaddon and exact matching source handoff. Preserve
profile/cache/settings/saved-session identities. Do not redesign from prose.
Study List0.6.15, Study Sounds1.1.8 and the new separate AnkiLink1.0.0 are untouched.
Avoid long tests, guide clutter and unnecessary confirmations.

## Current cumulative fixes

The user requested visible entry buttons on normal/filtered native deck screens,
aligned practice setup, Restart inside MAIN settings (fresh shuffle only when
order=shuffle), uncut MCQ feedback borders, time to read wrong answers, and MAIN
Writing/occlusion parity with ANKI CRAM.

__init__.py adds scoped main-webview refresh/style hooks that evaluate entry.js
on deckBrowser/overview only. entry.js adds an isolated idempotent button row
near Study Now, with a flow fallback for deck-list/finished pages and an observer
for theme rerenders. Existing bottom links/Tools shortcuts remain. Native launch
still opens the current setup. A deck context menu can select the requested deck
then open setup. No entry action invokes native Study Now or grade handlers.

web/app.js now holds every missed practice result until Continue/Enter, and
fillBlanks uses original correct answers on the revealed side. Original picks
stay intact for red/green feedback. app.css aligns setup tracks with subgrid and
an older-browser fallback. appearance.css gives the MAIN answer pane border/focus
space and enforces full disabled borders without changing correct/wrong colors.

Writing shares writing.js through options.practice, preserving options.review
native behavior. Misses remain editable, an unchanged second Enter reveals,
final matches finish once, empty checks can explicitly reveal, and revised text
is rechecked. MAIN finishWriting sends the independent practice grade with
unknown=true only for an incomplete attempt. Wrong results wait for Continue.
The revealed count says N/N revealed without falsifying accepted matches.
dialog.py keeps checked events canonical across stale checkpoints and ignores
extra submissions after completion; native matcher/scoring rules are unchanged.
Grade/write/restart messages carry session IDs and late old-session requests are
ignored. Older valid saved sessions remain usable.

In-session Start over calls restart(), which clones original questions without
queued retry copies, preserves the selection/config, resets results/view/time
and replaces only that checkpoint after the new one saves. order=shuffle is
reshuffled with a changed-order fallback for >1 card; fixed orders are retained.
It makes no collection/scheduler/network requests. Cached choice positions can
be shuffled as at a fresh session. Other saved practices and history stay intact.

MAIN IO mirrors native target-mask interaction classes and access labels.
Individual open/closed masks plus seen state are optional ioMasks checkpoint
data; backend filters their indices against mask_count. Global reveal clears
individual overrides. All image/viewer nodes remain stable. Mouse or focused
Enter/Space toggles only that mask and never grades/continues. Once answers were
seen, recall controls remain usable after rehiding. Full-screen viewer moves
the same image stage. Native IO and reviewer implementations are unchanged.

## Evidence and boundaries

229 fast Python tests, full Node UI harness and tests/test_main_parity_qt.py
pass. The Qt test uses real WebEngine rendering/keyboard/mouse input and actual
MAIN controller methods through the existing synthetic-host harness. It covers
setup alignment, all four disabled borders under an adverse theme rule, wrong
MCQ text/hold, Settings restart/reshuffle, Writing miss/reveal/correct/extra Enter,
individual IO mouse/keyboard behavior, stable images and entry recovery.
Screenshots are internal scratch QA, not deliverables. No user collection,
Windows Anki/Rust scheduler or live Gemini was used; do not claim otherwise.
Existing normal/filtered/reschedule/undo boundary tests pass. No changes to
native scheduling, Gemini prompts, matching rules or custom appearance storage.

The separate screenshot's native overview “Click to reveal / hide” is absent
from Cram and Study Sounds. Study List0.6.15 was also inspected: its reveal text
is confined to its own list window and its overview script only adds Study List.
Do not disable unknown third-party add-ons or claim an exact culprit from pixels.

Build python3 build.py; handoff includes tests, exact installer and checksums.
Preserve Library identities: installer libfile_bf06728858748191a6434c01246d2905
(previous version43) and handoff libfile_b24f0c73e4b481919f9cd80a85e8b294
(previous version44); refresh metadata if continuing after this release's save.
Historical notes follow and apply only to their original versions.

# Continue Cram Studio 2.0.9

Continue this exact UI/source under package cram_studio. Each update must include the full installer and exact matching handoff. Preserve existing profile/cache/saved sessions/customizations. Study List0.6.15 and Study Sounds1.1.8 remain separate and untouched. Avoid extra guides, long tests and unnecessary confirmations.

## Current request: Space keeps flipping Flashcards

The user explicitly requires Space to reveal first, then keep flipping while rating buttons wait for an explicit vote. Scope is Flashcards only in MAIN CRAM and ANKI CRAM. Ordinary Anki, Multiple Choice, Writing and image occlusion must retain existing shortcuts.

Native: live_review.py can_flip_flashcard() requires active native review, Flashcards mode and flash/native display (not IO or an MCQ original-card fallback). The existing Space shortcut is wrapped dynamically; it calls cramNative.flip() only in that scope, otherwise delegates the original callback. No duplicate Space shortcut is created. This covers focus in Anki's bottom WebView. The existing input event filter lets the card WebView receive unmodified Flashcard Space so the DOM can prevent default button activation. Settings/photo overlays retain their guards. web/live.js flip() uses the same existing guarded ans bridge on the question side and visual class toggles on the answer side. Held DOM repeats are prevented, rating keys are untouched, and the native question/answer state is never reset when visually hiding the answer.

MAIN: Space for non-IO Flashcards is checked before generic post-grade Continue routing. S.flashSeen records first reveal separately from S.revealed's current visible side, so recall controls and 1/2 still work after flipping back. This is saved as optional flashSeen in the existing checkpoint/view, sanitized by dialog.py to accessible non-IO Flashcard indices; old snapshots infer from revealed. No practice grading or scheduling algorithm changes. After an explicit rating, configured auto-advance still applies; pressing Space to inspect cancels that timer via the existing reveal() behavior. Enter/Right/Continue remain explicit navigation.

223 quick Python tests, complete Node UI checks and tests/test_flash_space.py pass. The bounded Qt regression uses the real controller + separate real card and rating WebViews + actual native Space/1–4 QShortcuts and native reveal/rating spies. It confirms repeated flips from both focus locations, no unintended native rating/default button click, explicit 1–4 from the clue side, MCQ Space delegation, Writing spaces, and ordinary native Space after exit. MAIN persistence and normal/filtered/reschedule on/off controller tripwires pass. No real collection, Windows/Rust scheduler or live Gemini API was used. Runtime CSS, matching, Gemini generation and native scheduling/undo implementations are unchanged.

Historical handoff notes below apply to their original releases.

# Continue Cram Studio 2.0.8

Continue this exact source and UI. Keep package identity cram_studio and profile/cache/session/customization data. Deliver the full same-package installer and exact matching handoff every update. Study List0.6.15 and Study Sounds1.1.8 remain separate and untouched. Do not redesign the interface or introduce guide clutter.

## Current request: revealed ANKI CRAM mode consistency

The user's screenshots show a Flashcards answer rendered while Multiple Choice was selected, then Writing with all three answers visible but a 0 / 3 counter, and a later MCQ view with choices. Root cause: web/live.js exam() used nativeCard() when q.ready was false on the answer side; this made an MCQ view flippable. Backend automatic/manual MCQ generation and frontend ready redraws were question-side only.

web/live.js now renders an exam panel regardless of readiness/side. Answer-side loading/errors/Create choices stay visible, and late ready packets redraw its choices on the answer side too. Correct options are marked and disabled. No synthetic wrong-answer score appears when no MCQ selection was made. Flip clicks are explicitly limited to native/flash displays. Writing's shared UI uses items.length / items.length revealed only for revealed native-review views (options.review); accepted/missed/attempt data and MAIN/question-side counters are untouched.

live_review.py allows missing MCQ preparation when the native reviewer and packet both have the same question/answer side. In-progress missing choices survive the same card's reveal. Existing ready sets/regeneration still cancel on reveal, and forced replacement after reveal stays blocked so choices/pick indices do not change under an existing answer. Stale mode/card epochs and worker IDs retain their guards. Mode switching still never calls native reveal, rating, undo, queue or scheduler operations. Missing choices use the user's existing generation opt-in/key; do not silently fabricate distractors or bypass disabled preparation.

219 Python tests, the complete Node UI suite and real Qt tests/test_mode_transitions.py pass. The new regression fails against the old source. Real controller/WebEngine checks cover three-cloze Flashcards reveal -> uncached MCQ -> late choices -> Writing; repeated cached switches; an actual partial Writing attempt -> Flashcards reveal -> MCQ -> restored Writing, with accepted=[0] yet 3 / 3 revealed. Native callback spies confirm explicit rating only. No real Anki collection, Windows/Rust scheduler or live Gemini API was used. QA images in scratch are internal and not shipped. All package CSS, appearance/pointer/matching/storage/MAIN implementations stay unchanged except the app version label.

Historical handoff notes below apply to their original releases.

# Continue Cram Studio 2.0.7

Continue this exact source; do not redesign/reinterpret the UI. Deliver a full same-package installer plus the exact matching source handoff each update. Preserve cram_studio/profile/cache/session identity, customization and all prior features. Study List0.6.15 and Study Sounds1.1.8 remain separate/unchanged. User dislikes unnecessary confirmation, long tests and in-product guide clutter.

## Current request: clicks flip, dragging selects

The user now explicitly wants flashcard clicks on or near letters to FLIP, including rapid clicks, with no whole-word/paragraph blue selection. A held mouse drag should select text for normal copy/paste. This supersedes the older1.10.11 policy that stationary text clicks should not flip. Scope is Flashcards in MAIN CRAM and ANKI CRAM; the attached image happened to show Writing, which is not turned into a clickable flip surface.

web/appearance.js flashcardPointer retains glyph/padding hit tests only to decide when native selection may start, not whether a stationary click flips. It tracks primary-button movement (>5px), mouseup and blur. A click clears a range intersecting that card and flips; a drag release is suppressed. Non-text/repeated presses cancel default word/paragraph selection. If such a prevented press turns into a drag, caretPositionFromPoint/caretRangeFromPoint plus native Selection.setBaseAndExtent (or collapse/extend) restore a real range. Ordinary first-press text drags remain browser-native. Unrelated ranges, controls, scrollbars and right-click remain outside the flip gesture; clipboard handling is not replaced.

web/live.js restricts the [data-blank] click handler to display===exam. Previously it swallowed direct clicks on revealed flashcard cloze words before the flip handler. This was caught by the real mouse test and fixed. Native question text clicks still call the existing reveal path once; answer-side text/surface flips are visual and never rate/advance. All Python implementation files, styling, note/matcher/cache/generation/session code remain unchanged from2.0.6; app.js changes only its version label. No new guide row.

## Checks and delivery

Complete Node suite and JS syntax checks pass. Optional tests/test_flashcard_pointer.py uses actual Qt mouse presses/moves/releases, key Ctrl+C and clipboard content across four MAIN/ANKI x Basic/Cloze scenes. Text clicks flip, held drags select, copying preserves selection text, drag release does not flip, rapid/Qt double-clicks do not select, and no automatic rating/practice grade fires. Synthetic notes/native callbacks only. No Windows Anki/Rust scheduler integration, user collection or Gemini call; private runtime dependencies are not shipped.

Build with python3 build.py. Deliver BOTH **dist/Cram-Studio-v2.0.7.ankiaddon** and **dist/Cram-Studio-Handoff-v2.0.7.zip**, containing exact source, full installer, tests and checksums. Historical release-specific notes follow.

# Continue Cram Studio 2.0.6

Continue the exact source. Deliver the full same-package installer plus matching source handoff at every update. Preserve cram_studio/profile/cache/session identity and all earlier UI; do not reinterpret/rebuild the project. Study List0.6.15 and Study Sounds1.1.8 are separate and untouched. User dislikes long tests and unsolicited guides/confirmation.

## Current fix: MCQ IEEE/ITU blank formatting

The screenshots were MULTIPLE CHOICE, not Writing. Filled long organization names were inline-block boxes with white-space:pre-wrap. Raw pasted line breaks stayed in the term; an inline-block's last-line baseline put the surrounding bullet beside the second line, and the active highlight became a tall box.

web/appearance.js adds blankText/fillBlank, used only when filling MCQ question blanks. For the authored correct option, it reads existing sanitized answer_html using a detached DOM walk: collapses soft text-node whitespace; retains explicit BR/block/list/pre structure and list markers/start/value/nesting. Generated plain options collapse unmarked soft lines while explicit numbered/bulleted enumerations retain lines. All results are assigned via textContent; original slot.answer/choices/cache strings are never rewritten. The existing choiceText case adaptation still applies to distractors. Choice buttons are unchanged.

web/app.js and web/live.js call that helper for selected/revealed MCQ blanks and clear the multiline display class on empty placeholders. Shared appearance.css scopes normal inline flow to filled MCQ blanks, excluding .write-card. Source-intended multiline answers get cram-blank-lines and pre-wrap. No Python implementation change, scheduler/grader/generation/storage change or cache migration. Existing snapshots can render through their stored answer_html; no regeneration is required. All2.0.5 features remain.

## Verification and delivery

Full Node UI suite and JS syntax checks pass. Optional tests/test_mcq_blank_layout.py runs four bounded Qt WebEngine scenes (MAIN/ANKI x1360/540px) with synthetic IEEE/ITU and explicit-BR source terms, exercising actual choice selection, first-line bullet alignment, text/whitespace style and native answer remount. Fails with released2.0.5 CSS, passes with corrected CSS; wide/narrow screenshots inspected. Private dependencies/screenshots are not packaged. All Python implementation files stay byte-identical to2.0.5, whose215 quick backend checks passed. No real user collection, Windows/Rust scheduler integration or Gemini request.

Build with python3 build.py. Deliver BOTH **dist/Cram-Studio-v2.0.6.ankiaddon** and **dist/Cram-Studio-Handoff-v2.0.6.zip**, containing exact source/installer/tests/checksums. Historical version-specific notes follow.

# Continue Cram Studio 2.0.5

Continue the exact source in this handoff. Do not recreate the UI from prose. The user expects a full installer AND its exact matching source handoff at every update, dislikes long tests/confirmations and in-card tutorial clutter. Preserve package cram_studio/profile/cache/session identity. Study List0.6.15 and Study Sounds1.1.8 remain separate and unchanged.

## Current cumulative scope

The user repeated an omitted request: ONLY ANKI CRAM must allow switching Flashcards/Writing/Multiple Choice from a small expanding Settings icon in the same panel. They also required double-click image enlargement with X, a shorter Writing input, proper multiline Up/Down caret navigation, two-item enumeration handling (Ethernet sublayers → LLC and MAC), a redundant-acronym match (frame check sequence vs frame check sequence (FCS)) and visible feedback for unaccepted/incomplete submissions. All are included here. MAIN has no new in-session mode switch or image viewer; shared Writing input/matching/grouping fixes apply to both renderers.

## Implementation

live_review.py factors interface_packet from native make_packet and adds switch_mode. It reads only the current native reviewer card, verifies cid/fingerprint, persists live_mode in the existing profile store, retains per-mode question/Writing attempt snapshots for that card, rotates the presentation epoch, cancels old worker ids, preserves native question/answer side and sends cramNative.switchMode. It never calls native Show Answer/Study Now/rating/queue/reset callbacks for a switch. New native question/undo clears per-mode state. An initial Flashcards-mode switch honors saved live_generate opt-in/opt-out rather than inheriting the disabled Flashcards checkbox. Waiting Writing cache readiness initializes/emits state immediately. Native rating/interval/undo ownership and filtered rescheduling remain unchanged.

web/live.js caches picks/active blank/Writing draft+target/scroll per mode within one card, redraws only its own presentation and rejects stale/different-card switches. The header uses a small sliders Settings icon with three mode choices. Equal side tracks retain centered deck text. Native original-card wrappers are cleaned up before redrawing. Generic double-click photos use a scoped fixed overlay with contained image fitting, zoom, X/Escape; IO reuses its existing mask-preserving viewer. Native redraw clears a detached viewer. Overlay focus flags plus the Qt shortcut guard prevent unmodified rating keys behind menus/photos; modifier shortcuts remain native. Image clicks do not flip flashcards. No original photo is rewritten or exported.

web/writing.js/css use a one-row, auto-growing textarea capped at160px. Plain Up/Down are native caret navigation; Alt+Up/Down retain blank selection. The Qt input guard accepts bare Up/Down before native window shortcuts. Incomplete checks now share red feedback styling, with a distinct incomplete message; successful checks remain quiet. The previous scroll-anchor fix remains. Existing settings/appearance/geometry are reused; no guide row is added.

writing.py answer_variants recognizes only a source suffix/prefix parenthetical abbreviation whose uppercase initials match a multiword expansion (optionally ignoring common connective words). It preserves authored text and numeric/qualifier/negation safeguards and composes with the existing local matcher. Gemini receives explicit question-grounded two-item grouping instructions. plan_key policy is Basic2/cloze-group-2 so stale single/list classifications are prepared again on fresh questions. No per-answer AI call, general semantic grader or universal model correctness guarantee. Ambiguous prose without successful enabled preparation still uses its whole-answer fallback. Existing saved MAIN plans stay intact.

## Checks and delivery

215 quick Python tests and the complete Node suite pass. Real offscreen Qt WebEngine tests include eight Writing layouts, four customizer scenes, six format scenes, two combined-cloze scenes, five Enter flows, plus a real-controller mode/menu/photo/caret flow: preserve card/side/draft/picks; accept Shift+Enter; actual Up/Down move through 40 text lines despite real Qt shortcuts; native rating key blocked in menus/photo and fires only explicitly after reveal. Four image-first scroll scenes pass. Representative menu/photo screenshots inspected. No Windows Anki/Rust integration, user collection or live Gemini call. Dependencies/screenshots are not shipped.

Rebuild using python3 build.py. Deliver BOTH **dist/Cram-Studio-v2.0.5.ankiaddon** and **dist/Cram-Studio-Handoff-v2.0.5.zip**, containing the full exact installer/source/tests/checksums. Historical version-specific notes follow.

# Continue Cram Studio 2.0.4

Continue this exact source; do not recreate the UI. Deliver the complete same-package installer and matching source handoff on every update. Preserve cram_studio/profile/cache/session identity and the separate Study List/Study Sounds add-ons. The user dislikes long tests and unnecessary guide text or confirmations.

## Current fix: Writing scroll perspective

The user reported an image at the start of a long question, with blanks farther down: entering/revealing an answer left the panel at the image, requiring manual scrolling to see the filled blank.

`web/writing.js` now retains a presentation-only view.anchor for the matched/selected item. A correct response prefers the just-answered active item, otherwise the first newly accepted item; it does not overwrite that anchor with the next unanswered target. showTarget uses the existing question-pane-only showInPane helper, immediately and after a requestAnimationFrame so restored card sizing/text zoom have applied. Native mount reuses its existing writeView for the same card/epoch and restores the anchor on the revealed face. Explicit reveal uses the anchor/current target; images finishing loading recheck it. Detached components do not scroll. New native cards retain their existing writeView reset behavior.

Input focus and MAIN's final Check-answer-button focus use preventScroll:true. Partial inputs retain focus; final native checks still send ans once and await the user's native rating. No scheduler/controller/matcher/generation/storage changes. This is a scroll fix, not an answer-matching or layout redesign. Existing Ignore extra text behavior remains.

205 quick Python tests and the full Node UI suite pass. `tests/test_writing_scroll.py` is a separate optional bounded real Qt WebEngine regression: four MAIN/ANKI scenes at 1360x900/normal text and 900x680/150% text. Synthetic image-first questions exercise three partial/final matches, keyboard focus, question-pane scrolling, no outer-page jump and native answer DOM replacement. It fails with released 2.0.3 writing.js and passes with the correction. Private Qt dependencies and QA screenshots are not shipped. No live Anki/Rust scheduler/user collection or Gemini call.

Build with `python3 build.py`. Deliver BOTH **dist/Cram-Studio-v2.0.4.ankiaddon** and **dist/Cram-Studio-Handoff-v2.0.4.zip**, including exact installer/source/tests/checksums. Historical notes follow.

# Continue Cram Studio 2.0.3

Latest user requests: combined enumeration inside a single c1 block must become separate Writing targets, including arbitrary connecting wording, without manual setup. User also showed January 1 1978 wrongly rejected for January 1, 1978 and challenged narrow hardcoded examples. Preserve all prior UI and 2.0.1 keyboard behavior, 2.0.2 removal of green Matched feedback, saved progress and scheduling boundaries. Do not re-create the add-on from this description.

## Current implementation

`writing.py` builds a Basic-style source plan for EACH original active cloze slot, then composes their templates/items back into the original clue. cloze_sources supplies source/context; cloze_plan remaps local item indices to global data-write-item IDs, retains original cloze_slot/cloze_member metadata, rich source runs, exact context and whole-block groups. Separate and combined blocks coexist. Non-active cN content stays visible. MAX_ITEMS cap falls back to complete original blocks. Old serialized plans remain valid (version1); existing MAIN Resume does not rebuild/reset them.

`attach` prepares every component, uses cached literal ranges or offline explicit-list parsing, deduplicates identical missing jobs, and exposes a question only when all component plans are ready. Cloze grouping has a separate cloze-group-1 source/context cache namespace; existing Basic and MCQ cache keys are retained. Unknown/disabled/offline/invalid generation falls back to complete original cloze blocks through the existing whole=True path. Actual Anki card identity/order/ordinal is unchanged; multiple Writing targets are NOT new scheduled cards.

`Gemini.group_answers` now includes required connectors array in its response schema. Model reads QUESTION and exact TEXT (Basic answer OR one active cloze block). It must choose genuine independent answer items, preserve compound/single statements/dates and copy all strings exactly. It explicitly classifies arbitrary joining/framing wording from source, not a hardcoded connector list. Returned connectors are source-only text fragments; numeric fragments/invalid metadata are rejected. validate_spans accounts for the rest of the source using annotated connectors and existing harmless layout. No source HTML is generated by the model. Semantic classification still depends on Gemini: source-grounding validates representation/coverage, not universal factual correctness. Do not claim that every connector/list decision is independently proven.

`item_pattern` now lexes words, decimal/number tokens and punctuation. Prose comma/space separators are tolerant across the whole answer, combined with existing n/ñ, quotes, casing, hyphen/space and plural forms. Structural punctuation in references/arithmetic/code stays literal. Numeric candidate guards reject attached subsection/decimal/sign extensions, additional unmatched numeric content even in ignore-extra mode, and attached code/operator extensions such as C++ for C. Exact original plan/group text can satisfy all remaining members of that group. Group connector annotations are reused to accept source phrasing in strict typed batches without a global phrase whitelist. No per-keystroke/per-answer network call, general edit-distance judge or unrestricted synonym reasoning was added.

Only runtime writing.py/gemini.py, version labels and docs changed from 2.0.2. UI layout/styles, Enter/reveal/rating, native reviewer/controller, filters/sorting/choices and storage implementations remain the existing source. Scheduling is still Anki-owned in ANKI CRAM and untouched by MAIN. Study List 0.6.15 and Study Sounds1.1.8 remain separate and unchanged.

## Evidence and packaging

205 Python checks and the full Node UI suite passed. Eleven new Python cases cover token/date combinations, arbitrary annotated connector transport/schema/source validation, combined/mixed/repeated/offline clozes, independent whole-answer fallback, partial disk Resume, native combined grouping and date checks without scheduling access. Earlier boundary/undo/filtered tests pass. No live Gemini call or user collection.

Optional tests/test_writing_layout.py passed with private PyQt6-WebEngine: eight layout scenes, four previews, six raw-whitespace/explicit-BR scenes, two actual composed-cloze scenes, focus/shortcut handling and five Enter/reveal/rating keyboard flows with synthetic callbacks. The combined scenes use actual Python-generated plans; partial banana fills only its target, connectors/other cN remain visible, full reveal retains inline sentence/bold text. Formatting checks account for source runs across multiple placeholders with one item ID. This is not live Windows Anki/Rust integration.

Build with python3 build.py. Deliver BOTH full installer **dist/Cram-Studio-v2.0.3.ankiaddon** and exact matching **dist/Cram-Studio-Handoff-v2.0.3.zip**, which includes installer/source/tests/checksums. Preserve package cram_studio/profile/cache/session identity. Historical notes below apply only where not superseded.

# Continue Cram Studio 2.0.2

Latest user asks to remove the green Matched banner beneath the Writing input and retain the red warning only on wrong answers. Changes are presentation-only: writing.js omits success/completion/incomplete feedback text and no longer applies write-correct; writing.css removes its success surface. Wrong text/input/error styles remain, and the reserved empty feedback height prevents shifting the input. Customizer Writing controls/preview no longer fabricate success feedback; correct colors remain for MCQ and palette values are preserved. Existing input/check/reveal/rating/matching behavior is unchanged.

Verified with full Node suite, including partial correct feedback absence, wrong warning, both study paths and customizer roles, plus 29 Writing backend checks. Syntax/source/archive checks pass. No long tests, user collection or live AI. Runtime backend/scheduling code matches 2.0.1. Full package identity cram_studio, complete installer **dist/Cram-Studio-v2.0.2.ankiaddon** plus matching **dist/Cram-Studio-Handoff-v2.0.2.zip**. Always deliver BOTH and preserve profile data/UI/source. Study List and Study Sounds untouched.

Historical handoff follows; latest version-specific instructions supersede older success-color controls and feedback descriptions.

# Continue Cram Studio 2.0.1

Continue this exact source and existing package `cram_studio`; do not recreate the UI from descriptions. User supplied several cumulative Writing bug reports while work was active. This release includes all of them. Latest user instruction overrides older memory of strict singular/plural grading: explicitly accept banana/bananas, n/ñ, outer quotation marks and hyphen/space presentation. Preserve exact original display text.

## Current changes and final agreed flow

- `writing.py`: normalized matching keys only; outer straight/curly quote removal, letter-separating hyphens to spaces, NFC/NFKC ñ to n. Cached regular noun forms + common irregular pairs. Both individual and batch matches use these forms. No unrestricted edit-distance/synonym judge or per-answer AI. Protected numeric candidate boundaries reject Section4(c)(4) for Section4 even with ignore_extra. Numbers/operators retain meaning. The optional noise setting still accepts the previously requested banana/noise/mango/noise/lemon case. Cache/source-plan keys and authored strings are unchanged.
- `web/writing.js` + native `web/live.js` option `review:true`: Enter checks. A final correct match automatically calls the existing native reveal callback once, releases input focus, and waits for the USER's Anki rating. A correct partial enumeration continues writing. WRONG/INCOMPLETE remains editable; a second Enter with no edit explicitly reveals. Editing or changing the target resets that reveal choice and Enter rechecks. Empty Enter explicitly reveals. Space remains a typed space. Native wrong submissions do NOT automatically reveal; the user corrected that proposal to allow typo revision. Button label changes Check answer / Reveal answer, without adding a new row or tutorial guide. MAIN remains explicit independent scoring and does not auto-grade/reveal through this native option.
- `web/writing.css`: filled placeholders become inline; CLOZE answer fragments collapse raw HTML whitespace, avoiding the reported existing/logic and official/proceedings vertical split. Explicit BR/list/paragraph structure retained. Basic source whitespace/list layout not flattened. Existing native check button has a stable minimum width so its label change does not shift the input. No card dimension/palette reset. Live-start Writing label now describes Enter/check/rating.

## Validation and packaging

194 Python tests and full Node DOM suite passed. `tests/test_writing.py` covers screenshots, Unicode, regular/irregular plurals, numeric reference/decimal/sign guards, distinct concept/negation guards, unchanged source/plans and existing persistence/scheduling cases. `tests/test_ui.cjs` now tests native final-match reveal, editable miss, no-edit second Enter reveal, revision recheck, empty skip, partial enumeration, held keys/stale packets and original rating-button nodes/callback separation. Only native `ans` is sent automatically after a successful explicit check; NEVER ease/grade/queue/scheduling commands.

Optional `tests/test_writing_layout.py` runs with separately installed PyQt6-WebEngine. It passed eight real-renderer Writing scenes, four customization scenes, six inline/raw-whitespace vs explicit-BR format scenes, actual Qt focus/E shortcut checks, and five keyboard flows connected to the real Python matcher with synthetic reveal/rating callbacks. Real key presses verify that a correct final check reveals once, wrong input remains editable, a second Enter can reveal, a corrected typo is rechecked, Space is typed, and rating happens only on the explicit native key afterward. No Windows/aqt/Rust/user collection or live Gemini call. Private Qt dependencies/screenshots are not shipped.

Rebuild using `python3 build.py`. Full installer **dist/Cram-Studio-v2.0.1.ankiaddon** and matching source **dist/Cram-Studio-Handoff-v2.0.1.zip**, including exact installer/checksums/tests. Deliver BOTH each update. Preserve package/profile/session/cache identity. Study List 0.6.15 and confirmed Study Sounds1.1.8 untouched. No new guide PDF in this update.

Historical handoff follows. Earlier 2.0.0 instructions requiring exact plurals or a second Enter on a correct final answer are superseded.

# Continue Cram Studio 2.0.0

## Current work: Writing mode for MAIN CRAM and ANKI CRAM

Continue the exact source in this handoff. Do not rebuild the UI from these descriptions. The user authorized 2.0 Writing after extensive existing feature work, dislikes unnecessary confirmation/long tests, and requires the complete same-package installer PLUS matching source handoff with each update. Existing package identity is `cram_studio`; preserve its profile data, sessions, cache and all earlier UI. Study List 0.6.15 and Study Sounds 1.1.8 are separate and unchanged.

Latest clarification: the user's noisy-input example (`banana, waaaa, mango, jdjd, lemon`) was a SUGGESTION to allow extra text, not just a question about a bug. Both setups now expose optional **Ignore extra text**, default false; enabling matches complete expected items anywhere. Strict mode remains. This option is stored in profile preferences and MAIN session config. Do not silently remove this requested behavior or treat it as rejected.

### Implementation map

- New `writing.py`: sanitized source HTML/text mapping; offline explicit-list/cloze parsing; source-range grouping/cache; exact item/layout matching; strict or ignore-extra behavior; replayed attempts and first-miss scoring; asynchronous grouping batches (first1, then5). No collection writes. Casefold/NFKC, whitespace normalization, whole-word guards and whole-compound matching. Missing plural suffix is wrong, never a new item.
- `gemini.py:group_answers`: existing Gemini request transport/schema; reads question AND exact answer; list only for true independent enumeration, otherwise single complete statement. Copies literal source substrings, converts them to validated ranges. No manual enumeration setup. Source prefix/punctuation/numbering/and/HTML stay in display. Invalid/quota/offline fallback is full original answer, never invented items. Cache keys have a separate `writing:` namespace; MCQ `PROMPT_VERSION=4` unchanged.
- `content.py` compiles mode `write` (image occlusion stays `flash`); active cN only; grade dispatches to Writing. `session.py` restores Writing snapshots; existing retry/score behavior retained.
- MAIN `dialog.py` uses existing generation/task framework, saves partial event/draft/target in session view and recomputes progress on Resume. `app.js` adds Writing setup and optional extra-text setting; final match never auto-checks. Reveal does not grade; explicit Check does. Failure unlocks input for retry. Existing file storage model preserved; no migration/reset.
- Native `live_review.py` compiles the actual native card in Writing mode and tracks server-owned events; no queue or scheduling APIs. Async results guarded by worker/epoch/side/cancel. Source edits invalidate typed state. `live_start.py` adds Writing radio and extra-text checkbox. A scoped Qt ShortcutOverride guard allows normal text/spaces/Enter while the Writing textarea has focus; it never intercepts Ctrl/Alt/Meta combinations. Native rating/reveal/undo/interval callbacks stay native. `live.js` sends only custom typing/focus events until explicit native reveal.
- Shared `web/writing.js/css`: one input, source-position blanks, stable nodes and local feedback, Enter/Shift+Enter/Up/Down/Esc, no own scheduler/grade calls. Input retains draft; completed/revealed answer is read-only. `appearance.js` aliases `write` to existing `exam` palette/geometry/bottom controls. `customize.js/customize-preview.js` adds Writing selection and actual shared component, input/feedback/answer color targets and size save/cancel. Writing SHARES MCQ question-card size/colors/layout by design; flashcard size separate. Do not introduce an incompatible profile schema or reset existing customization.

### Matching and limits

The source determines whole items, never leftover character counts. Basic numerical/bulleted lists need no AI. Ambiguous prose is grouped once with Gemini; full statement fallback is always possible. `NO, it depends on the organization` stays one item; `research and development` stays a compound. One input accepts multiple/all expected items with commas, bullets, numbering, line breaks, omitted “and” and other harmless separators. Strict mode accounts for substantive extra words; ignore-extra deliberately accepts unknown content around full matches. No per-Enter online semantic judge or unlimited paraphrase parser was implemented. Do not claim one exists. Original source markup is retained using placeholder pieces across rich-text runs. Partial recognized items fill their source positions; unknown remaining targets stay blank. Cloze targets come only from actual current cN slots.

### Verification and boundaries

190 Python tests and entire Node suite passed. `tests/test_writing.py` includes grouping/schema/ranges, all discussed source cases, flexible input/noise, cache, retries, no-auto-grade, partial disk Resume and native filtered/on-off/edit/stale/cancel/failure boundaries. Node covers MAIN/native focus interaction, stable input/panel nodes, error retry, manual check/reveal, customization controls and real locator targets. Existing scheduling/source-write tripwires still pass. `SCHEDULING-AUDIT.md` records the latest evidence and older audit.

Optional `tests/test_writing_layout.py` ran directly with privately installed PyQt6 6.7.1 + Qt6/WebEngine6.7.3. It does not import Qt during ordinary unittest discovery. Eight real-renderer Writing scenes plus four customization scenes, bounded widths/containment/errors, and real Qt E-shortcut/input focus checks passed. Temporary screenshots/runtime dependencies are not shipped. Run it only if PyQt6-WebEngine is separately available. There is no actual Anki/aqt/Rust or Windows/user-collection validation, no live Gemini request, and no claim that tests prove model interpretation in all subjects.

Build from this folder with `python3 build.py`; allowlist includes all Writing files and optional renderer test. Installer `dist/Cram-Studio-v2.0.0.ankiaddon`, handoff `dist/Cram-Studio-Handoff-v2.0.0.zip`. Handoff includes byte-identical installer and CHECKSUMS.json. Do not overwrite old release names. Installation updates existing package; no deletion required. Existing PDF guide is still version1.10.11 and is not an updated2.0 guide. Study Sounds observes MAIN result grades, so no Cram audio hooks were added.

## Historical handoff notes follow

# Continue Cram Studio 1.10.14

## Current update: do not reveal the answer by unique capitalization

User screenshot has correct OBJECT CLASS TESTING in capitals, with distractors in sentence case. Shared web/appearance.js choiceText(answer,option) now applies answer casing to visible options and picked blank text in app.js/live.js. Covers ALL CAPS, lowercase, ordinary title and sentence case; preserves numbered/newline layout, mixed-case answer identifiers, and acronyms/identifiers inside title/sentence patterns. Correct answer text remains unchanged. Use the shared helper in BOTH paths; do not mutate slot.choices/slot.answer, cache, picked indices or source notes just to format the screen.

This is display-only and works for old cached choices and restored MAIN snapshots; no generation or progress reset. Cache policy remains4 and Gemini code is unchanged from1.10.13 (one correct + exactly3 wrong, broader-related fallback, no deliberate no-choices result). No CSS/layout/color/size, flashcard behavior, native scheduling/controller/ratings/interval/undo, session/storage changes. Current customizer samples already have uniformly cased options. New pure/MAIN-resume/native DOM tests assert case labels, filled blanks, preserved question/options/indices and no native reveal/rating; entire Node suite passes. 165 Python backend checks pass. No real Windows renderer, user collection or AI call.

Full installer dist/Cram-Studio-v1.10.14.ankiaddon plus matching dist/Cram-Studio-Handoff-v1.10.14.zip. Always deliver both. User also requested reveal audio removal: that is implemented in SEPARATE Study Sounds1.1.8, including old profiles. Do not add sound playback to Cram or change the working WASAPI engine. Study List unchanged. Install the two corresponding add-on updates and restart Anki.

## Previous release history follows

# Continue Cram Studio 1.10.13

## Current correction: every MCQ requires one correct plus three wrong choices

User explicitly rejected 1.10.12's deliberately empty/no-choices path. Their intended fallback was already stated: prefer real sibling types in the question's classification when applicable; otherwise use real related concepts wrong under the question. Same-category relevance must never be a requirement for supplying choices. Do not reintroduce refusal, skipping or flashcard conversion solely because too few narrow siblings exist.

gemini.py now requires EXACTLY THREE wrong options for EVERY job, explicitly broadening from siblings to the question topic and then surrounding subject. Removed the permission to return wrong:[] and its special AIError recommending a revised clue/flashcards. responseSchema wrong minItems=maxItems=3 again. Real-term, distinctness, answer-alias checks and per-blank context remain. Ordinary malformed API output or connection/quota failures still error instead of becoming valid cache entries. No additional retry/API pass or model change; do not promise the network/model can never fail.

PROMPT_VERSION remains 4 on purpose: valid already-generated sets have the same value format/meaning and are reused. No forced regeneration or progress reset. Changed runtime files only gemini.py, manifest/README and the MAIN displayed version in app.js; content.py, all UI/CSS/interactions, storage/session, native scheduler/controller/rating/undo and generation call sites match 1.10.12. Both MAIN/ANKI/current/deck generation use the corrected contract. Study List and Study Sounds remain unchanged.

165 quick Python tests pass, including required three-option schema, broader related-term fallback contract, absence of deliberate empty-array instruction/refusal, invalid batch preservation, synonym checks and all existing native/filtered scheduling and saved progress checks. No real Gemini request, semantic quality measurement or user collection. Package complete Cram-Studio-v1.10.13.ankiaddon plus matching Cram-Studio-Handoff-v1.10.13.zip; deliver BOTH. Install over Cram Studio and restart Anki. Prior refusal notes below are superseded history.

## Previous release history follows

# Continue Cram Studio 1.10.12

## Current update: real sibling distractors and synonym exclusion

User showed partition testing competing with equivalence partitioning. They want real confusing sibling terms from the same recognized classification when applicable, not synonyms or invented vocabulary. Otherwise nearby real concepts are acceptable only if wrong under the actual question. Preserve all previous UI and scheduling behavior; do not rebuild from descriptions.

Runtime changes are limited to content.py, gemini.py, version metadata, the MAIN displayed version and README. valid_distractors(answer,wrong,aliases=()) excludes the contextual answer_aliases returned by the same structured Gemini request. The result/cache format remains three strings; aliases are not displayed or persisted. A deliberately tiny reviewed choice_identity guard blocks partition testing / equivalence partitioning in both directions and as duplicate wrong options, from ISTQB Glossary 3.7. Do not confuse equivalence partition (a data class) with equivalence partitioning (the technique), or merge related concepts indiscriminately. Manual choices/cache loads receive the known-pair guard without any new online request.

Prompt prioritizes REAL SIBLING TYPES/stages/methods in the stem's classification; when that is inappropriate or insufficient, use real close related concepts wrong for the exact question. Exclude accepted aliases, answer paraphrases, fabricated taxonomies and broader/narrower terms that could be right. Full per-blank target/context is retained. The structured schema requires answer_aliases and permits wrong:[] when no safe three can be identified. An empty/invalid set raises AIError; no part of that batch is saved, and earlier saved batches survive. Existing Retry/flashcard fallback paths remain. No extra API call, automatic retry, model/temperature/timeout change or reference lookup during study.

PROMPT_VERSION=4. Fresh preparations use new cache keys, while old entries remain. Saved MAIN snapshots/options/progress are deliberately not rebuilt. Tell the user to use current Regenerate choices or Tools > Regenerate deck choices > Preview > Regenerate to change existing options. MAIN/ANKI/current/deck generation share the new policy. General synonyms, real-term existence and semantic correctness still depend on Gemini; do not claim comprehensive factual validation or measured live improvement. No actual Gemini calls, user key or collection were used.

165 Python tests passed (<1 second): six new known/contextual alias, cache, schema, single-call and unsafe-batch tests, plus existing native/filtered scheduling, undo, saved progress, multiline and generation checks. Contract tests do not prove that a live model always generates real or difficult choices. All UI runtime files match 1.10.11 except app.js's version label. No CSS, pointer, layout, zoom, size/color/image, native controller/queue/rating/undo or storage/session changes. Study List and user-confirmed Study Sounds1.1.7 remain unchanged.

Full same-package release: dist/Cram-Studio-v1.10.12.ankiaddon and dist/Cram-Studio-Handoff-v1.10.12.zip. Preserve cram_studio/profile data. Always deliver BOTH complete installer and source handoff. Install over existing Cram Studio and restart Anki. The separate PDF guide remains for 1.10.11; this update changes generation only, not the interface.

## Previous release history follows

# Continue Cram Studio 1.10.11

## Current update: intentional flashcard text selection vs empty-space flipping

User clarified that rapid cursor flipping causes unwanted text SELECTION (blue highlight), not automatic clipboard copying. Keep flashcard words selectable/copyable on purpose. Empty space should flip without selecting; image occlusion should never select. Apply MAIN/ANKI/preview without new controls or UI changes.

Shared appearance.flashcardPointer(root,selector) tracks primary mousedown origin and mouse movement. A press on actual text does not flip; dragging from text to background also cannot flip on release. Empty-surface presses prevent browser selection and can clear only a noncollapsed selection intersecting that card. A pointer drag on the background is not a click-to-flip. Right/middle presses, form/contenteditable/link/button/canvas/SVG controls and detected scrollbars keep native behavior. No keyboard/copy/cut/clipboard handlers. Space/arrows/explicit reveal buttons still use their existing paths. Native card reveal delegates ans once; answer-side flipping remains visual, with untouched ratings/intervals/edit/browse/undo.

Hit test: require the target to be inside a text content root, then try caretPositionFromPoint or older caretRangeFromPoint. Check adjacent non-whitespace characters using Range.getClientRects to distinguish letters from the large content element's empty padding. Older fallback walks text nodes and uses text-line rectangles. If geometry APIs fail, favor copyability within text roots. Check only on presses/clicks, not mouse-hover or animation frames. Track drag intent until the next press/blur so a selection drag cannot become a background reveal. Noncollapsed selections outside the card are not cleared or used to block another card's flip. Native fallback and compiled flashcards share this behavior.

Removed blanket ct-blank selection blocking from FLASHCARDS only. CSS marks empty card shells non-selectable and text content/descendants selectable, including revealed cloze answer spans. Empty placeholder spans, images and MCQ blank controls retain their guards. MAIN IO .io-card/#viewer and native .cl-io whole frames (including captions/tools) suppress selection/drag, while buttons retain normal pointer focus and SVG masks retain their existing programmatic focus. Shared studyScrollbar detects pointer positions in a real scrolling element's scrollbar strip, so the new guards cannot cancel thumb dragging or flip while using a scrollbar. Existing image DOM/zoom/viewer/mask state remains.

Changed runtime files only shared appearance.js/css, app.js/live.js binding/click checks, customize-preview.js binding/click check, manifest/docs/version label. All Python runtime, AI prompt/context/cache policy, generation, storage/session, scheduler/queue/rating/undo, card content and customizer settings implementations are byte-identical to1.10.10. Study List and user-confirmed working Study Sounds1.1.7 are untouched. Retain all previous features.

159 Python tests and full Node DOM suite pass. Added bounded pointer scenarios for char-vs-padding geometry, current/older caret and text-line fallbacks, select/drag released on background, rapid stable flips, copyable revealed clozes, ranges inside vs outside a card, right-click/forms/links, scrollbar gestures, IO caption/fullscreen selection protection, native fallback/compiled flip, no rating/extra reveal and unchanged keys/native button identity. Existing selection/MCQ/pager/formatting/AI/scheduling tests pass. Tests use simulated ranges/geometry; there is no live Qt/Chromium/Anki renderer here. Do not call them actual blue-selection/pixel QA. No long tests or live AI/collection.

Full same-package release: dist/Cram-Studio-v1.10.11.ankiaddon and dist/Cram-Studio-Handoff-v1.10.11.zip. Preserve cram_studio/profile data and return BOTH complete installer and handoff. Install over Cram Studio and restart Anki. No source rebuild from descriptions.

## Prior history follows

# Continue Cram Studio 1.10.10

## Current update: formatting correction and stronger contextual choices

User screenshots show only the header bold in Anki's editor, but Cram renders most of the sentence bold. Found a concrete shared sanitizer defect in content.SafeHTML: it retained <b>/<strong> and bold style declarations, but discarded explicit normal/400 overrides. Such overrides inside a surrounding bold tag are common in Anki/pasted field markup. Their removal can reproduce this exact class of display mismatch. User supplied screenshots, not raw field HTML; do not claim to have inspected their original HTML or measured Windows rendering.

Added safe_font_weight() and used it for allowed style output. Explicit normal→400, bold→700, weights100–1000 in hundred increments and bolder/lighter are retained. Parse only exact font-weight declarations; last valid declaration wins except earlier important cannot be replaced by a later non-important. !important priority is retained. Reject URLs, expressions, variables, extra values and unrelated properties; other existing sanitization remains. Re-cleaning is idempotent. No global font reset or stripping of deliberate header/body bold.

Production changes: content.py formatting/AI job context/cache revision and gemini.py prompt, plus version label/metadata/docs. No CSS, pager, zoom/type, customizer, native scheduler/queue/undo, generation scheduling, storage or practice-session implementation changes. Retain all1.10.9 behavior. Source notes are untouched. Old saved MAIN snapshots are intentionally not recompiled/changed; already discarded formatting cannot be reconstructed from the snapshot. New launches/native renders compile correctly.

User further requested harder choices grounded in the actual question, showing a sex-hormone cloze whose insulin/thyroxine/growth-hormone alternatives were easy category outliers. The previous prompt DID already request full-question context; do not falsely claim it ignored/sent no question before. Strengthened the narrow-category/difficulty rules, explicit-category constraints, nearby mechanism/stage/role/structure misconceptions, common confusions, matching grammar/length/specificity, a final category-outlier/alternate-valid-answer screen and accuracy over artificial difficulty. This is an instruction-level quality improvement, not a deterministic guarantee of semantic quality. No second API pass, model/endpoint/temperature/schema change or longer output contract.

New question_for_blank() creates an AI-only text stem. It substitutes just the target compiled data-blank span with [TARGET BLANK N] and fills the other current-question slots with their correct answers, using escaped text and the existing safe plain-text serializer. Job question_for_this_blank is supplied alongside original clue/answer/blank/other_blanks; no answer is newly shown in the actual UI and the question's stored clue is unchanged. Both MAIN and native/current/deck regeneration use prepare_choices and receive this context. Basic questions use their full original stem.

PROMPT_VERSION is now3. Fresh preparation treats revision2 sets as old and prepares new keys, retaining old entries on disk rather than deleting or clearing cache. Newly generated revision3 keys are reused. Existing automatic-generation preferences/key requirements and MAIN preparation consent remain in charge; installing performs no bulk generation. Existing saved MAIN practice retains old mounted options and progress; explicit current/deck regeneration applies the new policy there. Keep Regenerate choices / Regenerate deck choices entry points. Formatting alone still leaves normalized clue text/cache identity unchanged within a policy revision.

159 Python tests and complete Node DOM suite pass. Six new backend cases cover formatting/cascade/sanitization/cache identity, targeted four/sibling blank context without changing the displayed clue, revision2 isolation with retained entries and revision3 reuse. Existing fake HTTP contract checks assert narrow-category/target-context/one-defensible-answer instructions and unchanged schema/secret handling. No real Gemini API call or user collection, and no semantic quality/difficulty measurement. No Windows/Anki/Qt browser renderer or long tests. Never present prompt contract tests as proof that generated choices are factually wrong/difficult.

Full update dist/Cram-Studio-v1.10.10.ankiaddon and matching dist/Cram-Studio-Handoff-v1.10.10.zip. Preserve package cram_studio/profile data. Always deliver both. Study List unchanged. Study Sounds1.1.7 remains user-confirmed working and untouched.

## Prior history follows

# Continue Cram Studio 1.10.9

## Current update: one blank's choices and larger, adjustable question panel

User's latest steering replaces the earlier separate-scrolling stacked-groups idea: show ONLY the active blank's four choices; after selecting, advance to the next blank, stop on last without checking/revealing/rating/continuing. Up/Down arrows and clicking sentence blanks revisit/change selections. Apply in MAIN and ANKI CRAM. They also report question panel too short, choices dominating, and choices becoming tiny when shrinking question text. Preserve existing appearance, colors and all other behavior.

Changes are scoped to appearance.py, shared appearance.js/css, app.js/live.js, customizer and native preview markup, tests and version/docs. examLayout is an additive, validated profile appearance schema: questionHeight default60 range30–75 (share of usable question/choices region), choiceTextSize default18 range12–32px. Both Python and JS normalization agree. Defaults apply to old profiles without automatically saving/resetting their dimensions, palette, image, text zoom or practice data. Customize Cram → Card size → Multiple choice exposes both fields with existing live preview, Save/Cancel and Reset. MCQ Reset clears its dimensions and resets examLayout; flashcard dimensions/colors/images stay. Shared CSS variables control tracks/type in MAIN/native/matching previews.

MCQ frame now uses bounded grid rows: MAIN heading + question + choices + check footer; native question + cl-answers wrapper. Question gets60% of usable track height; choices get40%. Saved sized-card aspect/scene bounds remain in effect. One slot group is unhidden; the others remain mounted with hidden=true. Choice boxes use less padding/min-height, independent18px type. Extremely long content can scroll inside question/choices surfaces, without scrolling the whole MCQ card or ejecting the question. Native cl-question-panel still owns text overflow; no 100% min-height regression. Shared showInPane adjusts only question-pane scrollTop when a newly active blank is outside the visible panel; no ancestor scrollIntoView or page jump on arrows.

On selection, update selected classes and fill question, then select i+1 only if it exists. Last blank never wraps/auto-checks. Arrows wrap and sentence click picks exact blank; existing choice focus sync is retained. No card/panel/choice rebuild on picks or navigation. MAIN checkpoints retain activeSlot and partial picks through the existing storage schema. Already-answered questions permit viewing other groups but cannot change results. ANKI retains Anki-controlled reveal/rating phase; no new native commands, rating key interceptions, auto-submit or timers. Native Qt shortcut/controller implementation is byte-identical; its existing guard applies in its normal contexts.

Removed choice text from existing question/flashcard text-zoom targets in both JS paths. Choice text uses examLayout.choiceTextSize via CSS. Saved text_zoom still applies to question/flashcard rich text; heading/highlight scaling stays. New native cl-answers wrapper is also used in synthetic preview so geometry matches. No new study controls/guides, colors, melody or alternate app.

153 Python tests and complete Node DOM suite pass. New regressions: four blanks, visible group only, automatic next with final waiting, arrow wrap/mouse revisits, changed picks, fixed nodes, no native grade/reveal/advance, original interval-button identity, independent type, same iframe under draft edits, invalid-save guard, layout persistence/reset, existing MAIN checkpoint/resume and scheduling-boundary matrix. Older tests requiring manual next after each selection were updated to the explicitly requested automatic-next behavior. No long tests or AI/user collection.

LIMIT: no desktop Anki/Qt or usable browser renderer here. Headless Playwright download returned unusable/truncated data. Do NOT claim actual Chromium/Windows pixel or keyboard QA. CSS containment/proportions need user confirmation on their real setup. DOM and profile/scheduling checks are real but simulated layout does not prove physical geometry.

Full same-package release: dist/Cram-Studio-v1.10.9.ankiaddon and dist/Cram-Studio-Handoff-v1.10.9.zip. Always deliver both. Preserve cram_studio and existing profile data/cache/sessions. Study List unchanged. Separate Study Sounds1.1.7 was confirmed by user to sound clear and responsive; do not change its working WASAPI engine or rebuild it for this Cram update.

## Previous release history follows; newer instructions above supersede old layouts

# Continue Cram Studio 1.10.8

## Current update: 1.10.8 resized multiple-choice question containment

User screenshot shows large clue text extending below the colored question panel in a resized ANKI CRAM multiple-choice card. The old shared sizing rules scrolled .cl-question-body (grid wrapper) while .cl-question-panel remained a centered grid with min-height:100%. That split the visible background from the overflowing text.

Only runtime change is web/appearance.css, plus manifest version and README. The native wrapper is now a flex column; the colored panel is its shrinkable flex child, min-height:0, overflow:auto. Clue flex-shrink:0 and auto block margins center short clues without negative centering for long clues. The conflicting sized-panel 100% minimum and scrolling-wrapper rule are removed. Both MAIN .question-panel and native .cl-question-panel explicitly own overflow, with horizontal/vertical containment and thin scrollbars. MAIN and ANKI customizer previews already load the same shared stylesheet, so require no JS changes. Do not reduce text size or reset saved custom dimensions to work around this bug.

151 Python tests and the complete Node DOM suite pass; syntax/build/checksum checks pass. All scheduling, setup, generation, storage/session, content/cache and frontend JavaScript files match 1.10.7 bytes. No new test duplicates CSS declarations. A browser renderer/desktop Anki are unavailable here, so no actual pixel-layout verification is claimed. Keep that limitation clear; this fixes the identified containment rules but should be visually checked on the user's Windows setup. No long tests, user collection or AI calls.

Full same-package update: dist/Cram-Studio-v1.10.8.ankiaddon and dist/Cram-Studio-Handoff-v1.10.8.zip. Preserve package cram_studio and all prior features/profile data. User needs only the latest full installer over existing Cram Studio and a restart. Study List and the separate Study Sounds companion remain unchanged. Always deliver installer plus matching source handoff for continuation in another GPT/account.

## Previous update: 1.10.7 stop browser selection/image drag on recall controls

User reports that repeatedly cursor-clicking clozes selects the image and turns it blue. There were no user-select/native drag guards on blanks/images/masks. Added shared appearance.js preventStudySelection(root, selector), called once by MAIN app, native live view and synthetic customizer preview. Delegated mousedown (primary only), selectstart and dragstart prevent defaults only on matching controls. Existing browser ranges are cleared only if Range.intersectsNode matches the clicked control; unrelated copied text is retained. Text-node targets resolve to parentElement, form/contenteditable targets are excluded, SVG tabindex=0 masks retain keyboard focus. No pointer/touch/wheel/keyboard capture or global selection clearing; no stopPropagation of the actual click. Scoped CSS user-select/-webkit-user-select:none and -webkit-user-drag:none on blanks and IO/attached card images/descendants complements the event guards. MAIN full-screen IO stage remains inside the same delegated root after reparenting; ANKI root delegation is document with #cram-live selectors. Current selection/click/reveal/grade/schedule semantics remain.

Only shared presentation helpers/styles, binding calls in web/app.js/live.js/customize-preview.js, version metadata and docs/tests change. Native backend reviewer, setup/default preference, scheduler, content/cache keys, practice sessions/storage, Gemini code and Study List are untouched. 151 Python tests and the full Node DOM suite pass. New interaction checks cover repeated masks and nested blank targets, stale intersecting ranges vs unrelated selections, image dragging, right/middle click, form/copy/scroll exclusions, stable nodes/zoom/viewer and untouched native keys/ratings. Tests are DOM spies, not a pixel reproduction of Chromium's blue selection or actual Windows/Qt input. No installed browser/Anki runtime, no live AI calls or collection changes. Keep this limitation clear.

Build outputs: dist/Cram-Studio-v1.10.7.ankiaddon and dist/Cram-Studio-Handoff-v1.10.7.zip. Full same-package update cram_studio with identical embedded installer/source and checksums. Preserve the existing UI, profile data and all previous features. Continue giving both installer and source handoff every update.

## Previous update: 1.10.6 approved blank style and enabled Gemini default

User reviewed the AI mockup and approved the clean flashcard blue underline but rejected ALL inline MCQ numbers/circles because they read them as sentence words. Implemented only display cleanup in web/app.js and web/live.js, shared appearance.css underline/active outline, matching customize-preview.js. Do not change backend content.py numbered clues or cache revision: those are internal Gemini context/identity and preserve existing cached choices/resumable snapshots. Visual placeholders use NBSP + cram-blank-empty CSS ::after (4.5em consistent width, no answer-length hint); no textual underscores/numbers appear inline. data-blank and accessible labels retain slot IDs. The active blank tint/1px outline also marks selected answers until checked. Rich flashcard answer HTML/authored numbering stays intact. Real numbered choice answers must not be stripped. Group labels outside the sentence stay to associate choices and arrows. Waiting questions and old saved snapshots also normalize when displayed, without mutating their questions or cache keys.

User explicitly requested “Automatically create missing choices with Gemini” default enabled. That exact checkbox is in live_start.py (ANKI CRAM setup). New default is checked, including legacy preferences because flashcard starts previously wrote the disabled control as false. Saving Start records live_generate_configured=True plus the checkbox's actual value independent of current mode; controller.auto_generate is gated to exam. Subsequent manual off is respected, including after starting flashcards. Open/cancel makes no preference write, network call or reviewer start. Existing live_review.py generation logic is unchanged and runs only when a multiple-choice question mounts; keys remain required, cached choices are reused, errors/fallbacks stay. No new automatic network behavior added to MAIN preparation or saved-session resume. No automatic grade/reveal/scheduling behavior.

151 Python tests and complete Node DOM suite pass in seconds; added actual LiveStartDialog Qt-spy tests for default adoption/save/cancel/opt-out/flashcard persistence and native fake-client checks for missing-once/cache/no-key/no-rating. Existing scheduling boundary matrix passes. No live AI/network test, browser pixel test or Anki/Qt runtime available. Do not claim rendered visual/Windows verification. Native scheduler/queue/rating/undo, content/cache, MAIN lifecycle/storage and Gemini implementation files match 1.10.5 bytes. Only setup preference, web presentation, metadata/docs/tests change. Build outputs dist/Cram-Studio-v1.10.6.ankiaddon and dist/Cram-Studio-Handoff-v1.10.6.zip are complete same-package updates. Study List is separate and untouched. Preserve this UI/code; deliver installer and matching handoff every release.

## Previous update: 1.10.5 presentation, sizing and interactive occlusion

Continue the exact package/UI. User supplied screenshots of ANKI CRAM vs Quizlet and native Anki cloze; asked for preview/live size consistency, stronger close shadows, less wasted padding, larger attached photos, independent multiple-choice resize, native colored/heavier/no-fill cloze emphasis, and a larger independent occlusion frame. Latest request: remove ANKI IO bottom Reveal row; native Space remains reveal/rating; compact top mask toggle and per-target taps/Enter reveal visually without scheduling. No Study List changes.

Changes are limited to appearance.py's validated additive examSize schema and web appearance/customizer/live/app presentation files, version metadata/docs/tests. Scheduler/queue/ratings/undo/filtered reschedule code is unchanged. Size percentages derive a reference aspect ratio (MAIN 1360x900; ANKI 1360x828 excluding the mock native footer), and shared CSS constrains both preview/live to available scene bounds. Native header/padding reserve is 122px rather than subtracting the bottom bar twice. size remains flashcard settings; examSize is independent and defaults to null dimensions. Preview handles support both types and keep existing DOM while dragging. Custom MCQ question content can scroll while choices retain their space; the card can scroll for many blanks. A projectSize pure helper verifies ratios/bounds but is not a browser layout engine.

fitImages enlarges attached images by measured face content width/height with aspect ratio intact, reserves space for text, handles late loads and window resizing. Image dimensions are unaffected by text-only zoom. IO has its own flexible viewport below header/tools/captions inside a responsive frame, not saved size controls. SVG target masks opt into pointer events; inactive masks remain inert. Native IO state distinguishes packet side from all-mask/per-target visual visibility. Global toggle and target clicks/Enter send no bridge command. On transition question→answer target masks open normally; rehide does not change native rating state; new epoch/undo resets. Image node, zoom and fullscreen persist across reveal. No new Space interception. The original MAIN IO controls stay intact.

Default/automatic cloze fill is transparent; accent text uses bolder + .12px text stroke. Author bold/highlights remain. Explicit manual answerBackground still works for users who intentionally customize it; existing color picker/harmonies preserved. All 145 Python tests and Node interaction tests pass, including the scheduling boundary matrix and new size/mask cases. No installed Anki/aqt, browser renderer or Rust scheduler, so no live pixel/Windows/touch verification is claimed. Do not call geometry spies a visual test. No long tests/Gemini calls.

Build with python build.py. Full installer is dist/Cram-Studio-v1.10.5.ankiaddon, matching source handoff dist/Cram-Studio-Handoff-v1.10.5.zip. Each update is the complete same add-on package cram_studio, not a second install. Continue delivering installer plus handoff. Preserve profile config/cache/saved sessions and UI; never rebuild from descriptions. Keep native schedule boundaries and Study List separation.

## Historical scheduling audit after the 1.10.4 release

User reported finishing ITPM and later seeing30 more cards the same day, asking for unit tests to ensure MAIN CRAM does not affect Anki scheduling and ANKI CRAM follows the native reviewer. Added tests/test_schedule_boundary.py (nine tests, including108 MAIN mode/filter/order combinations) and a scheduling-isolation matrix in the Node DOM suite. All144 Python tests and full UI checks pass. See SCHEDULING-AUDIT.md for evidence, limits and reproducible commands. MAIN lifecycle writes no SQLite collection data in guarded fixtures; native review retains current card/queue/ratings/undo and filtered reschedule flags; no UI-generated ratings/auto-advance. No production-code change was needed. That audit did not change the 1.10.4 runtime. The new presentation update below supersedes the historical instruction to preserve the installer bytes. Do not claim real Anki/FSRS/Windows testing or diagnose the user's30 cards from unit tests. Read-only Card Info/history and learning/relearning settings would be needed for that. Handoff contains the same full installer plus the new tests/report.

## Current update: persistent MAIN CRAM progress and stationary choice hover

Exact continuation of1.10.3. User accidentally closed MAIN CRAM and lost an unfinished session; asks for progress to remain until completion/reset/deletion, plus choice hover pulsing/moving nearby choices. Implemented profile-local saved practice without touching ANKI CRAM or the collection/scheduler. No UI rewrite.

Store now retains a sessions metadata index in its existing practice.json and atomic per-session queue/view JSON files in the profile/cram_studio folder. Session IDs are generated32-digit hex UUIDs and validated before file access. Full snapshots preserve PracticeSession questions/results/retries/original_count/repeat setting; restore bypasses __init__ so it never resets retry flags or reshuffles saved choices. UI-only checkpoints write a separate small view file, without rewriting queue/cache. Controller saves before emitting grade/queue/choice changes, pause/home and window close; rejects route through close. Browser checkpoint messages are scoped to the currently active session ID and can update only validated UI state, never grades/questions. Exact existing scope selection resumes its old set; different sets are retained independently with no expiry or silent eviction.

Home now lists unfinished sets with Resume and a confirmed Reset action. Closing/Save & exit preserves progress. Resume restores cursor, partial blank picks/active blank, reveal state, preview zoom and available scroll position. Results remain server-authoritative. Reopening an answered card does not auto-grade/auto-advance/auto-finish. Missing MCQ choices remain paused; no automatic network or search/recompile occurs. The restored set is a snapshot, not a live re-run of time-dependent filters or later note edits. Elapsed time resumes from saved active time and excludes closed downtime. Completing saves history and removes only that session from the index in one atomic practice.json update, then cleans up its files. Reset leaves cached choices/preferences/other sessions untouched. Already-lost pre-update sessions are unrecoverable; profile-local saves are not Anki-synced.

No deliberate hover animation was present in app.css; isolated MAIN choice buttons from inherited Anki hover effects with explicit no transform/translate/scale/animation/transition/filter/shadow and fixed2px borders/margins. Choice text/key transitions are suppressed too. Existing theme/selected/correct colors, focus outline, text zoom and all interaction nodes remain. This is a targeted mitigation; exact Windows/Qt rendering and the original inherited rule cannot be independently verified here.

Added short actual-controller/disk reopen tests and UI restore/hover-node checks. They cover retries and first-pass scores, unchanged MCQ choices, partially selected blanks, multiple saved sets, matching-scope resume without rebuild, stale checkpoint rejection, small view saves, profile isolation, corrupt-file preservation, durable grades, paused AI, completion/reset cleanup and UI reset confirmation. Existing native reviewer tests must still pass. Runtime changes only storage.py,session.py,dialog.py,app.js,app.css; tests/startup fixtures updated for added methods. build.py includes the new test_progress.py in the handoff. Run quick Python/Node/syntax/build/checksum checks; no long tests or Gemini calls.

Deliver full Cram-Studio-v1.10.4.ankiaddon and matching Cram-Studio-Handoff-v1.10.4.zip with exact source/docs/tests and identical embedded installer/checksums. Preserve cram_studio identity and all earlier features. No session/profile/history/cache/key files, user media, helper scripts or test logs in releases. Keep Study List separate. Explain where Resume/Reset are in the final response.

## Earlier implementation and release history retained

# Continue Cram Studio 1.10.3

## Current update: readable Question order menu and note highlight zoom

User's latest screenshot shows the expanded MAIN CRAM Question order popup as a solid black rectangle. Replaced only that native popup with a page-rendered select-only combobox/listbox, using existing panel/ink/accent colors. The hidden select remains the source of all original values, labels, Anki column groups and disabled retrievability choices; no order values, backend queries or scheduler behavior change. Existing order-direction visibility and start config are retained. Mouse choice, hover, keyboard arrows/Home/End/Page keys, Enter/Space, Escape cancellation, Tab commit and prefix/repeated-letter navigation are handled explicitly. Focus stays on the trigger with aria-activedescendant; held Enter/Space is ignored. Menu width/height and opening direction fit the viewport, its own scrolling stays open, and outside pointer/page scroll/blur/resize dismiss it. app.css changes are scoped to the order control/menu. No real Windows/Qt rendering available; the native popup cause is not independently confirmed.

Exact continuation of1.10.2. User reports note highlights look too small when enlarging flashcard text. Found a concrete nested-markup case: ANKI CRAM's applyTextZoom collected only elements with direct text nodes. A highlighted span wrapping only b/i/span children therefore kept its original font metrics, while the leaf glyphs enlarged. Collect text-containing ancestors as well, excluding script/style/SVG/math/canvas. Restore cached inline font-size/line-height and their priorities before measuring any new descendant, then capture all missing baseline metrics before applying scaled sizes. This avoids compound enlargement, including dynamically inserted text in an already zoomed wrapper. Reset restores original inline styles.

MAIN CRAM now uses zoomContent for its existing text roots (flash faces, MCQ/waiting clues and choice text), preserving the existing29/22/21/16px root baselines. It restores cached styles, measures nested rich text at100%, and applies absolute scaled font-size/line-height to text-containing wrappers and children together. Fixed inline note font sizes now zoom too. A no-getComputedStyle fallback keeps the old basic behavior for reduced environments. No new script dependencies or build entries. Native and MAIN text size ranges/preferences/keys are unchanged. Images themselves are not zoom targets; frame dimensions/styles, colors/highlight backgrounds, render/flip nodes and scheduler/ratings remain untouched.

Added short DOM regressions with a20px highlighted span (28px line-height) wrapping nested b/i and an adjacent image. Both MAIN faces and ANKI compiled/native fallback cards produce30px/42px at150%,32px at160%, preserve highlight color, restore original20px/28px formatting on Ctrl+0, and retain the same image/frame/native-rating nodes. New descendants inserted at an existing zoom use the unzoomed baseline. The fixture's computed styles are simulated; this is not real browser pixel validation. Existing124 Python tests, full short Node suite, changed JS syntax and deterministic build/checksums must pass. No long tests or Gemini calls.

All earlier features,1.10.1 clean inspector outline,1.10.2 removed duplicate answer panel, color mappings/images, shortcuts and storage identity remain. No Python runtime changes. Added short interaction/placement regressions for the replacement order menu as well as the nested-highlight cases. Deliver full Cram-Studio-v1.10.3.ankiaddon and Cram-Studio-Handoff-v1.10.3.zip with identical embedded installer/checksums, exact source/docs/tests. Exclude profile/cache/history/API keys, user media, helpers and test logs. Keep Study List separate. Actual desktop Anki/Qt rendering remains unverified.

## Earlier implementation and release history retained

# Continue Cram Studio 1.10.2

## Current update: remove the duplicate Full Anki answer panel

User explicitly requests removing the expandable Full Anki answer shown below the revealed ANKI CRAM flashcard. Removed creation of the details/summary and moving/unhiding original content from both compiled flashCard() and ready multiple-choice exam() in live.js. Removed the corresponding sample-original mockup and unused details/sample CSS, including its obsolete appearance-width rule. The actual compiled answer, choice feedback, flip/text zoom, ratings/intervals and all prior UI remain. Hidden #cl-original is retained for Anki lifecycle compatibility; fallback nativeCard() still presents unsupported/typed/scripted/unmapped cards normally. Do not remove native fallback content or affect standard Study Now.

No Python/runtime scheduling, storage, preference or mapping changes. All1.10.1 outline fixes and1.9.1 shortcuts retained. Existing interaction assertions now check absence of duplicate details, original content retained hidden in supported compiled modes, clean mockup, and unchanged native fallback/reveal/ratings/zoom. Run124 quick Python tests, existing Node DOM suite, changed JS syntax and build/archive checks; actual desktop rendering is unverified.

Deliver full Cram-Studio-v1.10.2.ankiaddon and matching Cram-Studio-Handoff-v1.10.2.zip containing exact source/docs/tests and identical embedded installer/checksums. Preserve cram_studio identity and all earlier features. No keys/profile/cache/history, user images or helper files in releases. Earlier history below may describe the removed original-answer panel; this current section supersedes it.

## Earlier implementation and release history retained

# Continue Cram Studio 1.10.1

## Current update: complete, clean picker outline

Exact continuation of1.10.0. User screenshot showed only the left/top dashed hover outline when pointing at the preview page. hoverInspector clamped left/top but added the entire element width/height, letting its right/bottom edges extend beyond the hidden-overflow iframe. It now intersects all four target edges with the iframe viewport, inset5px for the border/halo; fully offscreen targets remove the outline. A2px solid border replaces the3px dashed one, with a1px light halo and explicit border-box sizing. Reuse the mounted hover node instead of re-appending it on every move. Clear hover on pointer leaving the iframe/document, blur and resize.

Only customize-preview.js runtime behavior changes. Real study interfaces, picker role/part mappings, exact selected-property locator, colors, Auto/edit/save/cancel, profiles, native scheduler and all shortcuts remain unchanged. app.js changes only its visible version label. Manifest1.10.1, full installer and matching full source handoff.

Geometry regression recreates an oversized page rectangle(-20,-10,1420,1080) in a1360x900 iframe, verifies every edge lies inside the viewport, stable outline-node reuse, both pointer exit handlers, and removal of wholly offscreen targets. Run existing short suites/syntax/build/archive checks. The supplied screenshot was inspected; no actual Qt/browser pixel render is available, so do not claim visual runtime testing. No long tests.

Deliver Cram-Studio-v1.10.1.ankiaddon plus Cram-Studio-Handoff-v1.10.1.zip, with identical embedded installer and checksums. Preserve the same cram_studio identity and all earlier features/UI. No user images, keys/profile/cache data, upload helpers or temporary test outputs in either artifact. Earlier history follows; this section supersedes1.10.0's dashed outline description.

## Earlier implementation and release history retained

# Continue Cram Studio 1.10.0

## Current update: accurate color locators and reverse component picker

Exact continuation of cram_studio1.9.1. User reports some double-click color locators show nothing, and requests reverse selection by clicking the interface, explicitly concerned about nearby/overlapping text, backgrounds and borders. Implemented only in CUSTOMIZE CRAM's synthetic live preview. Real study screens, native rating/reveal/queue/undo/reschedule behavior, MAIN CRAM practice logic and all1.9.1 shortcuts are unchanged.

Root cause found: customize-preview.js used document.querySelectorAll(...).find(...). Browser NodeLists have no find, so generic/selected/correct/incorrect choice locators threw before drawing. Existing fake DOM returned Arrays and missed this. The shared preview all() now uses Array.from, and new tests supply a browser-like iterable/indexed NodeList with forEach but no Array.find. Those tests cover both modes/themes/card types and the affected roles.

Forward locators keep explicit role-to-element/CSS-property bindings. Default/inherited styles can legitimately differ from the editable palette, e.g. default Correct text inherits ordinary ink while the same semantic green is used on borders. The old CSS equality gate could suppress useful pointers. Targets now remain locatable and explicitly show Setting vs Shown hex/property, rather than switching a text role onto an unrelated border or pretending colors match. A missing element produces a labeled no-component message. This is semantic control inspection, not screenshot pixel matching. No styles or draft values are changed by locating.

New Pick from preview / Stop picking controls exist only in the color customizer. The parent sends an inspect flag and visible role labels to its source-checked iframe. While inspecting, clicks do not flip/reveal/select an answer. Hover offers a dashed component outline; click opens a menu with separate text/background/border choices. Each entry binds a role to an exact element/property/region. Choice text/background/border distinguish neutral/selected/right/wrong states. Selected letter badges have their actual Card/Accent bindings separately from the surrounding choice. Neutral letter circles and muted labels are identified as automatic shades with no separate control. Active blank shading is identified as derived from Accent/Question panel. Nested question-panel/card surfaces remain separate entries. Native footer labels/backgrounds map to the shared button/reveal controls, without calling Anki.

Selecting a menu entry draws a persistent exact-property locator and posts role/mode/view/theme/face to the parent. Only the current iframe and matching current context are accepted while inspection is on. The parent opens the relevant details group, scrolls/highlights its row, and focuses the hex input or label. Inspection itself never turns off Auto, pins a color, writes preferences, sends text to Gemini, or commits. Explicit manual edits and Save/Cancel retain existing behavior. Color edits keep preview nodes and exact target mounted. Context changes clear stale target/menu references; exiting inspection restores normal mockup behavior. Locate-by-name exits picking and still uses existing automatic context/face switching. No new appearance schema, role, scheduler or profile data is introduced.

Quick validation:124 Python tests, expanded Node fake-DOM suite including browser NodeList semantics, identical-color overlap disambiguation, neutral vs selected badge roles, correct/wrong choice states, active-label category, separate nested surfaces, cloze highlights, native footer, guarded source/context selection, stable exact target after draft edits, unchanged Auto/config, no flip/bridge/rating calls, and exit/panel behavior. JS syntax and deterministic archive/checksum checks are required. Real desktop Anki/Qt/pixel hit-testing is unavailable; a headless browser download attempt failed, so do not claim real Chromium rendering or screenshot validation. No long tests/Gemini calls were run.

Build allowlists unchanged; all edits fit existing files. Deliver the complete Cram-Studio-v1.10.0.ankiaddon and Cram-Studio-Handoff-v1.10.0.zip, including identical embedded installer and checksums. No keys, profile/cache/history data, user images, helper scripts or intermediate outputs. Preserve exact existing UI/source for continuation; Study List remains separate. Earlier history below records the implementation at that release and may describe superseded locator behavior; this current section is authoritative.

## Earlier implementation and release history retained

# Continue Cram Studio 1.9.1

## Current update: quick access, no study-interface guide

Exact continuation of the same cram_studio package and UI, retaining all1.9.0 color harmonies/locators/images and earlier features. User requests easy shortcuts for MAIN CRAM and ANKI CRAM, explicitly no printed guide in the interface. This is1.9.1, not the proposed2.0 feature set.

__init__.py registers Ctrl+Alt+M (primary) and existing Ctrl+Shift+T (alias) on the same MAIN CRAM QAction, and Ctrl+Alt+A on the existing ANKI CRAM QAction. Both use WindowShortcut and disable auto repeat; no global/application shortcut, new window buttons, card guides or settings changes. Existing menu entries show the primary keys, and existing overview button tooltips match. Separate editor/browser/practice/customizer windows keep their own key handling.

ANKI CRAM launch accepts the deckBrowser state as well as overview: move to the currently selected deck's overview, then run the unchanged LiveReviewer.open setup. The user must still choose Start ANKI CRAM. A running native CRAM review focuses the main window without restarting/altering the current card; an existing setup dialog is raised. Ordinary native review/other states show the existing style of warning to return to deck list/overview first. Profile-unavailable launch returns. No scheduler/queue/order/rating/undo/reschedule code changes.

Five quick launcher regressions execute the actual initializer against Qt/Anki spies: QAction keys/alias/context/repeat and callbacks, selected-deck navigation without scheduler access, missing collection/unsupported state, focus without restart, and overview button deduplication/tooltips. All prior quick tests remain required. Actual Windows/Qt shortcut delivery cannot be verified here; do not claim desktop testing.

Always deliver Cram-Studio-v1.9.1.ankiaddon plus Cram-Studio-Handoff-v1.9.1.zip. The source handoff includes this continuation record, exact source/UI, quick tests, build.py, checksums and the identical full installer. No profile, API key/cache/history, user images or upload helpers. All earlier source history below remains for continuity. Study List is separate.

## Earlier implementation and release history retained

# Continue Cram Studio 1.9.0

## Current update: seven color harmonies and corrected color locator

Exact continuation of the same `cram_studio` add-on/UI. Retains1.8.0 local page/card images, collapsed trees, all color controls, plain Basic answers, choice circles and prior generation/filter/shortcut/IO behavior. MAIN CRAM remains independent practice; ANKI CRAM only presents the native reviewer, queue/rating/interval/reschedule/undo remain Anki-owned. Always deliver a full installer and complete handoff for continuing the exact code/UI elsewhere.

User asked to research harmony choices beyond the existing subdued Card-based palette, then also reported inaccurate double-click color tracking. Both are included in this release.

Research: Adobe's primary palette guide lists monochromatic, analogous, complementary, split complementary, triadic, tetradic rectangle and square. Sources: https://www.adobe.com/uk/creativecloud/design/discover/color-palette.html and https://color.adobe.com/create/color-wheel. Names/relationships informed the selector; the local implementation uses a digital HSL wheel, not Adobe's exact algorithm or an online API.

appearance.py adds optional palette metadata harmony with an allowlist: monochromatic, analogous, complementary, split_complementary, triadic, tetradic, square. Current normalizes away. No new storage/schema version; missing metadata preserves original behavior exactly. Invalid choices reject before atomic Save; old presets/images/size/manual values remain intact. Per light/dark × flash/exam choice is shared between MAIN and ANKI like existing colors.

appearance.js retains the legacy harmony() branch byte-for-byte for missing/current. New harmonyColors() generates primary/supporting/tertiary hues from Card using offsets: mono0/0/0, analogous+30/-30/0, complement180/0/180, split150/210/0, triadic120/240/0, rectangle180/60/240, square180/90/270. Card itself remains unchanged. White/gray uses the renderer's original accent as hue anchor for chromatic harmonies; monochromatic neutral stays gray. Tones use current card luminance, and foregrounds run existing relative-luminance contrast adjustments. Primary drives accent/selection, supporting drives reveal/answer, tertiary contributes page/button/question/border tints. Semantic green/red feedback remains separate (its tones can adapt to different surfaces). Explicit role pins always win.

Customizer has Color harmony beneath Color scheme, enabled only in Automatic mode (including custom palettes still based on auto). Generated hue swatches, short descriptions, existing mode/theme/face live previews remain. Harmony edits preserve manual pins. Selecting Automatic again clears those pins and keeps selected harmony/Card. Current removes metadata. Default and Reset all colors clear it; image and size reset semantics from1.8.0 unchanged. Editing Card updates swatches without rebuilding iframe/card nodes. Swatches use actual card luminance even for a dark Card in Light theme and vice versa. No new guide text is added to review cards.

Locator audit found broad container targets and fixed left-side anchors could point into letter badges, text instead of background, or the native bottom bar for page color. Replaced locatorTarget() with explicit locatorSpec(): target element, actual CSS property and region type. Text specs use choice-text/heading/answer spans, Range glyph bounds when available. Background specs use empty padding patches. Border specs use a 1px top-edge segment. Page specs use the exposed margin, excluding native footer. Labels show expected hex/property; image backgrounds are identified as underlying base colors. Before drawing a pointer, computedHex compares the browser's computed property with the palette value. Original default Correct/Wrong may fall back to an actual matching border. Other mismatches show a not-visible message with no false arrow. Transparent/unrecognized computed CSS values do not silently pass as matches.

Removed the fabricated neutral-button example entirely. When locating generic button colors from MAIN flash, preview visibly switches to ANKI flash answer ratings (the shared flash palette controls those real native buttons); Hard is the sample target so the original default Again/Easy semantic coloring is not confused with generic text. Native mockup buttons now carry data-ease matching their real styles. Revealed-answer colors in MAIN MCQ still switch to actual ANKI MCQ as introduced1.8.0. Main primary-text locator uses the genuine graded footer structure (Correct / Show clue / Continue) rather than relabeling a Got it button. Preview context selectors update visibly, and no actual review state/picks/scheduling or saved color is changed by locating.

Validation:119 quick Python tests plus expanded fake-DOM interaction suite and shipped JS syntax. New tests cover every harmony's hue relationships, distinct palettes, eight readable foreground/surface pairs over sampled neutral/dark/saturated bases in both modes/themes/views, preserved Card/manual pins/legacy-current behavior, neutral monochrome, persistence/rejection/reset preserving images/size, picker lifecycle, precise CSS-property/element targets avoiding letter badges, page/footer separation, removal of invented neutral components and CSS-mismatch guards. Existing native isolation and image tests remain passing. Tests are local/spies; no real Qt/Windows/browser pixel rendering, actual file-picker/image encoding or Gemini request is verified here. Runtime computed-style guard will execute in Anki's Chromium webview. Do not claim pixel-tested screenshots.

Build allowlists unchanged (new features fit existing shipped files). Run bounded existing suites and build.py/archive audit; release Cram-Studio-v1.9.0.ankiaddon and Cram-Studio-Handoff-v1.9.0.zip with identical embedded installer/checksums. No user images, profile/cache/key data, research downloads or upload helpers may be packaged. Study List remains separate.

## Earlier implementation and release history retained

# Continue Cram Studio 1.8.0

## Current update: visual color locators, collapsed trees and local appearance images

Exact continuation of existing `cram_studio` source/UI, retaining1.7.2 plain Basic answers,1.7.1 choice circles, all1.7 color settings, navigation and prior scheduling/generation/filter/IO boundaries. MAIN CRAM is independent practice; ANKI CRAM only skins Anki's real Reviewer. Do not rebuild the UI or change package/profile/cache/history identities. Always deliver the full installer plus complete source handoff.

User requested: double-click a color name to point to its component in the mockup, deck children collapsed by default, uploaded page/card images with opacity and visual readability protection. No new scheduler or practice behavior is added.

Color locator: customize.js renders color-name spans rather than labels that would open a native color picker on double-click. Delegated dblclick and Enter/Space post a source-checked iframe configuration with a transient role/label/serial. customize-preview.js maps every visible role to a real sample component, chooses answer/question/selected/correct/wrong state as appropriate, renders an outline/connector/label, and dismisses on X/Esc/7s. It changes mockup state only, never saved colors or current actual review picks. MAIN MCQ revealed-answer roles are used in ANKI MCQ, so locating them visibly changes the preview mode to ANKI while keeping the same shared theme/view palette and not changing production MCQ logic. Neutral button roles in MAIN flash mode show an explicit temporary neutral-button example; primary text shows Continue and restores the normal sample controls on close. Locator overlay is scoped to the preview iframe, never actual study cards. Config/style updates retain iframe nodes; only explicit preview state/locator context changes rebuild synthetic content.

Decks: app.js tracks seen parent paths; first bootstrap collapses every parent. User toggles persist for that window and refresh preserves opened parents while new branches default collapsed. Search bypasses hiding so nested decks remain discoverable, and selecting/include-subdeck/count behavior is unchanged. deck_choices.py uses collapseAll() for its Qt regeneration picker and avoids scrolling to a hidden selected child. Ordinary Anki deck browser behavior is not modified.

Images: new appearance_images.py has pure normalization plus lazy Qt file-picker/decoder imports. Source selection uses QFileDialog/QImageReader; max30MB source and40MP, EXIF auto orientation,1600px max edge, re-encoded PNG (alpha) or JPEG (opaque) up to256KiB each by quality/downsampling. Only two global slots (background/card); encoded data and short basename stay in profile preferences appearance.images, with opacity/overlay0..100 and boolean smart. No arbitrary path or external URL is saved or loaded. Header/base64/size/type/range validation rejects SVG, remote URLs and malformed data before committing. Images are local presentation preferences, not collection media/notes or Gemini input. Source/install bundles exclude all profile/user images. Qt decoder/file-dialog functionality is not exercised in this environment.

Appearance schema remains version1 with optional images; absent/empty images are omitted so old normalized settings remain identical. Python save remains atomic with rollback, and Cancel/image-picker cancel do not write. choose-image bridge emits processed image to the draft (including None on file-dialog cancel to release pending controls); image/remove/opacity/overlay/smart edits only commit on explicit Save. Customizer bridge cap1MB accommodates at mosttwo bounded data URIs. Existing color reset leaves images/size intact; Remove all images clears only images. Existing profile settings/keys/cache/history remain intact.

appearance.js normalizes image data and computes CSS background layers (solid-color veil over image) without changing dimensions or rebuilding card nodes. Smart checks worst-case black/white image pixels against current foreground/base pairs; lowers effective alpha until preserving the existing ratio, capped at4.5:1 target. Card checks normal text plus the effective Basic answer foreground when a custom palette is active; default Basic answer uses ordinary ink. Page checks main text/accent. This is conservative pair protection, not pixel sampling/full accessibility certification, and cannot fix an already low-contrast manual foreground. Both images and their requested opacity/overlay are saved unchanged; effective alpha is recalculated per current mode/theme/view. UI reports visible strength and offers Smart off for manual control. Native bottom webview receives colors only, avoiding duplicate image payloads.

appearance.css applies page layer to MAIN session / native body, card layer to flash faces / MCQ panels. Buttons and question panels retain solid colors above images. IO is excluded and clears image variables; images do not affect IO geometry/masks. All upload controls use the same actual rendering CSS/functions in live previews for MAIN/ANKI and Light/Dark. No answer highlight bar is reintroduced for Basic.

Validation:117 quick Python tests plus expanded fake-DOM suite and all shipped JS syntax checks. New checks cover image normalization/ranges/non-raster URL rejection, profile save/reset and image-picker bridge cancel/error without Save, footer payload isolation, worst-case readability/manual opacity, stable image control/card nodes, locator source/state/dismissal and all visible roles, collapsed-searchable decks and refresh expansion preservation. Existing native reviewer tests trap queue/scheduler access and remain passing. These checks do not execute real Qt image encoding/file selection, native focus delivery, real browser pixel layout or Gemini requests. Do not claim runtime screenshots/Anki visual QA.

Build allowlist includes new appearance_images.py; existing test files include added checks. Run quick suites, JS syntax, build.py, and archive/checksum audit. Deliver Cram-Studio-v1.8.0.ankiaddon and Cram-Studio-Handoff-v1.8.0.zip with identical embedded installer/checksums. Study List remains separate.

## Earlier implementation and release history retained

# Continue Cram Studio 1.7.2

## Current update: remove Basic answer highlight bars

Same complete `cram_studio` add-on/UI, retaining1.7.1 choice circles and all earlier color, navigation, generation and scheduling boundaries. User supplied an ANKI CRAM Basic answer screenshot with a full-width tinted bar behind "Layer 2 Address" and asked to remove the ugly highlight. This was introduced when1.7.0 applied `--cram-answer-bg` to generic block answers as well as cloze spans.

appearance.css now leaves `.session .answer-item .answer-value` and `#cram-live .cl-answer-item` backgrounds transparent. They retain the separate answer text color, including manual/automatic palette support. Only actual revealed-cloze spans continue using the highlight role. Removed the generic answer blocks from the descendant background-clearing rule too, preserving intentional original field highlights/formatting rather than overwriting them. No note fields or saved colors are changed; no new setting is needed. The existing highlight picker is relabeled "Cloze answer highlight" to make its scope clear. Both modes' non-cloze compiled flashcards use these existing answer blocks; the synthetic preview's cloze sample correctly keeps its highlight. IO, native full-answer disclosure, card geometry, flips, buttons, choices and rating callbacks are unchanged.

This is a small CSS/picker-label fix. Use the existing113 fast Python tests, DOM interaction suite and shipped JavaScript syntax checks, followed by build/checksum audit; no new redundant CSS tests or long tests. No real Anki/Qt/browser pixel test is available, and the supplied screenshot is reference only. No user/profile data or screenshots are packaged.

Deliver full Cram-Studio-v1.7.2.ankiaddon and matching Cram-Studio-Handoff-v1.7.2.zip with identical embedded installer/checksums. Install over the existing Cram add-on. Always include the handoff so the user can continue this exact source/UI in another account. MAIN CRAM remains independent practice; ANKI CRAM remains a presentation over the real Reviewer, preserving native queue, scheduling/reschedule setting, ratings, intervals and undo. Study List is a separate add-on.

## Earlier implementation and release history retained

# Continue Cram Studio 1.7.1

## Current update: ANKI CRAM choice-letter circles

This is the same full `cram_studio` continuation and existing UI. The user supplied four color-preview screenshots: ANKI CRAM's yellow A/B/C/D circles disappeared into the yellow hovered choice, while MAIN CRAM kept a subtle circle distinct from its yellow hover. Match the existing MAIN behavior rather than redesigning choices or adding settings.

Cause: live.css used `--cl-tint` (the selected/hovered answer background) for `.cl-key`; app.css uses independent `--soft` for `.choice-key`. Native default light/dark roots now define `--cl-soft` matching MAIN's original subtle surfaces (#f6f7fb/#1c2440). Shared appearance.apply derives custom `--cl-soft` by mixing5% effective text into Card, exactly like MAIN's custom soft color; it clears this managed variable on reset/view changes. This is derived only, with no new saved role/schema/storage change. Existing preferences/auto/custom pins remain intact.

Native letter circles use `--cl-soft` and `--cl-muted` at rest and during hover, with MAIN's13px/650 typography and28px fixed circle. A selected native choice uses `--cl-panel` and `--cl-accent` for its letter circle, matching MAIN's selected-card circle rule. Only live.css and the native appearance token derivation change behavior; actual and synthetic native preview load the same styles. No MAIN choice rule, button geometry, grading, shortcut, reveal, AI choice generation or native scheduler/reviewer callback is changed. Keep all1.7.0 color controls and native footer isolation.

Validation uses the existing quick Python/DOM suites and shipped JavaScript syntax checks, plus deterministic archive/checksum audit. No new tests for this low-impact CSS adjustment, no browser/pixel test or actual Anki/Qt test. Do not claim screenshots were generated from the runtime. No screenshot/user/profile/API-key data is packaged.

Release full Cram-Studio-v1.7.1.ankiaddon plus complete Cram-Studio-Handoff-v1.7.1.zip with identical embedded installer/checksums. The user always wants both files for exact continuation elsewhere. Install over the same Cram Studio; Study List stays separate. MAIN CRAM is independent practice, ANKI CRAM is a skin over the native Reviewer, queue/rating/interval/undo remains Anki-owned.

## Earlier implementation and release history retained

# Continue Cram Studio 1.7.0

## Current update: independent answer/button colors and automatic palettes

Full continuation of the existing `cram_studio` package and UI, including all1.6.1 blank navigation, raised question surface, regeneration, totals, IO, zoom, filters/order and scheduling boundaries. MAIN CRAM remains independent; ANKI CRAM remains presentation over the real Reviewer. Study List is separate. Do not rebuild the UI or change package/profile/cache/history identities.

The supplied screenshot showed a pink custom card, a green revealed cloze answer sharing Correct, and a pink Show clue button sharing Card. The user asked for independent revealed-answer text/highlight, button backgrounds/text and Show clue colors, a coordinated automatic palette based on Card, and Reset all colors returning to the actual original light/dark defaults.

appearance.py/js retain schema version1 with additive optional hex roles `buttonBackground`, `buttonText`, `revealBackground`, `revealText`, `primaryText`, `selectionText`, `correctBackground`, `incorrectBackground`, `answerText`, `answerBackground`. Existing roles include `question`. A palette may additionally contain `auto: true`; false normalizes away, other Python values reject before writing. Missing roles remain backward compatible. Existing explicit legacy colors are preserved. Atomic profile Save/rollback and unrelated preferences, keys, cache/history are unchanged.

Shared palette() has independent revealed-answer derivation: in automatic mode it uses the accent; legacy palettes use the original renderer's green, never a manually changed Correct. Explicit answers/feedback/surface roles never overwrite one another. Automatic from Card uses a complementary hue for chromatic cards (existing accent for near neutrals), coordinated surfaces, and relative-luminance contrast adjustment for automatic foregrounds. Tests check at least4.5:1 for automatic main text, buttons, reveal, correct/incorrect feedback, revealed answers, selection and primary button over sampled light/dark/saturated/midgray bases. This is scoped color-pair verification, not an accessibility or visual-layout certification. Manual colors are honored even when their contrast is low.

Customizer controls are grouped under Card and page, Revealed answer, Buttons, Answer feedback. Per-role Auto removes only that role's override. First Card edit from a completely default palette activates auto; subsequent edits store only the edited override rather than copying the resolved palette and freezing every color. Automatic scheme clears pins for the current theme/view, preserving Card; Custom pins the current resolved palette. Default clears only the selected palette. Reset all colors clears allfour light/dark × flash/exam palettes (including auto/base Card), preserving size. Save commits, Cancel does not. Group expansion/sidebar scroll survive updates. Color changes retain the same iframe and card nodes.

appearance.css maps separate surface/foreground variables without rebuilding cards. MAIN Basic/custom answers get `.answer-value`; cloze only colors the revealed spans, preserving clue context. Native compiled flash Basic uses existing `.cl-answer-item`; cloze uses `.cl-revealed-answer`. Native MCQ fill() adds that class only on the answer side, clearing it on questions. Explicit/auto answer colors take priority over descendant font/span colors while preserving rich HTML structure. Empty palettes remove managed variables/classes and use the original shipped CSS. IO remains excluded. MAIN generic button colors, Reveal/Show clue, correct/wrong feedback and selected states are independent; no tutorial text is added.

ANKI native bottom colors now use the shared appearance script too. web_content adds validated configuration in head and appearance.js alongside existing live-bottom.css; original body/button markup is untouched. render/emit send only current appearance/view to bottomWeb via guarded eval, and invalidate/exit clears styles. applyBottom() only adds/removes four CSS variables and a body class; it never changes button HTML, labels, intervals, event handlers, ratings or queue. Generic button background/text apply to native rating buttons; separate reveal background/text apply to Show Answer. The bottom theme observer only reapplies when the actual night-mode state changes, avoiding a class-mutation loop. Image/native fallbacks without flash/exam scope remove these color overrides. The live synthetic ANKI preview applies the same function to its sample footer. There is no replacement scheduler, automatic grading or Anki collection write.

Validation:113 fast Python tests and the expanded fake-DOM interaction suite pass. New checks cover all new roles/auto validation and profile reload/reset, native bottom configuration/exit cleanup with read/write traps, automatic readable pairs in both renderers/themes/views, independence from Correct, manual pins, auto recalculation, stable preview/Basic card nodes, all-theme exact reset preserving dimensions, native button DOM/actions/intervals untouched. All shipped JavaScript syntax-checks. Tests are fast local unit/spies, not real Qt/Windows rendering, real browser pixel checks or live Gemini verification. The supplied screenshot is reference only; do not ship it or user/profile data.

Build: `python3 -m unittest discover -s tests -q`, `node tests/test_ui.cjs`, `node --check` each shipped web/*.js, `python3 build.py`. Deliver Cram-Studio-v1.7.0.ankiaddon and Cram-Studio-Handoff-v1.7.0.zip, with identical embedded installer and verified CHECKSUMS. Keep installer/source identities for subsequent releases. The user wants the full installer plus handoff every update so another GPT can continue this exact code/UI.

## Earlier implementation and release history retained

# Continue Cram Studio 1.6.1

## Current update: reliable blank targeting and separate question surface

Full continuation of the same cram_studio add-on, retaining all1.6.0 home/filtered totals, deck-wide regeneration, earlier Gemini/list fixes, profile data and scheduling boundaries. Source is the actual updated existing project, not a UI rewrite. Every release includes full installer + complete handoff.

The user supplied an ANKI CRAM screenshot with two blanks and asked for Up/Down blank targeting while 1–4 answers the active blank, a subtle active emphasis synchronized with mouse selection, plus a raised borderless question panel with its own live theme color setting. Existing webview document handlers already implemented arrows, but native number keys also used Qt; arrows depended on review-webview focus and did not reach it from native bottomWeb. Do not claim a Windows reproduction was observed; this is the identified routing gap from source.

live_review.LiveReviewer now supports an injectable shortcut_factory for tests and lazily creates native QShortcut Up/Down handlers with WindowShortcut scope, no autorepeat. They exist/enabled only for active ready question-side MCQs; callback additionally checks native reviewer.state=='question'. Callback evaluates cramNative.moveBlank(delta) explicitly in reviewer.web, irrespective of bottom-bar focus. render()/emit()/invalidate() synchronize enable state. State exit/fallback/reveal/waiting disable; profile close disables/deletes and clears them. Number/rating/Space/E/B/undo callbacks remain original. DOM arrow listener remains as a fallback; Qt-owned physical arrows consume the event once. No rating, reveal, queue or Anki collection write is introduced.

live.js selectBlank()/moveBlank() and app.js selectBlank() centralize index validation, wraparound, question-only guards, optional nearest-group scrolling and fill/highlight. Mouse choice/blank clicks and focusin on choice buttons update the same target; choosing an option keeps other selections unchanged. Keyboard arrows do not auto-advance to another question, reveal or mark anything. Public cramNative.moveBlank supports native Qt callbacks. Fill functions expose aria-current only on the active blank. Grading/reveal removes active markers. Active choice-group labels use a small CSS dot instead of explanatory guide text. Text/choice/panel DOM nodes stay mounted while navigating.

MAIN MCQ now wraps its clue in .question-panel; native wraps .cl-clue inside .cl-question-panel within existing question-body. Styles add gentle rounded surfaces/shadows, padding and separation, no visible panel border. Existing source text, numbered blanks, list layout and rich heading HTML are untouched. Text zoom selector updated for MAIN's nested clue; native font logic already finds descendants. Flashcards and image occlusion do not get the panel. The question may grow for long content; choices stay below it. No screenshot is used as a runtime asset.

appearance.py/js adds optional six-digit hex role 'question', preserving settings schema version1 and missing-key backward compatibility. Shared palette() derives the panel from card/accent (~3.5% accent light,7.5% dark) when no override exists. apply() sets MCQ-only --cram-question-panel, --cram-blank-active and --cram-question-shadow; switching view/reset clears the managed variables. Flash/IO remain unaffected. Active selection is subtly emphasized; filled inactive blanks have transparent background so they are not indistinguishable from the current target.

Customizer shows Question panel only for Multiple choice, with 'Match card automatically' on by default. Unchecking stores the current derived color for explicit editing; checking deletes the override. Editing Card/Accent while automatic updates the derived swatches and preview without accidentally freezing the panel color in the full custom palette. An explicit override stays fixed across other palette edits. Default/reset removes it. Existing independent Light/Dark palettes, source-checked iframe, Save/Cancel, mode previews and stable drag/size behavior are retained. Synthetic preview uses the actual new panel classes and active marker. No external font/asset/library is added.

110 fast Python tests and expanded DOM interaction checks pass. New checks in existing test_live_review, test_appearance and test_ui verify native Up/Down enable/callback/disposal with a shortcut factory spy; web/Qt routing, mouse/blank/focus synchronization; one active aria/highlight; preserved picks and stable question/panel nodes; answer-side guards; panel color persistence/validation/automatic derivation/override and customizer auto-toggle behavior. There is no actual Qt/Windows delivery, pixel/browser screenshot test or live Gemini validation. The ImageGen preview in chat was edited from the exact supplied target and is illustrative; do not call it runtime QA or package it with source/user deck content.

Source inspected for native callback preservation: https://github.com/ankitects/anki/blob/main/qt/aqt/reviewer.py (_shortcutKeys). No upstream source is shipped. Build.py's existing allowlists include all changed production/test files. Ship Cram-Studio-v1.6.1.ankiaddon and matching handoff with embedded identical installer/checksums.

## Earlier implementation and release history retained

# Continue Cram Studio 1.6.0

## Current update: complete card totals and deck-wide regeneration

This is the same full add-on/package cram_studio. Retain shared profile storage, API keys, cache/history and both mode boundaries. MAIN CRAM remains read-only independent practice; ANKI CRAM delegates queue/reveal/rating/interval/undo to Anki. Study List is separate and untouched.

The user's screenshots showed a selected lesson with only2 cards BEFORE filters even with All/All questions, plus parent rows showing0. Root causes in the old code: catalog counted only current cards.did, excluding cards whose odid linked to the selected home deck while borrowed by a filtered deck; parent labels showed only directly owned cards. The screenshots cannot prove how many cards the user's collection contains or that all missing cards are borrowed; do not invent their true count.

content.catalog now reads sparse (did,odid,count) groups. Each group has current did and home=odid or did. Deck count is direct logical membership (current or home), total_count includes descendant deck membership and counts each physical group once, borrowed_count records borrowed home members. scope_groups exports only grouped IDs/counts to the picker, not card fields. Frontend union-counts selected current/home membership instead of summing overlapping deck totals. With Include subdecks on, parent row labels use total_count; off uses count. All questions/limit0 is now the frontend default. Refresh next to deck picker reloads catalog through existing bootstrap while preserving selection/filter state.

count_matches and new scoped_rows use parameterized current did OR original odid membership, deduplicating card IDs across500-ID batches. Selecting a regular home deck includes borrowed cards read-only; selecting a filtered deck alone still selects its current contents. snapshot normalizes row deck labels to a selected home when present, otherwise current selected filtered deck, then delegates all raw filters and sorting as before. Cloze rows now use each actual card row's normalized deck label, preserving sibling lessons when split across different decks. Do not move/empty/rebuild decks to implement membership. All stays all independent cards, not daily-limited due queue. Native review queues are untouched.

bulk_choices.py validates a bounded explicit deck selection and forces modeexam, limit0, filters{}, created order for the full deck regeneration plan. snapshot provides MAIN's mapped/grouped questions; actual Basic/reversed cards are additionally passed through native review_question(col.get_card(cid),...) to cover template directions distinct from MAIN's shorter-term mapping. Deduplicate by content cache key. Only reads occur; no rating/scheduler API is called. Long/image-only/unsupported native templates are not made into AI MCQs.

deck_choices.py is the dedicated normal native Qt dialog: checkbox family tree, Include subdecks, full Preview stats, Gemini settings, Regenerate N sets, Pause/Resume and Close. Uses existing QueryOp read operations, shared profile Store and stdlib Gemini client. API generation starts only after the user clicks its generate button; preview does not call Gemini. Replaces previously cached sets deliberately. No practice filter or count limit leaks into the deck-wide operation; the dialog labels that scope. Small batches use existing generate_batches. The worker captures client/store/jobs/cancel token, tracks complete batches and resumes only unfinished jobs after pause/quota failure. Already completed keys are retained across selections in the same dialog. Closing cancels later batches and suppresses callbacks; an in-flight request may still cache its completed batch. No persistent unfinished-job queue exists. Run tokens prevent late progress updates overwriting a completed/resumed UI state.

Entry points: MAIN home beneath Start studying; ANKI CRAM below ready unanswered MCQs next to single-question regeneration; Tools → Regenerate deck choices. Main bridge passes current selected decks/include-children only effectively (bulk planner ignores other config fields). Native preselects its current deck, including filtered decks. Root modal lifetime pauses MAIN's auto-continue and guards conflicting active generation. After completion/close, changed keys may refresh only the SAME cid/epoch question-side native MCQ with all slots cached. Revision increments reset picks; answer-side/changed cards are never replaced. No reveal, rating or navigation occurs. In-flight batches finishing after dialog closure are simply available for later cards.

107 bounded Python tests and DOM checks pass. tests/test_deck_choices.py uses read-only SQLite and native spies: accurate parent/direct/borrowed membership, overlap and500-batch deduplication, unchanged collection dumps, filters/limit bypass for full-deck plans, Basic direction coverage, cached replacement, pause/quota resume and active-native refresh/reveal guard. DOM checks cover home totals/checkboxes, all-question default, Refresh and bulk entry. Fixtures in test_core/test_filters_session now include Anki's real odid column. New production files and regression file are in build.py allowlists. No real Qt/Anki, pixel rendering or live Gemini generation was run; do not claim that validation.

Authoritative Anki behavior consulted: https://docs.ankiweb.net/manual/filtered-decks (home deck links and temporary movement). The membership change is a read-only view over that link; native queue/scheduling operations remain untouched. Deliver full Cram-Studio-v1.6.0.ankiaddon plus complete matching handoff, with identical embedded installer and verified checksums.

## Retained earlier implementation and history

# Continue Cram Studio 1.5.1

## Current update: context-aware distractors and multiline choices

This is the full continuation of package `cram_studio`, including shared appearance from1.5.0. Keep all UI and profile identities. MAIN CRAM stays independent; ANKI CRAM stays only the native reviewer presentation. Study List is separate. No scheduler, rating, FSRS, collection or native undo behavior is added/replaced.

Gemini already received clue text before this release. The update strengthens its instructions to read the whole question first and evaluate each wrong choice against BOTH the full clue and correct answer, including qualifiers and grammar, favoring close concepts/common misconceptions while excluding other valid answers, synonyms and mere answer-similar words. Questions and correct answers are locked. Each job includes structured other_blanks answers for the same current question; they provide context, never add tests for another cN. Multiline/list distractors should match the complete source list's count/order/numbering/newlines. No extra model call is made for verification; semantic wrongness cannot be proven locally and must not be claimed fully tested.

`content.py` adds ChoiceText/choice_text: clean HTML → safe plain visible option text retaining explicit br/block/newline layout, ordered-list markers/start/li-value and nested indentation. Basic and cloze slot.answer now use this; answer_html retains the actual sanitized field for flashcards. valid_distractors preserves lines but keeps existing distinct/nonempty/600-character constraints. plain() is intentionally unchanged for flattened matching/length heuristics. SafeHTML now preserves bounded integer ol.start/li.value. Do not insert option strings as raw HTML.

PROMPT_VERSION=2 invalidates old generation keys without deleting existing cache/history. Cache keys include multiline clue, model, target answer/number, plus all same-question slot answers because other_blanks affects generation. New sessions need generation for new keys. Normal generation and explicit MAIN regeneration both use prepare_choices, ensuring the same full structured context. dialog.py wrong-option editor uses QPlainTextEdit/toPlainText rather than single-line edits.

MAIN choice-text and native cl-choice-text use pre-wrap, left alignment and min-width0; selected/revealed cloze option text also pre-wraps. Both buttons and blank text stay escaped/textContent. Newlines do not affect exact choice-index grading. MAIN Regenerate choices remains below an unanswered MCQ card; during background generation it is disabled until Pause. Its existing single-question replacement clears prior selections and never rates Anki.

ANKI CRAM status adds one functional Regenerate choices button below a ready unanswered MCQ. It has no new shortcut guide/toolbar. Backend action regenerate → generate(force=True), bypassing cache for that current question's slots, not an entire deck. Existing choices/picks stay mounted while generating and on error; the successful current-card question-side callback force-attaches and increments choices_revision. live.js detects this explicit revision, clears selections and redraws only choices; ordinary status/theme updates retain them. Stale cid/epoch results and answer-side callbacks cannot replace the displayed question or grade/advance. Native bottom buttons/intervals remain Anki-owned. A forced request queued behind another card's worker retains its force flag when the first finishes. Failed regeneration preserves existing usable choices and saved cache; partial multi-batch output can still be retained in cache by the existing batch writer, but is not force-applied to the current display on failure.

Regeneration works on the question currently studied from any deck. It is not whole-deck regeneration. Shared profile cache is keyed by content, so identical question/answer content may reuse generated sets across decks; do not claim per-deck caches. Cards from other decks are never fetched as distractors.

95 fast Python tests plus DOM regressions pass. New tests/test_choices_update.py covers source/list forms, nested numbering, preserved Basic/cloze answer choices, context/jobs/prompt contract and cache revision, native force/failure/reveal-race/queued requests. DOM tests cover both modes' choice text/newlines, regeneration visibility/message, unchanged picks while pending/error, reset after success, and untouched native rating DOM. Tests use a fake API/native reviewer and DOM; no live Gemini call, real Qt/Anki or pixel-layout verification was available. Never claim semantic distractor quality was empirically measured. New files are allowlisted in build.py. Ship the full .ankiaddon and matching source ZIP with identical embedded installer/checksums.

## Retained appearance implementation and earlier releases

# Continue Cram Studio 1.5.0

## Current update: shared appearance editor

The full installer and this source are the continuation of the exact existing add-on, package `cram_studio`. Install over the existing release and restart Anki. Do not rebuild the interface from scratch or change either mode's scheduling boundary. Study List remains separate and untouched.

Entry points: **Anki → Tools → CUSTOMIZE CRAM** and **MAIN CRAM → Settings → Customize Cram → Open**. New dialog has Flashcard size and CUSTOMIZE CRAM COLOR, Save/Cancel and separate reset controls. It opens maximized with native window controls, no instructional paragraphs. Preview supports MAIN/ANKI, Light/Dark, question/answer, and flash/MCQ for colors. It uses synthetic tissue/cloze samples, never real notes or Gemini.

`appearance.py` validates and normalizes version-1 data under existing profile preferences['appearance']: size width35..100%, height30..85%, null = renderer default; light/dark × flash/exam palettes, empty = renderer's exact default. Only eight six-digit hex color roles are accepted. No storage location/migration/schema-version or collection API is changed. Invalid Save does not mutate profile data; corrupt existing appearance falls back visually without overwriting the stored value. Profile/API key/cache/history remain intact.

`customize.py` owns a private bounded `cram_custom:` bridge: ready, save, cancel. Drafts stay in the webview until Save. Save validates, writes existing atomic profile Store, emits appearance to open MAIN/native views without re-rendering/requeuing cards, then closes. Modal open/close pauses MAIN's auto-advance (also when opened from Tools). Closing does not automatically resume a pending next action. Native reviewer ratings/undo/queue remain Anki-owned.

`web/appearance.js` shares canonical config, renderer/theme-specific defaults, validated palette mapping, derived contrast/tints, percentage geometry and the centered-edge resize helper. apply() clears managed CSS/classes then sets only needed overrides on the current card's root; default returns to the original CSS, IO is excluded. Width-only/height-only edits preserve the other renderer default. `appearance.css` implements bounded responsive dimensions and native canvas colors; min-height is cleared for custom MAIN flash size so the mobile default cannot override a smaller chosen frame. Preserve stable nodes, picks, current index and first-flip double-RAF behavior.

`web/customize.js/css/html` are the settings shell. A source-checked iframe loads actual app/live/appearance CSS and `customize-preview.js` via same-origin Anki web exports. Two preview scripts use properly closed script tags. Live drag stays inside preview, captures the pointer and changes styles only; parent updates config/fields without recreating/echoing the iframe. Resize handles are width/right, height/bottom and corner. Sample native footer occupies72px; native preview geometry uses the remaining simulated reviewer viewport so the real ratings bar is represented without overlap. Size is percentages, not saved device pixels. Layout may cap sizes on narrow/zoomed windows. Colors apply only to flash/MCQ; native footer remains Anki-owned, matching the settings scope.

MAIN CRAM persistent under-card shortcut/self-marking and repeat-mode instructional text is removed; optional help in Settings/? remains. Mode labels distinguishing independent practice/native scheduled review remain, preventing scheduling confusion. No current native guides are restored.

86 Python tests and expanded DOM tests pass in under a second. Test cases include bridge Save/Cancel/invalid data, file roundtrip, preservation of unrelated profile data, in-place native packet updates, MCQ picks/node identity, four palette scopes, default/reset, malformed input rejection, source-checked iframe messages, correct script closure, pointer capture and auto-advance pause. The DOM harness simulates events and geometry; it does not prove real browser paint, pixel layout, Windows/Qt behavior or live Gemini latency. No long tests, dependency installs or live API calls were run. On desktop, verify handles in both preview modes, tiny/large sizes, themes/colors/reset/save/cancel, current card preserved, native ratings/undo and Ctrl-wheel text versus outside-card interface zoom.

New files: appearance.py, customize.py, web/appearance.js/css, web/customize.html/js/css, web/customize-preview.js, tests/test_appearance.py. Existing build.py allowlists each new shipped file and test. `node tests/test_ui.cjs` includes new appearance checks. Run the bounded existing checks then build.py to produce the complete .ankiaddon and handoff with embedded identical installer/checksums. Do not ship profile data or downloaded tool helpers.

## Earlier change history and compatibility boundaries

# Continue this exact add-on

Current release: **MAIN CRAM + ANKI CRAM 1.4.2**. Package identity: **cram_studio**.

## 1.4.2 ANKI CRAM only — clean layout and F11 menus

The user explicitly restricted this update to ANKI CRAM. Preserve every MAIN CRAM implementation file and its guides/settings/buttons unchanged. MAIN CRAM's in-app version text remains 1.4.1 because its app.js was deliberately not edited; the shared installer manifest is 1.4.2. Keep package identity cram_studio, original profile data, and Study List untouched.

The ANKI CRAM header has 1fr/2fr/1fr symmetric tracks: brand left, deck/status in the middle, small exit X right. Removed the duplicated Edit/Browse/Undo controls, text-size toolbar/percentages, shortcut guide and instructional MCQ captions. Native keys still delegate to Anki; Ctrl/Cmd+wheel and reset stay functional without on-screen buttons. Only the duplicate native bottom Edit button is hidden in ANKI CRAM's scoped bottom CSS; rating/preview buttons, labels/intervals, More and native callbacks are retained. Full Anki answer remains available after reveal.

live.css uses an adaptive cl-card-height (up to 74vh/dvh, with viewport-space allowance), shared by both flashcard faces and the MCQ minimum area. The old native flashcard 58vh/650px limit is removed. MCQ's clue body centers within remaining space above choices; long/multi-slot questions can grow without losing content. The occlusion preview height, masks, zoom, and viewer behavior are retained. The 1.4.1 two-frame first-flip helper remains unchanged.

Official Anki main.py was inspected: the main webview Leave event calls mw.show_menubar() in fullscreen, including when entering the bottom rating area. LiveReviewer installs a temporary instance-level wrapper during native review and restores it when leaving/closing/failing startup. Its predicate requires active review, mw.fullscreen and actual mw.isFullScreen() where available, avoiding the shared flag being set for another window. Missing APIs are tolerated. The wrapper delegates normally when fullscreen is off; restore does not clobber a later add-on wrapper. No window/fullscreen/bar preferences, scheduling values, queue logic or ratings are changed.

78 short Python checks plus the DOM harness pass, including flash/MCQ clean headers, fullscreen hover suppression/restoration, other-window handling, profile closure/failure cleanup, later add-on wrappers, original keyboard callbacks and first-card paint boundaries. No real Windows/Qt/browser pixel verification was available. Deliver the full Cram-Studio-v1.4.2.ankiaddon and matching source/handoff ZIP.

## 1.4.1 first-card flip fix retained

`web/live.js` uses one `flipToAnswer(scene)` helper for compiled and original-renderer answer scenes with a front snapshot. It commits the initial turn style/layout, then uses nested requestAnimationFrame callbacks to leave a front-paint opportunity before adding is-flipped. The previous single RAF could change the transform before the first front was rendered, producing an instant answer on a cold first card. `web/live.css` explicitly starts cl-turn at rotateX(0deg). Callbacks use the captured scene, isConnected, card ID, epoch and answer-side guards, so stale work cannot flip a subsequent card or an undo/edit redraw. Keep reduced-motion behavior intact. Native fallback with no prior front snapshot still displays its original answer immediately.

A new DOM regression uses queued animation frames in fresh contexts for both display=flash and display=native, checks the first and later cards, and cancels detached/changed-epoch scenes. It does not simulate actual browser paint. The existing DOM interactions pass; real desktop Anki/Qt remains unverified. Only presentation timing/version/docs changed; the scheduler/controller and stored user data are byte-identical to 1.4.0. Ship the full Cram-Studio-v1.4.1.ankiaddon plus the matching handoff ZIP, retaining package identity cram_studio.

## 1.4.0 naming and UI behavior retained

User-visible names are exactly MAIN CRAM (independent practice) and ANKI CRAM (native review presentation), including Tools entries, overview buttons, native start dialog, window/session headers and settings. Preserve these names to avoid scheduling confusion. MAIN CRAM always labels its schedule as unchanged; ANKI CRAM labels actual native scheduling or filtered preview according to resched. MAIN CRAM keeps its practice count/order/filter controls and never answers an Anki card. ANKI CRAM uses Study Now's actual native queue and contains no replacement count/order controls. Do not merge those flows or silently switch modes.

ANKI CRAM now supports Ctrl/Cmd+wheel text zoom inside flashcards/MCQ, plus text −/+/Reset and a shortcut guide. Outside cards it delegates interface zoom to the native reviewer and bottom webviews, restoring previous zoom on mode exit or profile closure. Text zoom is profile-local, stored in the existing shared preferences; no collection edit is involved. JS measures text-host fonts before applying sizes, preserves original inline styles/priorities, leaves images/card dimensions untouched, and ignores scripts/SVG/math/canvas text. Native/Qt reveal/rating shortcuts are retained.

Supported Basic/cloze flashcards now have display='flash' and use the same sanitized compiler/numbered cN blanks as MAIN CRAM. Both faces use a vertical rotateX flip; cloze answers fill their original sentence. Full original Anki answer is included after reveal. Basic/reversed direction still follows the actual card template. Typed, scripted (front OR back), unsupported or unmapped templates use display='native' with original rendering. Explicit Use original flashcard still means original rendering, even if a compiled question exists. Supported IO and MCQ keep their existing displays and actual-card isolation.

The installer remains Cram-Studio-v1.4.0.ankiaddon with package identity cram_studio, for an in-place update. Keep the existing profile path/keys/cache/history and Study List unchanged. 74 Python checks plus expanded DOM interaction checks pass. Tests cover rich text zoom/reset, stable card/image nodes, compiled c1 faces, native original answer access, unchanged rating buttons/intervals, native queue delegation and filtered schedule boundaries. Real desktop Anki/Qt/Gemini execution is still unverified.


1.3.1 adds a native **Tools → Answer in Cram Interface** action because the user's customized deck overview did not show either Cram button from `overview_will_render_bottom`. The screenshot alone does not establish whether a theme suppressed the bottom hook or an older release was loaded. The new action bypasses overview HTML entirely. Open a deck first; other states show an explanatory message and do not launch/restart review. This is the complete 1.3.0 release plus the entry-point fix; no review, scheduling, practice, or card UI logic changed. Both releases retain the same package identity. The user navigation image is an annotated illustration and is not runtime verification.

1.0.1 fixes the user's screenshot showing a permanent “Opening Cram Studio…” screen. Anki's stdHtml can load an add-on script in the head, before body elements exist; QWebChannel initializes asynchronously at DocumentReady. The original code immediately accessed a null root and/or silently discarded its ready message. Startup now waits for DOMContentLoaded, polls for the bridge with a 10-second bound, then waits up to 15 seconds for the catalog before showing Retry. A late response still recovers; backend errors are visible before a catalog exists. Bootstrap requests are deduplicated in Python. Do not remove either readiness check. The original JavaScript was run against the new startup harness and reproduced the null-root crash; the updated code passes.

Official integration reference inspected: https://github.com/ankitects/anki/blob/main/qt/aqt/webview.py . No new external service is used by startup, and opening the window makes no Gemini request. Native Anki/Qt execution remains unverified in this environment; these are simulated startup-order regressions.

This is a NEW separate independent-practice add-on commissioned alongside the existing Study List (`studylist_quizlet`). Do not replace, disable, rename, merge with, or reconstruct Study List. Do not recreate Cram Studio from its description. Edit the exact supplied source and preserve its UI unless the user explicitly requests a design change.

## Native review integration retained from 1.3.0

The same add-on package now includes an opt-in **Answer in Cram Interface** button in a deck overview, beside the existing controls. Flashcards and Multiple choice are chosen in a native Qt dialog. `live_review.py` is a PRESENTATION ADAPTER to mw.reviewer, not a scheduler. begin() invokes mw.overview._linkHandler('study'), the same entry point as Study Now. card_will_show changes HTML only in the opt-in reviewQuestion/reviewAnswer context and for the current actual card. Browser/preview/ordinary Study Now return original HTML unchanged. The default independent Cram dialog still uses its own PracticeSession and never rates an Anki card.

**Scheduling boundary is essential:** do not implement next-card queues, calculate review intervals, call answer_card/build_answer/col.sched, write revlog/cards, change filtered-deck resched flags, change deck limits/presets, or create a second undo stack. Keep Anki's bottom bar HTML and native ratings/interval labels. Its original callbacks do the actual review operation and next-card advance. Preview-mode filtered decks may expose a different number of buttons on old versions; preserve whatever Anki supplies. The skin adds only scoped bottom-bar CSS while active. Anki's own Show next review time preference controls interval visibility.

state_shortcuts_will_change wraps existing 1–4 callbacks only while live review is active: on the QUESTION side of a ready MCQ, it selects a choice in the view; on the ANSWER side the saved original callback runs. E/B/Space/Ctrl+Z and every other binding are untouched. Edit/Browse/Undo toolbar actions delegate to mw.onEditCurrent(), mw.onBrowse(), mw.undo(). Do not add a state_did_undo invalidation hook after native redraw: it would destroy the fresh presentation state. Native question renders already increment the epoch and clear choices after undo. Leaving review disables the skin so ordinary Study Now remains normal.

Original-renderer fallback flashcards retain Anki HTML/scripts/typed-answer behavior. Supported Basic/cloze flashcards now use the 1.4.0 shared compiler display described above. Vertical rotateX faces use a sanitized noninteractive DOM snapshot only for the previous front; IDs are renamed and SVG fragment references updated so snapshots cannot steal native typeans/mask IDs. This snapshot is cosmetic and never calls a rating. Native images/audio/typing are otherwise rendered by Anki. Live MCQ extracts only the current actual cN; Basic/reversed direction follows its template fields rather than the shorter-field heuristic. Typed-answer templates and unmapped/complex custom templates use native flashcards. Unsupported native IO masks also fall back to original HTML, rather than skipping the scheduled card. Supported IO retains active masks, headers, a fixed zoomable preview, reveal, a larger viewer and return controls.

Live MCQ does not auto-grade on selection. Native reveal displays feedback and keeps native rating buttons; a Full Anki answer detail preserves extra original content. Native Space behavior on the answer side follows Anki's own preference, including any default-rating behavior. Independent automatic-continue/repeat-mistakes timers are never used in live review.

Missing choices can be generated per card. The start dialog's automatic-generation checkbox defaults off and explicitly authorizes current-card text/API quota usage. Gemini settings and choice cache are shared per profile, but no live-review result is written to independent practice history. storage.profile_store() now returns one shared Store per profile so two windows cannot overwrite each other's cache/preferences. Only profile closure clears session keys/registry; closing the independent window does not remove the live mode's key. Worker captures a Store/client; cancellation and epoch/worker guards prevent stale results from changing the next card or profile. Native render/reveal/rating/undo never wait on Gemini. A failed API request leaves the card available as a native flashcard.

Independent Cram now uses vertical flips; flip tutorial text is removed; deck chevrons are geometrically centered; underscore blanks are inline-blocks without an extra border/text-decoration underline. Catalog explicitly requests filtered decks with an old-version fallback. Search is still passed to Anki verbatim within an AND group, with tag/flag/note-type refinements; quick buttons are optional conveniences, not a search allowlist.

ordering.py discovers all native sortable card columns and uses native direction enums plus find_cards(order=column,reverse=...) without changing Browser preferences. Added random-note/card-type/deck patterns and native-Due tie-break presets; apply limits only after ordering. The independent practice list is a selected-card set, not the actual daily scheduler queue. Live review always inherits actual Anki order, learning steps, sibling burying and per-deck/daily limits.

74 Python regressions plus the expanded DOM harness pass, including a scheduler/DB-rejecting native-reviewer spy, reschedule on/off invariance, original callback/HTML preservation, actual-card direction, arbitrary filters, current filtered-deck location, native ordering, late workers, MCQ phase changes and stable IO nodes. No real desktop Anki/Qt/browser or authenticated Gemini was available here. Do not claim actual scheduling, filtered-deck undo or pixel layout was run in Anki. Source inspected: current and 23.10 reviewer.py, overview.py, main.py, GUI hooks, browser.py and reviewer TypeScript. Only the add-on source is shipped, not downloaded upstream files or failed runtime installs.

## 1.2.0 current behavior — keep these corrections

The latest user requests override any older merged-cloze description: **every mode tests one actual cN card at a time**. All same-cN spans stay together; other cNs are visible context. Learn gives one four-choice set per physical blank. Clicking a choice fills that blank via textContent, and changing the selection replaces it. Flashcard backs use the original clue HTML with controlled data-blank spans replaced by the corresponding sanitized answer HTML, retaining the whole sentence. No all-cN merged Learn question remains.

The fixed card is a CSS perspective scene with preserve-3d / rotateY back-to-back faces and backface-visibility hidden. Both faces remain mounted, so a flip changes classes/ARIA instead of reloading images. Fixed padding contains text; Ctrl/Cmd+wheel over the card adjusts only font sizes and saves text_zoom. Images and frame dimensions stay fixed. Outside the card, the wheel delegates to the Qt webview's zoom factor. The three rating/flip controls use equal centered columns, including their graded state. Reduced-motion disables transition.

Automatic continue defaults on: Learn after adjustable feedback (1000 ms default), flash after explicit Still learning/Got it (180 ms). Never auto-rate on reveal. Navigation, Options, guide and image viewer cancel timers; Space during feedback cancels the old timer before continuing, preventing double advance. Auto advance preferences take effect immediately; repeat-mistakes changes still apply to the next session.

Deck names form a sorted indented family tree with separate expand/collapse buttons and checkboxes. Search exposes matching descendants through collapsed branches. Session order is shuffle, created_asc/desc, or retrievability_asc/desc. Creation uses note IDs, with c1 before c2 on ties. Native retrieval order discovers Anki's sortable browser column, reads the protobuf enum direction and calls the public find_cards(order=column, reverse=...) API. Do not substitute ease/lapses/random scores. Older versions without the native column disable those options. Limit is applied after ordering.

Generation is progressive, with one small priority request for the first waiting question (up to 5 sets), then batches of 5. Questions get ready flags; flash/cached questions work immediately. The background worker writes cache, schedules a main-thread refresh, and emits choicesReady updates only when a question becomes ready. attach_choices(partial=True) preserves existing choice indices and never reshuffles an active question. Only ungraded questions are refreshed. Backend busy (collection/UI) is separate from generating; users may grade while future choices prepare. Pause/429 preserves results and cached work; pending questions offer Retry/Resume or per-question flash fallback. Stale token callbacks cannot mutate another session. Editing/regenerating waits for generation to pause. Explicit regeneration/manual edits use force=True, and retakes shuffle choices at a new launch. No API key or real Anki runtime was available for live latency/native verification.

Keyboard guide is in Settings or ?. Learn: 1–4/A–D select active blank; Up/Down changes active blank; Space/Enter checks/continues. Flash: Space/Up/Down flips, 1/2 rates after reveal, arrows navigate answered questions. User wanted Quizlet-like shortcuts; only officially verified common patterns are called Quizlet-style. Do not claim a comprehensive exact clone of every Quizlet shortcut. Keys ignore inputs, modifiers and repeated keydown events. Existing native filters, honest scores and source boundaries below remain intact.

51 Python checks and the expanded DOM harness pass. New tests/test_v120.py exercises cloze isolation, ordering and progressive controller behavior. The DOM harness proves interactions and stable nodes; no screenshot/pixel QA, real desktop Anki, live Gemini or Windows DPAPI execution is claimed. Tests are deliberately bounded and fast.

## 1.1.0 changes authorized by the user

The user rejected the dashboard/marketing aesthetic and malformed-looking icons, supplying Quizlet screenshots. The current UI intentionally replaces that design with a white centered study screen, large fixed card with separate clue/answer faces, plain labels, numbered choices, simple complete SVG geometry, and a Settings modal. Preserve this new UI. No Quizlet branding, private account information, screenshot assets or remote fonts are shipped.

Native Anki filters were added: `search_query()` groups the raw search with tag/flag/note-type refinements, then `col.find_cards()` returns card IDs. Intersect these with the selected deck IDs BEFORE cloze grouping. Blank search skips the native parser and includes all selected cards. `count_matches()` uses the same scope for the Check matches control; frontend request IDs reject stale results. Invalid queries must surface, never fall back to all cards. `is:due` is Anki’s search result, including overdue cards, not the daily-limited scheduler queue. Do not import Study List custom stars or write any tags.

`session.py` owns PracticeSession. Default repeat_mistakes is false; saved per-profile under preferences. When enabled, a miss creates a deep copy at a random unseen position, with another question in between when possible. It keeps the whole cloze question/mask group; choices are reshuffled locally from cached wrong options, never regenerated over the network. Answered indices do not move. A duplicate grade cannot enqueue a second copy. Queue additions are returned in the graded packet and inserted into the web view’s unseen queue. Disabling the preference during a session affects the NEXT session, explicitly stated in Settings.

Summary earned/total/questions are FIRST attempts and original question count. final_earned/final_total/mastered/repeat_attempts/attempts are separate fields. Never overwrite an initial miss with a later correct retry. Retake/review uses original questions once, not accumulated duplicates. Three different c1 spans remain three numbered answer slots in one question, with independent four-choice sets and scores.

51 Python checks pass, plus startup/DOM/control checks for filters, card flip, preferences, retry insertion and results. Native Anki, live Gemini, and real-browser pixel rendering remain unverified here. Do not claim visual screenshot QA was performed. Refer to the user’s supplied references if further visual tuning is needed.

## User priorities

- A polished Quizlet-inspired interface; large readable study cards, a clean deck picker, blue/indigo accents, responsive light/dark layout, normal maximized desktop window with X and restore controls.
- Select subjects/decks/subdecks; flashcards, per-blank multiple choice, mixed practice and native image occlusion.
- Cramming must never affect the collection or its schedule, review history, FSRS, daily limits or new-card progress.
- All modes must blank only the current card cN, keeping repeated same-cN spans together. Multiple choice uses the same cN grouping with numbered physical blanks, separate four-choice sets, and partial credit. Nested outer deletions cover their inner deletion.
- Retain native occlusion behavior: reveal active mask group only; fixed preview frame, zoom/scroll inside it, separate larger viewer with X, reveal in both views, header visible. Keep the image element stable when revealing and moving between views.
- Gemini user-owned API key, native Qt private entry, Save/Test/Refresh model controls, structured validated wrong choices, original answers locked, per-content/model cache, five sets/request, pause/retry after quota. Never include keys in chat/artifacts/logs/web view. No automatic billing/model switch or local-AI dependency.
- Offer manual distractor editing and deliberate AI regeneration. Do not imply that semantic correctness can be fully checked programmatically.
- Every release must deliver a full .ankiaddon and a complete matching source/handoff ZIP. Keep the package identity for in-place future Cram Studio updates. Never ship user data, keys, real deck snapshots or caches.
- Connection drops frustrate this user: keep updates concise, use bounded relevant checks, no long tests.

## Source map

- `cram_studio/__init__.py`: additive Tools/deck entry points, window lifetime, theme hook.
- `live_review.py`: opt-in native reviewer presentation, original shortcuts/operations, scoped content/assets, per-current-card choices and stale-result guards.
- `live_start.py`: native mode selector and explicit automatic Gemini consent.
- `ordering.py`: native sortable columns, Due tie-breaking and note/card-type/deck patterns.
- `web/live.js`, `web/live.css`, `web/live-bottom.css`: scheduled review presentation; no ratings or independent practice queue.
- `dialog.py`: Qt window, native API-key/model/mapping/choice dialogs, allowlisted web bridge, read QueryOp, background Gemini work, backend grading/history.
- `content.py`: pure HTML cleanup, field mappings, cloze compiler, IO SVG groups, read-only SQL snapshot and native search intersection/counting, choice hashing/validation/attachment, grading.
- `session.py`: pure independent queue, optional random retries, first-attempt/final summaries, original-question retakes.
- `field_render.py`: field/cloze/native-IO parsing helpers recovered from the user's exact working Study List v0.6.15 handoff. This file was copied, not modified in the original add-on.
- `gemini.py`: stdlib urllib HTTPS REST client, structured JSON validation, model discovery, secret-safe error messages, incremental batch generation/cancellation.
- `storage.py`: atomic profile-local JSON, RLock, persistent cache and bounded history, Windows DPAPI key storage/session/environment key support.
- `web/app.html`, `app.css`, `app.js`: actual shipped UI. No remote framework/font/CDN. `window.cram.receive(event,data)` is the Python-to-JS interface; JS uses `pycmd('cram:'+JSON.stringify({action,...}))`.
- `tests/test_core.py`: pure/backend/API contract/SQLite read-only tests.
- `tests/test_filters_session.py`: native search delegation/intersection, repeated c1 slots, optional repeat queue, honest scoring and preferences migration.
- `tests/test_live_review.py`, `tests/test_ordering.py`: native delegation/scheduling boundary, template direction, stale callbacks, native filters and order behavior.
- `tests/test_v120.py`: current cloze isolation, native sorting and progressive-generation controller regressions.
- `tests/test_ui.cjs`: small DOM interaction harness. It exercises navigation and stable IO node identity but DOES NOT prove real-browser pixel layout or native Qt behavior.
- `build.py`: exact allowlisted package build and matching full handoff. Never package `user_files`, profile data, dpapi keys, secrets, caches or pycache.

Run `python3 -m unittest discover -s tests -v`, `node tests/test_ui.cjs`, `node --check cram_studio/web/app.js`, then `python3 build.py` from the extracted source root. Installer ZIP entries must be at the archive root, not wrapped in a cram_studio directory. The handoff contains the exact installer and per-file hashes.

## Honest validation limits / first checks in Anki

No live Anki, Windows DPAPI, real browser rendering or authenticated Gemini call could be run here. A pip attempt to obtain Anki/Qt timed out against the restricted package network. Do not claim the release was tested in desktop Anki or against a real Gemini account. Default `gemini-3.5-flash-lite` was verified against Google's current official model/pricing lists on 2026-10-22; 2.5 models are limited to prior users now, so do not revert to a 2.5 default. Model availability and quotas can change; keep refresh/test/settings functional.

After installation verify: Tools shortcut/window controls, checkbox selection with exact subdeck boundaries, Basic Auto and override, multi-cN flash/exam grouping and repeated cN, native IO rectangle/ellipse/polygon groups, preview/fullscreen sizes, no image reload on reveal, dark/narrow layouts, native Test connection, generation/cache/offline repeat, manual edits/regeneration, quota retry, per-blank scoring, mistakes-only retry, profile separation, and unchanged schedule/revlog. Unsupported legacy IO mask formats are skipped intentionally; add support only with representative sample notes to avoid exposing answers.

User data lives at `Path(mw.pm.profileFolder())/'cram_studio'`, not in this ZIP and not in the installed add-on source folder. Closing a window cancels subsequent batches; an in-flight request may finish and cache its batch. An unfinished session is not restored. History stores only completed summaries. Cache keys use prompt version+model+plain clue+blank number+correct answer; edits to content/model invalidate those sets. Image-only/long answers fall back to recall.

Do not introduce direct scheduler writes during compatibility fixes. Independent mode uses only `col.db.all(SELECT...)`, `col.find_cards`, deck/model catalog reads and `col.get_image_occlusion_note`. The opt-in scheduled skin delegates rating/edit/undo to Anki’s existing UI handlers; it never implements their collection operations. Preserve both boundaries. Changes should be incremental, versioned, and accompanied by a full matching handoff.
