# Joomla Toolkit — пакет знаний для Process Forge

**Joomla Toolkit** — подключаемый и обновляемый пакет знаний для [Process Forge (PF)](https://github.com/WebTolk/process-forge). Он содержит архитектурные правила Joomla, образцы структуры расширений и справочник REST API Joomla 6.

Пакет подключается к рабочему месту PF, выбирается в контексте проекта и используется агентом при разработке. Новые версии распространяются через GitHub Releases и обнаруживаются штатным апдейтером Process Forge. Обновление устанавливается по явной команде оператора с проверкой SHA-256.

- **Основной репозиторий PF:** [WebTolk/process-forge](https://github.com/WebTolk/process-forge).
- **Скачать пакет:** [GitHub Releases](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases).
- **Версия:** `1.0.1`.
- **ID пакета:** `joomla.toolkit.documentation`.
- **ID ресурса:** `joomla-toolkit`.

## Состав

- [Назначение исходного Toolkit](resources/joomla-toolkit/README.md).
- [Архитектурные правила Joomla](resources/joomla-toolkit/joomla-architecture-rules.md).
- [Структура расширений](resources/joomla-toolkit/joomla-extension-structures.md).
- [REST API Joomla 6](resources/joomla-toolkit/joomla6-rest-api-core-full.md).

Первый самостоятельный выпуск переносит существующий пакет PF `1.0.0` в отдельный репозиторий. Два документа сохранены побайтно; в двух других заменены пять ссылок на локальные каталоги. Содержательная доработка Toolkit запланирована отдельным релизом. Исторические ссылки на development-flow сохранены в исходных материалах.

## Подключение

Скачайте из релиза установочный ZIP `joomla.toolkit.documentation-1.0.1.zip`, распакуйте его в выбранный каталог пакетов вашего workplace и зарегистрируйте `package.yaml` через его реестр корней и пакетов знаний. Автоматические архивы GitHub **Source code** содержат репозиторий целиком; для установки используйте ZIP из assets релиза.

Сохраните ID пакета и ресурса. Корпус знаний находится внутри пакета, ссылки на него относительные. После регистрации выполните `knowledge-package-doctor` и обновите контекст проекта штатными средствами PF. Для поиска используется объявленная политика `index_policy: fulltext`.

## Обновления через GitHub Releases

- [Стабильный манифест обновлений](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/joomla-toolkit.json).
- [История изменений](https://github.com/WebTolk/pf-joomla-toolkit-knowledge/releases/latest/download/CHANGELOG.md).

Эти URL включены в `update_sites` внутри поставляемого `package.yaml`. Манифест содержит ссылки на ZIP конкретных версий и их SHA-256. Адрес `latest` переходит на следующий стабильный релиз; предварительные выпуски не должны заменять стабильный канал. Уже опубликованные assets не заменяются: изменённый пакет получает новую версию.

У исходной установки `1.0.0` сервера обновлений ещё нет. Для первого обнаружения добавьте блок из [bootstrap-package-site.yaml](updates/bootstrap-package-site.yaml) в её установленный `package.yaml`, сохранив версию и остальные поля. Одной записи в глобальном bootstrap-реестре недостаточно для обнаружения кандидата установленной сущности в проверенной версии PF. В последующих установках нужный блок уже входит в ZIP.

```text
python <pf-cli> update entity-sources rebuild --workplace <workplace>
python <pf-cli> update candidates refresh --workplace <workplace>
python <pf-cli> update candidates list --workplace <workplace>
python <pf-cli> update stage --workplace <workplace> --candidate <candidate-id>
python <pf-cli> update verify --workplace <workplace> --candidate <candidate-id>
python <pf-cli> update apply --workplace <workplace> --candidate <candidate-id> --confirm
```

Каталог установки выбирает принимающий workplace. Перед применением обновления сохраните резервную копию установленного пакета.

## Сопровождение и выпуск

```text
python -m pip install -r requirements.txt
python tools/check.py
python tools/release.py
python tools/test_native_updater.py --pf-root <installed-pf-root>
```

Перед новым выпуском согласованно обновите `VERSION`, `package.yaml`, версию ресурса, индекс и `CHANGELOG.md`. Выполните проверки, соберите пакет, сделайте commit/push и тег точного коммита. В стабильный GitHub Release загрузите сгенерированные ZIP, `joomla-toolkit.json`, `SHA256SUMS` и `CHANGELOG.md`. После публикации выполните нативную проверку с `--remote`.

Сборка сохраняет предыдущие версии манифеста и запрещает менять архив под уже записанной версией. Нативные проверки выполняются в изолированных workplace внутри `.pf/tmp/initial-release/`; они не заменяют пакет в общем рабочем месте.

Проект подключён к PF: процесс `knowledge-package-update`, режим `simple`, локальная специализация сопровождения знаний. Приватное состояние PF и настройки компьютера исключены из Git и архива. [Происхождение и условия использования материалов](NOTICE.md), [изменения](CHANGELOG.md), [исходные контрольные суммы](docs/source-provenance.json).
