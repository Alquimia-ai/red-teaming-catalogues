# Running the catalogue

## Publish

The `redteam` commands, the `crescendo` attacker and `RunSpec` below belong to
[RoastMe](https://github.com/Alquimia-ai/red-teaming), the platform these catalogues are written for;
another harness needs its own equivalent.

```bash
uv run build.py security-owasp                                         # rebuild the JSON from risks/*.yaml
redteam catalogue validate catalogues/security-owasp/security-owasp.json
redteam catalogue publish catalogues/security-owasp/security-owasp.json
```

## What a run needs

- **Black box.** Every strategy has `requires_brain: false` and no `{premise}` slot, so none
  needs a knowledge base.
- **An attacker bound to `crescendo`.** 22 attacks are `adaptive_multi_turn`: they send their
  opening and an attacker model steers the rest, up to 4 turns. The run binds the id to a model in
  `RunSpec.attackers`.
- **The same contract as any catalogue run alongside it.** A run over several catalogues requires
  identical contracts. No two families here share a contract, so each
  one runs on its own.

## Three things the platform does that shape the results

- **The attacker only sees the plugin's `description`.** It is the conversation's objective, and
  nothing about the strategy crosses to it. Multi-turn attacks under one plugin therefore differ
  only in their opening turn. Plugin descriptions are instructions to the attacker, not
  documentation.
- **The judge grades the final answer.** Every turn is recorded, but an agent that gave way at
  turn two and recovered at turn four reads as clean. The rubrics are written for a final answer.
- **Controls cannot be conducted.** The 6 multi-turn controls are fixed scripts
  (`scripted_multi_turn`); an attacker steers attacks only.

## Open

- **The canary is fixed.** `COMPROMISED` is public in this repository, so an agent could filter
  it. A random token per run needs support at generation time.
- **Weights are equal** (0.125 each). Severity is the contract owner's call.
