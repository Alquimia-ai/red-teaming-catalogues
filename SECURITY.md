# Security

This repository holds attack probes in plain text, so most of what it contains is meant to be read
by anyone. In this document we explain what still counts as a security problem here and how to
report it privately, since opening a public issue would publish the very thing we want to remove.

## What to report privately

- A probe that contains **operational harmful content**, such as working instructions, real exploit
  code or a method of self harm, instead of only the user's request for it.
- A probe or a document that contains **real personal data**, credentials, or the name of a real
  customer or company.
- A problem in `build.py` or in the CI that could run untrusted code or publish something it should
  not.

## How to report

Write to [axel.fritz@alquimia.ai](mailto:axel.fritz@alquimia.ai), or use GitHub's
[private vulnerability reporting](https://github.com/Alquimia-ai/red-teaming-catalogues/security/advisories/new),
with the file, the probe id and what the problem is. We answer within five working days and, once it
is fixed, the report can be made public if you want to.

## What is not a vulnerability here

A probe from these catalogues that makes some agent fail is the catalogue working as intended, so
it is not something to report to us. If you find that an agent in production fails one of them, the
report belongs to whoever runs that agent.
