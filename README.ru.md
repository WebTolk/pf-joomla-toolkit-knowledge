# Joomla Toolkit

[English](README.md) | **Русский**

Подключаемый и обновляемый пакет знаний для [Process Forge](https://github.com/WebTolk/process-forge): архитектура Joomla, структура расширений и REST API Joomla 6. Все статьи и метаданные устанавливаемого пакета — на английском языке.

## Справочные материалы

- [Обзор Toolkit](resources/overview.md).
- [Архитектурные правила](resources/joomla-architecture-rules.md).
- [Структура расширений](resources/joomla-extension-structures.md).
- [Ревью расширений](resources/joomla-extension-review.md): доказательства, безопасность, маршрутизация и меню, проверка API по версиям.
- [REST API Joomla 6](resources/joomla6-rest-api-core-full.md).

## Подключение и обновления

Скачайте ZIP из [GitHub Releases](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases), распакуйте его в каталог пакетов вашего workplace, зарегистрируйте [package.yaml](package.yaml) в PF и выберите пакет в контексте проекта.

- ID пакета: `joomla.toolkit.documentation`.
- ID ресурса: `joomla-toolkit`.
- [Стабильный манифест обновлений](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/joomla-toolkit.json).

Адрес сервера обновлений включён в `update_sites`. Штатный апдейтер PF обнаруживает релизы на GitHub, проверяет SHA-256 и устанавливает обновление по явной команде оператора. Для исходной установки `1.0.0` без сервера обновлений однократно скопируйте этот блок в её установленный `package.yaml`, сохранив остальные поля.

## Структура пакета

```text
package.yaml
resources/                 # статьи на английском языке
indexes/resource-index.yaml
CHANGELOG.md
NOTICE.md
```

Пакет соответствует типовой структуре PF. Английский и русский README предназначены только для репозитория и не входят в скачиваемый ZIP. Инструменты сопровождения и приватное состояние PF также исключены из поставки.

[История изменений](CHANGELOG.md) · [Происхождение и условия использования](NOTICE.md).
