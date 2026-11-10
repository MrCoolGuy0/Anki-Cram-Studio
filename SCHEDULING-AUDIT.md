# Cram Studio 2.0.24 — Groq quality and hover presentation

Provider-specific choice prompts/response validation and pure context guards
have no collection access. Network pools, batching, keys, cache ID policy,
queues, ratings, undo and filtered-deck rescheduling remain unchanged. Hover
changes affect CSS and presentation memoization only. The existing native ans
bridge and Space fix remain unchanged. MAIN practice still does not call the
Anki scheduler. Invalid choice results fail before saving, with no hidden retry.

302 short Python tests include MAIN schedule/revlog and native normal/filtered
tripwires. Native Groq generation still performs one request without revealing,
rating or replacing a queue. Node and real Qt checks cover hover, no hover
bridge traffic, retained option nodes, theme/customization changes, Space,
Writing and revealed mode transitions. No live API or user collection is used.

Historical audits follow and apply to their named releases.

# Cram Studio 2.0.23 — MCQ Space reveal presentation

Question-side MCQ Space now calls the existing JavaScript reveal guard, which
sends Anki's native `ans` bridge message once. Anki still performs Show Answer,
selects the next card, computes intervals and applies ratings/undo. Answer-side
Space, numeric ratings, filtered deck rescheduling and normal Anki callbacks
remain native. No scheduler or collection calls are added. Retained DOM nodes
and a pending selection guard affect presentation only.

294 short Python tests include normal/filtered reschedule-on/off tripwires.
The Node suite covers correct/wrong/incomplete reveal and fresh-card reset.
Real Qt checks use synthetic cards, native callback spies and no live API;
Flashcard Space and mode transition regressions are included. No Windows OS
or user collection was accessed.

Historical audits follow and apply to their named releases.

# Cram Studio 2.0.22 — choice stability and validation feedback

Runtime changes affect selection focus/scroll, native shown-hook installation,
idempotent DOM setup, native choice hover CSS and AI validation error reasons.
The native controller’s queue/reveal/rating/undo methods are unchanged. MAIN
practice generation/session paths are unchanged. Prompts, acceptance criteria,
cache keys, AI endpoints and bounded worker settings remain intact. The new
ChoiceValidationError is a ValueError subclass with fixed displayable reasons;
unexpected parser errors use a generic safe-format message.

293 short Python checks include existing MAIN schedule/revlog and native filtered
rescheduling tripwires. Node DOM and real Qt mouse/focus/remount/hover checks pass.
The actual-native-controller Qt mode-transition regression also passes with
explicit ratings only. No user collection, live API or Windows OS was used.

Historical audits follow and apply to their named releases.

# Cram Studio 2.0.21 — xAI provider addition

Grok (xAI) uses the existing shared generation/grouping validators and bounded
network pools, with its own xAI origin, cache namespace and profile key. API
selection writes only profile settings. All call sites retain their captured
model-to-key routing. The Grok client cannot access an Anki collection.

288 short Python checks passed, including existing schedule/revlog tripwires
and two new MAIN/native Grok integrations. The native filtered/reschedule-off
fixture generates through the production router without any reveal, rating or
scheduler access. The MAIN fixture creates choices and saves only profile cache
and practice state without a collection. Existing normal/filtered scheduling
checks remain intact. Node UI and real Qt settings tests passed; no actual user
collection, Windows OS or live xAI request was used.

Historical audits follow and apply to their named releases.

# Cram Studio 2.0.20 provider integration

Gemini and Groq share choice validation, Writing source-span validation and the
existing bounded batching pipeline. Provider selection and keys live in profile
settings only. Network pools are partitioned by thread AND provider origin;
captured generation models select the matching provider key even if another
window later changes active settings. Requests remain outside Anki’s collection
executors and diagnostics never contain keys or note text.

The 277-test short Python suite passed, including unchanged MAIN schedule/revlog
tripwires and native normal/filtered rescheduling behavior. A new native Groq
fixture generates choices through the production provider router without any
reveal, rating or scheduler access. The complete Node interaction suite and a
real Qt settings test passed. These are synthetic/local tests, not a real user
collection, live provider request or Windows scheduling integration.

Historical audits follow and apply to their named releases.

# 2.0.10 follow-up — 26 October 2026

The new in-session MAIN restart resets only its profile-local practice checkpoint.
New tests trip on any collection access during restart. Canonical Writing events,
held missed-answer feedback, mask toggles and corrected revealed clue text are
practice/presentation changes. Native rating/queue/undo/filtered rescheduling
code is unchanged. 229 fast Python checks (including prior boundary checks) and
the complete Node suite pass; real WebEngine input checks use synthetic notes
and native-operation spies, not a user collection or a live Windows Anki session.
The native entry buttons open setup only. This follow-up does not attribute
unexpected reviews in a real collection to a specific cause.

Original detailed audit follows.

# Cram Studio 2.0.9 Flashcard Space follow-up

Space is now explicitly a presentation action only while active ANKI CRAM is in Flashcards mode and flash/native display. It uses the existing guarded native ans bridge once for the initial reveal; subsequent presses only toggle the rendered face. No default-rating callback is invoked by Space in this scope. 1–4 and native buttons still own every rating, native intervals, undo and filtered-deck rescheduling remain unchanged. The original Space callback is retained and invoked in ordinary Anki and other modes, including image occlusion. Mode changes are checked at keypress time. Native card/side/queue are not reset by visual re-hiding.

MAIN uses an optional profile-only flashSeen view field, separate from which side is showing, to keep explicit recall controls available after a reveal. Its checkpoint sanitation and resume do not write collection/card/scheduling data. Space precedes generic Continue handling for non-IO Flashcards; explicit rating and configured continuation after an actual rating retain existing behavior. Every CSS, content/matching, generation, session grading and collection-facing implementation outside the scoped native Space guards is unchanged from2.0.8.

223 Python tests and the complete Node suite pass. Real Qt tests/test_flash_space.py uses the actual LiveReviewer, native shortcut wrappers, actual QShortcuts, two WebEngine views, and native callback spies. Repeated Space presses from card/rating-button focus never grade, native ratings remain mounted and require explicit keys, MCQ and Writing controls stay native, ordinary Anki Space is restored after exit, and normal/filtered/reschedule settings stay unchanged. The MAIN seen-answer checkpoint survives reopening without inventing a score. No user collection, Windows Anki/Rust scheduler or live Gemini request was used. Historical audits below apply to their original releases.

# Cram Studio 2.0.8 revealed-view follow-up

Runtime changes are limited to native MCQ preparation guards (live_review.py), native mode rendering (web/live.js), and a native-review-only visible Writing counter (web/writing.js), plus the app version label. Every CSS file and matching/extraction/storage/MAIN controller/session implementation is unchanged from2.0.7. The existing native card, side, deck, callback and rating-button ownership remain Anki's. No queue, scheduler, rating, undo, reset or next-card implementation is added or invoked by these fixes. Missing choices may finish preparing while that same card's answer is displayed. Forced replacement/reshuffling of an existing revealed choice set remains blocked. Native Writing accepted/missed/events are not changed by displaying all items as revealed.

219 quick Python tests and the complete Node UI suite pass. New regressions reproduce the prior uncached-answer flashcard fallback and missing answer-side preparation before the fix. A bounded actual Qt WebEngine/controller test verifies uncached/loading/late/cached choices, no MCQ flip surface, repeated mode changes on the same card, complete visible counts with empty/partial typing history, and no automatic native reveal/rating. A real Qt rating shortcut is still invoked explicitly at the end. Normal/filtered deck boundaries, including rescheduling on/off, and existing forced-generation protections continue passing. No user collection, Windows Anki/Rust scheduler or live Gemini API was tested. Historical audits below apply to their original releases.

# Cram Studio 2.0.7 pointer follow-up

Only the shared flashcard pointer gesture and the frontend MCQ blank-handler scope change, plus version/docs/tests/build documentation list. Every Python implementation file remains byte-identical to2.0.6. Text clicks now follow the same existing native Show Answer path as surface clicks; no new rating/queue/reset/scheduler/undo operation is introduced. Native question reveal is guarded once, answer-side flips remain visual, and MAIN flips/selection never grade.

Complete Node UI and four real Qt mouse/clipboard scenes pass: MAIN/ANKI x Basic/Cloze, text click, true held drag, copy clipboard content, rapid/double click without word selection, and drag release without flipping. A revealed-cloze click swallowed by the MCQ handler was found and fixed. No live user collection, Windows Anki/Rust scheduler or Gemini request. Historical audits apply to their own releases.

# Cram Studio 2.0.6 MCQ display follow-up

Only the MCQ question-blank display callers (web/app.js, web/live.js), shared appearance.js/css, manifest/version/docs and tests/build documentation list change. Every Python implementation file, including live_review.py, writing.py, dialog.py, session.py, storage.py and content.py, is byte-identical to2.0.5. Cached question/choice strings and grading indices stay unchanged. No rating, queue, reveal, undo, filtered-rescheduling or Gemini-generation operation changes.

Full Node UI checks and four real Qt WebEngine synthetic MCQ layout scenarios pass. They verify inline first-line bullet alignment for long IEEE/ITU names, soft-newline collapse, explicit source BR preservation, narrow-pane wrapping and native answer redraw. Released2.0.5 styling fails the regression. No user collection, live Windows Anki/Rust scheduler or Gemini request was used. The prior215-test Python boundary verification remains applicable to unchanged implementations.

Historical audits below apply to their respective releases.

# Cram Studio 2.0.5 presentation/typing follow-up

The new ANKI CRAM mode switch preserves the actual reviewer card object and native question/answer side, saves only profile preferences, rotates presentation epochs/cancels stale workers and redraws our own view. No Anki Show Answer/Study Now/answerCard/next-card/rating/reset/undo operation is called by switching. Normal and filtered decks with rescheduling on/off are covered by controller tripwire tests. Native rating-button HTML and callbacks remain owned by Anki. MAIN controller/session/storage and native shortcut routing are retained; focused input/menu/photo guards affect presentation keyboard handling only.

215 Python tests and the complete Node DOM suite pass. Real Qt WebEngine coverage connects the actual LiveReviewer controller to a synthetic DOM/media fixture and real Qt shortcuts. It verifies same-card mode changes, Writing draft/MCQ restoration, caret movement through 40 lines, image fitting, overlay/menu rating-key blocking, and an explicit native rating callback after reveal. Earlier layout/Enter/formatting and four image-first scroll checks also pass. No user collection, live Gemini request or Windows Anki/Rust scheduling integration. Gemini classification behavior is prompted/validated with local fixtures, not claimed to be universally correct.

Historical audits below apply to their original releases.

# Cram Studio 2.0.4 Writing scroll follow-up

The runtime change is confined to web/writing.js and preventScroll focus/version label in web/app.js, plus manifest/docs. All Python controller, scheduler-boundary, matching, generation and profile-storage files remain byte-identical to 2.0.3. Remembered blank anchors and question-pane scrolling are presentation only. Native final matches still invoke the existing answer reveal once, then await explicit native rating. No queue/ease/rescheduling/undo changes.

205 quick Python tests and the full Node UI suite pass. Four real Qt WebEngine image-first scroll scenarios use synthetic notes and verify normal/enlarged text, partial/final matches, focus, native revealed-side DOM replacement and no outer-page scrolling. The regression fails against released 2.0.3 Writing and passes after the fix. No real user collection, Windows Anki/Rust scheduler or live Gemini request was used.

Historical audits follow; version-specific claims below apply to those releases.

# Cram Studio 2.0.3 grouping follow-up

205 quick Python tests and the full Node UI suite passed. New source plans can expose several Writing targets inside a single c1 block while retaining the original card/note/ordinal. Native tests prepare a combined cloze through the actual controller, type its members and verify the same cid, unchanged filtered-deck settings and no scheduler/queue/rating calls. A typed final match still relies on the existing native UI reveal path and explicit user rating; MAIN remains independent. Native controller/Enter/undo/scheduling implementation files are unchanged from 2.0.2.

Actual Qt WebEngine checks passed eight layouts, four previews, six format cases, two composed-cloze scenes and five existing keyboard/reveal/rating flows. Backend grouping and source preservation are covered by real-code tests with fake Gemini responses. No Windows Anki/Rust scheduler, live Gemini request or user collection was used. No long tests.

Historical audits follow; their version-specific source identity claims apply to those releases only.

# Cram Studio 2.0.1 Writing follow-up

194 quick Python tests and the full Node suite passed. Matching changes are local, with no scheduling writes. Native Writing now sends the existing native `ans` command once after the user's successful final Enter/check. Wrong input stays editable; a second unedited Enter explicitly reveals, and edited input is rechecked. Empty Enter can skip/reveal. No ease/grade/queue/reschedule commands are introduced. The native rating remains the user's explicit next action; MAIN scoring is unchanged.

Real Qt WebEngine keyboard tests connected the Writing component to the actual Python matcher and synthetic native callbacks. Five flows passed: correct final check, wrong then reveal, wrong then revision, correct partial enumeration, empty skip. No rating fired during typing/check/reveal. An explicit native `1` afterward invoked the original Again callback. E/typing focus guard, eight layouts/four previews and six inline-format scenes also passed. This is stronger keyboard/rendering evidence than DOM spies, but is still not an integration test of Windows Anki, aq.t or the Rust scheduler. No user collection/live Gemini call; all tests bounded and short.

Historical audits follow; version-specific source/byte claims below apply only to their original releases.

# Cram Studio 2.0.0 Writing scheduling follow-up

Writing adds typed recall while preserving the MAIN/ANKI ownership boundary. All 190 Python checks and the full Node DOM suite pass. New native cases cover normal/filtered decks, rescheduling on/off, source edits resetting only display state, stale messages, full-answer fallback, cancelled/failed/cached grouping and typing every item without invoking reveal/rating/scheduler APIs. MAIN partial matches/drafts survive disk reopen, and matching/reveal alone do not write a practice grade. Existing source-mutation guards, native callback/undo and read-only SQLite scheduling checks still pass.

The shared Writing component contains no scheduler or grade commands. MAIN explicitly grades through its separate PracticeSession/profile files. Native typing updates only the presentation packet; native Anki owns Show Answer, Again/Hard/Good/Easy, interval labels, queue and undo. The new Qt input guard is scoped to focused Writing text on the question side; modifier shortcuts retain their roles.

Eight real Qt WebEngine synthetic MAIN/ANKI Writing layouts and four customizer layouts were checked for containment/JS errors, with representative screenshots inspected. A real Qt E-shortcut/input check passed: typing text/spaces does not trigger Edit; blur restores Edit. This extends the historical DOM-spy checks but does not replace Windows Anki/Rust scheduling integration. No user collection or live Gemini request was used; short tests only.

Historical audit and limits follow. Version-specific byte-identity statements below apply only to their original release, not to 2.0.

# Cram Studio 1.10.4: scheduling boundary audit

## 1.10.8 resized multiple-choice question-panel follow-up

151 Python tests and the complete Node DOM suite pass. The only runtime correction is shared appearance.css question overflow/flex containment, plus version/docs. All scheduling, setup, generation, storage/session, content/cache and frontend JavaScript files are byte-identical to 1.10.7. No native rating, queue, undo or filtered-deck code changes. Actual browser layout/desktop Anki rendering remains unverified; no long tests, live AI calls or user collection writes.

## 1.10.7 selection-guard follow-up

151 Python tests and the complete Node DOM suite passed after adding scoped selection/image-drag guards to recall controls. New tests verify repeated mask/blank interactions retain existing behavior, no native answer/rating is generated, and native Space/1–4/edit/browse keys remain unhandled by the new guard. All Python scheduling/reviewer/setup, content/cache, Gemini and session/storage runtime files are byte-identical to 1.10.6. No live Anki/Qt or browser selection-paint test was possible; the historical runtime/integration limitations still apply.

## 1.10.6 setup/display follow-up

151 Python tests and the complete Node DOM suite passed after removing displayed blank numbers and changing the ANKI setup default. Additional tests exercise actual setup with Qt spies and automatic missing-choice readiness/cache/no-key behavior with a fake Gemini client. Setup starts flashcards with generation disabled while retaining the user's checkbox preference; saved opt-out persists. Visual selection/focus and choice generation do not reveal or rate cards. live_review.py, session.py, dialog.py, storage.py, content.py, ordering.py and gemini.py remain byte-identical to 1.10.5; live_start.py changes only the saved generation preference/default. Existing native ratings/queue/undo/filtered rescheduling boundary tests pass. This is not an Anki/Rust/Qt integration test; no live AI or collection writes were performed.

## 1.10.5 presentation follow-up

The 1.10.5 release changes UI/appearance preferences as described in README/START-HERE. The historical 1.10.4 audit below still records its original results; the newer installer is intentionally different. **145 Python tests and the complete Node DOM suite passed again** after the presentation changes. Native live_review.py/live_start.py, session.py, dialog.py, storage.py, ordering.py, content.py and generation code remain byte-identical to 1.10.4. Added mask controls/taps/Enter are visual only, while native Space/rating callbacks stay untouched. UI scheduling assertions now explicitly verify that IO masks do not send native ans or ratings; native question→answer still arrives from Anki. The earlier unit/Qt limitations still apply.

Date: 23 October 2026

No collection scheduling write or replacement scheduling algorithm was found in the exercised add-on paths. **144 Python tests passed**, including nine added scheduling-boundary tests. The complete Node DOM interaction suite also passed, including added reveal/rating isolation checks. No production-code correction was required. The installer remains byte-for-byte the previously delivered 1.10.4 installer; no reinstall is required for this audit.

These results support the intended separation. They cannot guarantee the absence of every bug or identify why 30 cards reappeared in a particular user's deck.

## What was checked

| Area | Check | Result |
| --- | --- | --- |
| MAIN CRAM card selection | 108 combinations: Flashcards/Learn/Mixed, four search conditions and nine question orders | Read-only test collection unchanged |
| MAIN CRAM lifecycle | Actual controller start, choice generation with a local fake client, grading, wrong-answer retry insertion, checkpoint, close, disk reopen/resume, finish, repeat set, pause and reset | Read-only test collection unchanged |
| Bulk choice generation | Full-deck regeneration plan, including both Basic directions | Read-only test collection unchanged |
| Native card ownership | Flashcards and Learn, normal decks and filtered decks with rescheduling on/off, native-selected cards in a deliberately non-creation sequence | Same native card objects, order and scheduling fields retained |
| Native ratings | All four native keyboard callbacks on the answer side; front-side ready MCQ number keys | Original native rating callbacks invoked once per explicit rating; MCQ choice selection never invokes them |
| Native bridge | Native reveal/rating commands, unknown custom rating/reschedule commands, stale IDs/epochs and unrelated window contexts | Native commands pass through; custom messages do not implement ratings or rescheduling |
| Undo | Explicit native undo and rejection of stale/unrelated-context commands | Delegates to Anki's undo handler |
| UI reveal/feedback | Compiled flashcards, native fallback, cloze MCQ and image occlusion; repeated reveals and 60 seconds of simulated timers per display | Reveal sends only `ans`; no ease/grade/finish/reschedule command generated; native interval/rating buttons retained |
| Source guard | Runtime Python source scan for direct scheduler/back-end/collection mutation APIs and mutation-capable SQL calls | None found |

The read-only fixture includes new, learning, review, relearning, suspended, buried, filtered and cloze-sibling data. It preserves complete serialized SQLite database bytes, deck settings and mutation counts before/after each exercised path. Card fields include due, queue/type, interval, ease factor, repetitions, lapses, original due/deck, flags and serialized FSRS stability/difficulty data. Review log records and collection configuration are included. SQLite query-only mode and explicit API tripwires reject attempted writes or direct scheduler access. A negative-control test verifies that these guards actually fail on attempted writes.

MAIN CRAM saves its scores, generated choices and resumable progress in its separate profile-local practice files. This is distinct from Anki's cards, review log and FSRS data. Completing or resetting MAIN CRAM sessions did not change the scheduling fixture.

ANKI CRAM invokes Anki's existing Study Now entry point, skins the card selected by Anki, leaves the native bottom rating buttons/intervals mounted, and retains native rating/undo callbacks. Tests covered filtered-deck rescheduling flags in both states and verified they were not modified. **The tests do not emulate or independently validate Anki's scheduling calculations.** Native callbacks are spies; they test delegation rather than pretend to implement FSRS or filtered-deck preview behavior.

## Limits

- Anki/aqt and its Rust scheduler were not installed in the test environment. This was not a live Anki scheduling integration test or Windows/Qt input/rendering test.
- The user's ITPM collection, card history, Anki version/settings, sync events and other installed add-ons were not available for inspection.
- The SQLite search helper is a read-only spy, not a replacement Anki search parser. The tests concern whether operations mutate scheduling, not the correctness of Anki search or FSRS.
- The source guard supplements execution tests; it is not a formal proof against arbitrary future code or other add-ons.
- No user collection was opened or changed, and no live Gemini request was made. The checks completed in seconds.

## Why cards can return later on the same day

Anki can finish the currently available cards while learning/relearning cards are still waiting for their next step. Those cards may become available later that day. Learn-ahead settings affect when they appear. Pressing Again on a review card can send it through relearning steps. This is a possible explanation, **not a diagnosis of the reported 30 cards**. Finishing MAIN CRAM independent practice also does not complete Anki's scheduled reviews.

To identify an actual returning card, inspect its Card Info: current card state/due time and review-history timestamps/ratings, together with the deck's learning/relearning steps. A card in timed relearning has a different explanation from a review card unexpectedly receiving an additional review-log entry. A list count by itself cannot distinguish these cases or identify which add-on, native action or sync change was responsible.

Official references consulted:

- [Anki Preferences: Scheduler / Learn ahead limit](https://docs.ankiweb.net/manual/preferences#scheduler)
- [Anki Deck Options: Relearning Steps](https://docs.ankiweb.net/manual/deck-options#relearning-steps)
- [Anki Studying: Editing and More / Card Info](https://docs.ankiweb.net/manual/studying#editing-and-more)

## Reproduce

From the extracted handoff source folder, with Python 3 and Node available:

```sh
python3 -m unittest discover -s tests -v
node tests/test_ui.cjs
```

Focused scheduling-boundary tests:

```sh
python3 -m unittest discover -s tests -p test_schedule_boundary.py -v
```

Relevant additions: `tests/test_schedule_boundary.py` and the scheduling-boundary section at the end of `tests/test_ui.cjs`. No add-on runtime file changed for this audit.
