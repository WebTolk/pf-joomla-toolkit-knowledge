# Joomla Toolkit

## Purpose

`joomla-toolkit` is a **knowledge layer for Joomla development**.

It provides **architecture rules, patterns, and reference material** used by `development-flow`. Development processes and skills remain separate responsibilities.

---

## Scope boundaries

`joomla-toolkit`:

- is not a collection of skills;
- does not define a development pipeline;
- does not orchestrate agents;
- does not contain role-based instructions;
- does not replace `development-flow`.

Working procedures are handled by:

- `development-flow` (skills)
- `flow-orchestrator`
- `.agents/` (project artifacts)

---

## Contents and responsibilities

`joomla-toolkit` provides:

- Joomla architecture rules;
- permitted and prohibited patterns;
- extension directory structures;
- API, event, and dependency injection details;
- reference material for decisions made within skills.

---

## Position in the architecture

```
[ GLOBAL ]

development-flow (skills)
        ↓
joomla-toolkit (knowledge)
        ↓
project artifacts (.agents)

[ PROJECT ]

.agents/
scripts/orchestrator.py
templates/
```

---

## When to use it

Use `joomla-toolkit` when you need to:

- make an architectural decision;
- determine how to implement something correctly in Joomla;
- choose between multiple patterns;
- check whether an approach is deprecated;
- look up an extension structure or API.

---

## Responsibilities outside the toolkit

Use the process and skill layers to:

- manage development stages;
- select the next pipeline step;
- perform orchestration or routing;
- decide what to do next.

---

## Reference documents

### `joomla-architecture-rules.md`

The main architecture reference covers:

- coding preferences;
- prohibited and deprecated patterns;
- dependency injection and service providers;
- events and subscribers;
- general constraints and best practices.

---

### `joomla-extension-structures.md`

Extension structures include:

- components;
- plugins;
- modules;
- API and webservices;
- CLI and console applications.

---

### `joomla-multi-extension-architecture.md` (optional)

An optional reference for complex systems may cover:

- communication between extensions;
- a shared data layer;
- boundaries and dependencies;
- risks.

---

### `joomla6-rest-api-core-full.md`

The Joomla 6 REST API reference is stored in `joomla6-rest-api-core-full.md`. Additional supporting material may be added when needed.

---

## Using the toolkit with development-flow

For example:

1. The `architecture-plan` skill defines boundaries.
2. It consults `joomla-toolkit` when selecting an approach.
3. The decision is recorded in:
   - `architecture.md`
   - `project-invariants.md`

---

## Principles

### 1. The toolkit contains knowledge

- Orchestration rules belong in the process layer.
- Agent instructions belong in the agent or skill layer.
- Role-based scenarios belong in their corresponding workflows.

---

### 2. Keep skills and toolkit knowledge separate

- Process rules belong in `development-flow`.
- Joomla-specific rules belong in the toolkit.

---

### 3. Keep Joomla rules authoritative

Joomla-specific constraints and patterns should either be documented here or explicitly recorded in project artifacts.

---

### 4. Minimize duplication

- Keep each topic together.
- Maintain a compact, understandable structure.
- Consolidate related material.

---

## Content outside the toolkit's scope

Keep the following in their responsible process or configuration layers:

- orchestration rules;
- agent workflows;
- subagent prompts;
- pipeline instructions;
- tool execution policy, including Serena and PHPUnit;
- machine-specific local settings.

---

## Extending the toolkit

Suitable additions include:

- new Joomla-specific patterns;
- explanations of edge cases;
- clarifications for new Joomla versions;
- common architectural solutions.

---

## Related layers

- `development-flow` manages the process.
- `.agents/templates` defines artifact structures.
- `scripts/orchestrator.py` manages execution state.

---

## Focus

The toolkit describes how to write Joomla code correctly. Working procedures are handled by the process and skill layers.
