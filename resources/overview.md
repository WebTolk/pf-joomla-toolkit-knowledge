# Joomla Toolkit

## Purpose

Joomla Toolkit is a connectable, versioned knowledge package for Process Forge. It provides reference material for Joomla extension development and review. The selected PF process controls work stages and permissions; this package does not install tools, orchestrate agents or adopt project policies automatically.

## Reference documents

- [Architecture and project conventions](joomla-architecture-rules.md): Model/Table and domain service decisions, DI, events, database practices, version-aware migration advice and explicitly optional project profiles.
- [Extension structures](joomla-extension-structures.md): components, plugins, modules, CLI and webservices, plus source/manifest/archive/installed-payload correspondence.
- [Extension review](joomla-extension-review.md): practical review order, finding categories, security boundaries, routing/menu context and source-pinned API checks.
- [Joomla 6 REST API](joomla6-rest-api-core-full.md): API application routing, authentication, controllers and core endpoint reference. Its stated version scope remains applicable; verify the exact target before reusing examples.

## Use and authority

Select `joomla.toolkit.documentation:joomla-toolkit` explicitly in the relevant PF project/Work context and resolve it through the native PF resource mechanism before loading reference content. Package selection does not change every existing project's requirements.

Use the project's declared Joomla/PHP versions, verified core sources and installed dependencies for API facts. Keep general advice distinct from a project-specific accepted convention. A preference is not automatically a defect; an accepted architectural exception does not negate a demonstrated vulnerability.

Record decisions and review evidence in the project's own private artifacts. This package contains reusable knowledge only. Source existence, archive contents, successful installation and installed runtime behavior are different evidence levels.

## Maintenance

Keep one primary location for each topic, link existing material instead of duplicating it, and qualify facts by version where behavior differs. Publish knowledge changes through package versions and the configured update site. PF update discovery and explicit resource selection remain separate from installing or testing a Joomla extension.
