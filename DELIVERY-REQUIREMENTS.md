# Permanent delivery requirements — updated 27 October 2026

For EVERY future update, provide the user TWO separate download links for EACH
changed add-on: the complete .ankiaddon installer and its complete matching
source ZIP. Never deliver only a patch, only changed files, or a combined ZIP
containing unrelated add-ons as the main delivery. Keep existing package IDs.

Source ZIPs must retain all source code, assets, prompts, build/dependency files,
relevant tests and continuation notes. Verify packaged source bytes against the
installer. Preserve current UI, saved-state compatibility and scheduling rules.
Use the included source as a continuation; do not recreate it from descriptions.
Include these delivery requirements in future source packaging/build allowlists.

For AnkiLink, the FULL source ZIP must ALSO include the exact published hosted
server source, migrations, dependency lockfile, deployment/configuration
TEMPLATES, provenance and restore instructions, in addition to the desktop
add-on and compatible standalone server. This remains necessary when a desktop
update does not change the deployed server version. Never silently substitute
standalone-server source for the exact hosted implementation. Include updated
server source with any server update as well.

Clearly distinguish source backups from personal profile data, live account/chat
rows, private uploads and secret values. Source ZIPs do not contain those data
backups or grant access to an old hosting account. Do not embed live credentials.

Release 2.0.24 adds single-request Groq concept checks, narrow contextual ambiguity guards and expanded hover/appearance stability. Continue to include this
file and all provider prompts, transports, tests and guides in every full source
package. Other add-ons remain separate.
