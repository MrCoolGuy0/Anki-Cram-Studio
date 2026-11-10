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

# Earlier release history

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

# MAIN CRAM + ANKI CRAM 2.0.16

Install Cram-Studio-v2.0.16.ankiaddon over Cram and restart Anki.
Keep Cram-Studio-Handoff-v2.0.16.zip for exact continuation.

Gemini work now uses a small dedicated profile-owned worker pool. The previous
2.0.15 fix protected Anki's collection executor but moved generation into Anki's
shared general pool, also used by AnkiLink downloads and other add-ons. A busy
shared pool can delay generation before it contacts Gemini. The new route
starts independently of either Anki executor. All six Gemini entry points use
it, including single/deck-wide regeneration and Writing. Completion stays on
the main thread. Profile closure cancels queued tasks and rejects old callbacks.

The prompt, model selection, request body/schema, token limits, timeout and
per-generation batch sequence remain unchanged. No UI or scheduling changes
are included. Request/JSON/cache-save timing totals plus queue and worker time
are recorded locally in profile/cram_studio/generation-timings.jsonl. Logs are
bounded, contain only numbers/status and exclude API keys, URLs and study text;
logging errors do not fail generation. There is no remote telemetry.

247 short Python checks passed in3.55 seconds and the complete Node UI suite
passed. All six submissions started while both Anki worker pools were held busy.
Worker/result/error/close/cancellation/log-failure/privacy/rotation regressions
passed. A synthetic before/after request comparison verified identical request
bytes and generation method bodies. No real API call, user key, collection or
Windows session was used, so these checks do not measure real Gemini latency
or prove shared-pool contention was the sole cause on the user's PC.

# MAIN CRAM + ANKI CRAM 2.0.15

Install the full Cram-Studio-v2.0.15.ankiaddon over Cram and restart Anki.
Keep its matching Cram-Studio-Handoff-v2.0.15.zip for exact continuation.

Six network-only jobs (Gemini connection/model checks, MAIN CRAM choices and
writing, ANKI CRAM choices and writing, deck-wide regeneration) now use Anki's
non-collection worker pool. Anki's default background executor shares a single
worker with native collection operations, so a waiting request could stall a
native answer/next card. Actual card/catalog/search QueryOps stay serialized.
This changes worker assignment only: UI, customization, progress, AI prompts,
cache, grading/undo, queue order and filtered-deck settings are retained.

242 short Python tests passed in2.21 seconds and the complete Node UI suite
passed. Held-generation tests reproduce the old queue blockage and verify next
card work remains available after the fix. A separate local real TaskManager
probe verified Anki25.9.2's queue behavior. No live user collection, Gemini
request or long tests were run. AnkiLink1.1.2 fixes its own HTTP/media worker
assignment separately; Study List0.6.17 and Study Sounds1.1.8 remain unchanged.

# MAIN CRAM + ANKI CRAM 2.0.14

Install the full Cram-Studio-v2.0.14.ankiaddon over Cram and restart Anki.
Keep its matching Cram-Studio-Handoff-v2.0.14.zip for continuation.

MAIN CRAM's home screen now separates regular deck families from standalone
filtered decks. Nested filtered decks stay under their actual parents. Parents
still start collapsed; expand, search, multi-selection, subdeck scope and card
counts keep their existing behavior. No decks are moved, renamed or created.

Resume practice shows short current deck names, mode and progress. It shows the
two most recent sets first; View all and search keep every saved set accessible.
Full paths remain in hover titles, with short parent hints only where needed
to distinguish duplicate lesson names. Resume and confirmed Reset use the same
session IDs and stored queues. Nothing is discarded or migrated. Modes/options
align in a two-by-two layout, and lengthy search help is available on demand.
The colors and responsive spacing follow the existing light/dark theme.

This is a home-screen presentation update, plus read-only filtered-deck metadata
in the catalog. Native ANKI CRAM ratings, schedules, answer UI, shortcuts, Gemini
cache/choice generation, writing, images, custom sizes/colors and progress files
are unchanged. The session header displays only the current deck's leaf name.

Validation: 240 short Python checks passed in 1.25 seconds, plus the complete
Node UI suite. Actual Qt6.9.2 WebEngine renders were inspected in light/dark at
1440px and at a narrow 760px, with no horizontal overflow. A native Anki25.9.2
collection verified regular versus filtered deck metadata. Real Windows Anki
was not run. ADDON-PERFORMANCE-AUDIT.md records the separate review-delay audit.

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

19 short launcher/practice tests and JavaScript syntax checks also pass.

All quiz behavior, Writing border, scheduling boundaries, progress and saved
appearance from 2.0.11 are retained. No scheduler/reviewer implementation is
changed. Keep Cram-Studio-Handoff-v2.0.12.zip for exact continuation.

Historical release notes below apply to their named versions.

# MAIN CRAM + ANKI CRAM 2.0.11

Install Cram-Studio-v2.0.11.ankiaddon over the existing Cram add-on and restart.
This full update keeps the 2.0.10 practice fixes, saved progress and appearance.

The native deck overview now gets only ONE additional ANKI CRAM button, beside
its existing regular/filtered/finished-deck controls. The two-button MAIN/ANKI
wrapper from2.0.10 is removed. Existing buttons are not wrapped, moved, restyled
or resized. The new button inherits the adjacent control's class and inline
style and keeps its own label on one line. No global button CSS is added.
Cram no longer adds MAIN/ANKI links to the native bottom bar. If a theme already
shows Options/Empty/Description in the page, its duplicate native overview bar
is hidden; its prior visibility is restored before leaving overview, including
before normal review or ANKI CRAM. An existing already-hidden bar stays hidden.
Native rating controls and unrelated screens are not hidden. Study List's own
existing delayed visibility checks continue to place its fallback button.
The Tools entries and existing MAIN CRAM shortcuts remain available.

The MAIN Writing Check answer button now has an explicit complete border even
when disabled or styled by Anki's global button theme. Its response pane reserves
space for the frame. Correct final Enter, editable misses, second-Enter reveal,
held wrong feedback, restarting and individual IO masks from2.0.10 remain.

231 short Python tests, the full Node UI suite and a bounded Qt keyboard/mouse
check pass. The Qt check compares original buttons' exact HTML and heights
before/after insertion in regular/filtered/finished layouts, confirms exactly
one new button without a wrapper/style bar, and checks Writing borders under an
adverse disabled-button rule. Native bottom visibility restoration has separate
unit coverage. Synthetic data only; no live Windows Anki/collection was tested.

Keep Cram-Studio-Handoff-v2.0.11.zip to continue this exact source elsewhere.
Historical notes below apply only to their original releases; their two-button
entry and native bottom-link descriptions are superseded here.

# MAIN CRAM + ANKI CRAM 2.0.10

Install **Cram-Studio-v2.0.10.ankiaddon** over the existing Cram add-on and restart
Anki. This is the full same-package update, including all previous features.
Keep **Cram-Studio-Handoff-v2.0.10.zip** for exact continuation in another account.
Study List, Study Sounds and AnkiLink remain separate and unchanged.

- Visible MAIN CRAM and ANKI CRAM buttons are added to Anki's deck list and
  regular/filtered deck overview, including finished-deck screens. They recover
  after a theme redraw. ANKI CRAM opens the existing native setup for the selected
  deck; the button itself does not grade or start a review. The deck's menu also
  has Study in ANKI CRAM. Existing Tools entries and shortcuts remain.
- Practice questions and Question order now share aligned label/control tracks,
  with enough width for All questions and a narrow-window fallback.
- During a MAIN CRAM quiz, open Settings → Start over. The confirmation resets
  that practice's answers, retries, position and elapsed time. Random cards get
  a different order when there are at least two; fixed orders stay fixed. Saved
  choices, other unfinished sets, completed history and Anki scheduling remain.
- Wrong MAIN CRAM answers stay visible until Continue/Enter. The automatic
  continuation preference still applies to correct answers/Got it. Revealed
  MCQ sentences show the correct answer while the choices retain red/green
  feedback. Disabled choice borders and focus-ring space stay intact.
- MAIN CRAM Writing uses the same check/retry/reveal controls as ANKI CRAM.
  Enter checks; a miss remains editable. Enter again with the same unchanged
  miss reveals and finishes checking, so a correct answer is never mandatory
  before continuing. Editing the text checks the revision instead. A final
  correct Enter finishes checking immediately. Reveal answer also permits an
  incomplete attempt. Wrong feedback waits for Continue; ordinary typing still
  accepts spaces, Shift+Enter newlines and caret arrows. Accepted answers cannot
  be checked again by an accidental Enter or stale checkpoint. Writing's first
  attempt/missed-item scoring remains honest; reveal does not invent matches.
- MAIN CRAM image occlusion supports individually revealing and rehiding target
  masks with mouse or focused Enter/Space, including in full screen. The same
  image element is retained through reveal/zoom/viewer moves. Show/Hide masks
  remains available. Individual mask state is saved with paused practice. Mask
  taps do not grade a card or alter Anki scheduling; recall still needs a vote.

The deck-overview label “Click to reveal / hide” in the supplied screenshot is
not added by these versions of Cram, Study Sounds or Study List. Study List's
similarly named reveal controls are inside its own card-list window. The exact
other add-on/theme responsible cannot be identified from the screenshot alone.

229 short Python tests and the complete Node UI suite passed. A bounded real
Qt WebEngine test exercised the actual MAIN controller methods with synthetic
questions, real Enter/mouse input, fresh/fixed restarts, editable misses and
one-Enter completion, correct revealed MCQ text, held wrong feedback, aligned
controls at 1360/740 px, complete disabled borders despite a hostile theme rule,
individually tappable SVG masks and stable IO image nodes, and entry buttons in
regular/filtered-like/finished layouts. Screenshots were inspected locally.
No real user collection, Windows Anki session or Gemini API was used. Native
Anki ratings, queues, intervals, filtered rescheduling and undo implementations
are unchanged; existing boundary tests pass. This does not claim every possible
third-party theme or add-on combination has been tested.

Historical notes below describe their original releases. The behavior above
supersedes older MAIN descriptions requiring corrected Writing answers or
advancing automatically after misses.

# MAIN CRAM + ANKI CRAM 2.0.9

In ANKI CRAM Flashcards, Space reveals/flips the first time, then keeps flipping between clue and answer while Anki's rating buttons remain available. Space no longer chooses the default rating or advances a Flashcard. Choose Again/Hard/Good/Easy with the native buttons or 1–4. Rating shortcuts, intervals, scheduling and undo still belong to Anki. This also works when focus is in the native bottom rating WebView.

In MAIN CRAM Flashcards, Space always flips, including an already rated card; it no longer means Continue there. Once the answer has been revealed, Still learning/Got it remain available even when the clue is showing again. That display history is saved with the existing practice position. Explicit ratings, the existing Enter/Right/Continue actions and the configured post-rating automatic continuation retain their behavior. Space never submits a rating. The first reveal remains required before an ungraded card can be rated.

This is limited to ordinary Basic/Cloze/custom Flashcards in the two Cram interfaces. Ordinary Anki review, Multiple Choice, Writing, image occlusion, modified shortcuts and other add-ons retain their existing controls. In-session mode changes update Space's routing immediately. No new onscreen guide/buttons or visual styling are introduced. Existing 2.0.8 mode-transition fixes and 2.0.7 click/drag-to-copy behavior remain included.

Install **Cram-Studio-v2.0.9.ankiaddon** over the existing Cram add-on and restart Anki. Keep **Cram-Studio-Handoff-v2.0.9.zip** for exact continuation. Both files contain the full add-on and prior features.

223 quick Python tests and the complete Node UI suite pass. A bounded real Qt WebEngine test uses the actual controller, actual Space/1–4 shortcuts, separate card/rating WebViews, and native callback spies. It verifies repeated flips, first reveal once, Space while a native rating button is focused, preserved button nodes/labels, explicit ratings while showing the clue, normal MCQ Space, literal spaces in Writing, and restored ordinary-Anki Space after exit. Normal/filtered review boundaries and durable MAIN recall display state pass. No user collection, live Windows Anki/Rust scheduler or Gemini API call was used.

Historical notes below apply to their original releases. Older descriptions that Space always retains native default-rating behavior are superseded only for ANKI CRAM Flashcards.

# MAIN CRAM + ANKI CRAM 2.0.8

ANKI CRAM now keeps Multiple Choice on its own panel when switching from an already revealed Flashcard or Writing view. Missing choices no longer produce a flippable original flashcard. Cached choices appear immediately; enabled Gemini preparation can create missing choices after reveal, and Create choices remains available when automatic preparation is off. Loading/errors stay visible in the Multiple Choice panel. Once ready, choices stay visible and disabled with the correct answers marked; every blank's choices can be inspected. A reveal without any MCQ selections no longer reports a misleading zero-correct attempt.

Writing now displays **3 / 3 revealed**, for example, when all three answers are already visible. This counts revealed items; actual Writing attempts, accepted items and missed items are preserved. Question-side Writing progress and MAIN CRAM keep their existing counters.

Switching retains the same native card and revealed side. Ratings still require an explicit Anki rating; no mode switch, background completion or displayed counter rates or advances a card. Choices still preparing for the same card can finish after reveal. Existing ready choice sets are not forcibly regenerated/reshuffled after reveal, preserving selections and their indices. A next card, mode change, exit or stale worker cannot replace the wrong presentation. Unsupported templates and image occlusion retain their existing behavior. No size, color, matching or note-formatting changes are included.

Install **Cram-Studio-v2.0.8.ankiaddon** over the existing Cram add-on and restart Anki. Keep **Cram-Studio-Handoff-v2.0.8.zip** for exact continuation. Both are full packages with previous features. Existing valid cached choices need no regeneration; missing choices still require the configured Gemini key/preparation or an explicit Create choices request.

219 quick Python tests and the complete Node UI suite pass. A bounded real Qt WebEngine regression connects the actual controller to synthetic three-cloze cards and fake Gemini responses: Flashcards reveal, uncached/late/cached MCQ choices, repeated mode switches, partial Writing history, revealed counters and an explicit native rating shortcut. Representative screenshots were inspected. Source/installer/handoff/checksum and JavaScript syntax checks pass. No user collection, live Windows Anki/Rust scheduler or live Gemini call was used.

Historical notes follow and apply to their original releases.

# MAIN CRAM + ANKI CRAM 2.0.7

Flashcard clicks now flip even when you click directly on text or near letters. Dragging across the text still selects it for normal Ctrl+C/copy. Repeated/double clicks no longer select a whole word or paragraph. Releasing a selection drag does not flip the card. This applies to Basic and Cloze Flashcards in both MAIN CRAM and ANKI CRAM; Writing, Multiple Choice, image occlusion selection rules and controls/links/scrollbars retain their behavior.

A second issue was corrected in ANKI CRAM: its Multiple Choice blank-click handler also swallowed clicks on flashcard cloze words. The handler is now limited to Multiple Choice, so revealed cloze text can flip the flashcard too.

Install **Cram-Studio-v2.0.7.ankiaddon** over the existing Cram add-on and restart Anki. Keep **Cram-Studio-Handoff-v2.0.7.zip** for exact continuation. Both files are complete packages with all previous features. No choice regeneration is needed.

The complete Node UI suite and JavaScript syntax checks pass. Four bounded real Qt mouse scenes (MAIN/ANKI x Basic/Cloze) verify text-click flips, actual held-mouse text selection, Ctrl+C clipboard contents, rapid clicks, Qt double-clicks without word selection, and no automatic grading/rating. Native question clicks delegate one existing Show Answer command, and answer-side flips remain visual. All Python implementation files are byte-identical to2.0.6; no scheduling, matching, storage or generation change. No real user collection, live Windows Anki/Rust scheduler or Gemini request was used.

Historical notes follow. Older instructions saying a stationary click on letters must NOT flip are superseded by this explicit user request.

# MAIN CRAM + ANKI CRAM 2.0.6

Filled Multiple Choice blanks now flow inline with their sentence or list item. Long terms such as the IEEE and ITU organization names no longer sit in a tall inline-block box that moves the bullet beside the last line. Raw pasted newlines inside a term collapse to ordinary spaces; narrow panes still wrap naturally. Intentional source BRs, paragraphs, numbered/bulleted lists and preformatted lines remain visible. Choice buttons retain their existing text/formatting.

This is display-only, in both MAIN CRAM and ANKI CRAM. Original note HTML, cached answer/choice strings, answer indices, grading, Gemini cache keys, Writing, flashcards, image occlusion and native scheduling are unchanged. No regeneration or note editing is needed. The 2.0.5 mode menu, image viewer, Writing input/caret fixes, feedback and matching updates remain included.

Install **Cram-Studio-v2.0.6.ankiaddon** over the existing Cram add-on and restart Anki. Keep the matching **Cram-Studio-Handoff-v2.0.6.zip** for exact continuation. These are full packages.

The complete Node UI suite and JavaScript syntax checks pass. A bounded real Qt WebEngine regression checks four MAIN/ANKI layouts at1360px/540px: IEEE/ITU source-newline handling, bullets aligned with the first text line, inline styling, preserved explicit BRs and native revealed-side redraw. The regression fails with 2.0.5 styling and passes after the correction. Representative renderings inspected. Every Python implementation file and other UI/controller file outside the two display callers/shared appearance files is byte-identical to2.0.5; its 215-test backend validation remains applicable. No real user collection, live Windows Anki/Rust scheduler or Gemini call was used.

Historical notes follow.

# MAIN CRAM + ANKI CRAM 2.0.5

## ANKI CRAM controls

Use the small Settings/sliders icon beside X in the ANKI CRAM header to change the current card between Flashcards, Writing and Multiple Choice. The card, native question/revealed side, queue and rating buttons stay the same. Switching does not reveal, rate or advance. Unfinished choices, Writing draft/target and checked Writing items survive switching away and back on the same card. The chosen mode is used for subsequent cards and remembered for the next start. Normal Study Now and MAIN CRAM receive no in-session mode menu. Image occlusion keeps its image recall view in every mode; unsupported templates keep their native rendering.

Double-click an attached image in ANKI CRAM to enlarge it. X or Escape closes it; +, −, Fit and Ctrl+wheel zoom inside the viewer. Double-clicking image occlusion opens its existing masked viewer. Generic image enlargement cannot reveal an unmasked occlusion image. Images keep their aspect ratio. Unmodified rating shortcuts are guarded while the Settings menu or photo viewer is open; explicit native ratings continue normally after closing/revealing.

## Writing corrections

The input starts at one line instead of two and grows with the text, up to a capped scrolling height. Shift+Enter inserts a line break. Plain Up/Down move the text caret and scroll the input to its line; Alt+Up/Down change the active blank. Qt's native arrow shortcuts no longer steal caret navigation while the Writing input is focused. Existing Enter/check, editable wrong attempts, second unedited Enter/reveal, final-match/native ratings and scroll-to-filled-blank behavior are retained.

Wrong AND incomplete checks now show a red warning; successful matches still have no green Matched banner. `frame check sequence` or `FCS` can match the authored `frame check sequence (FCS)` because the initials are verifiably repeated information. The authored display remains intact. This is a local initials check, not arbitrary synonym matching: unmatched parenthetical qualifiers, changed numeric references, negation and unrelated acronyms remain required/rejected.

Gemini grouping now explicitly treats two independently requested terms as a list, including `Ethernet sublayers` → `LLC and MAC`, while keeping compound terms/statements together. Writing grouping cache policy advances to refresh older classifications on fresh questions; existing saved MAIN sessions retain their stored plans. Ambiguous prose still needs enabled Gemini preparation/a key; offline/failed preparation retains a whole answer. No claim of perfect model classification or live API verification is made. Switching out of an initially selected Flashcards mode now honors the saved Gemini preparation opt-in/opt-out. Cached Writing groups becoming ready are emitted immediately rather than leaving a waiting view stale.

## Install and verification

Install **Cram-Studio-v2.0.5.ankiaddon** over Cram Studio and restart Anki. Keep **Cram-Studio-Handoff-v2.0.5.zip** for exact continuation. This is the full same-package add-on; profile settings, colors/sizes/images, cache and sessions remain. Study List and Study Sounds are separate and unchanged.

215 short Python tests, the complete Node DOM suite and JavaScript syntax checks pass. Qt WebEngine checks cover existing layouts/customizers/formatting, actual Enter/reveal flows, current-card switching through the real controller, draft/choice restoration, multiline caret movement despite real Qt arrow shortcuts, image fitting, Settings/viewer rating-key protection, and an explicit native rating callback after revealing. Four image-first scrolling scenarios also pass. Representative menu/viewer images were visually inspected. These use synthetic notes/native callbacks: no user collection, Windows Anki/Rust scheduler integration or live Gemini call was used.

Historical release notes follow.

# MAIN CRAM + ANKI CRAM 2.0.4

Writing now keeps the answer you just entered in view inside the question panel. It remembers the matched or selected blank, scrolls to it after a check or reveal, and restores it when ANKI CRAM redraws the answer side. A leading image no longer leaves the revealed answer below the visible area. Partial enumeration answers remain visible while the input keeps keyboard focus; final answers retain the same reveal/rating behavior. Normal input/button focus no longer scrolls the page. An image finishing loading also restores the remembered blank. Card dimensions, colors and the surrounding page layout are preserved.

Install **Cram-Studio-v2.0.4.ankiaddon** over the existing Cram add-on and restart Anki. The complete matching source is **Cram-Studio-Handoff-v2.0.4.zip**. All previous features, settings, saved sessions and answer matching remain. Ignore extra text keeps its previous behavior.

205 quick Python tests and the full Node UI suite pass. Four bounded Qt WebEngine scenarios verify real scrolling with an image and long text before/between three blanks, in MAIN and ANKI at normal/enlarged text sizes: partial matches, final matches, typing focus, native answer remount and no outer-page jump. The same regression fails with the released 2.0.3 Writing component. These use synthetic notes, not a user collection or live Windows Anki/Gemini session. Scheduling/controller and matching Python files are unchanged.

Historical release notes follow.

# MAIN CRAM + ANKI CRAM 2.0.3

## Lists inside one cloze

Writing can now turn a true enumeration inside ONE active cloze block into several answer items. `{{c1::mango, banana, apple}}` can supply three targets, just like three separate c1 occurrences. The original Anki card remains one scheduled card. Mixed separate/combined c1 blocks share one Writing counter and item index; other cloze ordinals remain visible as context.

Explicit numbered/bulleted lists are recognized offline. Ambiguous cloze contents use the same Gemini grouping preparation as Basic answers. The model reads the question and exact original text, identifies complete answer items and annotates connecting/framing wording copied literally from that source. “and then”, “most importantly” and unfamiliar connectors can remain visible between the blanks without a fixed phrase whitelist. Validation checks source ranges, exact connector substrings, coverage, word boundaries and numeric content; invented fragments are rejected. Bold, source punctuation, lists and intended line breaks are retained. Dates, single explanations and compound terms should stay one item.

One input can accept one item or several/all items. Accepted terms fill their original positions. Source connector wording can be included or omitted when typing the list. Your n/ñ, casing, plural and extra-text options remain. Preparation reuses the existing Gemini key/model and caches per source/context; no per-answer AI call is added. Without a key, with preparation disabled in ANKI CRAM, or on failed/invalid generation, each original cloze block remains a complete typed answer. A grouping cap falls back to original whole blocks. There is no manual per-note setup. Model classification still needs checking; literal-source validation cannot prove that every semantic classification is correct.

## Combined formatting differences

Writing comparison now tokenizes words, number values and structural punctuation together. It accepts `january 1 1978` for `January 1, 1978` through general prose comma/spacing tolerance, combined with existing quote, n/ñ, hyphen/space and plural handling. There is no special case for that date or month name. Changed dates/days/years, decimals, arithmetic structure, function-call separators and reference extensions are not discarded. Extra-text mode cannot silently accept additional numeric details around a numeric target, or C++ as C. This remains local matching, not unrestricted semantic/synonym/typo grading.

All previous Enter behavior remains: correct final check opens ANKI ratings, a miss stays editable, Enter again without editing explicitly reveals, and revised text is checked again. No automatic rating/queue advancement. The removed green Matched banner stays removed. MAIN remains independent practice.

## Installation and checks

Install **Cram-Studio-v2.0.3.ankiaddon** over Cram Studio and restart Anki. Keep **Cram-Studio-Handoff-v2.0.3.zip** for continuation. Fresh Writing questions use the new grouping; existing saved MAIN sessions retain their stored plans/progress. Existing sizes/colors/images and Study List/Study Sounds are unchanged.

205 quick Python tests and the full Node UI suite pass. New cases cover all reported cloze list forms, unfamiliar source connectors, mixed blocks, preserved rich markup, partial disk resume, AI request/schema validation, job deduplication, whole-answer fallback, native grouping without scheduling writes, dates and protected numeric/code details. Qt WebEngine checks cover eight layouts, four customizer scenes, six inline/line-break cases, two combined-cloze scenes and five actual keyboard flows. Representative rendered images were inspected. No live Gemini request, Windows Anki/Rust scheduler or user collection was used. Existing scheduling-boundary checks pass; native queue/rating/undo implementations are unchanged.

Historical notes follow; this section supersedes the old one-target-per-cloze-block behavior.

# MAIN CRAM + ANKI CRAM 2.0.2

Writing now has no green “Matched” banner in either MAIN CRAM or ANKI CRAM. The feedback area shows the red mismatch warning only after a wrong submission; positive/completion/incomplete status text is quiet. Answer progress and revealed words still update. Pending checks and successful responses clear the mismatch warning. The reserved feedback area remains to avoid moving the input and buttons.

Writing customization previews use the same behavior. Removed unused Matched text/background controls from the Writing view; multiple-choice correct colors and saved shared palette values remain available. Wrong-warning colors still follow the existing appearance controls. No matching, Enter flow, scheduling, source-note, size or profile-data changes.

Install **Cram-Studio-v2.0.2.ankiaddon** over the existing Cram Studio and restart Anki. This is a full same-package update including all 2.0.1 fixes. Keep **Cram-Studio-Handoff-v2.0.2.zip** for continuation. The full Node UI interaction suite and 29 focused Writing backend checks pass; JavaScript syntax and archive/source/checksum checks pass. No long tests or live collection/AI operations. Actual Windows Anki remains unverified here.

Historical release notes follow.

# MAIN CRAM + ANKI CRAM 2.0.1

This full update combines the user's Writing fixes. Install **Cram-Studio-v2.0.1.ankiaddon** over the existing Cram Studio and restart Anki. Keep the matching **Cram-Studio-Handoff-v2.0.1.zip** for continuation. Same add-on and profile data; Study List and Study Sounds remain separate and unchanged.

## Writing answers and Enter

- In **ANKI CRAM Writing**, Enter checks the typed answer. A correct final answer immediately reveals the native answer and opens Anki's rating phase. Then choose Again/Hard/Good/Easy normally. No second Enter is required for a final match, and no rating is chosen automatically.
- A wrong or incomplete submission stays editable. The existing button changes to **Reveal answer**: press Enter again without editing to reveal and reach ratings, or revise the text and Enter checks the revision. The latest user correction explicitly supersedes the earlier idea of revealing every wrong submission immediately. Space keeps typing spaces. An empty Enter is an explicit skip/reveal. Correct partial enumerations continue to the remaining items.
- Existing native buttons, interval labels, review queue, filtered-deck rescheduling and undo remain Anki-owned. MAIN CRAM remains independent practice with its own explicit Check/score; this update does not automatically grade MAIN answers.

## Less rigid matching, original display

Both Writing modes now tolerate surrounding straight/curly quotation marks, a word-separating hyphen versus a space, `n` for `ñ` (including decomposed Unicode), and common singular/plural forms. Examples: `set at naught` for `"set at naught"`; `in-writing` for `In Writing`; `Jaypoy Lavina` for `Jaypoy Laviña`; `banana` for `bananas` or vice versa. Regular plural rules and a small common irregular dictionary are local and cached; no per-keystroke or per-answer AI request is added. Whole item names and compound phrases still matter. Different concepts, negation, quantities and mathematical signs are not broadly fuzzy-matched. This is not unrestricted semantic grading or comprehensive English morphology.

**Ignore extra text** remains optional. A numeric match cannot be extracted from an attached, different reference: `Section 4(c)(4)` is rejected for `Section 4`, including when extra-text matching is on. Numeric subsection extensions, changed subsection numbers, negative signs and decimal extensions are covered by checks. Existing harmless enumeration numbering remains optional.

Authored answers and source notes are unchanged. Revealed Writing clozes now flow inline with normal HTML whitespace: raw newlines inside `existing
logic` or `official
proceedings` no longer create a tall answer box with words above/below the sentence. Real `<br>` line breaks, paragraphs, bullets, bold and original text remain. Basic source-list formatting is retained. Existing sizes/colors/custom images are not reset; only native Writing's existing check/reveal button gets a stable minimum width.

## Verification

194 quick Python checks and the full Node interaction suite pass. New cases cover all reported matching examples, plural enumeration/noise, protected references, correct final Enter, editable misses, second-Enter reveal, typo revision/recheck, empty skip, partial enumerations, Space typing, stale/repeated results and absence of automatic ratings. Existing scheduling-boundary, MAIN resume, appearance and MCQ tests still pass.

Bounded Qt WebEngine tests cover eight Writing layouts, four customization previews, six raw-newline/explicit-break formatting cases, and five actual keyboard flows. Keyboard checks use real Qt input and shortcut dispatch with synthetic native reveal/rating callbacks: a final match reveals once, a miss remains editable, a second Enter can reveal, revision can succeed, and only an explicit `1` invokes the original Again callback. These do not replace testing in the user's Windows Anki installation; no live user collection, Rust scheduler or Gemini request was used.

Historical release notes follow; this section supersedes their earlier strict-plural and manual-final-reveal instructions.

# MAIN CRAM + ANKI CRAM 2.0.0

## Writing mode

Type answers in **MAIN CRAM → Writing** or **Tools → ANKI CRAM → Writing**. This is a full update of the existing `cram_studio` add-on, retaining Flashcards, Learn/multiple choice, Mixed, filters, ordering, appearance, saved practice and Gemini choices. Study List and Study Sounds remain separate.

- One answer box accepts one item, several items or all items. Enter checks the input; Shift+Enter inserts a line break. Accepted items appear in their original positions. Up/Down or clicking an unfilled blank selects another target. The last match waits for an explicit check/reveal; it never rates or advances automatically.
- Checking ignores letter case and normalizes whitespace. Numbered/bulleted layouts and harmless list separators are accepted without requiring the original numbering or connecting “and”. Complete compound terms remain complete targets. No character-count heuristic creates an extra blank for a missing suffix: `banana` does not complete `bananas`.
- **Ignore extra text** is an optional setup checkbox, off by default, available in both modes. With it enabled, `banana, waaaa, mango, jdjd, lemon` can satisfy those three expected items. It requires complete item names with word boundaries; `mangosteen` does not satisfy `mango`. With it off, substantive extra words fail checking. It is shared as a profile preference and captured in each MAIN session.
- Cloze targets come from the active cN card. Five c1 occurrences mean five targets; c2/c3 stay visible as context when testing c1. Basic numbered/bulleted lists are detected offline. Ambiguous Basic prose is grouped by Gemini using the question and exact original answer, then cached. No manual per-note enumeration setup is required.
- Introductory wording, punctuation, numbering, “and”, bold/normal markup and source list formatting are preserved. `The fruits are banana, mango, and lemon.` becomes `The fruits are [blank], [blank], and [blank].` and fills in place. The display is not rewritten into a new numbered list.
- Full statements such as `NO, it depends on the organization` remain one answer. Ambiguous/unavailable/invalid AI grouping falls back to typing the full original answer. **Use full answer** is also available while preparation is pending. API/network failures do not invent targets. Cached groups work offline; preparation uses the existing Gemini key/model/quota. Images are not sent for grouping.
- MAIN CRAM saves partial accepted items, attempts, selected target and draft text for Resume. Reveal remaining only reveals; Check answer explicitly records a practice score. Items missed on an earlier attempt stay missed for that question's score. Existing retry-mistakes behavior remains available. Practice never changes Anki's schedule.
- ANKI CRAM typing and partial feedback never reveal, rate or schedule a card. Leave the answer box with Esc, then Space/native Show Answer reveals; native Again/Hard/Good/Easy and intervals still control scheduling and advancement. Native undo, queue/daily limits and filtered-deck rescheduling settings remain Anki-owned. While typing, spaces, numbers and letter shortcuts are input text. After leaving the box, native shortcuts resume. Image occlusion retains its existing image recall controls instead of becoming a text-writing question.

## Appearance and installation

**Tools → CUSTOMIZE CRAM → Card: Writing** shows live MAIN/ANKI mockups with resize handles and color picking. Writing deliberately shares the existing multiple-choice question-card dimensions, question-panel height, input/choice text size and palette. Flashcard size remains separate. Saved colors, harmonies, images and text zoom are reused. Changes to those shared question-card controls also affect multiple choice. No automatic size/color reset is performed. Save applies; Cancel discards; Reset restores the existing defaults.

Install **Cram-Studio-v2.0.0.ankiaddon** over the current Cram Studio package and restart Anki. Do not delete the existing add-on or its profile data. Keep **Cram-Studio-Handoff-v2.0.0.zip** to continue this exact source in another account; it includes the complete source, matching installer, tests and checksums. Study List and the user-confirmed Study Sounds 1.1.8 are unchanged.

## Validation

190 quick Python checks and the complete Node DOM suite pass. Added checks cover source-grounded grouping, case/list formats, strict/extra-text behavior, whole compounds, plural boundaries, invalid grouping, partial disk resume, no implicit grading, native filtered-deck/source-edit/stale-message behavior, grouping failure/cancellation, retryable UI errors and Writing customization. Existing flashcard/MCQ, scheduling-boundary and progress checks still pass.

A bounded Qt 6.7 WebEngine smoke check rendered eight actual MAIN/ANKI Writing scenes at 1360×900, 900×680 and 540×520 in light/dark themes, plus four Writing customization scenes. Card/input containment and JavaScript errors were checked, and representative images inspected. A real Qt shortcut check typed spaces/letters into the input without invoking Edit, then invoked Edit after blur. These synthetic render/input checks are not a live Windows Anki or Rust-scheduler integration test. No user collection or live Gemini request was used; grouping semantics still depend on model output. Typed matching is local exact-item/layout matching, not unlimited AI interpretation of every possible paraphrase.

The earlier release notes below are historical. This section supersedes their version-specific validation counts and current-release instructions.

# MAIN CRAM + ANKI CRAM 1.10.14

A desktop Anki add-on with independent practice and an optional Cram-style interface for Anki's real reviews. Keep your existing Study List installed: this package neither replaces it nor depends on it.

### 1.10.14 Choices match the answer's capitalization

Multiple-choice options now use the correct answer's casing at display time in MAIN CRAM and ANKI CRAM. ALL CAPS answers give all-capital options; lowercase answers give lowercase options; ordinary title/sentence patterns are matched too. Mixed-case answers such as pH/NaCl are left alone. Acronyms and mixed-case identifiers are retained within ordinary title/sentence presentation. The authored correct answer is unchanged. Choices keep uniform button styling; original numbered lines and line breaks remain.

The shared presentation helper is used for option labels AND the text inserted into a selected blank. It also applies to cached choices and restored MAIN sessions, so no Gemini regeneration, cache migration, progress reset or extra API call is needed. Original question/option strings, grading indices, note formatting and saved picks stay intact. This is display capitalization, not rewriting scientific/code meaning or copying one answer's bold HTML onto only that option. Flashcards, note content and Anki ratings/intervals are untouched.

The complete Node DOM suite passes, including new uppercase/lowercase/title/sentence/list cases, cached/restored choices, filled blanks, unchanged source strings/answer indices and no native reveal/rating commands. The 165 Python checks still cover native/filtered scheduling, generation and saved progress. No live Gemini call, user collection or actual Windows pixel test was used. Generator policy 4 and the requirement for one correct plus three wrong choices remain unchanged.

Install **Cram-Studio-v1.10.14.ankiaddon** over Cram Studio and restart Anki. Keep **Cram-Studio-Handoff-v1.10.14.zip** for continuation. The separate **Study Sounds 1.1.8** update removes reveal/flip/mask audio while preserving rating/Again/session-complete cues and the working audio engine. Install that package separately for the sound change. Study List is unchanged.

### 1.10.13 Always complete the multiple-choice set

Corrects the unwanted refusal behavior introduced in 1.10.12. The user's rule is: first prefer real sibling types within the same classification; when that does not apply or supplies too few wrong options, broaden to real concepts related to the question, then the surrounding subject. Being related and wrong is an acceptable fallback. Same-category difficulty is a preference, not a reason to withhold choices.

Every multiple-choice generation request requires exactly **three wrong choices plus the original correct answer**. The JSON schema again has minItems=maxItems=3. Removed the instruction allowing an empty set and its special question-refusal error. The prompt explicitly says not to skip a question or switch it to flashcards because of a shortage of narrow-category alternatives. Synonym/duplicate rejection, real-term requirements and full per-blank question context remain. Invalid API output and connection/quota errors are still reported; malformed results are not saved as valid choices.

Existing cache policy 4 and all valid saved choices are retained, avoiding unnecessary regeneration. There is no added API call, retry loop, UI change, progress reset, scheduler change or forced deck regeneration. MAIN CRAM, ANKI CRAM and whole-deck generation share this corrected contract.

165 quick Python tests pass, including the exact three-option schema, broader related-term fallback instruction, no deliberate empty-set instruction/error, invalid-response handling, synonym validation, saved progress and native/filtered scheduling boundaries. These are code/contract checks; no live Gemini call or user collection was used.

Install **Cram-Studio-v1.10.13.ankiaddon** over the existing Cram Studio and restart Anki. Keep **Cram-Studio-Handoff-v1.10.13.zip** for continuation. The prior 1.10.12 refusal instructions below are historical and superseded by this section.

### 1.10.12 Real sibling choices and synonym exclusion (historical)

Generation prioritizes other REAL members of the same recognized classification when the question identifies a type, subtype, stage or method. If there are five established types and the question asks for one, prefer other established types that are wrong under the exact stem. Do not invent additional members. When this strategy does not fit or there are too few suitable siblings, use the nearest real related concepts that remain clearly wrong. Broader/narrower terms that could also answer the question, synonyms and answer paraphrases are excluded. Accuracy takes priority over artificial difficulty.

The same Gemini request now returns an `answer_aliases` exclusion list. Before saving, the client rejects wrong choices that match these contextual aliases. A small deterministic guard independently blocks the reported partition testing / equivalence partitioning synonym pair, in either direction, including case/punctuation variants and duplicate wrong concepts. The guard also applies to cache/manual choices. It deliberately does NOT merge equivalence partition (a class of values) with equivalence partitioning (the technique). The source is ISTQB Glossary 3.7, which explicitly lists partition testing as a synonym:
https://www.ctqb.org/en/downloads/istqb.html?cid=33119&file=files/content/ctqb/downloads/istqb/Glossary-terms-version-3.7.pdf

If Gemini cannot find three real, distinct wrong options after considering related concepts, it may return an empty set. The client refuses that batch with a clear message instead of padding it with invented terms or aliases. Earlier completed batches remain saved. There is no extra API pass, automatic retry loop, model/temperature change or study-time reference lookup. The general alias list and judgments about real terms/semantic correctness still come from Gemini; this is not comprehensive independent factual verification.

Cache policy is now revision 4. Fresh preparation uses new keys without deleting older entries. Existing unfinished MAIN CRAM sessions keep their saved questions, options and progress until explicit regeneration. To change already-generated choices, use **Regenerate choices** below an unanswered MCQ, or **Tools > Regenerate deck choices > select decks > Preview > Regenerate** for whole decks. ANKI CRAM has current/deck regeneration controls on the question side. Full-deck regeneration ignores practice filters and limits and uses API quota. MAIN, ANKI and deck generation share the same pipeline.

**165 Python tests pass** in under a second, including known/contextual aliases, invalid cached sets, single-request behavior, malformed metadata, refusing an unsafe batch without overwriting saved choices, existing native/filtered scheduling and undo boundaries, saved progress and multiline choices. No real Gemini call, user key/collection, long test or Windows UI test was used. The tests check code boundaries and request/response behavior, not live model accuracy/difficulty.

Install the complete **Cram-Studio-v1.10.12.ankiaddon** over Cram Studio and restart Anki. Keep **Cram-Studio-Handoff-v1.10.12.zip** for continuation. All existing layout, card selection/flipping, sizes/colors, zoom, scheduling and profile/session runtime files are retained; only the MAIN version label changes in the UI. Study List and Study Sounds are untouched.

### 1.10.11 Select text deliberately; flip from empty card space

In MAIN CRAM and ANKI CRAM flashcards, click empty card space to flip without starting accidental blue text selection. Clicking, double-clicking or dragging actual text keeps the current face visible so you can select it and use normal Copy/Ctrl+C. Revealed cloze answer words are selectable too. A text-selection drag ending on empty space does not flip the card. Existing Reveal/Show clue buttons, Space/arrow flipping, native ratings and all keyboard shortcuts retain their roles.

The pointer handler checks rendered text ranges rather than treating the whole text container as letters, so empty padding inside a text box can still flip. It supports current caretPositionFromPoint, older Chromium caretRangeFromPoint and a text-line-range fallback. No per-frame renderer or mouse-hover hit-testing is added. Selected ranges outside the clicked card are retained. Primary empty-surface presses prevent default selection; right-click, links, form controls, wheel/touch scrolling and scrollbar dragging keep their normal behavior. No clipboard replacement, copy commands, new buttons or guide text.

Image-occlusion frames are selection-free throughout, including captions, masks, toolbar labels and the full-screen viewer. Mask reveal/hide, zoom, native reveal/rating and viewer node identity are retained. Flashcard photos still cannot start native image dragging. MULTIPLE-CHOICE blank controls keep their existing selection protection; ordinary MCQ question text stays copyable.

This is a presentation/interaction-only update. The previous bold/normal formatting fix, question-based Gemini prompt and policy revision 3, one-blank-at-a-time multiple choice, adjustable panel/choice text, colors, scheduling and saved practice are retained. All Python runtime files and Gemini code match 1.10.10.

**159 Python tests and the full Node DOM interaction suite pass**, including glyph vs padding hits, text/word/drag selection without revealing, eight repeated surface flips with stable nodes, copyable revealed clozes, older-engine fallbacks, selection-range isolation, scrollbars, protected IO captions/viewers and original native keyboard/rating controls. JavaScript syntax and archive/source/checksum checks pass. The geometry/selection checks use DOM spies; actual Windows Qt/Chromium selection painting and hit testing remain unverified here. No long tests, live AI or user collection.

Install **Cram-Studio-v1.10.11.ankiaddon** over Cram Studio and fully restart Anki. Keep the matching full source handoff for continuation in another GPT/account.

### 1.10.10 Faithful formatting and closer question-based distractors

Fixed a formatting-cleanup defect: explicit `font-weight:normal` or `400` was discarded while surrounding `<b>`/`<strong>` tags remained. Anki's editor can use those overrides to keep body text normal inside a bold wrapper; losing them makes the sentence incorrectly inherit bold. The cleaner now preserves safe explicit normal, numeric and relative weights, using the last valid declaration and its `!important` priority. Header/intentional bold stays intact. This applies to newly compiled cloze, Basic/custom fields and occlusion captions in both Cram modes; no global removal of bold or reset of your note formatting.

Gemini generation now explicitly targets challenging recall within the narrow category named or implied by the question. It is instructed to replace obvious category outliers, choose nearby concepts/common misconceptions that differ on the decisive fact, match grammar/specificity/length, and reject synonyms or alternate valid answers. For example, a question explicitly about sex hormones should test distinctions in that context instead of being a grab bag of unrelated hormone families. Accuracy takes priority when the question is too broad to support three close, unambiguously wrong options.

Each cloze choice request also carries an AI-only question focused on that blank, with the other blanks correctly filled as context. The displayed study question is unchanged. The original full clue, correct target answer and other-slot answers remain supplied. No extra generation pass, API endpoint/model change, live answer rewriting or new study UI is added; existing small/progressive batches remain.

The generation policy uses cache revision 3. Freshly prepared questions use new keys so older easy sets are not mistaken for the revised policy. Existing cache files/entries are retained; generated revision-3 sets are reused normally. Actual generation still follows your existing key, generation preference and explicit MAIN preparation controls. Installing does not regenerate entire decks. Use **Regenerate choices** for the current card or **Regenerate deck choices** for selected decks to replace existing/saved sets deliberately. Unfinished MAIN CRAM practice retains its saved questions/options until explicit regeneration; it is not silently rebuilt.

The previous one-blank-at-a-time flow, question-panel height, independent choice text, card size/colors and native cloze-answer emphasis are retained. No source notes, scheduling or appearance preferences are rewritten. Saved MAIN snapshots remain intact; formatting already discarded from an old snapshot cannot be reconstructed from that snapshot alone.

**159 quick Python tests and the complete Node DOM suite pass.** New checks cover font-weight overrides, repeat cleaning/cascade/markup safety, per-blank AI context without changing displayed questions, revision-2 cache isolation without deletion, revision-3 reuse and the outgoing prompt contract. Formatting alone preserves plain-text cache identity within a policy revision. No live Gemini request or semantic difficulty assessment was run; tests verify payloads/behavior, not that every generated set is difficult. Desktop Anki/Qt pixel rendering remains unverified. Install **Cram-Studio-v1.10.10.ankiaddon** over Cram Studio and restart Anki. The full matching handoff includes all prior features and exact installer.

### 1.10.9 More question space and one blank at a time

Multiple choice in **MAIN CRAM and ANKI CRAM** now shows only the active blank's four choices. Selecting an option fills that blank and moves to the next blank; the last blank stays selected and waits for your manual check/reveal. A choice never automatically checks, reveals, rates or moves to another card. Up/Down wraps through blanks, and clicking a blank selects its choice group. Previous selections remain available to change. Blank labels show the current number and total outside the sentence; no numbers are added inside the clue. Native rating, reveal, edit, browse and undo shortcuts retain their existing roles.

The question panel now receives **60% of the usable question/choices area by default**, with more compact choice buttons and only one visible choice group. It no longer shrinks toward a small minimum to make room for every cloze group. The question remains in the same card while navigating blanks. Exceptionally long questions/answers scroll within their own surfaces without taking the question off the page. Existing card dimensions/aspect ratios, colors and frame appearance remain available; changing blanks keeps the existing nodes.

Open **Tools → CUSTOMIZE CRAM → Card size → Card: Multiple choice** for **Question panel height** (30–75%) and **Choice text size** (12–32 px, default 18 px). Both MAIN/ANKI live mockups use the same layout/styles as the study interface. These settings save per profile, apply in both Cram modes and have no effect on flashcards. Reset to default size in Multiple choice resets its dimensions, panel height and choice text, while keeping flashcard size/colors/images. Cancel discards drafts. Existing saved width/height and preferences are not automatically reset.

Question/flashcard text zoom retains your saved value. Multiple-choice **choice text has its own size** and no longer shrinks when you reduce question text with Ctrl+wheel or the existing text-size controls. Choice letters retain their compact badge styling. Text-only zoom still leaves images and frame dimensions intact.

**153 quick Python tests and the complete Node DOM suite pass**, including four-blank automatic navigation/manual-check guards in both modes, stable question/choice nodes, mouse/keyboard revisits, existing MAIN resume state, independent type, transactional profile settings and customizer preview/save/reset. Existing scheduling-boundary checks also pass. Scheduling, queue/undo, filters/orders, generation/cache, content and practice-session storage implementations match 1.10.8 bytes. Study List and the working Study Sounds 1.1.7 are untouched. No long tests, live AI or user collection were used.

Actual Windows Anki/Qt rendering remains unverified here. A headless browser installation was attempted but the download was unusable, so DOM checks must not be described as visual/pixel testing. Install the full **Cram-Studio-v1.10.9.ankiaddon** over Cram Studio and restart Anki. The matching source handoff preserves the exact implementation and all prior features.

### 1.10.8 Keep resized multiple-choice text inside the question panel

Fixed question text escaping the colored question surface when the multiple-choice card is resized, especially with larger text in ANKI CRAM. The native question surface now owns its scrolling instead of its outer grid wrapper. It can shrink within the card without a conflicting 100% minimum height. Short clues remain vertically centered; long clues start at the top and scroll inside the same colored panel. MAIN CRAM also explicitly contains question overflow. The customizer previews use the same shared stylesheet, so the fix applies there too. Saved card dimensions, text zoom, colors, choices and scheduling behavior are retained.

This is a CSS-only runtime correction apart from version/docs. **151 Python tests and the complete Node DOM suite passed**; JavaScript syntax, archive/checksum/source checks passed. Scheduling, generation, saved sessions, content and all frontend JavaScript files match 1.10.7 bytes. A browser renderer and desktop Anki are unavailable here, so actual Chromium/Qt pixel layout remains unverified. No long tests or AI calls were run. Install the complete **Cram-Studio-v1.10.8.ankiaddon** over the existing Cram Studio and restart Anki; no resizing reset is required.

### 1.10.7 Prevent accidental blue selection while clicking masks/blanks

Clicking cloze blanks or image-occlusion masks repeatedly now suppresses browser selection and native image dragging in those controls. Occlusion images are protected in both preview and full-screen viewers; attached flashcard/multiple-choice images have the same protection. A browser selection range is cleared on interaction only when it overlaps that particular control. Ordinary clue text remains selectable/copyable, form fields and right-click menus remain available, and wheel/touch scrolling is not intercepted. SVG masks keep keyboard focus. This adds no new buttons or guide text.

The click handlers still do their existing work: select a multiple-choice blank or reveal/hide an individual mask. Zoom, viewer state, image/card nodes and native review keyboard shortcuts remain. Clicking masks does not reveal/rate a card in Anki; Space and explicit native ratings keep their normal role. All previous features, including 1.10.6's blank style and Gemini default, are retained. Install this complete same-package update over Cram Studio and restart Anki.

**151 Python tests and the complete Node DOM suite passed**, including new repeated-click/selection-range/drag guards, copy/form/right-click/scroll exceptions, viewer/zoom stability and native scheduling checks. JavaScript syntax, package/checksum/source matching checks passed. No long tests, live Gemini requests or user collection changes. Actual browser blue-selection painting and Qt mouse/touch delivery remain unverified here because the desktop Anki/browser runtime is unavailable.

### 1.10.6 Clean cloze blanks and automatic missing choices by default

Flashcard questions now show a short, consistent accent-colored underline, matching the approved preview. Multiple-choice sentences use the same blank style with **no inline numbers or circled labels**. A selected choice replaces only its blank without adding a prefix: “The heart pumps ____ through the body.” The currently active multiple-choice blank has a subtle tint and thin accent outline; arrows, choice number keys and mouse selection keep their existing behavior. Blank/group labels remain outside the sentence, and accessible blank labels retain their slot identity. Revealed flashcard/cloze answers keep the colored, slightly heavier, unhighlighted default from 1.10.5. Custom colors and note-authored formatting remain available.

This is a presentation change. Underlying numbered question markup/slot IDs remain unchanged for Gemini context, cache keys and saved MAIN sessions. Old saved sets display the new blank style when reopened, without regenerating cached choices. Actual numbered lists inside answers are preserved. Waiting questions and CUSTOMIZE CRAM mockups use the same styling.

In **Tools → ANKI CRAM → Multiple choice**, **Automatically create missing choices with Gemini** is enabled by default. The update adopts this enabled default once because older flashcard starts saved the disabled checkbox as false. After you explicitly save the new setting with Start ANKI CRAM, a manual opt-out stays saved. Starting flashcards no longer overwrites the checkbox preference with false; it still disables actual generation for flashcards. Opening/cancelling setup does not write preferences, start studying or contact Gemini.

A configured Gemini key is still required. In multiple choice, the existing generation flow creates only missing current-card choice sets and reuses saved sets; no automatic regeneration of valid choices. Missing keys/network/quota errors retain the existing retry/flashcard fallback. Generating choices never reveals, rates or advances Anki cards. MAIN CRAM keeps its existing preparation/background-generation workflow.

Full same-package update. **151 Python tests and the complete Node DOM suite passed**, including setup-default adoption/opt-out/flashcard persistence, fake-client generation/cache/no-key checks, clean old/new flash/MCQ/waiting/preview blanks, multiline answers and native scheduling boundary checks. No live Gemini requests or collection changes. Real Anki/Qt visual/key behavior still needs checking in desktop Anki; no browser/Anki runtime is installed in this environment.

### 1.10.5 Card dimensions, photos and occlusion controls

Open **Tools → CUSTOMIZE CRAM → Card size**, then choose **Card → Flashcards** or **Multiple choice**. Each type has independent width/height, drag handles, live MAIN CRAM / ANKI CRAM previews, and Reset to default size. Save commits both; Cancel discards the draft. Size is shared between the two Cram modes for the selected type; themes keep the same size. Existing flashcard preferences remain saved. Multiple choice starts at its existing default until resized.

The preview and real reviewer now share scene bounds and a saved aspect ratio. The mockup accounts for its simulated native bottom bar exactly once; the actual reviewer uses the already reduced native webview. Cards scale down proportionally when a screen or whole-window zoom leaves less room. Long content still scrolls at its chosen text size. Custom multiple-choice question panels scroll within the card; many blanks/long choice groups can also require scrolling the card. Reset returns to responsive defaults. Card shadows are closer and stronger in both themes, with reduced internal padding. Attached flashcard photos enlarge to the available content area without changing aspect ratio or card size; mixed text/image content and multiple images retain scrolling.

Revealed cloze answers use the accent color, heavier type and a slight text stroke, with no add-on background highlight by default or in automatic palettes. Note-authored bold/highlights remain. An existing explicit **Cloze answer highlight** preference remains available in the color customizer; turn its Auto checkbox on to remove that optional fill. Basic answers remain ordinary answer text without an added highlight.

**ANKI CRAM image occlusion:** a larger responsive frame is independent of flashcard and multiple-choice size settings. The extra bottom Reveal row is removed. Its top toolbar has **Hide masks / Show masks**, zoom, Fit and Full screen. Click or tap a target mask to reveal/hide only that target. Enter also toggles a focused mask. Inactive context masks remain in place. These controls affect only the image; they never reveal/grade/advance a card in Anki. **Space still performs native Anki reveal and then native rating.** After native reveal, use Show masks to conceal the targets again while keeping the native rating phase active. Zoom/fullscreen and the image node persist across native reveal. The next question/undo resets target visibility. MAIN CRAM keeps its existing independent recall controls.

Complete same-package update retaining previous features, appearance, Gemini cache and saved MAIN sessions. Study List is separate and unchanged. Quick checks passed: **145 Python tests**, the complete Node DOM suite (including size/MCQ/photo/mask cases), JavaScript syntax and archive/checksum checks. Scheduling boundary tests were rerun; native queue/rating/undo/filtered-deck implementation files are byte-identical to 1.10.4. Actual Anki/Qt pixel rendering and touch/key delivery need a check in desktop Anki; no browser or Anki runtime is installed here. No long tests, live AI request or user collection changes.

### 1.10.4 Resume unfinished MAIN CRAM sessions and steady choices

Close MAIN CRAM or restart Anki, then open **MAIN CRAM → Resume practice → Resume**. Started sessions now save locally in the current profile: exact question/choice order, graded answers and scores, repeat queue, current question, partial multiple-choice selections, active blank, revealed side and image preview zoom. Different practice sets remain separate. Starting the same deck/mode/filter/order/limit selection resumes its existing unfinished session; it does not silently replace it. Changes in settings create a different set while retaining the older one.

The study-screen X now pauses practice with **Save & exit**. Finishing the session removes that completed save and records its results in history. **Reset** beside a saved set asks before deleting only its unfinished progress. It keeps other sessions, cached choices, settings and Anki scheduling intact. Saved practice does not expire or get automatically evicted. Sessions are snapshots of the original practice set; resuming does not rerun today's search, reshuffle choices, or contact Gemini automatically. If choice generation was incomplete, use its existing Resume control. Time spent with MAIN CRAM closed is excluded from session time.

The previous version kept unfinished progress in memory, so progress already lost before installing this update cannot be recovered. Saves are profile-local and do not sync to another computer through Anki sync. Small cursor/selection saves write separately from the full question queue; full snapshots are saved on grading, queue/choice changes, pause and close. Writes replace files atomically.

Choice buttons now explicitly suppress inherited transform/scale/animation/transition effects while retaining their hover/selection colors and keyboard focus outline. Their hit boxes, border widths and neighboring choices stay fixed. This change is scoped to MAIN CRAM choices.

Full same-package update retaining every previous feature, including the1.10.3 order-menu and text-highlight zoom fixes. Quick disk/reopen/controller, DOM, Python, syntax and archive checks passed. Actual Windows/Qt hover and display rendering remain unverified. No long tests or AI calls were run.

### 1.10.3 Readable Question order menu and highlight zoom

Replaced MAIN CRAM's black native **Question order** popup with a menu drawn inside the page. It uses the page's light/dark colors, keeps every existing order and Anki column, scrolls long lists within the available screen space, and supports pointer selection, arrows, Enter/Space, Escape, Tab and typing an order's name. Choosing an Anki column still exposes its Descending setting. No practice ordering or scheduling logic changed.

Fixed text zoom for note highlights that wrap nested bold/italic/span elements. Highlight wrappers now scale their font metrics and line height along with their text, in both MAIN CRAM and ANKI CRAM. Explicit font sizes in MAIN CRAM rich text now zoom consistently as well. Repeated zoom changes use the original baseline; resetting to100% restores the authored inline formatting. Both card faces update together while the frame stays fixed.

Retains every previous feature, including the picker-outline fix and removal of Full Anki answer. Complete same-package update; install over Cram Studio and restart Anki. Quick menu/keyboard, nested-highlight/zoom, Python, syntax and archive checks passed. Actual Anki/Qt rendering remains unverified.

### 1.10.2 Remove Full Anki answer

Removed the expandable **Full Anki answer** section below ANKI CRAM flashcards and multiple-choice answers, including its appearance mockup. The revealed flashcard/choices and original Anki rating buttons remain. Unsupported templates still show their actual Anki card as the primary flashcard.

Complete update with every earlier feature and the1.10.1 picker-outline fix. Install over Cram Studio and restart Anki. Quick interaction, Python, syntax and package checks passed; live Anki rendering remains unverified.

### 1.10.1 Complete picker outlines

The picker now uses a thin solid outline. All four edges stay inside the visible preview, including when the hovered page extends below or beyond the iframe. Leaving the preview clears the hover outline, and moving the pointer reuses the same outline node. Component categories and color editing are unchanged.

This is the full update, retaining all previous features and shortcuts. Install over Cram Studio and restart Anki. Quick geometry/interaction, Python, syntax and package checks passed; actual Windows/Anki rendering remains unverified.

### 1.10.0 Color inspection in both directions

Open **Tools → CUSTOMIZE CRAM → CUSTOMIZE CRAM COLOR → Pick from preview**.

Click a component in the live mockup. A small menu separates its **text**, **background**, and **border**, with the exact setting name and current color. Choose a part to point to that precise property and open/highlight its control on the left. Nested question-panel and card backgrounds are separate choices. A selected letter circle is separate from its surrounding choice; automatic circle/label shades are identified when they have no independent setting. Mapping follows component/state/property bindings, not equal-looking hex values or whichever pixel is closest.

Picking is inspection only: it keeps the card side, choices and automatic colors intact. If the selected setting says **Auto**, turn Auto off to enter a manual color. Draft edits update the existing preview nodes. **Save** commits; **Cancel** discards. Use **Stop picking** or Esc to exit inspection and restore normal mockup interactions. The picker is available only inside the color customizer; actual study screens remain unchanged.

Fixed double-click locators that failed because the browser returns a NodeList with no Array.find method. All preview collections now normalize to arrays. A known text/surface/border target remains pointed out even when its default/inherited computed color differs from its editable palette value: **Setting** and **Shown** distinguish the two. Missing components get an explicit message instead of silent failure. MAIN flashcard generic-button settings still switch the mockup to the genuine ANKI rating controls, and MAIN multiple-choice answer settings switch to the relevant ANKI preview.

Full in-place update, retaining all1.9.1 shortcuts and earlier features, appearance, preferences and scheduling behavior. Quick Python, browser-like NodeList/DOM interaction, syntax and archive checks passed. Actual Anki/Qt rendering and pixel hit areas remain unverified in this environment.

### 1.9.1 Quick access shortcuts

In Anki's main window, press **Ctrl+Alt+M** for **MAIN CRAM** or **Ctrl+Alt+A** for **ANKI CRAM**. MAIN CRAM's existing **Ctrl+Shift+T** also works. The primary keys appear beside the existing Tools menu entries and in the existing deck-overview button tooltips. No shortcut guide, instructions or extra buttons are added to the study interface.

From the deck list, ANKI CRAM opens the currently selected deck's overview and its existing mode setup. You still choose Start ANKI CRAM; pressing its shortcut does not answer a card or begin studying by itself. An already active ANKI CRAM review or open setup is focused without restarting. From ordinary Anki review, return to the deck list/overview first. The shortcuts are scoped to Anki's main window, rather than intercepting keys in separate editor/browser/customizer/practice windows, and held keys do not repeatedly launch them.

Full same-package update with all previous features and appearance retained. Install over Cram Studio and restart Anki. Quick launcher, unit, DOM, syntax and archive checks passed; actual Windows/Qt key delivery needs a runtime check.

### 1.9.0 Color harmonies and precise color pointers

Open **Tools → CUSTOMIZE CRAM → CUSTOMIZE CRAM COLOR**. Select **Automatic from card**, then choose **Color harmony**:

- Current automatic (preserves the previous look)
- Monochromatic
- Analogous
- Complementary
- Split complementary
- Triadic
- Tetradic · rectangle
- Square

The generated hue swatches and mockup update immediately. Card remains the base. Tones adapt for readable text; correct/wrong feedback retains its green/red meaning. Manual colors stay pinned when you change harmony. Choosing Automatic from card again clears manual pins while retaining Card and the chosen harmony. Light/dark and flashcard/multiple-choice palettes keep separate choices; both Cram modes use them. Neutral cards use the existing accent as a hue anchor; monochromatic neutrals stay gray. **Current automatic** keeps the old algorithm exactly. **Reset all colors** restores the original theme defaults and clears harmony choices, preserving image/size settings as before.

The double-click color locator now targets the actual **text**, an empty **background** patch, or the **border edge**, and displays the hex value and property. Text pointers avoid choice-letter circles. Page-background pointers avoid the native footer. This1.9.0 release checked computed CSS colors and suppressed some pointers when styles differed;1.10.0 fixes browser NodeList failures and shows the mapped property together with separate Setting/Shown values. With uploaded images, the popup identifies the underlying base color. For neutral button colors in MAIN flashcards, it visibly switches to the actual ANKI rating controls; the temporary invented neutral-button sample has been removed.

Harmony references: [Adobe palette guide](https://www.adobe.com/uk/creativecloud/design/discover/color-palette.html) and [Adobe Color wheel](https://color.adobe.com/create/color-wheel). The add-on uses local digital HSL hue relationships and contrast-adjusted tones; it does not reproduce Adobe's exact palette output or contact a color service.

This is the full same-package update, with all earlier features retained. Install over Cram Studio and restart Anki. Quick unit/DOM checks passed; real Anki/Qt rendering still needs a runtime check.

### 1.8.0 Color locators, collapsed decks and image backgrounds

Open **Anki → Tools → CUSTOMIZE CRAM** (or MAIN CRAM → Settings → Customize Cram → Open).

In **CUSTOMIZE CRAM COLOR**, **double-click a color name** on the left. The mockup switches to the relevant question/answer or selection state and points to the component with a labeled outline and connector. The marker closes with X/Esc or after7 seconds. Keyboard users can focus a name and press Enter/Space. This changes only the mockup, never your actual cards or color values. A revealed-answer color selected from MAIN multiple choice points to the ANKI multiple-choice preview, where that shared setting is used; its selector updates visibly. Generic neutral buttons in MAIN flashcards are represented by a temporary labeled neutral-button example.

In **Background & card images**, choose **Upload image** for the page background, card surface or both. PNG/JPEG/WebP/BMP input is optimized locally for the interface. Each has independent **Image opacity**, **Readability overlay**, **Smart readability**, Replace and Remove controls. Changes preview immediately; **Save** commits and **Cancel** discards them. Images are shared across both Cram modes and themes, for flashcards and multiple choice. Image occlusion keeps its own image display. They are kept locally in your profile and persist across add-on updates; no image file is added to your notes or collection media.

The overlay uses the current background/card color. Smart readability can further reduce image strength to preserve existing text contrast (up to4.5:1 for the checked text colors against light/dark image extremes). **Visible image** reports the resulting strength. Buttons and the question panel remain solid so images do not show through their current colors. Turn Smart off to control opacity/overlay manually. This cannot repair an already unreadable manual text/color combination. Card dimensions and text size do not change.

**Reset all colors** continues to reset colors only, preserving size and chosen images. Use **Remove all images** to clear the images as well.

The **MAIN CRAM deck picker starts with children collapsed**. Expand with its arrow or search directly for nested lessons. Include subdecks and selected deck counts still work while collapsed. Refresh preserves branches you opened. The deck-wide regeneration tree also starts collapsed. Anki's ordinary deck browser is unchanged.

Full same-package update; install this one .ankiaddon over Cram Studio and restart Anki. The matching handoff ZIP contains all source/docs/tests and an identical full installer. All earlier features are retained. Quick unit/DOM checks were run; actual Anki/Qt file selection, image encoding and visual layout still need a runtime check.

### 1.7.2 Plain Basic answers

Basic/reversed and other non-cloze flashcard answers no longer get an added highlight background, in either MAIN CRAM or ANKI CRAM. Your chosen revealed-answer text color still applies. Cloze answers retain their separate highlight setting, now labeled **Cloze answer highlight**. Original formatting in your fields is preserved. No setting change is needed; existing saved and automatic palettes work with this fix.

### 1.7.1 Consistent multiple-choice circles

ANKI CRAM's A/B/C/D circles now use a subtle fill like MAIN CRAM, instead of sharing the selected-answer background. Hovering keeps the circle distinct from the choice highlight; a selected choice uses the card-colored circle and accent letter, matching MAIN CRAM's selected style. This applies in both the color preview and actual ANKI CRAM, including light/dark and custom palettes. MAIN CRAM's choice style is unchanged. All1.7.0 color controls and reset behavior are retained.

### 1.7.0 Separate answer colors and automatic palettes

Open **Anki → Tools → CUSTOMIZE CRAM → CUSTOMIZE CRAM COLOR** (or Settings → Customize Cram → Open in MAIN CRAM).

- **Card and page:** card, page, text, accent, borders and the multiple-choice question panel.
- **Revealed answer:** its own text and highlight colors. These are independent of Correct/Got it and apply to Basic/custom answers, cloze answers and ANKI CRAM's revealed multiple-choice blanks.
- **Buttons:** separate background and text, primary button text, and Reveal answer/Show clue colors. ANKI CRAM also colors the real Show Answer button, plus the native rating buttons' shared background/text; their labels, interval text, handlers and scheduling remain Anki's.
- **Answer feedback:** separate correct/wrong choice text and background, selected choice text/background; in MAIN flashcards, Got it and Still learning have their own text/background. These controls are hidden in ANKI flashcard preview because its ratings are native.

Choose **Automatic from card**, then choose **Card**. It derives a coordinated accent, readable text, button surfaces, answer highlight and feedback colors from that base. A first Card edit from Default also starts Automatic. Turn off **Auto** beside an individual color to pin it; the other colors keep adapting. Choosing Automatic again removes manual pins for this theme/card type and keeps Card. Existing manually saved palettes remain intact until changed.

**Reset all colors** clears every light/dark × flashcard/multiple-choice color override and automatic setting. It restores the original white light theme and original dark theme for both modes, not a palette based on your custom card. It preserves flashcard size. **Default** in the scheme selector resets only the selected theme/card type. Changes are drafts until **Save**; **Cancel** discards them. MAIN/ANKI previews share the same saved palettes and show their respective layouts. The Question/Answer selector lets you inspect revealed answers and feedback.

This is the complete same add-on, package `cram_studio`. Install this one file over the existing Cram Studio and restart Anki. The matching handoff ZIP contains the full editable source, docs, quick checks and identical installer. Study List remains separate. No long tests or live Anki/Qt visual test were run for this update.

### 1.6.1 Blank navigation and raised question panel

In both MAIN CRAM and ANKI CRAM multiple choice, **Up/Down selects the previous/next blank** and **1–4 picks an answer for that active blank**. It wraps at the first/last blank. Your earlier selections stay in their own blanks. Clicking or focusing another blank's choice group synchronizes the keyboard target. Only the active blank has a soft background, and its matching Blank label has a small colored dot. No keyboard tutorial is added to the study card.

ANKI CRAM now also routes Up/Down through window shortcuts while an unanswered supported MCQ is ready. This reaches the review card even when keyboard focus is in Anki's native bottom bar. Those shortcuts disable on reveal, original-flashcard fallback, waiting choices and leaving review, and are deleted at profile closure. Anki's native Space, ratings 1–4 after reveal, E/B/undo and queue remain unchanged.

The question now sits in a separate rounded **borderless panel with a soft shadow**, above the choices, in both modes. Numbered blanks, rich headings and list layout are retained. The panel adapts to text zoom and screen width.

To change its color: **Tools → CUSTOMIZE CRAM → CUSTOMIZE CRAM COLOR → Multiple choice → Question panel**. Default **Match card automatically** derives a gentle tint from the current card/accent palette in Light or Dark. Uncheck it to pick an independent color. MAIN CRAM and ANKI CRAM have live previews; Save, Cancel and Reset continue to work.

Complete in-place update, including deck totals and whole-deck regeneration. 110 short Python tests and the DOM harness pass, including bottom-bar shortcut routing/enabling, mouse/focus/arrow synchronization, one active highlight, stable question nodes and automatic/custom panel colors. Real desktop Qt shortcut delivery, pixel layout and live Gemini generation remain unverified here. No long tests were run. The generated screenshot shown in chat is a visual mockup, not a runtime screenshot.

### 1.6.0 Complete deck totals and whole-deck regeneration

The deck picker now includes a lesson's cards temporarily held in filtered decks. Parent counts include subdecks when Include subdecks is on, matching the selected study scope. Selecting a home deck together with its filtered deck counts/loads each card once. Selecting a filtered deck alone still uses only the cards currently in that filtered deck. All filters continue to intersect the selected scope through Anki's search. MAIN CRAM does not move cards or change schedules to achieve this.

**All questions** is now the default practice limit. Deck totals are Anki card totals before filters. Practice question counts can be smaller because Basic/reversed siblings share one practice question and unsupported/empty notes may be skipped. Use **Refresh** next to Decks & subjects after changing decks/cards elsewhere in Anki.

**Regenerate deck choices** is now available:

- MAIN CRAM: select decks, then click **Regenerate deck choices** below Start studying.
- ANKI CRAM: below an unanswered ready multiple-choice card, click **Regenerate deck choices**.
- Either mode: **Anki → Tools → Regenerate deck choices**.

Choose decks, optionally include subdecks, then click **Preview**. It shows the full card count, practice question count and choice-set count. Click **Regenerate N choice sets** to replace cached choices for the entire selection. Practice filters and question limits do not constrain this action. The planner includes MAIN CRAM mappings and actual native Basic/reversed template directions, so saved sets work for both modes. Image-only/long answers continue to use flashcards.

Generation uses small batches and your Gemini quota. Pause keeps completed batches; Resume processes only unfinished sets. Closing retains batches already saved, but the in-memory unfinished plan is not restored after reopening. Existing single-question regeneration remains available. Finishing a deck operation can refresh the same still-unanswered native card, clearing its choice selection; an already revealed/different card is never replaced. Anki queue, native ratings, intervals, undo and filtered rescheduling are unchanged.

Complete in-place update, including customization and the question-aware/multiline-choice fixes. 107 short Python tests and the DOM harness pass. Tests cover parent/home/filtered totals, overlap/chunk deduplication, native-search intersection, full-deck scope despite filters/limits, Basic direction coverage, saved-batch pause/error/resume and native refresh guards. Actual desktop Qt layout and live Gemini generation remain unverified here. No long tests were run.

### 1.5.1 Question-aware choices, numbered answers and regeneration

Gemini now receives stronger question-first instructions: each wrong choice must fit the specific question's wording, context and grammar while remaining incorrect. It considers the correct answer and the other blanks in the same question, using close concepts or common misconceptions rather than merely similar words. The original question and correct answer remain fixed. The prompt asks for complete comparable lists for list answers. This improves the requested generation criteria; semantic correctness still needs your judgment.

Numbered/multiline answers retain their separate lines in MAIN CRAM and ANKI CRAM. HTML numbered lists get explicit markers, line breaks and nested indentation in option text; selecting a list keeps those lines in the cloze blank. Manual wrong-choice editing also supports multiple lines. Choices remain escaped text, not executable HTML.

**Regenerate choices:** in either mode, open an unanswered multiple-choice question and click **Regenerate choices** below the card. MAIN CRAM already had this action; ANKI CRAM now exposes it too. It replaces the current question's choices, including all blanks in that current cN, and clears selections on success. It does not bulk-regenerate an entire deck. Repeat on a question from any deck. MAIN CRAM may require pausing background generation first. ANKI CRAM keeps current choices while preparing a replacement, preserves them on failure, and rejects late replacements after reveal/card changes. It never answers or advances Anki's card.

New sessions use a new choice-cache revision so the question-aware instructions take effect. Previously stored cache/history is retained. Generate once for the selected/current questions, then reuse those results offline. No extra model verification call was added.

Complete in-place update, including 1.5.0 customization. 95 short Python tests and the DOM interaction checks pass, including list conversion/rendering, contextual job payloads, cache revision and forced/cancelled/failed/stale native generation. Real Gemini output quality and desktop Anki pixel layout were not tested here; no long tests were run.

### 1.5.0 Customize Cram

Open **Anki → Tools → CUSTOMIZE CRAM**, or **MAIN CRAM → Settings → Customize Cram → Open**.

- **Card size:** select Flashcards or Multiple choice, then drag the right, bottom or corner handle on the live sample to change width/height. Number fields offer precise adjustments. Switch Preview between MAIN CRAM and ANKI CRAM, and Side between Question and Answer. Save applies the selected type’s shared size to both modes. Reset to default size restores each mode's original responsive dimensions.
- **CUSTOMIZE CRAM COLOR:** choose Light or Dark, then Flashcards or Multiple choice. Pick Default or Custom and adjust background, card, text, accent, border, selection, correct and incorrect colors. Both modes have live previews. Colors are saved separately for each theme and card mode; Reset all colors restores every default palette.
- Save updates an open session in place. Cancel or closing the editor discards unsaved changes. MAIN CRAM's auto-continue pauses while customization is open and waits for your next study action afterward.
- Dimensions are responsive percentages, with viewport height caps keeping the study controls accessible. Ctrl/Cmd + wheel over the card still changes only text; outside it, interface zoom adjusts layout without storing zoom-scaled pixel dimensions. Narrow windows may constrain a saved size. Image occlusion keeps its existing frame, colors and zoom controls.
- Removed MAIN CRAM's persistent under-card keyboard/self-marking guide text and repeat-mode instruction. Functional study buttons and optional Settings help remain available. ANKI CRAM keeps its clean interface.

This is a complete in-place update. Existing profile preferences, API key, cache, history and all scheduling boundaries are retained. 86 short Python checks and the DOM interaction harness pass, covering transactional saves, invalid input, palette isolation, stable card/choice nodes, drag capture, reset and paused auto-continue. Desktop Anki/Qt and actual browser pixel layout could not be tested here; no long tests were run.

### Earlier releases included

### 1.4.2 ANKI CRAM layout and F11 cleanup

This update changes **ANKI CRAM only**. MAIN CRAM's dialog, HTML, JavaScript, CSS, practice queue, settings and study controls are unchanged from 1.4.1.

- ANKI CRAM's header now has a centered deck name and scheduling status, the mode name at the left and one small exit button at the right. Symmetric side tracks keep the deck centered independently of the left/right content widths.
- Removed duplicate Edit/Browse/Undo buttons, the text-size toolbar, visible zoom percentages, shortcut guide/button and instructional study text. The native bottom Edit button is hidden only in ANKI CRAM; E still edits. Anki's native ratings/intervals and More menu remain available.
- Keyboard controls remain functional: Space/reveal, native rating keys, MCQ choice/blank selection, E/B/Ctrl+Z, Ctrl/Cmd+wheel text/interface zoom, and Ctrl/Cmd+0 reset. MAIN CRAM retains its own guides and controls.
- Flashcards use a larger adaptive frame, up to 74% of the reviewer viewport, with room for the header and native ratings. The old 58vh/650px cap is removed. Both faces use the same height through reveal and text zoom. MCQ uses the same minimum study area and grows for longer questions or multiple choice groups.
- On Anki versions exposing show_menubar/hide_menubar, a temporary guard suppresses native hover-triggered menu reveals while ANKI CRAM's actual main window is in F11 fullscreen. Native F11 exit still restores the menu. Leaving ANKI CRAM, closing the profile or failing to start restores the previous callback, without overwriting a later add-on wrapper. Other modes/windows retain their menu behavior. No Anki bar preferences are changed.

The first-card flip timing fix and occlusion's fixed preview/viewer controls remain included. 78 short Python checks and the DOM interaction checks pass, including scoped fullscreen restoration and clean headers in both modes. Real Windows/Qt fullscreen hover behavior and pixel layout remain unverified here.

### 1.4.1 first-card flip timing

Fixes an ANKI CRAM answer appearing immediately instead of animating on the first flashcard. New answer scenes now commit their front transform and wait across two animation-frame callbacks before flipping vertically. The explicit initial rotateX(0deg) supplies the starting transform. This applies to compiled flashcards and original-renderer fallback cards with an available front snapshot. Detached scenes, changed cards/epochs and question-side redraws cancel stale callbacks. Reduced-motion preferences still disable the animation.

This is the complete 1.4.0 update plus the presentation timing fix. Anki reveal, ratings, scheduling, filtered-deck behavior and MAIN CRAM remain unchanged. The new DOM regression queues separate frame boundaries for cold first cards, later cards, native fallbacks and rapid redraws; it verifies callback timing, not real browser paint or desktop Anki rendering.

### 1.4.0 names, mode identity, and study controls

The two entry points are now **Tools → MAIN CRAM** and **Tools → ANKI CRAM**. Both are included in this complete update of the same add-on; keep the existing `cram_studio` package and profile data. The deck overview uses these same names. MAIN CRAM's window title, home header and session header say **Practice only · Schedule unchanged**. ANKI CRAM has its own visible name and a status showing actual Anki reviews, filtered rescheduling on, or filtered preview with rescheduling off.

| Mode | Queue and buttons | Effect on Anki |
| --- | --- | --- |
| MAIN CRAM | Choose practice count, filters and order; Still learning / Got it or practice choice feedback | No ratings, due-date changes, FSRS changes or Anki review entries, including when practicing cards from a filtered deck |
| ANKI CRAM | Anki's existing queue, limits, order, intervals, rating/preview buttons and undo | Anki handles the answer, including the filtered deck's rescheduling setting |

For the mode based on Study Now, open a deck and choose **Tools → ANKI CRAM → Flashcards or Multiple choice → Start ANKI CRAM**. ANKI CRAM does not offer a separate practice count or shuffle order. MAIN CRAM retains its deliberate independent practice options.

**Text zoom in both modes:** Ctrl/Cmd + wheel over a flashcard or multiple-choice card changes the card text. The flashcard frame and image sizes stay fixed; text can scroll inside the card. Outside those cards, Ctrl/Cmd + wheel zooms the interface. ANKI CRAM also has Card text − / + / Reset controls and a Shortcuts guide; Ctrl/Cmd + 0 resets the focused card text or interface. Its interface zoom includes the native bottom bar and restores both webviews' previous zoom when leaving ANKI CRAM. Text size is saved in profile preferences. Rich native text is measured before applying zoom so nested bold/highlighted text scales once, and Reset restores original inline styles.

**Flashcard consistency:** supported Basic/cloze cards in ANKI CRAM use the same compiler and numbered blanks as MAIN CRAM, with a vertical flip and the full cloze sentence restored on the back. Other cloze numbers stay visible as context. Basic/reversed direction follows the actual Anki card. The extra Full Anki answer panel was removed in1.10.2. Typed-answer, scripted and unmapped templates retain their original Anki rendering. Up/Down flip supported flashcards without rating them. Space/reveal and the rating/advance operation remain Anki-owned.

**Multiple-choice consistency:** choices fill the selected numbered blank and can be changed before reveal, with Up/Down to select a blank. ANKI CRAM uses 1–4 for choices on a ready question, then Anki's original 1–4 callbacks after reveal. E, B, Ctrl+Z and other Anki shortcuts are preserved. MAIN CRAM's automatic-continue and repeat-mistakes rules do not replace ANKI CRAM's required Anki rating/preview action. Image occlusion continues to use image recall with its fixed preview, zoom, reveal and larger viewer.

74 short Python regressions and the DOM harness pass, including native text sizing/reset, compiled cloze faces, fixed card/image nodes, original native rating buttons/intervals, zoom restoration, and scheduling isolation. No real desktop Anki/Qt or live Gemini verification was possible here.

### 1.3.1 visible entry point

Open the deck you want to study, then choose **Tools → ANKI CRAM**. Choose Flashcards or Multiple choice. This native menu entry remains available when an overview theme hides Anki's bottom controls. The existing overview button is retained. Outside a deck overview, the menu explains that you need to open a deck first. All 1.3.0 features remain included.

### 1.3.0 scheduled review and presentation update

Open a deck, then **ANKI CRAM** next to the overview controls. Choose Flashcards or Multiple choice. This starts the existing Anki reviewer through the same Study Now entry point. It does not build a replacement queue: Anki supplies the current card, daily limits, ordering, sibling burying, native ratings, displayed intervals, review operation, and undo. The regular Study Now button still opens Anki's usual presentation.

| Entry point | Progress and scheduling |
| --- | --- |
| Tools → MAIN CRAM / MAIN CRAM overview button | Independent practice. No Anki rating, scheduling change, or review log entry. |
| Open a deck → Tools → ANKI CRAM / overview button | Real Anki reviews. Ratings update Anki through its normal reviewer. |
| ANKI CRAM on a filtered deck with rescheduling off | Anki's own filtered-deck preview behavior, including its configured delays and return-to-home behavior. The add-on never changes the reschedule setting. |

**Scheduled flashcards:** Space or clicking the card reveals through Anki; then press the native rating key or click the native Again/Hard/Good/Easy button. That rating also advances; no separate Continue is required. The card flips vertically. The displayed times are Anki's actual button labels; they follow Anki's Show next review time preference. Native audio, typed-answer templates and original flashcard HTML remain available.

**Scheduled multiple choice:** before reveal, 1–4 choose A–D for the active blank. Change a choice freely; use Up/Down or click to switch numbered blanks. Space/Anki's Show Answer reveals feedback, then 1–4 are Anki's rating keys again. A correct choice never automatically assigns Good or Easy; you choose the rating. Cards without usable text choices, typed-answer templates, and unmapped custom templates use original flashcards. Basic reversed cards follow their actual Front/Back direction, rather than independent practice's shorter-field heuristic. Every cN remains its own scheduled card. The duplicate Full Anki answer panel was removed in1.10.2.

**Scheduled image occlusion:** the current actual card's mask group is shown in a fixed preview with header, image zoom, reveal, and a larger viewer. Revealing does not rate the card. Anki's rating buttons remain below the interface. Hiding/revealing an already shown answer is cosmetic; Anki remains on its answer side. Unsupported mask formats use the original Anki card instead of skipping it.

E, B, Space, Ctrl+Z, flags, bury/suspend, audio, and other native shortcuts stay assigned to Anki. The presentation only intercepts number keys for ready multiple-choice questions before reveal; afterward their original callbacks run. Edit and Browse open Anki's native current-card handlers. Undo uses Anki's own undo stack, including whichever Anki operation was most recent. Fresh question renders clear local selections. The independent Cram automatic-continue/repeat preferences do not control this mode.

Multiple choice reuses saved choices. The start dialog offers an explicit **Automatically create missing choices with Gemini** option (off by default), explaining that current-card text is sent to Google and uses API quota. Without it, Create choices is available per card. Space can still reveal a waiting card, or Use original flashcard can switch its presentation. API errors do not rate, skip, or discard a card. Only one choice request runs at a time; old results may fill the cache but cannot replace another current card. Profile-local settings/cache are shared to avoid entering a second key; independent practice history is kept separate from actual Anki reviews.

**MAIN CRAM changes:** vertically flipping cards; no instruction text inside the card; centered expand/collapse arrows; a single underline for each blank (including underlined note text); explicit native-search labeling; additional due/not-answered/today/suspended/leech quick buttons; explicit inclusion of filtered decks in the picker. The search accepts any syntax supported by the installed Anki version, including queries absent from the quick buttons. A blank search still means all cards in the selected current deck locations.

Question order now includes Random cards, Random note then card type, Card type then order gathered/random, Deck then random notes, creation ascending/descending, Due date then random/deck, Deck then due date, and retrievability ascending/descending. **Anki card columns** lists every sortable card column exposed by that Anki release, with a Descending toggle: this supplies Due, Interval, Ease, Lapses, Reviews, FSRS difficulty/stability and other available native sorts without guessed scores. Native-column orders run through Anki's find_cards column API. Due presets preserve native Due groups and adjust only tie-breaking. These order selected independent questions, before the question limit; actual scheduled reviews always follow Anki's own preset and filtered-deck ordering.

### 1.2.0 study flow update

Choices fill numbered blanks immediately and can be changed before checking. Every mode now tests one actual cN at a time; the other cloze numbers remain visible context. Same-cN spans stay together. Flashcards turn with a back-to-back 3D flip; their backs show the original cloze sentence with its answers restored in the blanks. Card size stays fixed. The three study controls have matching widths and a centered layout.

Learn starts as soon as the current question's choices are ready, with future choices prepared in the background. Previously saved choices are reused. The deck picker is a collapsible, indented family tree. Question order can be shuffled, creation date ascending/descending, or native Anki retrievability ascending/descending. Automatic continue defaults on after checking/rating and has an adjustable feedback delay. UI labels use American English; note content is preserved.

The 1.1.0 native Anki filters, light/dark centered layout, field mapping, private Gemini settings, optional repeat-mistakes queue, honest first-attempt scores, and startup fixes remain included. This is the complete add-on update, with the same package identity and profile data.

### Retained 1.0.1 startup fix

Fixes the window staying at “Opening Cram Studio…”. The app now waits for the HTML body and Anki's asynchronous bridge before requesting the deck list. The old startup order was reproduced in a regression test. Startup failures and missing responses now show a retry control instead of waiting indefinitely. Duplicate opening requests are coalesced. That fix kept the package identity and profile data. Install this file over the previous Cram Studio version and restart Anki.

## Install and open

1. In desktop Anki, choose **Tools → Add-ons → Install from file**.
2. Select **Cram-Studio-v1.10.7.ankiaddon**, then restart Anki.
3. Open **Tools → MAIN CRAM**, or press **Ctrl+Alt+M** (**Ctrl+Shift+T** also works). A MAIN CRAM button also appears in the standard deck overview and the deck options menu.
4. For actual Anki reviews, choose a deck and press **Ctrl+Alt+A**, or choose **Tools → ANKI CRAM**.

The window opens maximized with the normal title bar, restore button and X. It supports narrower windows and light/dark appearance. This is a desktop Python add-on; it cannot be installed in AnkiMobile or AnkiDroid.

## Practice

Select one or more decks, choose whether to include subdecks, set the number of questions or **All questions**, choose question order, then choose a mode. Use the chevron beside a parent to expand or collapse its children; selecting a deck and expanding it are separate actions. Searching temporarily shows matching descendants even inside collapsed branches.

| Mode | Text / cloze behavior | Image occlusion |
| --- | --- | --- |
| Flashcards | Read the clue, reveal, then mark Still learning or Got it. Each actual cloze card tests only its own cN. Other clozes remain visible context. | Recall the active mask group, reveal, then self-mark. |
| Learn (multiple choice) | Four choices per answer. Each actual cN is a separate question, with a numbered choice set for every span belonging to that cN. Choose all its blanks, then check; partial credit is given per blank. | Uses the same reveal-and-recall image test. |
| Mixed | Alternates recall and choices. Cloze groups remain separate actual cards in this mode. | Uses the same image test. |

Repeated deletions with the same cN stay together in every mode; each visible blank gets its own numbered choice set in Learn. For `{{c1::life}} is {{c2::good}}`, one question tests `life` with `good` visible, and another tests `good` with `life` visible. An active outer nested cloze covers its inner deletions. Only cloze cards included by the selected decks and filters are blanked. Basic reversed/optional-reversed templates become one question per note.

Basic defaults to the shorter field as the answer (Back wins ties). Use **Choose answer / clue fields** before starting if this is wrong for your deck. Custom note types can map both fields. The complete clue field, including semantic bold headings, is preserved. Template scripts, hidden content, audio directives, and remote images are stripped. This is field-based practice, not a complete execution of arbitrary custom card templates.

Native image occlusion supports rectangle, ellipse and polygon masks, grouped by the original card's cloze ordinal. Yellow masks are the current target; gray inactive masks stay masked for Hide All Guess One notes. Reveal removes only the current target group. The header remains visible; Back Extra appears after reveal. Unsupported legacy mask formats and cards with no recognizable target masks are skipped with a count instead of exposing an unmasked answer. Image-only clues, image answers, and answers over 600 text characters use flashcards rather than misleading AI text choices.

Image previews use a fixed frame. +/− zoom only the image and enable scrolling inside that frame; Fit resets it. The full-screen image viewer has its own reveal/zoom controls and an X (Esc also exits). The image element is moved between views rather than reloaded.

Results show partial-credit points, self-marked recall points, elapsed time and question review. **Review missed questions** repeats original questions that lost first-attempt points; **Repeat set** repeats the original set without duplicating its prior retries. The latest 30 completed session summaries are saved. An unfinished session is not restored after closing the window. “All questions” has no fixed 40-card truncation; the interface displays one question at a time.

## Anki filters

The **Filter cards** search box uses Anki’s native `col.find_cards()` search. Leave it empty for all cards in the selected decks. Quick buttons fill in All, Due, New, Learning or Review searches. Tag, note type and flag controls are combined with the search using AND; an OR expression in the search is grouped before combination. **Clear all** resets the filters while retaining deck selection. **Check matches** shows the matching card count before grouping cards into questions. Invalid searches show an error rather than falling back to all cards.

| Search | Cards included |
| --- | --- |
| blank | All cards in selected decks, including future/new/suspended cards |
| `is:due` | Anki’s due review/learning cards, including overdue cards |
| `is:learn` | Anki’s learning cards |
| `is:new` | New cards |
| `is:review is:due` | Review cards that are due |
| `is:due -rated:1` | Due cards not answered in Anki today |
| `rated:1` | Cards answered in Anki today |
| `is:due prop:due=0` | Due today only, excluding older overdue dates |
| `is:new or is:learn` | New or learning cards |
| `tag:leech` / `prop:lapses>=3` | Leeches / cards with at least three lapses |

Due means the native search result, not the limited daily reviewer queue. MAIN CRAM answers never change Anki’s `rated:1` results or due dates. ANKI CRAM ratings are actual Anki reviews and follow its normal search/scheduling behavior. The syntax available depends on your Anki version. This does not import Study List’s separate custom star data. See the [official Anki search manual](https://docs.ankiweb.net/manual/searching).

## Question order, keys and text size

**Question order** is selected before starting. Creation order uses Anki's note-creation ID, oldest or newest first; c1 remains before c2 for the same note. Ordering happens before the question limit is applied. Shuffled order is regenerated for a newly built set. The order menu affects question sequence; answer choices are independently shuffled.

Retrievability delegates to Anki's discovered sortable browser column through `col.find_cards(query, order=column, reverse=...)`. It does not estimate recall from lapses/ease or alter Browser sort preferences. Low-to-high and high-to-low account for the column's native default direction. Cards lacking FSRS values follow Anki's native handling. The options are unavailable when that version does not expose a suitable column. Use a current desktop Anki release if needed. Retakes preserve the selected original sequence; an enabled repeat-mistakes queue deliberately inserts retries later.

| Action | Keys |
| --- | --- |
| Choose A, B, C, D in Learn | `1`, `2`, `3`, `4` or `A`, `B`, `C`, `D` |
| Check / continue | `Space` or `Enter` |
| Select previous / next numbered blank | `Up` / `Down`; clicking a blank or its choices also selects it |
| Flip flashcard | `Space`, `Up` or `Down`, or click the card |
| Still learning / Got it after reveal | `1` / `2` |
| Navigate previous / next answered card | `Left` / `Right` |
| Open shortcut guide | `?` or Settings → Shortcuts |
| Close modal / image viewer | `Esc` |
| Resize flashcard text, fixed card frame | `Ctrl` + wheel while pointer is over the card (also `Cmd` on macOS) |
| Zoom the complete page | `Ctrl` + wheel with pointer outside the flashcard |
| Reset text / page size | `Ctrl+0` with focus on card / outside, or Settings → text size → Reset |

Number/letter keys act on the highlighted active blank; changing a selection updates the same blank. Use Down or click another blank for the next answer. Space on an incomplete question selects the first unanswered blank instead of submitting it. Typing inside inputs is never intercepted by study shortcuts. Held keys do not check/advance repeatedly.

This follows Quizlet's familiar Space-to-flip and arrow navigation, with additional Cram Studio grading/multiple-choice keys. It is not a claim to reproduce every shortcut in every Quizlet mode or editor. See [Quizlet's Flashcards guide](https://help.quizlet.com/hc/en-us/articles/360030988091-Studying-with-Flashcards) and [Quizlet's study tips](https://quizlet.com/blog/7-tips-and-tricks-for-studying-on-quizlet).

**Settings → Automatically continue** defaults on, saved per profile. Learn shows brief feedback after Check answer before advancing; delay choices are 0.6, 1, 2 or 4 seconds. Space/Enter can continue sooner. Flashcards continue after the self-rating, without another Continue click. Revealing alone never assigns a rating. Opening Settings, the shortcut guide or an image viewer pauses an already scheduled advance; you can then continue manually. Manual navigation cancels an old timer so it cannot skip another question. Turn automatic continue off to read every result at your pace.

**Settings → Flashcard text size** offers plus, minus and Reset too. Only letter size changes; card height, controls, and images retain their frame dimensions. Long text scrolls inside the card. Reduced-motion system preferences disable the flip animation.

## Several different answers with the same c1

For `A {{c1::cell}} forms {{c1::tissue}} and then {{c1::organs}}.`, this is one question with `(1) _____`, `(2) _____`, `(3) _____`. The correct answers remain `cell`, `tissue`, `organs` in that order. Learn supplies a separate four-choice set for every numbered blank; each is scored against its own answer. Flashcards reveal all three answers in their original sentence positions on the back. The shared c1 identifier does not merge their text or interchange their correct answers.

## Repeat missed questions during a session

**Settings → Repeat missed questions**, also visible under Study options, defaults **off** and is saved per profile. Off: the session ends after the set, even if there are mistakes. On: any missed point adds that whole question to a random later position in the same session, with at least one intervening question when another is available. It can return again until answered correctly. If it is the only question left, it returns next.

A partially correct three-blank cloze returns as the same three-blank question. Image recall returns the same active mask group. Repeats shuffle already saved choices locally; they make no Gemini request and do not reset the full set. Changing the setting during an active session applies to the next session; the running queue stays consistent.

Results and history keep the original first-attempt score separate from repeat attempts and final mastered-question counts. A correct retry does not erase an original mistake. The X can still leave an unfinished session; only completed sessions enter history.

## Gemini setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/apikey). Do not send your key in chat.
2. In Cram Studio, open **Settings → Gemini settings** → paste the key → **Test connection** → **Save**.
3. The default model is `gemini-3.5-flash-lite`. Use **Refresh models** and test another model if your project does not have access. The model ID is editable.
4. Start Learn or Mixed. Click **Generate choices** when requested. You can use Flashcards instead without an API key.

Connection testing makes one small real generation request. The first waiting question gets a small priority request (up to five sets), followed by batches of five sets. Every batch is validated and saved. A session opens immediately after you authorize Generate: cached/flash questions work at once, and a waiting question becomes answerable as soon as its choices arrive. The entire set no longer has to finish first. API/network latency still determines the first uncached response; no live timing benchmark is available here. Original answers are inserted locally and cannot be changed by the AI. Each blank gets one correct answer and three distinct wrong answers. Choices are shuffled for each attempt. Changed clue/answer text, a changed model, or a prompt-version change invalidates the matching cache key. Repeating unchanged questions uses the cache without a new API request.

Only selected text clues and correct answers needed for new choices are sent to Google. Images, full collection files, review history and keys are never sent in the prompt. No remote scripts or fonts are loaded by the UI. Gemini may still produce a semantically ambiguous or incorrect distractor; **Edit choices** lets you correct the three wrong answers while the original answer stays locked. **Regenerate choices** explicitly requests fresh choices for that question and may use additional quota.

The add-on does not enable billing, silently switch models, or retry paid requests automatically. To stay within the free tier, keep billing disabled in your Google project and select an eligible model. Free-tier quotas, eligibility, and data-use terms are controlled by Google. Model discovery lists access, not prices. A 429 pauses generation and preserves completed batches and the current practice answers. Ready questions still work; use Resume later or switch the waiting question to a flashcard. No repeated automatic retries or parallel request burst is used. Pause waits for the current in-flight request (35-second timeout). Invalid keys, unavailable models, rejected JSON output and network failures have separate messages. Cached choices, flashcards and image recall work offline.

On Windows, Save stores a key encrypted with Windows DPAPI for the current Windows account. On other systems the key is session-only; alternatively configure `GEMINI_API_KEY` in the environment before starting Anki. There is no plaintext-key fallback. **Forget saved key** removes the saved/session key; an environment variable must be removed outside Anki. Keys do not enter the web view, installer, source ZIP or practice JSON.

## Scheduling and local data

MAIN CRAM reads deck/card/note data through a `QueryOp`. It never calls Anki's scheduler or answer-card APIs and never updates cards, notes, tags, deck options, review history, due dates, FSRS values, or new-card progress. The new ANKI CRAM entry deliberately uses Anki's real reviewer; its ratings and undo go through native Anki operations. It adds no separate scheduling engine and makes no direct scheduling/database writes. With no filters, practice includes selected future/new/suspended cards too. Filters narrow that selection through native Anki search. This is independent practice; daily review limits do not reduce the result count.

Practice data is stored in **your Anki profile folder / cram_studio / practice.json**. It holds model preference, field mappings, repeat/automatic-continue/text-size and native-interface preferences, cached distractors and the latest 30 session summaries. The cache contains study text and should be treated as personal data. Windows protected keys use the adjacent `key.dpapi` file. These files are not included in either distributed package. Practice data is profile-local and is not synchronized through AnkiWeb by this add-on. A full deletion of that folder resets this add-on's local data; it does not touch your Anki collection. Windows keys must be entered again when moving to another Windows account.

## Validation and compatibility

This build targets the desktop Anki 23.10+ Qt6 API shape, using the working Study List integration as a reference. Future versions cannot be guaranteed. Python syntax, JavaScript syntax, 78 automated Python checks and the DOM interaction harness passed. The tests include native-reviewer delegation spies that reject scheduler/database access by the skin, filtered reschedule on/off preservation, native rating/reveal command pass-through, stock/reversed/cloze/typed template behavior, original HTML and button preservation, stale worker/packet rejection, and shared-store separation. They also cover native order delegation/direction, creation-order ties, live blank changes, small first batches, progressive readiness and stable option indices, grading while generation runs, stale worker rejection, Space/automatic-continue timer races, tree collapse, text-only/global zoom, and the preserved startup behavior. They also include a before/after SQLite collection snapshot, a mocked Gemini REST contract, quota interruption/resume persistence, distinct choices, grading, cloze grouping, mask-group rendering, startup request coalescing/retry, and stable image nodes across reveal/zoom/viewer transitions.

The DOM harness additionally covers scripts loading before body elements exist, a delayed Anki bridge, duplicate DOM events, bridge timeout, Retry, backend failure and a late successful response. The original 1.0.0 JavaScript fails the new startup-order test; 1.0.1 passes it.

Live desktop Anki/Qt execution, native Windows DPAPI, pixel-level layout, and a real Gemini request have **not** been verified in this environment. Anki/Qt and a browser binary were unavailable, and no user API key was supplied. Use the built-in Test connection after installation. No long test suite or real Google generation was run. A bounded attempt to obtain the Anki backend could not reach the package host; native review scheduling/undo behavior was checked by inspecting current and 23.10 Anki source and exercising the delegation boundary with spies, not by running a real collection review.

Primary references checked on 2026-10-23:

- [Anki reviewer source](https://github.com/ankitects/anki/blob/main/qt/aqt/reviewer.py)
- [Anki GUI hooks](https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py)
- [Anki filtered deck behavior](https://docs.ankiweb.net/filtered-decks.html)
- [Anki display order](https://docs.ankiweb.net/deck-options.html)
- [Anki public collection/search ordering source](https://github.com/ankitects/anki/blob/main/pylib/anki/collection.py)
- [Models and availability](https://ai.google.dev/gemini-api/docs/models)
- [Pricing and free-tier eligibility](https://ai.google.dev/gemini-api/docs/pricing)
- [Generate Content REST reference](https://ai.google.dev/api/generate-content)
- [Models API](https://ai.google.dev/api/models)
- [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

## Continue development

Give the complete **Cram-Studio-Handoff-v1.3.0.zip** to your next assistant and ask it to read START-HERE.md. That ZIP contains this exact source, tests, build script and matching installer, so development can continue without reinterpreting or redesigning the add-on.
