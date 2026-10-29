# Joomla 

## Coding Standards for Joomla projects

### Namespacing Guidelines
- All namespacing at the top of each file should be in alphabetical order for any Joomla task/project
- All component Classes namespaced under _vendor_\_name_ 
- 
- ### Code Standards
- PHP 8.3+ language features (constructor promotion, readonly properties, enums, match expressions, typed class constants, `#[Override]` attribute)
- Modern PSR-4 autoloading with Joomla namespaced classes
- Joomla 5.x/6.x conventions and security practices
- All files include `defined('_JEXEC') or die;` protection
- Uses container-based dependency injection
- PHPDoc comments for all public methods and properties
### Reference Libraries
- Always consult https://context7.com/context7/developer_joomla-coding-standards library for additional coding standards reference
- Refer to additional context7 libraries located in @.claude/includes/context7.json before starting any tasks
- Always use the latest version of the context7 libraries

### Input Handling
- NEVER access PHP superglobals (`$_REQUEST`, `$_GET`, `$_POST`, `$_COOKIE`) directly. Always use Joomla's `InputInterface` via `$this->app->getInput()` or `Factory::getApplication()->getInput()`.
- Use typed getter methods: `$input->getInt()`, `$input->getString()`, `$input->getCmd()`, etc.
- For HikaShop legacy plugins, use `$this->app->getInput()` (available via the parent class) — NOT `hikaInput::get()` or raw superglobals.
- Filter and validate all input at the point of retrieval. Never trust client-supplied values for security-sensitive decisions (e.g., payment status).

### Design Patterns
- Do NOT use the Repository design pattern in Joomla extensions. Use Joomla's native Model pattern (`ListModel`, `FormModel`, `AdminModel`, `BaseDatabaseModel`) for all data access.
- Models handle database queries, state management, and business logic — there is no need for a separate Repository layer.

### Manifest XML Naming
- Component manifest files MUST be named `{name}.xml` (e.g. `forum.xml`, `community.xml`), **NOT** `com_{name}.xml`.
- The manifest lives inside the admin folder: `admin/com_{name}/{name}.xml`.
- This matches Joomla's convention where the manifest filename is the extension name without the `com_` prefix.

### Configuration Parameters
- The manifest XML is for extension metadata, installation instructions, namespace, and file declarations.
- If extension type is `component` Extension configuration parameters MUST be defined in a separate `config.xml` file, NOT embedded as `<config>` blocks inside the extension's manifest XML file (`{name}.xml`).


### Repository Folder Structure
- Components are stored in `Components/com_{name}/` with `admin/`, `api/`, `media/`, and `site/` as peer subdirectories.
- The `/api` folder is a subfolder of the component — NOT a top-level directory.
- The `/src` folder belongs inside each component layer (e.g., `admin/src/`), NOT at the repository root.
- The `/tmpl` folder is at the same level as `/src` within each layer — NOT a subdirectory of `/View`.
- Plugins are stored in `Plugins/{group}/{name}/`.
- Build configuration goes in the `Phing/` directory.
- See `includes/joomla-devel-environment.md` for the full repository structure reference.

### Version Synchronisation (V.R.M)
- The extension version follows **V.R.M** (Version.Release.Modification) format (e.g. `0.0.5`)
- **Reset rules when incrementing**:
  - Incrementing **V** (version) resets both **R** and **M** to `0` (e.g. `1.2.3` → `2.0.0`)
  - Incrementing **R** (release) resets **M** to `0` (e.g. `1.2.3` → `1.3.0`)
  - Incrementing **M** (modification) changes only **M** (e.g. `1.2.3` → `1.2.4`)
- **Three files MUST stay in sync**:
  1. **SQL update file**: `sql/updates/mysql/{V.R.M}.sql`
  2. **Manifest XML**: `<version>` element in `admin/com_{name}/{name}.xml`
  3. **Phing build file**: `version` property in `Phing/com_{name}.xml`
- **When a schema change is needed**, ASK the user whether to:
  - **Append** to the current (latest) SQL update file, OR
  - **Create a new** SQL update file with the next version number
- Only when a **new** SQL update file is created should the manifest and Phing versions be bumped to match
- Appending to the current file requires no version changes — this supports iterative development before deployment

### Git Commit Message Convention
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

### Do Not Remove `$query->dump()`
- `DatabaseQuery::dump()` is marked deprecated since Joomla 3 but **must not be removed** from existing code
- It is actively used for debugging SQL statements during development
- Agents and code reviewers must leave existing `dump()` calls in place

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

### Filter Form XML Preferences
- **Do NOT include a `fullordering` field** in filter XML files — users sort via clickable column headings (`HTMLHelper::_('searchtools.sort', ...)`)
- The `<fields name="list">` section should only contain the `limit` (limitbox) field
- Filter dropdowns go in `<fields name="filter">`

### Model Error Surfacing
- All ListModel and AdminModel subclasses MUST use the `DebugErrorAwareTrait`
- The trait overrides `setError()` to enqueue errors as warnings when `JDEBUG` is active
- The trait file exists in each component's `Model` namespace (same namespace, no import needed)
- Add `use DebugErrorAwareTrait;` as the first statement inside the class body
- BaseDatabaseModel subclasses (DataModels, DashboardModel) do NOT need the trait

## Joomla 5 Dependency Injection Patterns

### Component Service Provider (`services/provider.php`)

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
| **API controllers** (within the component) | Same as admin — API controllers are in a separate namespace and don't have direct DI access |
| **Plugins** needing component services | `$this->getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |
| **CLI commands** | `$this->getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |
| **Other components** | `Factory::getApplication()->bootComponent('com_example')->getContainer()->get(Service::class)` |

#### Important notes

- This is an **internal convention**, not part of Joomla's public API — the same approach is used by Akeeba Backup and other major extensions
- `bootComponent()` triggers the component's `boot()` method if not already called, ensuring the container is populated
- Services resolved this way are the same singleton instances registered in `services/provider.php`
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
4. **Use PHP 8.3+ constructor promotion** with `readonly` properties
5. **Avoid circular dependencies** - use lazy loading or factory patterns
6. **Keep service providers simple** - complex logic belongs in the services themselves
7. **Use `#[Override]`** attribute when overriding parent methods

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

### `jexit()` (Deprecated since 4.0)
**Pattern**: Using `jexit()` for token validation exit
**Removal Version**: 6.0

#### Detection Pattern
```php
// WRONG — jexit() is deprecated
Session::checkToken() || jexit(Text::_('JINVALID_TOKEN'));
```

#### Recommended Migration
```php
// CORRECT — use BaseController's built-in method
$this->checkToken();
```

`BaseController::checkToken()` handles token validation and throws the appropriate exception. No manual `Session::checkToken()` or `jexit()` calls needed.

### `$this->app` in MVC Controllers
**Note**: `$this->app` is a protected property on `BaseController` that is always initialized in the constructor (with `Factory::getApplication()` fallback). It is safe to use `$this->app` directly in MVC controllers. `getApplication()` does NOT exist on MVC controller classes — do not use it there.

### Bootstrap Modals (Deprecated in Joomla 5)
**Pattern**: Using Bootstrap modals (`data-bs-toggle="modal"`, `bootstrap.modal` script, `new bootstrap.Modal()`)
**Issue**: Joomla 5 provides its own `<joomla-dialog>` web component. Bootstrap modals are deprecated and will be removed in Joomla 6.

#### Detection Patterns
```javascript
// WRONG — bootstrap is not a global in Joomla 5
new bootstrap.Modal(element).show();
```
```html
<!-- WRONG — Bootstrap modal markup -->
<div class="modal fade" id="myModal" data-bs-toggle="modal">
```
```php
// WRONG — Bootstrap modal asset loading
HTMLHelper::_('bootstrap.modal', '#myModalId');
$wa->useScript('bootstrap.modal');
```

#### Recommended Migration
Use Joomla's `<joomla-dialog>` web component with `data-joomla-dialog` attribute:
```php
// Load the dialog autocreate script
$wa->useScript('joomla.dialog-autocreate');
```
```html
<!-- Trigger button -->
<button type="button"
        data-joomla-dialog='{"popupType": "inline", "src": "#myDialogContent", "textHeader": "Title", "width": "500px", "height": "fit-content"}'>
    Open Dialog
</button>

<!-- Dialog content in a template element -->
<template id="myDialogContent">
    <div class="p-3">Dialog body here</div>
</template>
```

Reference: https://manual.joomla.org/docs/4.4/general-concepts/javascript/js-library/joomla-dialog/

### `$query->dump()` — Do NOT Remove
**Pattern**: `$query->dump()` marked deprecated since Joomla 3
**Status**: Despite the deprecation marker, this method **must not be removed** from existing code. It is actively used for debugging SQL statements during development. Agents and code reviewers must leave existing `dump()` calls in place.

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