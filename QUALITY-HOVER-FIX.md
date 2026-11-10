# 2.0.24 — Groq semantic distinctions and remaining hover layers

## Report and boundaries

The user supplied depletion/scarcity/shortage/exhaustion for an IPv4 address
limitation, MTU alongside MTU-size/name variants, and four names for the same law
in a fair-use stem. They report this mostly with Groq and say Gemini is working
well. They also still observe roughly one-second hover flicker in MCQ.

Gemini's existing prompt, schema and temperature are byte-for-byte unchanged.
The portable regression includes a SHA-256 golden contract captured from 2.0.23.
Grok's request contract and all providers' Writing grouping stay unchanged.
No credentials or user card data were accessed or included in this source ZIP.

## Choice changes

Groq's multiple-choice request is still one call with the selected model, same
temperature/output cap/reasoning setting and existing bounded transport/pools.
It now uses a shorter prompt with explicit bad-set examples and a same-response
concept audit. The original id/answer_aliases/wrong fields remain; additional
required fields are answer_concept, wrong_concepts and wrong_reasons. The latter
arrays have exactly three strings aligned with wrong. The instructions require
short factual contrasts, real sibling concepts when available, and broader
related-but-wrong concepts when the narrow category is insufficient.

Local validation checks all required contrast fields and rejects canonical
identities that repeat the correct concept, alias, or each other. It does not
claim to prove whether an AI's factual reason or canonical name is true. A
model can still make a semantic mistake with different fabricated identities;
no universal semantic dictionary or second independent AI is implied.

Pure shared guards address the reported ambiguities in their specific contexts:
IPv4 address-supply wording, MTU/MTU-size and misleading MTU name changes, and
alternate Copyright Act names in a Section 107/fair-use stem. They also apply
to fresh cache preparation/attachment and the manual choice editor. No general
merging of similar words or arbitrary legal/network terms is performed.

Invalid results fail before cache saving, using existing safe error handling.
There are no automatic paid retries, extra verifier calls, model substitutions
or invented fallback terms. Only the original three wrong strings are saved.
Additional response metadata can cost output tokens and time; no actual Groq
speed or quality measurement was made.

Use Regenerate deck choices for the affected Groq decks. PROMPT_VERSION and
cache IDs intentionally stay unchanged to retain valid Gemini sets. Existing
attached options and saved MAIN snapshots are not silently rewritten, because
that could invalidate picks. Known bad cached examples fail fresh preparation;
explicit regeneration replaces old attached choices as usual.

## Hover evidence

The previous release protected the button box but missed child label opacity,
panel animations and pseudo-element overlays. A real Qt/Chromium reproduction
injects generic inherited-theme hover CSS and moves/presses/releases the mouse.

With 2.0.23, the extended test observed label opacity 0, a theme-fade animation
on the choices panel and an active white pseudo-element overlay in BOTH modes,
even though the button itself correctly reported opacity 1/animation none.
Eight unrelated body-class mutations caused eight full appearance applications
in ANKI CRAM. These are verified synthetic cases, not proof of the user's exact
installed third-party theme or Windows compositing behavior.

With 2.0.24, label opacity stays 1, panel/label animations are none, overlays are
disabled, and unrelated class mutations cause zero appearance applications.
One real night-mode change applies once; changed customization still applies;
a repeated identical status/config packet does not repaint. Native/main scroll
positions stay at 357/412 in the overflow fixture, exact option nodes/picks
remain stable, and no additional ready/generation bridge message is sent.

Presentation memoization is keyed by root, mode, actual theme and appearance
value; a reference fast path avoids reserializing an unchanged image-heavy
configuration on incidental hover/focus mutations. No global Anki theme,
Flashcard flip animation, scheduler or native answer/rating control is replaced.

## Bounded checks

- 302 Python tests, including the eight new quality tests, passed.
- The complete Node UI suite passed.
- Extended test_choice_stability_qt.py passed, with before/after baseline above.
- test_mcq_space_qt.py retains the three-blank Space/selection guard.
- test_mode_transitions.py and test_flash_space.py retain mode, Writing,
  reveal and explicit native-rating behavior.
- Full installer/source parity, archive CRCs, all bundled checksums and the
  embedded installer are verified before delivery. Archive writes now use an
  atomic temporary-file replacement so a partial build is not exposed.

Tests run with synthetic fixtures and offscreen Qt 6.9.2/Anki 25.9.2 on Linux;
there is no Windows OS or live Groq/Gemini/Grok quality test. Commands:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -q
node tests/test_ui.cjs
python3 tests/test_choice_stability_qt.py
python3 tests/test_mcq_space_qt.py
python3 tests/test_mode_transitions.py
python3 tests/test_flash_space.py
python3 build.py
```

Keep the full installer and full source separate, preserve package ID
cram_studio, and include all previous prompts/assets/tests/docs in future
continuations. Do not treat this single-request self-audit as a guarantee that
an arbitrary model cannot return a wrong or ambiguous option.
