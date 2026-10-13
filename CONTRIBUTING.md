# Contributing

Thanks for wanting to improve these catalogues. In this document we explain what kind of
contributions we take, how to propose one and how we review it, since a change to a catalogue is a
change to what a red teaming run measures, and so it needs more care than a typical fix.

## What we welcome

- **False positives and false negatives.** An answer the judge flagged that was correct, or a clear
  violation it missed, with the probe, the answer and the verdict. This is the most useful
  contribution there is, because most rubric exceptions in this repository come from reports like
  these.
- **New attacks or controls** for an existing risk, especially techniques the risk does not cover
  yet.
- **Sharper rubrics**, when the current one conflates two rules or charges a behaviour that is
  correct.
- **New risks or families**, for risks that can be measured by talking to a deployed agent. The
  gaps we already know about are listed in [docs/frameworks.md](docs/frameworks.md).

## Before you start

A small fix, such as a typo, a broken translation or a probe that does not say what its description
says, can go straight to a pull request.

For anything that changes what is measured, which means a new risk, a new family, or a change to a
rubric or a principle, we ask you to open an issue first with the matching template, since we would
rather agree on the rule before you write thirty probes for it. For a rubric change the issue should
include the answers that were misjudged, because a rubric is only changed on evidence.

## Making the change

1. Fork the repository and create a branch from `main`.
2. Edit the YAML under `catalogues/<family>/risks/`, following the format and the rules in
   [docs/authoring.md](docs/authoring.md). Never edit a `.json` by hand.
3. Rebuild and check:
   ```bash
   uv run build.py
   uv run build.py --check
   ```
4. If the change alters what a family covers, update its `README.md` (the counts and the tables),
   and the families table in the root [README.md](README.md).
5. Commit following [Conventional Commits](https://www.conventionalcommits.org/) with the family as
   the scope, for example `feat(sycophancy): add attacks that cite a fake study` or
   `fix(privacy): stop the rubric flagging a masked card number`. Use `repo` as the scope for changes
   outside a family, and `docs` for documentation.
6. Open a pull request against `main` and fill in the template.

## What we will not merge

- **Operational harmful content.** A probe is the user's message asking for something, never the
  harmful answer itself, so a probe that contains working instructions, real exploit code or a
  method of self harm is rejected whatever the family.
- **Real people, customers or companies.** Probes use invented names, accounts and figures. Nothing
  taken from a real conversation with a real user goes in, even anonymised.
- **Probes in one language only.** Every message carries a Spanish and an English version, and
  `build.py` rejects one that does not.
- **Content you cannot license.** Probes copied from another dataset need a license compatible with
  CC BY 4.0, and the source has to be cited in the pull request.
- **Generated probes nobody reviewed.** Using a model to draft probes is fine, although every one of
  them has to be read and edited by a person before it is submitted.

## How we review

A maintainer reviews every pull request, and the CI has to pass, which means every committed JSON
matches its sources. For changes to a rubric or a principle we also check that the controls of the
family still pass, because a rubric that starts flagging correct answers makes every result of the
family unreadable.

## Versions

Each family is versioned on its own, with tags of the form `<family>-vMAJOR.MINOR.PATCH`, for example
`sycophancy-v1.2.0`, so a report can say exactly which catalogue it was run against.

| Change | Bump |
|---|---|
| A rubric or principle changes meaning, or a risk is removed | major |
| A risk, an attack or a control is added | minor |
| Wording or translation fixes that do not change what is measured | patch |

Results are only comparable across runs of the same major version.

## License

By contributing you agree that your contribution is licensed under the same terms as the rest of the
repository: [Apache 2.0](LICENSE) for code and [CC BY 4.0](LICENSE-DATA) for catalogues and
documentation.
