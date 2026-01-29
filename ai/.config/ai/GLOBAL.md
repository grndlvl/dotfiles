## Model Routing Guidance

Use a local model for:
- summaries, ticket drafts, docs
- PR descriptions, changelogs
- log or diff digestion
- small refactors in a single file
- unit test scaffolding

Use Claude for:
- auth, permissions, security
- migrations or data integrity
- multi-file refactors
- unclear or ambiguous requirements
- anything that feels risky

If a task fits the local category, suggest using the local model instead of doing it here.
