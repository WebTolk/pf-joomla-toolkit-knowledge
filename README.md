# Joomla Toolkit

**English** | [Russian](README.ru.md)

A connectable, updatable knowledge package for [Process Forge](https://github.com/WebTolk/process-forge), covering Joomla architecture, extension structures, and the Joomla 6 REST API. All documents and package metadata are in English.

## Reference material

- [Toolkit overview](resources/overview.md).
- [Architecture rules](resources/joomla-architecture-rules.md).
- [Extension structures](resources/joomla-extension-structures.md).
- [Joomla 6 REST API](resources/joomla6-rest-api-core-full.md).

## Installation and updates

Download the package ZIP from [GitHub Releases](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases), unpack it into your workplace's package directory, register [package.yaml](package.yaml) with PF, and select the package in your project context.

- Package ID: `joomla.toolkit.documentation`.
- Resource ID: `joomla-toolkit`.
- [Stable update manifest](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/joomla-toolkit.json).

The update server URL is included in the package's `update_sites`. The native PF updater discovers releases on GitHub, verifies SHA-256, and installs an update only after an explicit operator command. For the original `1.0.0` installation without an update site, copy the `update_sites` block into its installed `package.yaml` once, preserving all other fields.

## Package structure

```text
package.yaml
resources/                 # English reference documents
indexes/resource-index.yaml
CHANGELOG.md
NOTICE.md
```

The package follows the standard PF knowledge-package structure. The English and Russian repository README files are not included in the downloadable ZIP. Maintenance tools and private PF state are also excluded.

[Changelog](CHANGELOG.md) · [Provenance and licensing](NOTICE.md).
