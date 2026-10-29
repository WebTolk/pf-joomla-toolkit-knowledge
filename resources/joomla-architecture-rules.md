# Joomla architecture and project conventions

## Scope and authority

Use these references with the project's declared Joomla/PHP versions and accepted architecture. Joomla API facts, general engineering guidance and optional project profiles have different authority. A profile applies only when explicitly adopted by the project; loading this package does not adopt it. Record the reason and scope of accepted exceptions. An accepted architectural exception does not negate a demonstrated vulnerability. See the [review guide](joomla-extension-review.md) for evidence and finding categories.

## Coding Standards for Joomla projects

### Namespacing Guidelines
- All namespacing at the top of each file should be in alphabetical order for any Joomla task/project
- All component Classes namespaced under _vendor_\_name_ 
- 
- ### Code Standards
- Use language features supported by the declared minimum PHP version. PHP 8.3+ is an optional project baseline, not a requirement for every Joomla 5.4 extension. Constructor promotion, readonly properties and enums predate PHP 8.3; typed class constants and `#[Override]` require PHP 8.3.
- Modern PSR-4 autoloading with Joomla namespaced classes
- Joomla 5.x/6.x conventions and security practices
- All files include `defined('_JEXEC') or die;` protection
- Uses container-based dependency injection
- PHPDoc comments for all public methods and properties
### Reference Libraries
Use the exact supported Joomla release and its installed Framework dependencies as the API reference. Development branches, rolling documentation and compatibility plugins do not establish behavior on an older target. Resolve project-selected knowledge before reading it; do not assume unrelated local configuration files or external reference collections are present.

### Input Handling
- NEVER access PHP superglobals (`$_REQUEST`, `$_GET`, `$_POST`, `$_COOKIE`) directly. Use the application's input object via `$this->app->getInput()` or `Factory::getApplication()->getInput()`.
- Use typed getter methods: `$input->getInt()`, `$input->getString()`, `$input->getCmd()`, etc.
- Optional HikaShop project profile: for legacy plugins, use `$this->app->getInput()` (available via the parent class) — NOT `hikaInput::get()` or raw superglobals.
- Filter and validate all input at the point of retrieval. Never trust client-supplied values for security-sensitive decisions (e.g., payment status).

### Design Patterns

Joomla Model/Table is a good default for request state, lists, forms, ordinary CRUD and record lifecycle. Keep existing authorization, validation, checkout, events, assets and cache behavior when changing persistence code.

Use a domain service when an operation coordinates several steps or tables, external APIs, payments, files, retry policy or transaction boundaries. The service expresses the business operation; controllers adapt HTTP, models expose Joomla state/forms, and persistence collaborators perform storage work. A database transaction cannot roll back a remote payment or file operation: define idempotency, failure recovery and compensation explicitly.

A Repository is permitted when it provides a concrete benefit, such as isolating complex queries, sharing persistence across entry points or supporting a domain boundary. A wrapper around every Table method adds little value. Its presence or absence is not itself a defect and does not require refactoring working code.

Choose using the actual workflow, reuse, failure modes and project architecture. If a project explicitly prohibits a Repository or requires data access through models, preserve that restriction as an accepted project exception with its scope and rationale. It does not become a Joomla-wide rule and cannot waive a proven security defect.

When overriding `AdminModel::save()`, preserve the lifecycle actually needed by the caller. In the inspected Joomla 5.4.8, 6.0.4 and 6.2.0 implementations, an existing row is loaded, then `bind()` runs before `prepareTable()`, `check()`, the before-save event and `store()`; the after-save event follows storage. Form filtering/validation in the controller/form model is a separate earlier boundary. Do not describe `prepareTable()` as running before bind or silently bypass events in a service.

Source: [Joomla 5.4.8 AdminModel::save](https://github.com/joomla/joomla-cms/blob/5.4.8/libraries/src/MVC/Model/AdminModel.php#L1256), [Joomla 6.0.4 AdminModel::save](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Model/AdminModel.php#L1288).

### Manifest XML Naming
Use a manifest filename supported by the extension type and installer, and verify the archive and installed manifest location. A project may adopt `{name}.xml` and an `admin/` source directory as its packaging convention; that repository path is not a universal installed Joomla path. Renaming a working manifest requires checking the existing build/update contract first. See [installed payload verification](joomla-extension-structures.md#source-manifest-and-installed-payload).

### Configuration Parameters
- The manifest XML is for extension metadata, installation instructions, namespace, and file declarations.
- If extension type is `component` Extension configuration parameters MUST be defined in a separate `config.xml` file, NOT embedded as `<config>` blocks inside the extension's manifest XML file (`{name}.xml`).


### Repository Folder Structure (optional project profile)

The following layout is a project packaging convention. Joomla installation destinations are established by the manifest and extension adapter, not by the capitalization of repository folders.
- Components are stored in `Components/com_{name}/` with `admin/`, `api/`, `media/`, and `site/` as peer subdirectories.
- The `/api` folder is a subfolder of the component — NOT a top-level directory.
- The `/src` folder belongs inside each component layer (e.g., `admin/src/`), NOT at the repository root.
- The `/tmpl` folder is at the same level as `/src` within each layer — NOT a subdirectory of `/View`.
- Plugins are stored in `Plugins/{group}/{name}/`.
- Build configuration goes in the `Phing/` directory.
- Use the project's own build configuration for the complete source layout; see the [extension structure reference](joomla-extension-structures.md) for installed destinations.

### Version Synchronisation (V.R.M project profile)

Apply the following three-file/Phing convention only to projects that adopt it. General release rule: released archives and executed migration files are immutable; use a new migration for an already deployed schema change. Extension releases can contain code or security fixes without SQL changes. Synchronize each release's actual version declarations even when no SQL update exists.
- The extension version follows **V.R.M** (Version.Release.Modification) format (e.g. `0.0.5`)
- **Reset rules when incrementing**:
  - Incrementing **V** (version) resets both **R** and **M** to `0` (e.g. `1.2.3` → `2.0.0`)
  - Incrementing **R** (release) resets **M** to `0` (e.g. `1.2.3` → `1.3.0`)
  - Incrementing **M** (modification) changes only **M** (e.g. `1.2.3` → `1.2.4`)
- **Three files MUST stay in sync**:
  1. **SQL update file**: `sql/updates/mysql/{V.R.M}.sql`
  2. **Manifest XML**: `<version>` element in `admin/com_{name}/{name}.xml`
  3. **Phing build file**: `version` property in `Phing/com_{name}.xml`
- **During an unreleased development iteration**, follow the project decision on whether to:
  - **Append** to the current (latest) SQL update file, OR
  - **Create a new** SQL update file with the next version number
- Within that unreleased iteration, creating a **new** SQL update file also updates the manifest and Phing version to match
- Appending to the current file requires no version changes — this supports iterative development before deployment

### Git Commit Message Convention (optional project profile)
- Commit messages for extension changes MUST include the extension name and its current V.R.M version from the manifest XML
- Format: `{extension_name} {V.R.M} - meaningful description`
- Examples:
  - `com_forum 0.0.8 - Fix nested set rebuild and add utilities toolbar`
  - `plg_webservices_forum 1.0.0 - Add board API endpoint`
  - `com_community 0.0.2 - Add partner management CRUD`
- The version number is read from the `<version>` element in the extension's manifest XML
- For commits touching multiple extensions, create separate commits per extension

### DatabaseQuery `bind()` — By-Reference Gotcha
- `DatabaseQuery::bind()` accepts its value parameter **by reference** (`&$value`)
- **Never reuse a loop variable** across multiple `bind()` calls — all bindings will point to the final value of the variable
- Store each value in a separate array element so each binding has a stable reference:
  ```php
  // WRONG — $value is overwritten each iteration, all binds point to last value
  foreach (['scope', 'affiliation'] as $field) {
      $value = $this->getState('filter.' . $field);
      if ($value !== '') {
          $query->where($db->quoteName($field) . ' = :' . $field)
              ->bind(':' . $field, $value);
      }
  }

  // CORRECT — each array element is a distinct reference
  $filterValues = [];
  foreach (['scope', 'affiliation'] as $field) {
      $filterValues[$field] = $this->getState('filter.' . $field);
      if ($filterValues[$field] !== null && $filterValues[$field] !== '') {
          $query->where($db->quoteName($field) . ' = :' . $field)
              ->bind(':' . $field, $filterValues[$field]);
      }
  }
  ```

### SQL Filter Fields — Exclude NULL Values
- SQL-type filter fields in form XML (`type="sql"`) that use `SELECT DISTINCT` can return `NULL` values from the database
- On PHP 8.1+, passing `NULL` to Joomla's `Select` helper triggers deprecation warnings in `trim()` and `explode()`
- Always add `WHERE column IS NOT NULL AND column != ''` and `ORDER BY column` to filter field queries:
  ```xml
  <field name="scope" type="sql"
         query="SELECT DISTINCT scope AS value, scope AS scope FROM #__example_items WHERE scope IS NOT NULL AND scope != '' ORDER BY scope"
         label="FILTER_SCOPE" onchange="this.form.submit();">
      <option value="">FILTER_SCOPE</option>
  </field>
  ```

### SQL Debugging (accepted project exception)
A project may explicitly retain existing `$query->dump()` calls for controlled development diagnostics. This is a project exception, not a Joomla API guarantee or a requirement for new code. The inspected Framework DatabaseQuery class still provides the method with a deprecation marker.

Preserve the accepted diagnostic behavior unless a change is authorized, but check whether SQL, bound values, credentials or personal data reach public output or logs. Demonstrated sensitive-data disclosure remains a security defect even if the debugging architecture was approved. Report its reachable path and propose the smallest containment, such as a verified development-only guard or redacted restricted logging.

### Database Schema
- MySQL8+ and MariaDB 10+ support
- Changes to the database schema to be updated in /sql/updates/mysql/ with version numbers
- Use `DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci` for all tables
- Use `ENGINE=InnoDB` for all tables

#### Standard Joomla System Fields for Core/CRUD Tables

Main entity tables where users create, edit, and manage records through CRUD interfaces MUST include these standard Joomla system fields:

```sql
-- Publication & workflow
state TINYINT(1) NOT NULL DEFAULT 0,           -- 1=published, 0=unpublished, 2=archived, -2=trashed
ordering INT NOT NULL DEFAULT 0,                -- Display order within lists
access INT UNSIGNED NOT NULL DEFAULT 1,         -- Joomla access level (1=Public, 2=Registered, etc.)

-- Ownership & audit trail
created DATETIME NOT NULL,                      -- Record creation timestamp
created_by INT UNSIGNED NOT NULL DEFAULT 0,     -- Joomla user ID of creator
modified DATETIME,                              -- Last modification timestamp
modified_by INT UNSIGNED NOT NULL DEFAULT 0,    -- Joomla user ID of last modifier

-- Edit locking
checked_out INT UNSIGNED,                       -- User ID who has record checked out for editing
checked_out_time DATETIME,                      -- When the checkout occurred

-- Optional but common on content-like entities
asset_id INT UNSIGNED NOT NULL DEFAULT 0,       -- Joomla ACL asset reference (for per-item permissions)
alias VARCHAR(400) NOT NULL DEFAULT '',         -- URL-safe slug (for SEF routing)
publish_up DATETIME,                            -- Scheduled publish start
publish_down DATETIME,                          -- Scheduled publish end
language CHAR(7) NOT NULL DEFAULT '*',          -- Language code ('*' = all languages)
note VARCHAR(255) NOT NULL DEFAULT '',          -- Admin-only notes
```

**Required indexes for system fields:**
```sql
KEY idx_state (state),
KEY idx_created_by (created_by),
KEY idx_access (access),
KEY idx_checked_out (checked_out),
KEY idx_language (language)
```

#### When to Include System Fields

| Table Type | System Fields Required | Examples |
|---|---|---|
| **Core entity tables** (user-managed CRUD) | Full set: state, ordering, access, created, created_by, modified, modified_by, checked_out, checked_out_time | Items, Categories, Customers, Orders, Invoices |
| **Secondary entity tables** (admin-managed) | Minimum: state, created, created_by, modified, modified_by | Addresses, Contacts, Tax Rates, Pricing Rules |
| **Link/join tables** (cross-references) | NOT required — keep minimal | item_tag_map, category_item, user_role |
| **System/log tables** (auto-generated) | Only created (timestamp) | Audit logs, Stock movements, Payment transactions |

#### Reference: Complete Core Table Template
```sql
CREATE TABLE IF NOT EXISTS `#__example_items` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `asset_id` INT UNSIGNED NOT NULL DEFAULT 0,
    `title` VARCHAR(255) NOT NULL DEFAULT '',
    `alias` VARCHAR(400) NOT NULL DEFAULT '',
    -- ... entity-specific fields here ...
    `state` TINYINT(1) NOT NULL DEFAULT 0,
    `ordering` INT NOT NULL DEFAULT 0,
    `access` INT UNSIGNED NOT NULL DEFAULT 1,
    `created` DATETIME NOT NULL,
    `created_by` INT UNSIGNED NOT NULL DEFAULT 0,
    `modified` DATETIME,
    `modified_by` INT UNSIGNED NOT NULL DEFAULT 0,
    `checked_out` INT UNSIGNED,
    `checked_out_time` DATETIME,
    `publish_up` DATETIME,
    `publish_down` DATETIME,
    `language` CHAR(7) NOT NULL DEFAULT '*',
    `note` VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (`id`),
    KEY `idx_state` (`state`),
    KEY `idx_created_by` (`created_by`),
    KEY `idx_access` (`access`),
    KEY `idx_checked_out` (`checked_out`),
    KEY `idx_language` (`language`),
    KEY `idx_alias` (`alias`(191))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```


#### Hierarchical/Nested Tables (Parent-Child Relationships)

Tables with a `parent_id` column (adjacency list pattern) MUST also include **nested set columns** to enable efficient tree ordering and depth display in admin list views:

```sql
-- Required nested set fields (add after entity-specific fields, before Joomla system fields)
`level` INT UNSIGNED NOT NULL DEFAULT 0,    -- Depth in tree (0=root, 1=child, 2=grandchild)
`lft` INT NOT NULL DEFAULT 0,               -- Left boundary of nested set range
`rgt` INT NOT NULL DEFAULT 0,               -- Right boundary of nested set range
```

**Required index:**
```sql
KEY `idx_lft` (`lft`)
```

**Implementation requirements:**
- A `rebuildNestedSet()` method in the entity's **Service class** walks the adjacency list (`parent_id`) and computes `lft`, `rgt`, and `level` for every row
- The entity's **AdminModel** (`save()`) must call `rebuildNestedSet()` after every save so tree values stay current
- The entity's **ListModel** must default to `ORDER BY a.lft ASC` (set in both `populateState()` and the `getListQuery()` fallback)
- The entity's **ListModel** must include `level`, `lft` in both the SELECT column list and the `filter_fields` array
- The **list view template** renders indentation with: `<?php echo str_repeat('<span class="gi">&mdash;</span>', (int) $item->level); ?>`
- The **edit form** parent field must use `type="sql"` (not `type="list"`) to dynamically populate from the database

### Popups and Modals
- **Always use Joomla's `<joomla-dialog>` web component** — never use Bootstrap modals directly
- Reference: `joomla-dialog` on `https://manual.joomla.org`
- Load via Web Asset Manager: `$wa->useScript('joomla.dialog-autocreate');`
- Trigger with the `data-joomla-dialog` attribute on buttons/links:
  ```html
  <button type="button"
          data-joomla-dialog='{"popupType": "inline", "src": "#myTemplateId", "textHeader": "Dialog Title", "width": "500px", "height": "fit-content"}'>
      Open Dialog
  </button>
  ```
- Place dialog content in a `<template id="myTemplateId">` element — the web component clones it into the dialog body when opened
- Supports four popup types: `inline`, `iframe`, `image`, `ajax`
- For toolbar popups, use `$toolbar->popupButton()` with `->popupType('inline')` pointing to a `<template>` element
- Bootstrap modals (`data-bs-toggle="modal"`, `bootstrap.modal` script) are **deprecated** in Joomla 5 and must not be used

### View HtmlView Preferences
- Use the direct model call pattern, not deprecated `$this->get()` magic method
- **Edit/Form views MUST load the form validator** via Web Asset Manager: `$this->document->getWebAssetManager()->useScript('form.validate');`
- Place the `useScript` call in `display()` after `addToolbar()` and before `parent::display($tpl)`
- Without this, the `form-validate` CSS class on the `<form>` element causes a JS error: `document.formvalidator is undefined`

### Filter Form XML Preferences (optional project profile)
- **Do NOT include a `fullordering` field** in filter XML files — users sort via clickable column headings (`HTMLHelper::_('searchtools.sort', ...)`)
- The `<fields name="list">` section should only contain the `limit` (limitbox) field
- Filter dropdowns go in `<fields name="filter">`

### Model Error Surfacing (optional project profile)

`DebugErrorAwareTrait` below is a project-defined trait, not a Joomla core API. Apply this policy only when that trait exists and the project has adopted it. Avoid exposing sensitive errors even in a diagnostic mode.
- All ListModel and AdminModel subclasses MUST use the `DebugErrorAwareTrait`
- The trait overrides `setError()` to enqueue errors as warnings when `JDEBUG` is active
- The trait file exists in each component's `Model` namespace (same namespace, no import needed)
- Add `use DebugErrorAwareTrait;` as the first statement inside the class body
- BaseDatabaseModel subclasses (DataModels, DashboardModel) do NOT need the trait

## Joomla 5 Dependency Injection Patterns

### Component Service Provider (`services/provider.php`)

For a component, `bootComponent()` loads the provider from the installed administrator component directory, including when the caller is the site or API application. Do not create site/API providers merely because those client directories exist. A custom service dependency on a model/controller needs actual MVC factory wiring; declaring it in a constructor alone does not make core MVCFactory resolve arbitrary arguments. Preserve parent constructor contracts for the exact target version.

Sources: [Joomla 6.0.4 component boot](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/Extension/ExtensionManagerTrait.php#L42), [MVCFactory](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Factory/MVCFactory.php#L99).

```php
<?php

defined('_JEXEC') or die;

use Joomla\CMS\Dispatcher\ComponentDispatcherFactoryInterface;
use Joomla\CMS\Extension\ComponentInterface;
use Joomla\CMS\Extension\Service\Provider\CategoryFactory;
use Joomla\CMS\Extension\Service\Provider\ComponentDispatcherFactory;
use Joomla\CMS\Extension\Service\Provider\MVCFactory;
use Joomla\CMS\Extension\Service\Provider\RouterFactory;
use Joomla\CMS\HTML\Registry;
use Joomla\CMS\MVC\Factory\MVCFactoryInterface;
use Joomla\DI\Container;
use Joomla\DI\ServiceProviderInterface;
use Vendor\Component\Example\Administrator\Extension\ExampleComponent;

return new class () implements ServiceProviderInterface {
    public function register(Container $container): void
    {
        // Register core component factories
        $container->registerServiceProvider(new CategoryFactory('\\Vendor\\Component\\Example'));
        $container->registerServiceProvider(new ComponentDispatcherFactory('\\Vendor\\Component\\Example'));
        $container->registerServiceProvider(new MVCFactory('\\Vendor\\Component\\Example'));
        $container->registerServiceProvider(new RouterFactory('\\Vendor\\Component\\Example'));

        // Register the component extension
        $container->set(
            ComponentInterface::class,
            function (Container $container) {
                $component = new ExampleComponent($container->get(ComponentDispatcherFactoryInterface::class));
                $component->setMVCFactory($container->get(MVCFactoryInterface::class));
                $component->setRegistry($container->get(Registry::class));
                $component->setRouterFactory($container->get(RouterFactory::class));

                return $component;
            }
        );
    }
};
```

### Module Service Provider (`services/provider.php`)

```php
<?php

defined('_JEXEC') or die;

use Joomla\CMS\Extension\Service\Provider\HelperFactory;
use Joomla\CMS\Extension\Service\Provider\Module;
use Joomla\CMS\Extension\Service\Provider\ModuleDispatcherFactory;
use Joomla\DI\Container;
use Joomla\DI\ServiceProviderInterface;

return new class () implements ServiceProviderInterface {
    public function register(Container $container): void
    {
        $container->registerServiceProvider(new ModuleDispatcherFactory('\\Vendor\\Module\\Example'));
        $container->registerServiceProvider(new HelperFactory('\\Vendor\\Module\\Example\\Site\\Helper'));
        $container->registerServiceProvider(new Module());
    }
};
```

### Plugin Service Provider (`services/provider.php`)

```php
<?php

defined('_JEXEC') or die;

use Joomla\CMS\Extension\PluginInterface;
use Joomla\CMS\Factory;
use Joomla\CMS\Plugin\PluginHelper;
use Joomla\DI\Container;
use Joomla\DI\ServiceProviderInterface;
use Joomla\Event\DispatcherInterface;
use Vendor\Plugin\System\Example\Extension\Example;

return new class () implements ServiceProviderInterface {
    public function register(Container $container): void
    {
        $container->set(
            PluginInterface::class,
            function (Container $container) {
                $dispatcher = $container->get(DispatcherInterface::class);
                $plugin = new Example(
                    $dispatcher,
                    (array) PluginHelper::getPlugin('system', 'example')
                );
                $plugin->setApplication(Factory::getApplication());

                return $plugin;
            }
        );
    }
};
```

### Constructor Injection Patterns

#### Service Injection in Controllers
```php
<?php

namespace Vendor\Component\Example\Administrator\Controller;

use Joomla\CMS\MVC\Controller\AdminController;
use Joomla\CMS\MVC\Factory\MVCFactoryInterface;
use Joomla\CMS\Application\CMSApplication;
use Joomla\Input\Input;

class ItemsController extends AdminController
{
    public function __construct(
        $config = [],
        MVCFactoryInterface $factory = null,
        ?CMSApplication $app = null,
        ?Input $input = null
    ) {
        parent::__construct($config, $factory, $app, $input);
    }
}
```

#### Service Injection in Models
```php
<?php

namespace Vendor\Component\Example\Administrator\Model;

use Joomla\CMS\MVC\Model\ListModel;
use Joomla\Database\DatabaseInterface;

class ItemsModel extends ListModel
{
    // Database is available via $this->getDatabase() (inherited)
    // Application is available via Factory::getApplication()
    // No need to inject DatabaseInterface manually in MVC models
}
```

### Common DI Service IDs

| Service Interface | Description |
|---|---|
| `Joomla\Database\DatabaseInterface` | Database connection |
| `Joomla\CMS\Application\CMSApplicationInterface` | Current application |
| `Joomla\CMS\User\UserFactoryInterface` | User factory |
| `Joomla\CMS\Mail\MailerFactoryInterface` | Mailer factory |
| `Joomla\CMS\Language\LanguageFactoryInterface` | Language factory |
| `Joomla\Event\DispatcherInterface` | Event dispatcher |
| `Joomla\CMS\Cache\CacheControllerFactoryInterface` | Cache factory |
| `Joomla\CMS\Session\SessionInterface` | Session |
| `Joomla\CMS\Document\DocumentInterface` | Document |
| `Joomla\CMS\Router\SiteRouter` | Site router |
| `Psr\Log\LoggerInterface` | PSR-3 logger |

### Accessing Services from the Container

```php
// From anywhere with access to the application
$db = Factory::getContainer()->get(DatabaseInterface::class);
$mailer = Factory::getContainer()->get(MailerFactoryInterface::class);

// From within a component extension class
$db = $this->getContainer()->get(DatabaseInterface::class);

// From controllers (via MVCFactory)
$db = $this->getModel()->getDatabase();

// From models (inherited method)
$db = $this->getDatabase();
```

### Accessing Component Services via bootComponent (Internal Pattern)

Joomla's `MVCComponent` does not natively expose its DI container. When code outside the component's own MVC stack needs to resolve component services (API controllers, plugins, other components, CLI commands), use the **bootComponent pattern**:

#### Step 1: Expose the container from the Extension class

The component's Extension class must implement `BootableExtensionInterface` and store the container passed to `boot()`:

```php
namespace Vendor\Component\Example\Administrator\Extension;

use Joomla\CMS\Extension\BootableExtensionInterface;
use Joomla\CMS\Extension\MVCComponent;
use Psr\Container\ContainerInterface;

class ExampleComponent extends MVCComponent implements BootableExtensionInterface
{
    private ?ContainerInterface $container = null;

    /**
     * @internal Used by controllers/plugins to resolve services.
     *           Joomla's MVCComponent does not expose the container natively.
     */
    public function getContainer(): ContainerInterface
    {
        if ($this->container === null) {
            throw new \RuntimeException('Component container not available. Has boot() been called?');
        }

        return $this->container;
    }

    #[\Override]
    public function boot(ContainerInterface $container): void
    {
        $this->container = $container;
        // Other boot logic...
    }
}
```

#### Step 2: Resolve services from anywhere

```php
use Vendor\Component\Example\Administrator\Service\SomeService;

// From any code with access to the application (controllers, plugins, CLI)
$service = $app->bootComponent('com_example')
    ->getContainer()
    ->get(SomeService::class);
```

#### When to use this pattern

| Context | How to get services |
|---------|-------------------|
| **Admin controllers** (within the component) | `$this->app->bootComponent('com_example')->getContainer()->get(Service::class)` |
| **API controllers** (within the component) | Same custom bridge if adopted; constructor/factory injection is also possible when explicitly wired |
| **Plugins** needing component services | `$this->getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |
| **CLI commands** | `$this->getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |
| **Other components** | `Factory::getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |

#### Important notes

- This is an **optional project convention**, not a method guaranteed by Joomla's component interface. Prefer explicit factory/constructor injection for dependencies within the component
- `bootComponent()` triggers the component's `boot()` method if not already called, ensuring the container is populated
- Service lifetime depends on registration. Use a shared service explicitly when one instance is required; container registration alone does not imply singleton lifetime
- The `@internal` docblock on `getContainer()` signals that this is a bridge method, not a public extension point
- **Never call `getContainer()` from within the component's own models or views** — those should use constructor injection via the service provider

### Anti-Patterns to Avoid

```php
// WRONG: Direct static factory calls (deprecated)
$db = JFactory::getDbo();
$user = JFactory::getUser();
$app = JFactory::getApplication();

// WRONG: Service locator in constructors
public function __construct()
{
    $this->db = Factory::getContainer()->get(DatabaseInterface::class);
}

// RIGHT: Constructor injection
public function __construct(
    private readonly DatabaseInterface $db
) {}

// WRONG: Using global state
global $mainframe;

// RIGHT: Inject the application
public function __construct(
    private readonly CMSApplicationInterface $app
) {}
```

### Extension Component Class Pattern

```php
<?php

namespace Vendor\Component\Example\Administrator\Extension;

use Joomla\CMS\Extension\BootableExtensionInterface;
use Joomla\CMS\Extension\MVCComponent;
use Joomla\CMS\HTML\HTMLRegistryAwareTrait;
use Psr\Container\ContainerInterface;

class ExampleComponent extends MVCComponent implements BootableExtensionInterface
{
    use HTMLRegistryAwareTrait;

    public function boot(ContainerInterface $container): void
    {
        // Register custom services, HTML helpers, etc.
    }
}
```

### Best Practices

1. **Prefer constructor injection** over service locator pattern
2. **Use interfaces** for type hints, not concrete classes
3. **Register services as shared** (singleton) when appropriate
4. **Use constructor promotion and `readonly`** only when supported by the declared minimum PHP version
5. **Avoid circular dependencies** - use lazy loading or factory patterns
6. **Keep service providers simple** - complex logic belongs in the services themselves
7. **Use `#[Override]`** when the minimum PHP version supports it

## Deprecated Pattern Avoidance:
   ```php
   
   // Deprecated toolbar
   Toolbar::getInstance('toolbar'); // WRONG
   
   // Correct approach
   $toolbar = Factory::getApplication()->getDocument()->getToolbar();
   
   // Deprecated JFactory
   JFactory::getDbo(); // WRONG
   
   // Correct approach
   Factory::getContainer()->get(DatabaseInterface::class);
   ```

### View Model Access Pattern (Deprecated in 5.3.0)
**Pattern**: Using `$this->get('PropertyName')` in Joomla view classes to access model data
**Deprecation Version**: 5.3.0
**Removal Version**: 7.0
**Location**: `libraries/src/MVC/View/AbstractView.php`

#### Detection Pattern
Look for code like:
```php
// In view classes (HtmlView.php)
$this->items = $this->get('Items');
$this->pagination = $this->get('Pagination');
$this->state = $this->get('State');
```

#### Recommended Migration
Replace with direct model method calls:
```php
// Get the model instance first
$model = $this->getModel();

// Then call methods directly
$this->items = $model->getItems();
$this->pagination = $model->getPagination();
$this->state = $model->getState();
```

#### Detection Pattern
Look for code like:
```php
Factory::getUser()->get('id')
```

#### Recommended Migration
Replace with call to DI Container:
```php
Factory::getApplication()->getIdentity()->id;
```


#### Why This Change
- Improves code clarity and IDE autocomplete support
- Removes magic method overhead
- Makes debugging easier by showing explicit method calls
- Aligns with modern PHP best practices

### Token-check Control Flow
Prefer the Joomla controller token-check facility in state-changing web controller actions. In the inspected BaseController versions, `checkToken()` returns a boolean; invalid tokens redirect by default. It does not always throw for a failed token. If redirects are disabled, explicitly stop when the result is false:

```php
if (!$this->checkToken('post', false)) {
    throw new \RuntimeException(Text::_('JINVALID_TOKEN'), 403);
}
```

This assumes a Joomla web MVC controller and the appropriate `Text` import. A token check does not replace authorization or record ownership checks. Preserve the request method expected by the endpoint. For API authentication and endpoint-specific authorization, use the [REST API reference](joomla6-rest-api-core-full.md).

Source: [Joomla 6.0.4 BaseController::checkToken](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/MVC/Controller/BaseController.php#L1128).

### `$this->app` in MVC Controllers
**Note**: `$this->app` is a protected property on `BaseController` that is always initialized in the constructor (with `Factory::getApplication()` fallback). It is safe to use `$this->app` directly in MVC controllers. `getApplication()` does NOT exist on MVC controller classes — do not use it there.

### Modal Assets and Dialog Choice
Bootstrap modals are present in the inspected Joomla 5.4.8, 6.0.4 and 6.2.0 releases: the Bootstrap helper has `modal()` and the vendor asset registry declares `bootstrap.modal`. Do not report a removal in Joomla 6 merely because a project prefers Joomla dialog.

Load the asset required by the selected UI and verify its actual JavaScript API and template behavior. Joomla dialog can be a project choice; changing an existing modal requires compatibility, focus/keyboard and accessibility checks.

Sources: [Joomla 6.0.4 Bootstrap helper](https://github.com/joomla/joomla-cms/blob/6.0.4/libraries/src/HTML/Helpers/Bootstrap.php#L298), [Joomla 6.0.4 release payload](https://github.com/joomla/joomla-cms/releases/tag/6.0.4).

For SQL debugging policy, see [SQL Debugging](#sql-debugging-accepted-project-exception). For other version-dependent API claims, use the [review version checks](joomla-extension-review.md#version-specific-api-checks).

## Joomla 5 Events System Reference

### SubscriberInterface Implementation

All modern Joomla 5 plugins must implement `SubscriberInterface`:

```php
<?php

namespace Vendor\Plugin\Content\Example\Extension;

defined('_JEXEC') or die;

use Joomla\CMS\Event\Content\AfterSaveEvent;
use Joomla\CMS\Event\Content\BeforeDisplayEvent;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\Event\SubscriberInterface;

final class Example extends CMSPlugin implements SubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            'onContentAfterSave'    => 'handleAfterSave',
            'onContentBeforeDisplay' => 'handleBeforeDisplay',
        ];
    }

    public function handleAfterSave(AfterSaveEvent $event): void
    {
        $context = $event->getContext();
        $item    = $event->getItem();
        $isNew   = $event->getIsNew();

        // Handle the event
    }

    public function handleBeforeDisplay(BeforeDisplayEvent $event): void
    {
        $context = $event->getContext();
        $item    = $event->getItem();
        $params  = $event->getParams();

        // Modify content before display
    }
}
```

### Core Event Names by Group

#### Content Events
| Event Name | Event Class | Triggered When |
|---|---|---|
| `onContentPrepare` | `ContentPrepareEvent` | Content is being prepared for display |
| `onContentAfterTitle` | `AfterTitleEvent` | After content title is rendered |
| `onContentBeforeDisplay` | `BeforeDisplayEvent` | Before content is displayed |
| `onContentAfterDisplay` | `AfterDisplayEvent` | After content is displayed |
| `onContentBeforeSave` | `BeforeSaveEvent` | Before content is saved |
| `onContentAfterSave` | `AfterSaveEvent` | After content is saved |
| `onContentBeforeDelete` | `BeforeDeleteEvent` | Before content is deleted |
| `onContentAfterDelete` | `AfterDeleteEvent` | After content is deleted |
| `onContentChangeState` | `ChangeStateEvent` | When content state changes (publish/unpublish) |
| `onContentBeforeChangeState` | `BeforeChangeStateEvent` | Before content state changes |

#### User Events
| Event Name | Event Class | Triggered When |
|---|---|---|
| `onUserLogin` | `LoginEvent` | User logs in |
| `onUserLogout` | `LogoutEvent` | User logs out |
| `onUserAfterSave` | `AfterSaveEvent` | After user profile is saved |
| `onUserBeforeSave` | `BeforeSaveEvent` | Before user profile is saved |
| `onUserAfterDelete` | `AfterDeleteEvent` | After user is deleted |
| `onUserBeforeDelete` | `BeforeDeleteEvent` | Before user is deleted |
| `onUserAuthorisation` | `AuthorisationEvent` | During authorisation check |

#### System Events
| Event Name | Event Class | Triggered When |
|---|---|---|
| `onAfterInitialise` | `AfterInitialiseEvent` | After application initialisation |
| `onAfterRoute` | `AfterRouteEvent` | After routing is complete |
| `onBeforeRender` | `BeforeRenderEvent` | Before page rendering |
| `onAfterRender` | `AfterRenderEvent` | After page rendering |
| `onBeforeCompileHead` | `BeforeCompileHeadEvent` | Before head section is compiled |
| `onAfterRespond` | `AfterRespondEvent` | After response is sent |

#### Installer Events
| Event Name | Triggered When |
|---|---|
| `onExtensionBeforeInstall` | Before extension installation |
| `onExtensionAfterInstall` | After extension installation |
| `onExtensionBeforeUpdate` | Before extension update |
| `onExtensionAfterUpdate` | After extension update |
| `onExtensionBeforeUninstall` | Before extension uninstallation |
| `onExtensionAfterUninstall` | After extension uninstallation |

### Custom Event Creation

#### Defining a Custom Event Class
```php
<?php

namespace Vendor\Component\Example\Administrator\Event;

defined('_JEXEC') or die;

use Joomla\CMS\Event\AbstractEvent;
use Joomla\CMS\Event\Result\ResultAware;
use Joomla\CMS\Event\Result\ResultAwareInterface;
use Joomla\CMS\Event\Result\ResultTypeStringAware;

class ItemProcessedEvent extends AbstractEvent implements ResultAwareInterface
{
    use ResultAware;
    use ResultTypeStringAware;

    public function __construct(
        string $name,
        array $arguments = []
    ) {
        parent::__construct($name, $arguments);

        // Validate required arguments
        if (!isset($arguments['item'])) {
            throw new \BadMethodCallException("Argument 'item' is required.");
        }
    }

    // Typed getter for the item
    public function getItem(): object
    {
        return $this->arguments['item'];
    }

    // Typed getter for context
    public function getContext(): string
    {
        return $this->arguments['context'] ?? '';
    }
}
```

#### Dispatching Custom Events from Components
```php
<?php

use Joomla\CMS\Event\AbstractEvent;
use Joomla\CMS\Factory;
use Vendor\Component\Example\Administrator\Event\ItemProcessedEvent;

// Create the event
$event = new ItemProcessedEvent('onExampleItemProcessed', [
    'item'    => $item,
    'context' => 'com_example.item',
]);

// Dispatch via the application's event dispatcher
Factory::getApplication()->getDispatcher()->dispatch(
    'onExampleItemProcessed',
    $event
);

// Read results from plugins
$results = $event->getResult();
```

#### Alternative: Using AbstractEvent Factory Method
```php
$event = AbstractEvent::create('onExampleItemProcessed', [
    'subject' => $item,
    'context' => 'com_example.item',
]);

$this->getDispatcher()->dispatch($event->getName(), $event);
```

### Event Result Handling

```php
// In plugin - adding results
public function handleItemProcessed(ItemProcessedEvent $event): void
{
    // Add result using ResultAware trait
    $event->addResult('processed-by-example-plugin');
}

// In component - reading results
$event = new ItemProcessedEvent('onExampleItemProcessed', ['item' => $item]);
Factory::getApplication()->getDispatcher()->dispatch('onExampleItemProcessed', $event);

$results = $event->getResult();
foreach ($results as $result) {
    // Handle each plugin's result
}
```

### Event Naming Conventions

- **Prefix with `on`**: All event names start with `on`
- **Component events**: `on{ComponentName}{Entity}{Action}` (e.g., `onExampleItemProcessed`)
- **Use PascalCase**: `onContentAfterSave`, not `on_content_after_save`
- **Before/After pairs**: Provide both for operations that can be intercepted

### Plugin Group Registration

Plugins must be registered in the correct group in their manifest XML:
```xml
<extension type="plugin" group="content" method="upgrade">
```

Common groups: `content`, `system`, `user`, `authentication`, `webservices`, `console`, `task`, `editors`, `editors-xtd`, `fields`, `finder`, `installer`, `media-action`, `quickicon`, `workflow`

### Migration from Legacy Event Handling

```php
// WRONG: Legacy onContentAfterSave (Joomla 3/4 style)
public function onContentAfterSave($context, $item, $isNew): void

// RIGHT: Modern typed event (Joomla 5 style)
public function handleAfterSave(AfterSaveEvent $event): void
{
    $context = $event->getContext();
    $item    = $event->getItem();
    $isNew   = $event->getIsNew();
}
```

### Best Practices

1. **Always use typed event classes** instead of generic argument arrays
2. **Implement SubscriberInterface** - never use legacy `onEventName` method naming as sole registration
3. **Use `final` class** for plugin extensions to prevent unintended inheritance
4. **Keep event handlers focused** - one handler per concern
5. **Don't throw exceptions** in event handlers unless the operation must be blocked
6. **Use ResultAwareInterface** when plugins need to return data to the dispatcher
7. **Document custom events** with PHPDoc for discoverability