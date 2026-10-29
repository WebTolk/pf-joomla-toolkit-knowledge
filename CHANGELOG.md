# Changelog

## 1.0.1 - 2026-10-29

- Publish Joomla Toolkit as an independent knowledge package using the standard ProcessForge package structure.
- Preserve package ID `joomla.toolkit.documentation`, resource ID `joomla-toolkit` and all four source documents.
- Store the articles directly in `resources/`; replace five original private path references with portable references.
- Derive the package manifest from native `knowledge-package-create` and generate the resource index with native PF tooling.
- Include GitHub Releases update discovery and SHA-256 verification metadata. Maintenance tooling and private PF state are kept outside the published package.

## 1.0.0 - Existing workplace baseline

The original locally registered package had one externally stored Joomla Toolkit resource and no update site.
