# Project Rules & Guidelines

## Verification & Context Preservation (`$VERIFY_STEPS`)
- When code changes are requested and implemented, proactively run safe verification commands and display their output rather than asking the user to run them manually.
- List any remaining manual steps if interactive or non-automated testing is required.
- Be prepared to answer questions to help re-establish context.
- Questions asked for context clarification MUST NOT generate code changes or git commits.

## Clarify Unclear Requirements (`$NO_BIG_ASSUMPTIONS`)
- Do not make large assumptions without asking first.
- If requirements are unclear or underspecified, ask for clarification before implementing rather than risking having to undo work.
- Routine, obvious, or trivial changes are permitted without blocking.

## Minimal Edits & Options Prompting (`$MINIMAL_CHANGES`)
- Implement only what is explicitly requested; minimize unnecessary edits.
- If an unrequested feature or addition seems clearly helpful, present it as a suggestion using options format:
  - **Option 1**: Yes, do it
  - **Option 2**: No, don't
  - **Option 3**: Refine

## Explicitly Highlight Intent-Based Deviations (`$EXPLICIT_DEVIATION`)
- If deviating from explicit instructions because of an understood true intent, prominently highlight the deviation before proceeding.

## Rule Revision Protocol (`$RULE_MANAGEMENT`)
- Each rule is identified by its `$RULENAME`.
- When referenced via `$RULENAME>change`, work through the modification together by presenting:
  1. **Existing Rule**
  2. **Proposed Change**
  3. **Expected Effects**

## Mandatory Semantic Version Bumping (`$BUMP_VERSION`)
- Every set of code changes, rule updates, or feature additions must increment the project version following Semantic Versioning (`MAJOR.MINOR.PATCH`):
  - **`MAJOR`**: Incompatible rule redesigns, breaking API changes, or structural reorganizations.
  - **`MINOR`**: New rules, new features, or backwards-compatible capability additions.
  - **`PATCH`**: Bug fixes, rule clarifications, minor refactors, or documentation adjustments.
- Applies to this repository and projects adopting these rules across relevant build manifests (e.g., `package.json`, `pyproject.toml`, `Cargo.toml`), documentation, and visible version badges/footers.

## Commit Documentation & Prompt Provenance (`$COMMIT_PROVENANCE`)
- With each git commit, record the initiating prompt and an enumerated list of steps taken to address it within the commit message body.
- Standard commit message body format:
  ```gitcommit
  <type>(<scope>): <concise subject>

  Prompt:
  <user request or prompt>

  Steps Taken:
  1. <step 1>
  2. <step 2>
  ```

## Automatic Remote Push (`$AUTO_PUSH`)
- Whenever changes are committed, automatically push commits to the upstream remote repository (`git push`).

## Context Reminder Footer Line (`$CONTEXT_FOOTER`)
- The final line of output for every prompt response must be a bolded reminder to bring the user back into context.
- Format style: `**collaborating_agents><module>><action_or_change>**` (or a concise context summary line, e.g., `**collaborating_agents>core>add_endpoint**`).
