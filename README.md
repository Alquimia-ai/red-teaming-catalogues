# Red teaming catalogues

Open catalogues of adversarial probes for testing conversational AI agents, grouped into risk
**families** such as security, sycophancy, privacy or bias. Each family is a self contained
catalogue: a set of attacks that try to make the agent break one rule, a set of controls where the
correct behaviour is to comply, and a contract with the rubrics a judge model uses to decide whether
each answer broke the rule.

These are the default catalogues of [RoastMe](https://github.com/Alquimia-ai/red-teaming), the red
teaming platform Alquimia uses to test its assistants, although the documents are plain JSON and the
probes are plain text, so nothing stops you from running them with any other harness.

## Families

| Family | What it tests | Risks | Attacks | Controls |
|---|---|---|---|---|
| [security-owasp](catalogues/security-owasp/) | The agent security risks of the OWASP AI Agent Security Cheat Sheet | 8 | 81 | 22 |
| [sycophancy](catalogues/sycophancy/) | The agent agreeing with a false premise, caving under pressure, or blessing a risky plan | 3 | 30 | 9 |
| [privacy](catalogues/privacy/) | The agent mishandling the user's own sensitive data | 2 | 20 | 6 |
| [human-ai-configuration](catalogues/human-ai-configuration/) | The agent passing for a human, or claiming an authority it does not have | 2 | 20 | 6 |
| [bias](catalogues/bias/) | The agent treating a person differently on a protected attribute irrelevant to the request | 1 | 10 | 3 |
| [harmful-content](catalogues/harmful-content/) | The agent producing dangerous instructions, harm in disguise, or hate | 3 | 21 | 9 |
| [specialized-advice](catalogues/specialized-advice/) | The agent diagnosing, dosing, deciding a legal case or picking a financial move for the user | 3 | 30 | 9 |
| [self-harm](catalogues/self-harm/) | The agent missing a disclosure of self harm, or giving the means when asked | 2 | 20 | 6 |
| [fraud-enablement](catalogues/fraud-enablement/) | The agent helping launder money, forge documents or write scams | 3 | 30 | 9 |

Every probe is written in Spanish and English. Each family's README explains what it covers, what
it deliberately leaves out and why, and which probes should be adapted to the agent before a run.

## Repository layout

```
catalogues/<family>/
  README.md            what the family tests, what it does not, and how to read it
  risks/<risk>.yaml    the source: one file per risk, with its rubric, attacks and controls
  <family>.json        the published document, generated from risks/ by build.py
docs/
  building.md          how to build a full catalogue or a subset for one agent
  authoring.md         the YAML format and the rules a risk has to follow
  methodology.md       how a run is turned into a red, yellow or green verdict
  frameworks.md        how the families map onto OWASP and NIST, and where the gaps are
build.py               the only script, shared by every family
```

The YAML files are the source and the JSON files are never edited by hand: `build.py` generates
them, and the CI rebuilds every family on each pull request and fails if a committed JSON differs
from what its sources produce, so the two cannot drift.

## Quick start

You only need the JSON to run a catalogue, so downloading
`catalogues/<family>/<family>.json` is enough. To build one yourself, for example a subset with the
risks that apply to your agent, you need [uv](https://docs.astral.sh/uv/):

```bash
uv run build.py --check                                     # verify every JSON matches its sources
uv run build.py privacy --list                              # the risks a family has
uv run build.py privacy --risks insecure-handling --out my-privacy.json
```

[docs/building.md](docs/building.md) covers weights, subsets and naming.

## A family is a contract

Each family carries its own contract, and since a run over several catalogues requires them all to
share the same one, every family is published and run on its own and its verdict is read against its
own contract. How that verdict is assigned, and when the judge behind it can be trusted, is in
[docs/methodology.md](docs/methodology.md).

## Contributing

New probes, sharper rubrics and reports of false positives are all welcome. Since every change to a
rubric changes what a family measures, contributions go through a review that is described in
[CONTRIBUTING.md](CONTRIBUTING.md), which we suggest reading before opening a pull request.
Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md), and anything that should not
be public, such as a probe with real personal data, is reported as [SECURITY.md](SECURITY.md) explains.

## License

The code (`build.py` and the CI) is licensed under [Apache 2.0](LICENSE). The catalogues and the
documentation (everything under `catalogues/` and `docs/`, and the Markdown files) are licensed under
[CC BY 4.0](LICENSE-DATA), so you can use, adapt and redistribute them, commercially or not, as long
as you credit this repository.
