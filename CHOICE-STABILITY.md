# Choice stability — verified 30 October 2026

Reported: loaded choices disappear/flicker around cursor movement or choosing an
answer, appearing to reload for 1–2 seconds. The user also reported Groq’s generic
invalid-choice error and asked whether answer-letter randomness comes from AI.

## Reproduced on released 2.0.21

The bounded real Qt WebEngine fixture uses actual CSS/JS, a scrollable set of
long options, native mouse press/release and synthetic cards. Baseline output:

- MAIN: choices pane scrollTop 412 → 0 on choice focus. The clicked lower answer
  moved away before mouse release; no pick was recorded.
- ANKI: scrollTop 357 → 0; no pick recorded.
- ANKI under a simulated generic theme hover rule: computed animation theme-fade,
  opacity 0, nonidentity scale transform. MAIN already had a hover guard.
- ANKI: initialize with choices pending, receive ready choices, then invoke mount
  twice on the same root. Old code read the stale initial data-packet, deleted
  all four choices, changed ready back to false and sent two extra ready messages.

These are reproducible bugs that can explain the report. They do not establish
which installed theme/add-on or exact event sequence occurred on the user’s PC.
No claim is made that a live AI call was triggered by a plain pointer move.

## Corrected behavior

- selectBlank returns early for the already-active blank. It still honors a
  requested question-pane scroll, but does not reset the answer pane, rewrite
  blanks or create duplicate checkpoints merely because a button got focus.
- Native mount records the actual root identity and returns for the same root,
  card, epoch, side and display. receive synchronizes data-packet to the latest
  packet. A newly rendered root or a changed side/epoch still initializes.
- Native render uses one reusable window.cramNativeShown callback and checks its
  presence before adding it to the current Anki onShownHook array. Replacing the
  array still installs the callback. Ordinary Anki is not wrapped or overridden.
- Native answer buttons opt out of inherited animations/transforms/transitions
  and filters. Enabled options remain opaque. Palette hover/selection colors and
  rating UI are preserved. MAIN’s existing stable-hit-box rule remains.

## After-fix real Chromium observations

- MAIN: scrollTop 412 → 412, pick [3], computed animation none, opacity 1,
  transform none.
- ANKI: 357 → 357, pick [3], same stable hover values.
- Two repeat mounts retain all four exact option DOM nodes, ready:true and pick
  [3], with zero extra bridge calls.
- An explicit regeneration revision still replaces options and clears picks.
- Existing real native-controller mode-transition scenes retain late/cached
  choices, partial Writing history, reveal behavior and explicit ratings only.

## Specific, safe AI errors

Old error text combined incomplete/duplicate/synonymous/invalid outcomes. The new
error reports the actual local reason. Choice acceptance is otherwise equivalent:
three nonempty text options, each ≤600 characters, distinct from the correct
answer, its provided aliases and one another under the existing identity rules.
No semantic accuracy guarantee is added, and no hidden retry/API pass is added.
Untrusted parse-error strings are never interpolated into user messages.
Existing saved cache remains untouched on a failed batch.

## Answer letters

content.attach_choices uses random.SystemRandom locally. AI returns only the
three distractors; Cram inserts the original answer, shuffles, then saves its
correct index in the active question. Each position has equal probability; a
sequence of identical letters is possible. Tests cover all four positions with
an injected shuffle and ensure an attached question does not reshuffle on refresh.
This release leaves randomness, question ordering and saved cache IDs unchanged.

## Short validation

From the source root with Anki/Qt dependencies available:

    python3 -m unittest discover -s tests -p 'test_*.py' -q
    node tests/test_ui.cjs
    QT_QPA_PLATFORM=offscreen python3 tests/test_choice_stability_qt.py
    QT_QPA_PLATFORM=offscreen python3 tests/test_mode_transitions.py
    python3 build.py

Results: 293 Python checks, full Node suite and both real Qt scripts passed.
Python took about 2.4 seconds; no long test run was used. Headless Linux graphics,
D-Bus and Qt cleanup warnings are environment messages, not Windows validation.
No live provider, real API key or user collection was accessed. The fixture’s
--observe-baseline option prints the old-release observations without asserting
corrected behavior, for reproducing the before/after comparison when needed.

Preserve these regressions and complete-source delivery requirements in future
updates. Do not replace this add-on with a recreation based only on these notes.
