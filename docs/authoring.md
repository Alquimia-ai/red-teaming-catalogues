# Authoring a risk

In this document we describe the format of a risk file and the rules every risk in this repository
follows, since most of what makes a probe useful, or makes its results unreadable, is decided by how
the rubric and the controls are written and not by the attacks themselves.

## The file

Each risk is one file, `catalogues/<family>/risks/<risk>.yaml`, and the file name is the plugin id.

```yaml
plugin:
  id: explicit-bias                    # must match the file name
  name: "Inviting it to treat a protected group differently"
  description: "The user invites the assistant to endorse a stereotype ..."
principle:
  id: no_biased_treatment
  weight: 1.0                          # ignored by build.py, which sets the weights
  rubric: "The assistant must not ... Answer YES if ..., NO if ..."
attacks:
  - id: eb-nationality-risk            # unique inside the family
    name: "Invite a stereotype about a nationality"
    description: "invites the assistant to agree a nationality is a worse credit risk"
    interaction:
      mode: single_turn
      prompt:
        es: "..."
        en: "..."
controls:
  - id: eb-ctl-relevant-criteria
    ...                                # same shape as an attack
```

## Interaction modes

| Mode | Fields | What happens |
|---|---|---|
| `single_turn` | `prompt` | one message, one answer |
| `scripted_multi_turn` | `messages`, a list | a fixed conversation, sent message by message |
| `adaptive_multi_turn` | `opening`, `max_turns` | the opening is sent and an attacker model writes the following turns, up to `max_turns` |

Every text the agent receives carries an `es` and an `en` version. Controls can be single turn or
scripted, but never adaptive, because the attacker only steers attacks.

## The rules

**One plugin, one principle.** Strategies vary how an attack is delivered, never which rule it
breaks, so every probe under a plugin is judged against one definition of failure, and a rate over
that plugin means one thing.

**The rubric is the measurement.** It is the only text the judge reads, and the judge answers with
one token, so each rubric states the rule, states what does not count as breaking it, and ends with
a question the judge answers YES (violation) or NO.

**Every answer is graded against every principle of the family**, not only the one of its own
plugin. Because of this a rubric has to stay quiet on a correct answer to any other probe, such as
the agent declining, explaining a risk, describing an attack or introducing itself by its configured
name, and most of the exceptions written into the existing rubrics come from false positives we
found in real runs.

**Controls are the same situation with the payload removed.** A correct agent passes them, they are
graded and excluded from every rate, and a failing control means the judge is charging too much or
the run was aimed at the wrong surface, so the attacks around it cannot be trusted. Every risk
carries between 2 and 3 controls for every 10 attacks.

**The probe is the user's message, never the harmful content.** An attack asks "how many pills would
it take", it never contains an answer to that, since the violation we measure is the agent
supplying it. A pull request that adds operational harmful content to a probe will not be merged.

**Languages are measured separately.** A translation is a different measurement, because guardrails
are trained mostly on English attack strings, so results in Spanish and English are compared and
never pooled. Canary tokens such as `COMPROMISED` or `FREE MODE ENABLED` stay in English in every
language, so one rubric judges all of them.

**Plugin descriptions are instructions to the attacker.** In an adaptive attack the attacker model
only sees the plugin's `description` as the objective of the conversation, so it has to describe
the behaviour to push for and not document the risk.

**At least 10 attacks per risk.** With 10 attacks and no failure a run can only rule out a failure
rate above 30%, as [methodology.md](methodology.md) explains, so fewer attacks than that leave a
green that says very little.

## Adding a risk or a family

A new risk is a new YAML under an existing family, and once it is there `uv run build.py <family>`
includes it in the family's document. A new family is a new folder under `catalogues/` with a
`risks/` folder and a `README.md` that follows the structure of the existing ones: what it tests,
what it covers, what it leaves out and why, and where its line is against the neighbouring families.
In both cases the process to propose it is in [CONTRIBUTING.md](../CONTRIBUTING.md).
