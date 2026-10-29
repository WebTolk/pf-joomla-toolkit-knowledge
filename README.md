# Joomla Toolkit

Подключаемый и обновляемый пакет знаний для [Process Forge](https://github.com/WebTolk/process-forge): архитектурные правила Joomla, структура расширений и REST API Joomla 6.

## Статьи

- [Назначение Toolkit](resources/README.md).
- [Архитектурные правила](resources/joomla-architecture-rules.md).
- [Структура расширений](resources/joomla-extension-structures.md).
- [REST API Joomla 6](resources/joomla6-rest-api-core-full.md).

## Подключение и обновления

Скачайте установочный ZIP из [GitHub Releases](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases), распакуйте его в каталог пакетов вашего workplace и зарегистрируйте [package.yaml](package.yaml) в PF. Затем выберите пакет в контексте проекта.

- ID пакета: `joomla.toolkit.documentation`.
- ID ресурса: `joomla-toolkit`.
- [Стабильный манифест обновлений](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/joomla-toolkit.json).

URL сервера уже включён в `update_sites` манифеста пакета. Штатный апдейтер PF получает новые версии из GitHub Releases, проверяет SHA-256 и устанавливает обновление по явной команде оператора. Для исходной установки `1.0.0`, в которой ещё нет сервера обновлений, однократно скопируйте блок `update_sites` из этого манифеста в её установленный `package.yaml`, сохранив остальные поля.

## Структура пакета

```text
package.yaml
README.md
resources/                 # статьи
indexes/resource-index.yaml
```

Используется типовая структура пакета знаний PF. Дополнительные каталоги добавляются по мере необходимости. [package.yaml](package.yaml) и [индекс ресурса](indexes/resource-index.yaml) нужны для подключения к PF. Служебные инструменты сопровождения хранятся локально вне публикации.

[История изменений](CHANGELOG.md) · [Происхождение и условия использования](NOTICE.md).
