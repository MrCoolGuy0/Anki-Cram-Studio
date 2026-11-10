# Measured request wait and bounded parallelism — 27 October 2026

The user's supplied numeric-only log has6 jobs and19 HTTP calls. Aggregate
HTTP time444654.70ms /19 =23.403s per call. Queue maxima0.51ms, cache-save
mean6.587ms per saved batch, HTTP share99.967% of recorded worker wall time.
Thus the measured remaining wait is in HTTP, not queueing or saving. HTTP
includes network setup/transit and server generation; these numbers do not
identify Google processing alone, an ISP issue, free-tier throttling or a server
outage. Prior error labels may simply reflect Pause after a valid saved batch.

Version2.0.19 overlaps at most two bulk requests, using profile-owned API child
workers outside Anki's collection/general task pools. A priority first batch
completes before parallel background work. Single-card regeneration, native
per-card generation and Writing remain sequential. Choice instructions, model,
API options and validation are unchanged. There are no new automatic retries.

Bulk checkpointing tracks exact saved IDs, not an assumed completed prefix:
if a later batch succeeds before an earlier batch fails, the successful set is
retained and Resume targets only unsaved IDs. On cancellation/failure no further
requests are scheduled; in-flight results are collected and valid ones saved.
HTTP429 marks profile-session concurrency1 for the next explicit Resume; no
quota/billing change occurs. Profile close cancels queued work and rejects old
callbacks. Numeric timing context is shared with a lock; api_parallelism marks
that summed HTTP durations can exceed wall time when requests overlap.

The complete Python/Node suites passed, plus targeted final quota regressions. New bounded
worker/barrier tests verify two simultaneous starts and the two-request cap,
priority availability, cancellation draining, non-prefix failure/Resume and429
fallback. Privacy, timings, connection reuse, native scheduling boundaries and
all prior UI tests pass. These checks use synthetic replies, not the user's
API/collection; real Google latency and overall speedup remain unmeasured.

---

# Generation efficiency follow-up — 27 October 2026

User confirms the old-worker rollback2.0.17 remained slow and requests the
latest worker fix again plus actual speed improvements. Version2.0.18 restores
the2.0.16 base and adds persistent HTTP, selective MCQ cache copying and larger
bounded bulk batches. AnkiLink1.1.2 remains untouched.

The original urllib.request.urlopen transport sends Connection:close. The new
requests-based transport reuses a connection per profile-owned Gemini worker,
with a fresh API-key header per request, disabled cookies/machine auth, no
redirects or hidden retries, bounded reads and generic credential-safe errors.
Profile shutdown closes sockets on a separate cleanup thread, never while
blocking the UI on an active request. Controllers still run on dedicated
workers and return completions through Anki's main-thread bridge.

A local real HTTP/1.1 test served five requests on one connection and four new
Gemini clients on one worker connection. Tests verify quota/redirect requests
are never retried, unexpected origins are rejected before network, large
responses are capped and the connection can recover. A10,000-entry unrelated
cache with copy tripwires is never visited while updating a single card.
Bulk25 short sets now use10+10+5 requests instead of5+5+5+5+5; priority1 then
10+10+4 unlocks the first question early. Long answers shrink batches; cancel
and partial-error resume preserve completed work. This proves lower request/
connection/copy overhead, not an end-to-end speedup on Google's real service.

Validation:256 short Python checks passed in3.78 seconds; full Node UI checks
also passed. No live Google API or user collection was accessed.

Both Gemini generate/group_answers method ASTs match2.0.16 exactly: quality
instructions, schema, sampling/output limits and validation are unchanged.
There is no switch of model, reasoning level or automatic billing/retries.
All interface assets remain byte-identical to2.0.16. Local numeric timings
remain available if actual request latency is still excessive on the user's PC.

---

# Follow-up: regeneration queue isolation — 27 October 2026

The user reports regeneration became much slower after the review-worker fix.
The previous response assumed unchanged request bodies implied unchanged
latency; that was not a measured comparison and missed another scheduling path.
Anki's shared non-collection executor also accepts AnkiLink HTTP/media jobs.
When that executor is occupied,2.0.15's Gemini submission waits before issuing
its request. A bounded reproduction using the actual submission expression
confirmed the wait with a saturated shared pool, without any Gemini request.
This is a possible regression mechanism; it is not evidence of actual worker
saturation on the user's computer.

Cram2.0.16 routes all six network entry points into an independent three-worker
profile-owned pool. Collection operations still use QueryOp/CollectionOp.
Callbacks return through Anki's main-thread bridge. Profile close cancels queued
work and suppresses old completions without blocking the UI on network joins.
The existing per-generation batch and quota/error/cancellation logic is retained.
No concurrent batch fan-out or hidden retries were introduced.

Queue wait, HTTP/decode/cache-save totals and total worker time are recorded in
a bounded local numeric-only log. No key, URL, study text, error text or account
identifier is logged or sent anywhere. Logging failure is nonfatal. No interface,
choice prompt/model/schema/request options or scheduler logic is changed.

247 short Python checks (3.55s) and the full Node UI suite passed. Every Gemini
entry starts with both Anki worker pools held busy. Additional checks cover
result/error/main-thread handoff, queued cancellation, stale-profile callbacks,
log privacy/permissions/rotation. A before/after fake-transport comparison found
identical Gemini request URL, headers, body and timeout, and identical MCQ and
Writing method ASTs. No live user API key/request/collection was used. Actual
end-to-end Gemini response speed is not measured in this environment.

---

# Follow-up: review-worker contention — 26 October 2026

The user's pauses became less frequent after the previous fixes, but persisted.
The prior audit missed TaskManager.run_in_background's uses_collection=True
by default. Anki25.9.2's TaskManager uses one collection executor thread, so
HTTP/media/Gemini work submitted without opting out queues ahead of native
collection operations. It does not need to run on the GUI thread to delay
reviewing. A periodic AnkiLink bootstrap runs even with its window hidden;
this is a concrete plausible source of intermittent Processing pauses. There
is no fixed every-six-cards trigger in these add-ons; network timing and study
speed determine when contention is visible.

AnkiLink1.1.2 marks its HTTP/local-media Controller.run jobs collection-free.
Cram2.0.15 does the same at all six direct network-only TaskManager submissions.
Catalog/export/import/search/snapshot operations retain QueryOp/CollectionOp
serialization. Real collection access is never moved to the parallel pool.
No UI, native scheduling, ratings, undo or stored progress logic is changed.

Validation: new short queue tests failed before the fix and passed after it.
AnkiLink79 Python checks (12.29s), Cram242 Python checks (2.21s), both full
Node suites passed. A separate local probe ran the unmodified official Anki
25.9.2 TaskManager with real Qt signals/executors. The old default held up a
next-card job; the fixed Link method allowed it while HTTP remained pending;
completion stayed on the main thread. All six Cram flags were also checked.
Primary source: https://github.com/ankitects/anki/blob/25.09.2/qt/aqt/taskman.py

This demonstrates an avoidable queue blockage, not that it is the sole cause
on the user's PC. No actual user profile/collection, live Gemini request or
real chat account was accessed. Study List0.6.17 and Sounds1.1.8 unchanged.

---

# Add-on review-pause audit — 26 October 2026

The supplied Windows screenshot shows Anki's native “Processing…” progress
window during a normal review. That window signals a running operation; the
screenshot alone cannot identify which operation/add-on caused it. This audit
covers our four source versions, not every add-on installed on the user's PC.
No real collection, message or profile was opened or changed in these checks.

## Confirmed avoidable work and fixes

- Study List0.6.16: while its window remained open, operation_did_execute
  scheduled an external refresh after card/study-queue changes. The external
  callback rebuilt the current list through a serialized collection QueryOp,
  even while the window was behind the normal reviewer. A slow selection can
  therefore compete with review operations and show Anki's progress UI.
  Version0.6.17 marks it dirty during an inactive native review, defers both new
  notifications and already queued preserving refreshes, then refreshes once
  with the scroll anchor when Study List becomes active. Active Study List,
  Browser edits, filters, stars and closed-window cleanup remain intact.
  Four actual-method tests prove30 native answer notifications queue zero
  background collection queries, and returning still schedules a refresh.
- AnkiLink1.1.0: its read-only presence hook looked up the deck and submitted
  presence again for every card, including unchanged study activity. Version
  1.1.1 caches a same-deck leaf name briefly and coalesces equal notifications.
  Thirty same-deck callbacks now make one deck lookup and one submission in
  the controlled test. Deck/state changes and heartbeat expiry still work.
  No review hook performs synchronous network requests or collection writes.

## Other source checks

- Cram2.0.13/2.0.14: card_html immediately returns the original HTML when native
  ANKI CRAM is inactive. Study Now/ratings/undo remain owned by Anki. MAIN CRAM's
  catalog/filter QueryOps occur on its explicit UI requests, not on normal
  per-card transitions. The home layout patch does not change review rendering,
  native hooks, scheduling methods, Gemini generation or stored progress.
  The complete Cram suite passed240 short Python checks plus its full Node suite.
- Study Sounds1.1.8: reveals are intentionally silent. Windows rating callbacks
  post an in-memory command to the existing isolated audio worker. Pipe writes,
  acknowledgement waits, device operations and process cleanup happen in that
  worker, not on the GUI callback. There are no collection QueryOps. Its55
  checks passed; a deliberately stalled helper left reveal/rating/mute/close
  dispatch at0.027ms in the local test. No Sounds code/audio was changed.

## Practical limits

These tests identify and remove two concrete sources of unnecessary work. They
cannot prove those were the only cause of the user's intermittent pause. Native
scheduler operations, sync/backups, large templates/media, disk contention, or
other installed add-ons can also show Processing. A streak/achievement overlay
is visible in the screenshot; its implementation was not available in this
workspace and has not been blamed or modified. If pauses persist, record what
operation was active and compare in a separate test profile/add-on isolation
session before attributing the cause. No long or disruptive user-PC test was run.
