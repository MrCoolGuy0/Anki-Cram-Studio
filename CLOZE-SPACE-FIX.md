# Cram 2.0.23 — cloze blanks during native MCQ Space reveal

User symptom: a selected cloze answer was visible, then its blank appeared empty
after Space. The supplied screenshot shows ANKI CRAM, a filtered reschedule-off
deck, three blanks, and a selected option for the third blank.

## Scope and evidence

Source inspection found that native Show Answer rebuilt the MCQ clue from its
empty-placeholder HTML and rebuilt every answer button. It also found that an
option's click handler could still mutate picks after a reveal request was
pending. The native Space shortcut did not use the existing JavaScript reveal
guard for this mode. These are verified code paths; the exact original user's
Windows event/theme timing was not reproduced and cannot be proved from a still
screenshot alone.

The fix retains the existing `.cl-exam` subtree across a same-card answer DOM
replacement, keyed by card epoch, clue/slots/options and explicit choice revision.
It reuses the actual blank and button nodes, fills correct answers and updates
disabled/correct/incorrect feedback in place. New cards, different content,
newly ready choices and explicit regeneration still receive fresh nodes.
Only one subtree is retained; a fresh card clears it.

Question-side MCQ Space now routes through `cramNative.reveal()`, which sets
pending and sends the existing native `ans` command once. A JavaScript fallback
prevents Space's browser button activation; key-up on an answer option is also
cancelled. Clicks and number choices are ignored while pending. No incomplete
attempt is blocked from revealing. Wrong or missing picks show the real correct
answer after reveal. Answer-side Space and explicit rating keys stay native.

## Bounded validation

- 294 Python tests passed, including original MAIN scheduling/revlog tripwires,
  filtered-deck reschedule-on/off and native callback routing tests.
- Full Node UI suite passed, including new selected-text, repeat/pending-click,
  retained DOM identity, correct/wrong/incomplete reveal and new-card checks.
- `test_mcq_space_qt.py`: real Chromium/QTest mouse selections for binary,
  information and left to right; one Space reveal request; no lost text before
  or after the native reply; same clue/blank/choice nodes; delayed option click
  ignored; only an explicit 1 invokes a rating. No background API job started.
- Existing `test_choice_stability_qt.py`, `test_mode_transitions.py` and
  `test_flash_space.py` remain release checks for pointer/focus/hover, late and
  cached choices, mode switching, Writing, Flashcard flips and native ratings.

Run from the source folder. Python/Qt need the Anki/PyQt runtime; Node uses only
the bundled lightweight DOM harness. In a normal installed Anki development
environment, use:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -q
node tests/test_ui.cjs
python3 tests/test_mcq_space_qt.py
python3 tests/test_choice_stability_qt.py
python3 tests/test_mode_transitions.py
python3 tests/test_flash_space.py
python3 build.py
```

Tests were synthetic and run with offscreen Qt 6.9.2 / Anki 25.9.2 on Linux.
No user collection, private key, live AI request or Windows OS test was used.
Do not describe these checks as proof about every installed third-party theme.

## Continuation

Keep package ID `cram_studio` and the full release/source pair. Do not regenerate
valid saved choices just to install this UI fix. Preserve existing provider,
Writing, customization, queue and scheduling behavior. All prior prompts/assets
and release notes remain in the full source archive. Do not add auto-rating,
provider retries, alternative fallback choices or new profile storage to solve
a presentation-only problem.
