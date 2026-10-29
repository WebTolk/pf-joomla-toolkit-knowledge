# Joomla Toolkit

## Назначение

`joomla-toolkit` — это **knowledge layer для разработки на Joomla**.

Он не управляет процессом разработки и не заменяет skills.  
Его задача — давать **архитектурные правила, паттерны и справочную информацию**, которые используются внутри `development-flow`.

---

## Что это НЕ такое

`joomla-toolkit`:

- ❌ не является набором skills;
- ❌ не описывает pipeline разработки;
- ❌ не управляет оркестрацией агентов;
- ❌ не содержит role-based инструкций;
- ❌ не заменяет `development-flow`.

Все вопросы “как работать” решаются через:

- `development-flow` (skills)
- `flow-orchestrator`
- `.agents/` (артефакты проекта)

---

## Что это такое

`joomla-toolkit` — это:

- архитектурные правила Joomla;
- допустимые и запрещённые паттерны;
- структура расширений;
- особенности API, событий, DI;
- справочная база для принятия решений внутри skills.

---

## Место в архитектуре

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

## Когда использовать

Используй `joomla-toolkit`, когда:

- нужно принять архитектурное решение;
- нужно понять, как правильно реализовать что-то в Joomla;
- есть сомнения между несколькими паттернами;
- требуется проверить, не используется ли deprecated подход;
- нужно вспомнить структуру расширения или API.

---

## Когда НЕ использовать

Не используй toolkit:

- для управления этапами разработки;
- для выбора следующего шага pipeline;
- для orchestration или routing;
- как источник “что делать дальше” — это задача skills.

---

## Содержимое

### `joomla-architecture-rules.md`
Главный файл с архитектурными правилами:

- coding preferences;
- запрещённые (deprecated) паттерны;
- DI / service provider подход;
- события и подписчики;
- общие ограничения и best practices.

---

### `joomla-extension-structures.md`
Структура расширений:

- component;
- plugin;
- module;
- API / webservices;
- CLI / console.

---

### `joomla-multi-extension-architecture.md` (опционально)
Для сложных систем:

- взаимодействие расширений;
- shared data layer;
- границы и зависимости;
- риски.

---

### `joomla6-rest-api-core/`
Работа с REST API Joomla 6:

- основной файл: `joomla6-rest-api-core-full.md`;
- при необходимости — дополнительные материалы.

---

## Как использовать вместе с development-flow

### Пример

1. `architecture-plan` skill определяет границы.
2. При выборе подхода:
   - обращается к `joomla-toolkit`.
3. Решение фиксируется в:
   - `architecture.md`
   - `project-invariants.md`

---

## Принципы

### 1. Toolkit — только знания
- никаких orchestration правил;
- никаких agent-инструкций;
- никаких role-based сценариев.

---

### 2. Toolkit не дублирует skills
- если правило относится к процессу — оно должно быть в `development-flow`;
- если правило относится к Joomla — оно должно быть здесь.

---

### 3. Toolkit — источник истины для Joomla-правил
Все Joomla-specific ограничения и паттерны должны:

- либо находиться здесь;
- либо быть явно зафиксированы в проектных артефактах.

---

### 4. Минимизация дублирования
- не размазывать одну тему по нескольким файлам;
- поддерживать компактную и понятную структуру;
- объединять связанные темы.

---

## Что не должно появляться в toolkit

Нельзя добавлять:

- orchestration правила;
- agent workflows;
- subagent prompts;
- pipeline инструкции;
- tool execution policy (Serena, PHPUnit и т.д.);
- локальные machine-specific настройки.

---

## Расширение toolkit

Допускается добавлять:

- новые Joomla-specific паттерны;
- разборы edge-case сценариев;
- уточнения по новым версиям Joomla;
- типовые архитектурные решения.

---

## Связанные слои

- `development-flow` — управляет процессом;
- `.agents/templates` — задают структуру артефактов;
- `scripts/orchestrator.py` — управляет состоянием выполнения.

---

## Коротко

> `joomla-toolkit` — это не “как работать”,  
> а “как правильно писать код под Joomla”.
