# Building a catalogue

In this document we explain how `build.py` turns the YAML sources of a family into the schema v2
JSON document a run publishes, and how to build a subset of a family for one particular agent
without touching the committed catalogue.

## Requirements

The script only depends on pyyaml, which is declared inside the script itself, so running it with
[uv](https://docs.astral.sh/uv/) installs it on the fly and there is nothing else to set up.

## Commands

```bash
uv run build.py                          # rebuild every family's committed JSON
uv run build.py --check                  # fail if any committed JSON differs from its sources
uv run build.py security-owasp           # rebuild one family
uv run build.py security-owasp --list    # the risk ids of that family
uv run build.py security-owasp --risks prompt-injection,goal-hijacking,third-party-data \
    --out my-agent.json                  # only those three, weights split evenly among them
uv run build.py security-owasp --weights prompt-injection=3,third-party-data=3,goal-hijacking=2 \
    --name my-agent-security --out my-agent.json
                                         # those risks with those severities, under another name
```

A risk id is the stem of a file under `catalogues/<family>/risks/`, which is also its plugin id.
After editing any YAML, run `uv run build.py` before committing, because the CI rejects a pull
request whose JSON does not match its sources.

## Weights

Weights are severities, and the script normalises them so they sum to 1, which means only the
proportion between them matters (`a=3,b=1` and `a=0.75,b=0.25` produce the same document). Without
`--weights` every risk receives the same share.

The weight is what decides how a run is read: a risk whose weight is above its even share, that is
above 1 divided by the number of risks, becomes an *important category*, where a single confirmed
failure turns the whole run red. The details are in [methodology.md](methodology.md).

## Subsets

Not every risk applies to every agent, for example a banking agent is expected to talk about money
and so a run of `specialized-advice` against it should leave out `financial-advice`. In that case
we suggest building the subset with `--out` into a file of your own, since the committed
`<family>.json` is always the full family with even weights and the CI checks that it stays that
way.

## What the script checks

Before writing anything, the script verifies that every YAML has a `plugin`, a `principle`, a list
of `attacks` and a list of `controls`, that the plugin id matches the file name, that every
interaction mode is one the platform knows, that every message carries exactly an `es` and an `en`
version, that no control is adaptive, and that no strategy id is used twice in the family.
It also rejects weights that are not positive numbers, a risk given twice, and `--risks` together
with `--weights`, since the weights already name the risks.
It does not validate the document against the platform's full schema, which is what
`redteam catalogue validate` does before publishing in
[RoastMe](https://github.com/Alquimia-ai/red-teaming).
