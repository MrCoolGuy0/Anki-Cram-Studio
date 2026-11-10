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

# Groq choice quality in 2.0.24

Groq multiple-choice generation uses a shorter provider-specific instruction and
requires answer_concept, wrong_concepts and wrong_reasons in the SAME response.
The common pipeline validates these fields before storing the original three
wrong strings. No second validator API call, automatic repair loop, provider
fallback or model change is introduced. This does not change Gemini/Grok
contracts or any provider's Writing grouping request. More output metadata can
use more tokens; real API response speed/quality is not guaranteed.

Regenerate the affected Groq decks to replace old attached/saved choices. The
existing cache namespaces and formats are retained. Known reported ambiguous
sets are checked contextually across providers, including fresh cache reads.
The local rules are narrow; novel semantic correctness depends on model output.

# AI provider integration — 2.0.21

Current providers: Google Gemini, Groq, and Grok (xAI). Groq and Grok are separate
services; their keys and endpoints are not interchangeable. There is no arbitrary
custom/OpenAI-compatible URL option. Existing quiz UI, customizers, scheduling
boundaries and shortcuts are preserved.

The 2.0.20 shared prompts/factory design below remains in use. New details:

- ai.Grok adds xAI Responses support through fixed https://api.x.ai/v1/.
  POST responses uses input messages, text.format JSON Schema, max_output_tokens
  8192, stream:false and store:false. No tools or previous_response_id are sent.
  Reasoning items are ignored. Only completed assistant output_text is parsed;
  incomplete, error, refusal, unexpected tool and malformed responses fail before
  caching. Original choice/alias/source-span validation then applies unchanged.
- GET models reads the authenticated key’s model catalog, retaining Grok text
  IDs and excluding known image/video/voice/audio models. Test connection checks
  actual choice generation, rather than assuming catalog access proves inference.
- Current default is grok-4.7, as listed in xAI’s official documentation on
  30 October 2026. No model is changed automatically after an error. The add-on
  makes no free-tier or latency guarantee. API access may require xAI credits.
- Data model token: grok:<raw-model-id>. Old Gemini strings and groq: tokens are
  byte-compatible with 2.0.20. Do not conflate Groq and Grok namespaces.
- Grok key storage is key-grok.dpapi; environment fallback is XAI_API_KEY.
  key.dpapi/GEMINI_API_KEY and key-groq.dpapi/GROQ_API_KEY retain their meaning.
  Three providers use separate session keys and separate per-origin connections.
- KEY_ENV, KEY_URLS and KEY_CONSOLES define provider-specific settings help. The
  Grok help points to console.x.ai and explains that a Cursor/agent key may not
  grant model API access. Do not identify key validity from a prefix alone.
- HTTP402 reports billing/credit requirements. HTTP401/403 reports key/model
  access and the relevant console. Error bodies/secrets are not shown/logged;
  there are no automatic retries, fallback providers or alternate key probing.
- The user exposed a possible key in conversation. That value is not used,
  recorded in these sources, embedded in packages, or tested. The user must
  revoke it and enter a replacement privately in the installed settings UI.
- All production generation call sites still use ai.client under the historical
  Gemini injection alias for regression fixtures. That name is provider-neutral
  at those call sites; direct gemini.Gemini remains the Gemini-only REST class.

Additional official references checked 30 October 2026:

- https://docs.x.ai/developers/quickstart
- https://docs.x.ai/developers/models
- https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- https://docs.x.ai/developers/rest-api-reference/inference/responses
- https://docs.x.ai/developers/rest-api-reference/inference/models

Short validation: 288 Python tests, complete Node suite and real Qt settings
checks passed. Windows DPAPI was mocked for file-isolation tests. No live key or
user collection was used. See tests/test_grok_provider.py for xAI contracts,
three-provider migration and MAIN/native scheduling boundaries.

# Historical 2.0.20 implementation notes

# AI provider integration — 2.0.20

Supported providers in this release: Google Gemini and Groq. This does not add
arbitrary OpenAI-compatible/custom endpoints. Existing quiz UI, customizers and
Anki-native rating/undo/filter scheduling are retained.

- ai.py owns provider definitions, Groq REST adaptation and client routing.
- gemini.py keeps the original prompts/schema and shared choice/alias/Writing
  validation. generate_json is the only provider-specific generation seam.
- Production callers import ai.client under the historical Gemini injection
  name, preserving the existing regression-test seam. It is no longer a
  Gemini-only constructor in dialog.py/live_review.py/deck_choices.py.
- data.model keeps the original Gemini string for legacy compatibility, or
  groq:<raw-model-id> for Groq. That namespace flows through existing cache IDs.
  ai_models remembers the raw selected model for each provider. Do not remove
  the Groq namespace or alter old Gemini cache keys during future refactoring.
- Keys: legacy key.dpapi for Gemini, key-groq.dpapi for Groq; session keys are
  separate. GEMINI_API_KEY and GROQ_API_KEY are separate environment fallbacks.
  get_model_key resolves keys from the captured generation model, preventing
  a paused/stale plan from sending the active provider’s different key.
- On Windows existing DPAPI behavior is retained. DPAPI was mocked for the
  isolation test; actual Windows encryption was not run on Linux.
- NetworkJobs keeps bounded pools; transport identity is (thread, origin).
  Fixed HTTPS origins, header-only authentication, no redirect/retry/cookie
  persistence, bounded response reads and existing cancellation are retained.
- Groq uses POST https://api.groq.com/openai/v1/chat/completions and GET models,
  Bearer auth, non-streaming JSON and max_completion_tokens=8192. GPT-OSS uses
  low reasoning effort; other models do not receive an unsupported effort.
- Known strict-schema Groq models use lowercase JSON Schema types with all
  properties required and additionalProperties:false. Other text models use
  JSON Object mode plus the explicit schema in the system message. Both routes
  must pass the same local validators before anything is cached. Refresh models
  filters known audio/guard models; it does not prove every returned model has
  project access, JSON support or free pricing. Test the selected model.
- No hidden provider/model switch, automatic retry or credential probing.
- Provider changes preserve old cache/history/sessions. A resumed MAIN session
  retains attached choices. New/missing choices use the selected provider.
  To replace saved options deliberately, use single-card regeneration or
  Regenerate deck choices; preview selects the entire requested decks.

Run short checks from this source root:

    python3 -m unittest discover -s tests -p 'test_*.py' -q
    node tests/test_ui.cjs
    QT_QPA_PLATFORM=offscreen python3 tests/test_ai_settings_qt.py
    python3 build.py

Anki/PyQt dependencies (or the provided test stubs) are needed for relevant checks.
The production add-on uses Anki’s bundled requests/Qt and needs no Groq SDK.
No live API key is included. Supply your own key only in the installed UI.

Official API references checked 30 October 2026:

- https://console.groq.com/docs/api-reference
- https://console.groq.com/docs/structured-outputs
- https://console.groq.com/docs/models
- https://console.groq.com/docs/quickstart
- https://ai.google.dev/gemini-api/docs/structured-output

Current model availability and limits can change. Do not claim measured speedup
or perfect distractor quality without a real authorized API test.
