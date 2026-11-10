# 2.0.26 — shared Writing enumeration repair

## Cause and scope

All three providers already inherited Gemini.group_answers; Writing was not a
Gemini-only feature. The previous strict decoder could reject an otherwise valid
list because a model returned an empty connector field or capitalized/respaced
an exact source label. That error caused the existing whole-answer fallback.
The exact raw provider reply from the user's screenshot is unavailable, so the
specific failing field cannot be established from the screenshot alone.

## Shared changes

writing.grouping_from_items is the single response decoder used by Gemini,
Groq and Grok. Item case/whitespace differences align to original character
positions with word boundaries. Display text is always copied from the source;
no semantic alias, plural rewrite or numeric change is accepted in grouping.
Empty/whitespace and punctuation-only connectors are discarded as presentation.
Other connectors must occur in source gaps. Full coverage is still validated:
unknown framing words, dropped items, changed numbers and cut words fail.

The common prompt reinforces whole enumerations inside one active cloze,
original labels rather than canonical synonyms, and nonempty connector fields.
Groq's MCQ-only extra audit does not replace or modify Writing instructions.
Provider parity tests capture identical Writing prompts/schema/temperature and
exercise identical normalized results for Gemini/Groq/Grok.

An offline fast path handles an explicit count in an English plural heading
and a matching simple list of one-word labels. It supports commas, semicolons,
Oxford/non-Oxford and, source case, rich markup and hyphenated labels. It uses no
subject answer dictionary. For the reported five-item list it builds five targets
before consulting AI/cache, so a stale single-item cache cannot mask the repair.
It deliberately defers compounds, dates, prose, unfamiliar connectors, mismatched
counts and ambiguous multiple-cloze counts to the existing shared semantic path.
It is not a universal natural-language parser or a reason to ignore meaningful
content when AI/connection fails. The safe whole-answer fallback remains for
unresolved grouping errors, with its existing visible message.

Grouping/cache/MCQ IDs are retained. Matching, source templates, counters,
partial reveal, enter/reveal/rating handling, saved sessions, colors, dimensions
and scheduling implementations are unchanged. No extra paid verifier/retry,
model switch, collection write or UI redesign is added.

## Evidence

314 short Python cases pass. Nine new cases cover Basic/one-cloze five-target
offline plans, old single-cache precedence, separators/count boundaries, identical
provider requests, empty connector tolerance, literal source/markup preservation,
rejection of aliases/dropped numeric content, native filtered reschedule-off
read-only behavior for all three provider settings, and partial MAIN disk resume.
Existing tests retain changed-number protection, case/enye/plural input handling,
compound/date safety, ignore-extra policy, wrong-answer revision and rating guards.

The full Node UI suite passes. A focused real Qt 6.9.2 WebEngine test renders MAIN
and ANKI Writing at 1360px light and 620px dark: five blanks, 0/5 -> 1/5, only
sweet revealed while others stay blank, exact original comma/and layout on full
reveal and no horizontal page overflow. Its first QA attempt had an incorrectly
quoted test selector; corrected test passes without a product UI change.

Synthetic fixtures only; no live Gemini/Groq/Grok API request, Windows OS/GPU,
production account or actual user's scheduler was tested. Shared prompts and
validation do not guarantee an arbitrary model will classify every sentence.

Deliver the complete installer plus complete matching source, retain all earlier
features/prompts/assets/tests and package identity cram_studio on continuation.
