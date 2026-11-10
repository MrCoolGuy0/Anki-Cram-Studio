# Cram 2.0.25 — shared AI rules and balanced option wording

Groq now inherits the entire Gemini multiple-choice prompt instead of replacing
it with a shorter version. Its extra canonical-concept/reason audit is appended
to those shared rules, within the same single API request. Gemini and Grok use
the same base instructions. Writing grouping remains identical for all three.

The shared prompt explicitly requires matching capitalization, grammar, naming
level, specificity, approximate length, acronyms/expansions and list layout.
Wrong options must not all add a category suffix, prefix or explanation that the
unchanged correct answer lacks. The reported Parasympathetic / three Nervous
System expansions is an explicit example; the rule generalizes to other subjects.
It must choose accurate established labels, never blindly strip meaningful words.
The existing shared display-time ALL CAPS/lowercase/title/sentence-case handling
continues in both MAIN CRAM and ANKI CRAM. Original answers remain locked.

No extra verifier request, auto-retry, model substitution, scheduling change or
UI redesign is introduced. PROMPT_VERSION stays 4 to preserve valid caches and
saved picks. Regenerate choices or Regenerate deck choices for affected sets;
old saved choices are not automatically rewritten during a question.

305 short Python checks passed, including full Gemini-prompt inheritance,
request/data integrity, suffix/case instructions and writing-provider parity.
The Node UI suite also checks existing casing, formatting and both interfaces.
Tests use synthetic responses; no live provider key, paid request or real note
was used. Shared instructions improve consistency but cannot guarantee identical
quality from different models. Provider factual/semantic validation is unchanged.

Keep the full installer and matching source ZIP separate in every update.
Continue package cram_studio and retain all prompts/assets/tests/earlier fixes.
