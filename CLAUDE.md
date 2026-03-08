# CLAUDE.md — aegis-sdk

## Project
AEGIS client SDK — integration libraries published to npm and PyPI.

## Org Context
- GitHub Org: github.com/aegis-initiative
- IP Owner: Finnoybu IP LLC
- Parent Ecosystem: Finnoybu Holdings LLC
- Domain: aegissystems.app

## This Repo's Role
aegis-sdk is the primary integration surface for developers building on top of AEGIS. It provides TypeScript/JavaScript and Python client libraries that wrap the aegis-platform API. Published to npm as @aegis-initiative/sdk and to PyPI as aegis-sdk. Documentation auto-published to aegis-docs.

## Related Repos
- aegis-platform — API this SDK wraps
- aegis-docs — SDK reference docs published here
- aegis-ops — Publish pipeline for npm and PyPI releases

## Stack
TypeScript (primary), Python, published to npm + PyPI

## Key Conventions
- TypeScript source in /packages/sdk-ts
- Python source in /packages/sdk-py
- Versioning: semantic versioning, kept in sync across both packages
- All public methods must have JSDoc / docstring + type signatures
- Branch: main is protected; all changes via PR with 1 required review

## Current Focus
Initial scaffold — TypeScript and Python package structure, publish pipeline
