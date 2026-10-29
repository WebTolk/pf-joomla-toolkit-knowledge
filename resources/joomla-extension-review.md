# Joomla extension review

## Purpose and boundaries

Use this guide to review an extension against its declared Joomla/PHP versions, installed behavior and accepted project architecture. It supplies review knowledge, not a mandatory PF process or permission to install software, contact a live site, change project policy or refactor working code.

Start with the [architecture reference](joomla-architecture-rules.md), [extension structures](joomla-extension-structures.md) and, for webservices, the existing [REST API reference](joomla6-rest-api-core-full.md). Keep installation evidence distinct from source inspection.

## Review order

| Order | Examine | Questions to resolve |
| --- | --- | --- |
| 1 | Extension identity and target | Component, module, plugin/group, library, template or package? Which exact Joomla/PHP versions and compatibility plugins? Which site, administrator, API, console or scheduler entry points? |
| 2 | Manifest and payload | Do declared files, namespaces, language/media destinations, SQL and installer scripts match the actual release archive? See [payload verification](joomla-extension-structures.md#source-manifest-and-installed-payload). |
| 3 | Boot and DI | Is the correct extension booted? Does the installed provider register the needed interfaces/factories? Are custom dependencies actually injected? Can each supported client construct the extension? |
| 4 | MVC and domain operations | Trace input to controller, model/form validation, Table/service storage, events, cache and redirect. Preserve checkout and caller error contracts. Decide on services using the [design criteria](joomla-architecture-rules.md#design-patterns). |
| 5 | Security boundaries | Check ACL and ownership, CSRF for relevant web actions, input validation, query binding, context-specific escaping and file upload/storage boundaries. Authentication, authorization and CSRF are separate checks. |
| 6 | Routing and presentation | Verify menu/language context, SEF and non-SEF links, redirects, assets, translations, layouts and permissions. Include direct requests with no matching menu. |
| 7 | Installation and upgrades | Inspect install/update SQL, schema version progression and installer failure paths. A source file or valid XML does not prove an installed upgrade succeeds. |
| 8 | Version-specific API behavior | Compare the actual base class, method signature, dependency version and deprecation marker. Classify reachable breakage separately from a future migration task. |

Trace one complete relevant operation before reporting a pattern difference. An unused prototype, unregistered event or undeclared file may be inactive; demonstrate its loading/reachability before attributing runtime impact. An inactive file shipped in a web-accessible path can still be reachable directly.

## Finding categories

| Category | Required distinction |
| --- | --- |
| Functional defect or security risk | A reachable behavior violates a requirement or trust boundary. State the affected actor, prerequisite, input and result. Separate demonstrated exploitation from a plausible risk that still needs validation. |
| Architecture debt | A concrete maintenance/coupling/failure-recovery problem exists, but immediate user-visible breakage is not established. Name its cost and scope. |
| Accepted project exception | Identify the adopted decision, its rationale, boundary and remaining tradeoff. Do not silently replace the project architecture during review. |
| Inactive placeholder | Establish why the code is not loaded or invoked on the examined path. Do not claim the whole installed artifact is safe solely because one path is inactive. |
| Optional improvement | Explain the benefit without presenting a preference as a required repair. |

An accepted architectural exception does not negate a demonstrated vulnerability. Record both facts: the accepted design and the evidence of the security defect. For example, permission to keep SQL diagnostics does not authorize exposing sensitive query data to an unauthenticated visitor.

Every finding needs:

- Exact code location: version/commit, relative file and method or lines.
- Evidence: the relevant caller/registration and data flow, or a bounded reproduction with expected and observed behavior. State the evidence level and any untested boundary.
- Impact: who or what is affected, under which configuration and permissions. Confidence and severity are separate from category.
- Minimal correction: the smallest change that addresses the demonstrated cause while preserving documented contracts. Propose architectural work separately when useful.

Do not declare a defect solely because a service/Repository exists, because a repository folder differs from an example, or because code does not match a preferred testing style. Conversely, an approved pattern never substitutes for checking the actual security boundary.

## Security checks

### Authorization and state-changing requests

Check the server-side action permission on the correct component/record asset, the user's ownership/edit-own scope where relevant, and the actual object selected for the operation. A hidden button, inaccessible menu or successful login is not proof of action authorization. Direct requests must receive the same protection.

For state-changing web actions, inspect token generation, submitted method and the failure branch before storage or external side effects. In BaseController, a token check with redirects disabled must have its false result handled. Token validity does not grant ACL permission. Webservice endpoints require their own authentication/authorization and method contract; do not transplant an administrator form flow mechanically.

Sources: [Joomla 6.0.4 User::authorise](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/User/User.php), [FormController](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Controller/FormController.php), [BaseController token check](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Controller/BaseController.php#L1128).

### Input, database and output

Use the application's input object with filters appropriate to the expected type, then validate semantic constraints such as allowed states, ranges and object ownership. A command/string filter does not prove a business value is permitted. Never trust a posted price, payment state, user ID or filesystem destination as authoritative.

Bind query values with suitable types; allowlist dynamic column names, sort directions and other SQL syntax that cannot be bound as values. Keep bound variables alive with stable references. Escaping a query for debug output is unrelated to safe parameter binding.

Escape at the final output context: HTML text, HTML attributes, URLs and JavaScript need the appropriate encoding. Translation lookup and URL routing are not general sanitizers. A framework asset registration or a translated string does not make embedded untrusted markup safe.

### Files and uploads

Review authorization and CSRF before accepting a file, application size/type policy, server-side content checks, destination containment and collision behavior. Treat browser-provided names, MIME values and paths as untrusted. Derive the storage path from trusted configuration; reject traversal and unexpected executable content. Check replacement/deletion permissions, error handling, and whether generated URLs expose private files. The presence of a filesystem helper alone does not establish that an upload is safe.

## Routing and menu context

A component router builds/parses route variables. Controllers dispatch tasks and manage request/redirect flow. Authorization and content access still need server-side checks in the appropriate action/model path. A successfully built URL or a permitted menu item does not authorize the underlying record.

| Scenario | Check |
| --- | --- |
| Matching menu | Confirm the chosen `Itemid`, component/view/record and active menu. Verify menu parameters, assigned modules and breadcrumbs, not just the visible path. |
| Several matching menus | Compare link generation from different active pages; establish the project's canonical policy and detect unintended duplicate URLs or context changes. Do not assume routing alone emits the desired canonical tag. |
| No matching menu | Open/build the direct route, including SEF off. Verify the intended fallback or rejection, active-menu effects, layout and access checks. Avoid borrowing an unrelated menu merely to shorten a URL. |
| Multilingual site | Exercise language-specific menus, associations, language prefixes and `lang` values. An all-languages menu and a language-specific menu can lead to different selection. |
| Administrator to site | Use the intended site client, for example `Route::link('site', $internalUrl, ...)`. `Route::_()` uses the currently active application client; administrator context does not automatically mean a frontend route. |
| Return/redirect | Decode only as required by the contract, validate the destination with the target version's internal-URL facility and the application's allowed destination policy, and choose a trusted fallback on failure. Base64 encoding is not URL validation. |
| Edit task | Trace the actual FormController edit/save/cancel and checkout/held-ID flow. A direct `view=...&layout=edit` link is not automatically a lost-update defect; prove which protection is bypassed in this implementation. |

For redirects, check validation after decoding and before redirecting, disallowed schemes/hosts, malformed values and authorization at the destination. `Uri::isInternal()` is a useful Joomla boundary check, not proof that every internal action is allowed. Do not redirect to an untrusted referrer on failure.

Sources: [Joomla 6.0.4 MenuRules::preprocess](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Component/Router/Rules/MenuRules.php#L85), [Route::_ and Route::link](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Router/Route.php#L72), [Uri::isInternal](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Uri/Uri.php#L247), [FormController](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Controller/FormController.php).

## Version-specific API checks

The following observations are pinned to Joomla 5.4.8, 6.0.4 and 6.2.0 source snapshots. They are not a promise about every patch or a future major release. Recheck the actual installed release and compatibility configuration before applying a migration.

| API | Observed behavior and review guidance |
| --- | --- |
| `BaseDatabaseModel::getDbo()` | Present in all three snapshots. Prefer injected database access through `getDatabase()`. The 5.4.8 docblock plans removal in 6.0; the 6.x snapshots retain the method and move the plan to 7.0. A deadline in an older docblock does not establish actual removal. |
| `DatabaseDriver::createQuery()` / `getQuery()` | `createQuery()` exists in all three. The `$new` argument of `getQuery($new)` is deprecated in the inspected dependencies; do not describe every use of `getQuery()` as removed. Joomla 5.4.8 bundles database 3.4.3; the two Joomla 6 snapshots bundle database 4.0.0. Framework and CMS version numbers are distinct. |
| `CMSObject` | Present, deprecated, in all three snapshots; the 6.x docblock plans removal in 7.0. Verify the real return type and caller needs instead of asserting all model items are `stdClass`. |
| Model error handling | `AdminModel::save()` still uses boolean results and `setError()`. Preserve caller expectations when introducing exceptions; do not turn a compatibility cleanup into an unrelated behavioral change. |
| View `$this->get(...)` | Deprecated since 5.3.0 in `AbstractView`, with removal planned for 7.0. Prefer `$model = $this->getModel()` and explicit model methods. |
| Application/identity access | BaseController supplies protected `$app`, not a general `getApplication()` or `getIdentity()` method. CMSPlugin supplies protected `getApplication()`. Use the actual base-class/trait contract or explicitly injected application/current user. |
| CMS Input/Filesystem namespaces | The inspected Joomla 5.4.8 tree contains the legacy CMS Input/File classes; the two Joomla 6 trees do not. Use the installed Framework namespaces and signatures; inspect compatibility support separately rather than assuming aliases everywhere. |
| Plugin construction/events | Inspect the exact `CMSPlugin` constructor, provider and event dispatch code. The inspected base constructor supports config plus a deprecated compatibility branch for a Dispatcher argument. Match the listener/event signature to the actual event and target version. |
| Installer scripts | `InstallerAdapter` accepts a returned service provider or `InstallerScriptInterface` object in the inspected 6.0.4 source and retains a deprecated legacy adapter. The manifest `scriptfile` element itself is not a forbidden legacy pattern. |
| Bootstrap modal | The helper and `bootstrap.modal` asset are present in the inspected Joomla 6 releases. A preference for Joomla dialog is not proof that Bootstrap modal was removed. |

Sources: [5.4.8 BaseDatabaseModel](https://github.com/joomla/joomla-cms/blob/5.4.8/libraries/src/MVC/Model/BaseDatabaseModel.php#L393), [6.0.4 BaseDatabaseModel](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Model/BaseDatabaseModel.php#L393), [6.0.4 CMSObject](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Object/CMSObject.php), [6.0.4 AbstractView](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/View/AbstractView.php#L138), [6.0.4 CMSPlugin](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Plugin/CMSPlugin.php#L131), [6.0.4 InstallerAdapter](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Installer/InstallerAdapter.php#L928). Framework implementations: [database 3.4.3](https://github.com/joomla-framework/database/blob/3.4.3/src/DatabaseDriver.php), [database 4.0.0](https://github.com/joomla-framework/database/blob/4.0.0/src/DatabaseDriver.php). For bundled dependency versions and distributed files, use the corresponding official [5.4.8 release](https://github.com/joomla/joomla-cms/releases/tag/5.4.8), [6.0.4 release](https://github.com/joomla/joomla-cms/releases/tag/6.0.4) and [6.2.0 release](https://github.com/joomla/joomla-cms/releases/tag/6.2.0); vendor payloads are not necessarily tracked in the source repository.

When a deprecation claim cannot be verified, record it as unverified and keep it out of a required compatibility fix. For a removed method, establish the missing target API and reachable caller failure; for a retained deprecated method, describe the migration horizon separately from current functionality.
