# Joomla extension structures

- Этот файл содержит образцы файловой структуры расширений для Joomla 5+. 
- Также в качестве дополнительной информации можно использовать книгу `Joomla extensions development` в `joomla.development.articles / dionysopoulos-book`. Она о Joomla 4 и частично информация в ней может устареть. Но так же многое может быть полезно до сих пор или служить отправной точкой для поиска.
- Также в качестве дополнительной информации можно использовать статьи в `joomla.development.articles`

## Joomla 5+ Template Structure

See the `joomla.development.articles / sozdanie-shablonov-sajta-v-joomla-4.md` article.

## Joomla 5+ Library Structure

See the `joomla.development.articles / podklyuchenie-storonnih-php-bibliotek-v-joomla-web-tolk.md` article.

## Joomla 5+ Plugin Structure

### Plugin Structure

```
plugins/{group}/{name}/
├── {name}.xml                    — Manifest (metadata, namespace, files only)
├── language/en-GB/
│   ├── plg_{group}_{name}.ini    — Language strings
│   └── plg_{group}_{name}.sys.ini — System language strings
├── services/
│   └── provider.php              — DI service provider
└── src/
    └── Extension/
        └── {Name}.php            — Main plugin class
```

### Plugin Manifest `<files>` Element

The `<files>` block **MUST** include the `plugin="..."` attribute on the `src` folder
entry. This attribute tells the installer the plugin's `element` name for the
`#__extensions` table. Without it, installation fails with
`"Field 'element' doesn't have a default value"`.

```xml
<files>
    <folder plugin="{name}">src</folder>
    <folder>services</folder>
    <folder>language</folder>
</files>
```

### Plugin Key Files
- `/extension_name.xml` - Plugin manifest (defines version, namespace, file declarations, configuration)
- `/services/provider.php` - Service provider for dependency injection
- `/src/Extension/extension_name.php` - Main extension class
- `/language` - Language files are installed within the plugin.

### Language Loading
- **Always** set `protected $autoloadLanguage = true;` in the Extension class
- This tells Joomla to load the plugin's `.ini` language file when the plugin is instantiated
- Without this, `Text::_()` calls within the plugin will return untranslated language keys

### Plugin Preferences
- For smaller code bases keep everything in a single file in the extension_name.php
- For larger more complex code bases, separate the code in several classes in /src


## Joomla 5+ Module Structure

### Module Directory and File Structure
```
/modules/
└── mod_example/
    ├── mod_example.xml
    ├── config.xml
    ├── language/en-GB/
    │   ├── mod_example.ini
    │   └── mod_example.sys.ini
    ├── services/
    │   └── provider.php
    ├── src/
    │   ├── Dispatcher/
    │   │   └── Dispatcher.php
    │   └── Helper/
    │       └── ExampleHelper.php
    ├── tmpl/
    │   └── default.php
    └── media/mod_example/
        ├── joomla.asset.json
        ├── css/
        └── js/
```

### Administrator Module Structure
```
/administrator/modules/
└── mod_example/
    ├── mod_example.xml
    ├── config.xml
    ├── language/en-GB/
    ├── services/
    │   └── provider.php
    ├── src/
    │   ├── Dispatcher/
    │   │   └── Dispatcher.php
    │   └── Helper/
    │       └── ExampleHelper.php
    └── tmpl/
        └── default.php
```

### Module Key Files

#### Manifest (`mod_example.xml`)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<extension type="module" client="site" method="upgrade">
    <name>mod_example</name>
    <author>Vendor</author>
    <version>1.0.0</version>
    <description>MOD_EXAMPLE_DESCRIPTION</description>
    <namespace path="src">Vendor\Module\Example</namespace>
    <files>
        <folder>language</folder>
        <folder>services</folder>
        <folder>src</folder>
        <folder>tmpl</folder>
    </files>
    <media destination="mod_example" folder="media">
        <folder>css</folder>
        <folder>js</folder>
        <filename>joomla.asset.json</filename>
    </media>
</extension>
```

> **IMPORTANT:** Configuration parameters are defined in a separate `config.xml` file, NOT in the manifest XML.

#### Config (`config.xml`)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<config>
    <fields name="params">
        <fieldset name="basic">
        </fieldset>
    </fields>
</config>
```

#### Service Provider (`services/provider.php`)
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

#### Dispatcher (`src/Dispatcher/Dispatcher.php`)
```php
<?php

namespace Vendor\Module\Example\Dispatcher;

defined('_JEXEC') or die;

use Joomla\CMS\Dispatcher\AbstractModuleDispatcher;
use Joomla\CMS\Helper\HelperFactoryAwareInterface;
use Joomla\CMS\Helper\HelperFactoryAwareTrait;

class Dispatcher extends AbstractModuleDispatcher implements HelperFactoryAwareInterface
{
    use HelperFactoryAwareTrait;

    protected function getLayoutData(): array
    {
        $data = parent::getLayoutData();
        $helper = $this->getHelperFactory()->getHelper('ExampleHelper');

        $data['items'] = $helper->getItems($data['params'], $this->getApplication());

        return $data;
    }
}
```

#### Helper (`src/Helper/ExampleHelper.php`)
```php
<?php

namespace Vendor\Module\Example\Helper;

defined('_JEXEC') or die;

use Joomla\CMS\Application\CMSApplicationInterface;
use Joomla\Registry\Registry;

class ExampleHelper
{
    public function getItems(Registry $params, CMSApplicationInterface $app): array
    {
        // Business logic here
        return [];
    }
}
```

### Module Design Patterns

1. **Dispatcher Pattern**: All business logic is delegated through the Dispatcher, which calls Helper classes
2. **Helper Factory**: Helpers are instantiated via HelperFactory DI, not static calls
3. **No direct database access in Dispatcher**: Database queries belong in Helper classes
4. **Template data**: Pass data to templates via `getLayoutData()` return array
5. **Parameters**: Access module params via `$data['params']` in templates, `$params` argument in helpers
6. **Application access**: Use `$this->getApplication()` in Dispatcher, pass as argument to helpers

### Module Preferences
- Keep helper methods focused and testable
- Use the module's media folder for assets with Web Asset Manager
- Language constants follow `MOD_EXAMPLE_` prefix convention
- For admin modules, use `client="administrator"` in manifest

## Joomla 5 Component Structure

### Component Directory and File Structure - Administrator and Site
```
/
├── administrator/
│   ├── components/com_example/
│   │   ├── example.xml            ← Component manifest (NOT com_example.xml)
│   │   ├── config.xml
│   │   ├── access.xml
│   │   ├── forms
│   │   ├── language/en-GB/
│   │   ├── services/
│   │   │   └── provider.php
│   │   ├── sql/
│   │   ├── src/
│   │   │   ├── Controller/
│   │   │   ├── Event/
│   │   │   ├── Extension/
│   │   │   ├── Model/
│   │   │   ├── View/
│   │   │   ├── Service/
│   │   │   ├── Table/
│   │   │   └── Helper
│   │   └── tmpl/
├── components/com_example/
│   ├── forms
│   ├── language/en-GB/
│   ├── src/
│   │   ├── Controller/
│   │   ├── Helper/
│   │   ├── Layouts/
│   │   ├── Model/├
│   │   ├── Service/
│   │   │   └── Router.php
│   │   └── View/
│   └── tmpl/
└── media/com_example/
    ├── joomla.asset.json 
    ├── css/ 
    └── js/
```

### Component Directory and File Structure - Administrator Only
```
/
└── administrator/
    └── components/com_example/
        ├── example.xml            ← Component manifest (NOT com_example.xml)
        ├── config.xml
        ├── access.xml
        ├── forms
        ├── language/en-GB/
        ├── services/
        │   └── provider.php
        ├── sql/
        ├── src/
        │   ├── Controller
        │   ├── Event
        │   ├── Extension
        │   ├── Model
        │   ├── View/
        │   ├── Table
        │   └── Helper
        └── tmpl/
```

### Component Key Files
- `/extension_name.xml` - Component manifest (e.g. `forum.xml` for `com_forum`, **NOT** `com_forum.xml`). Defines version, namespace, file declarations only.
- `/config.xml` - Configuration parameters (NOT in the manifest XML)
- `/access.xml` - ACL action definitions
- `/services/provider.php` - Service provider for dependency injection
- `/src/Extension/extension_nameComponent.php` - Main extension class (must expose `getContainer()` for service resolution — see `joomla5-di-patterns.md`)
- `/language` - Language files are installed within the component.
- `/tmpl` - Template files are at the same level as `/src` — **NOT** a subdirectory of `/View`.

### View Conventions (Administrator and Site)
Views extend `HtmlView`. **CRITICAL**: Use direct model calls, NOT the deprecated `$this->get()` magic method (deprecated 5.3.0, removed 7.0):
```php
// WRONG (deprecated)
$this->items = $this->get('Items');
$this->pagination = $this->get('Pagination');
$this->state = $this->get('State');
$this->form = $this->get('Form');

// CORRECT — get model instance, call methods directly
$model = $this->getModel();
$this->items = $model->getItems();
$this->pagination = $model->getPagination();
$this->state = $model->getState();
$this->form = $model->getForm();
```

### Hierarchical List Views (Nested/Tree Display)

For entities with parent-child relationships (e.g., categories, boards), the admin list view should display items in tree order with indentation. This requires:

**ListModel** — Order by `lft` and select `level`:
```php
protected function populateState($ordering = 'a.lft', $direction = 'asc')
{
    parent::populateState($ordering, $direction);
}

// In getListQuery(), include level and lft in the SELECT:
$db->quoteName('a.level'),
$db->quoteName('a.lft'),

// Fallback ordering:
$orderCol = $this->state->get('list.ordering', 'a.lft');
```

**Template** — Render indentation before the title using the `level` property:
```php
<td>
    <?php echo str_repeat('<span class="gi">&mdash;</span>', (int) $item->level); ?>
    <a href="<?php echo Route::_('index.php?option=com_example&task=item.edit&id=' . (int) $item->id); ?>">
        <?php echo $this->escape($item->title); ?>
    </a>
</td>
```

**AdminModel** — Trigger nested set rebuild on save:
```php
public function save($data): bool
{
    if (!parent::save($data)) {
        return false;
    }

    // Rebuild the nested set tree so lft/rgt/level stay current.
    $container = Factory::getContainer();
    if ($container->has(EntityService::class)) {
        $container->get(EntityService::class)->rebuildNestedSet();
    }

    return true;
}
```

**Form XML** — The parent field must use `type="sql"` to dynamically populate:
```xml
<field
    name="parent_id"
    type="sql"
    label="COM_EXAMPLE_FIELD_PARENT_LABEL"
    query="SELECT id AS value, title AS text FROM #__example_items WHERE state = 1 ORDER BY title ASC"
    key_field="value"
    value_field="text"
>
    <option value="0">COM_EXAMPLE_FIELD_PARENT_ROOT</option>
</field>
```

**Edit/Form views MUST load the form validator** via Web Asset Manager. Without this, toolbar Save/Apply buttons fail with JS error `document.formvalidator is undefined`:
```php
public function display($tpl = null): void
{
    $model       = $this->getModel();
    $this->form  = $model->getForm();
    $this->item  = $model->getItem();
    $this->state = $model->getState();

    $this->addToolbar();

    // REQUIRED when template <form> has class="form-validate"
    $this->document->getWebAssetManager()->useScript('form.validate');

    parent::display($tpl);
}
```
## Joomla 5 CLI Console Command Structure

### CLI Command Location Within a Component
```
/administrator/components/com_example/
└── src/
    └── Console/
        ├── ExampleImportCommand.php
        └── ExampleExportCommand.php
```

### Standalone CLI Plugin Structure
```
/plugins/console/example/
├── example.xml
├── language/en-GB/
│   ├── plg_console_example.ini
│   └── plg_console_example.sys.ini
├── services/
│   └── provider.php
└── src/
    └── Extension/
        └── ExampleConsolePlugin.php
    └── Console/
        └── ExampleCommand.php
```

### CLI Command Key Files

#### Command Class (extends AbstractCommand)
```php
<?php

namespace Vendor\Component\Example\Administrator\Console;

defined('_JEXEC') or die;

use Joomla\CMS\Factory;
use Joomla\Console\Command\AbstractCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

class ExampleImportCommand extends AbstractCommand
{
    protected static $defaultName = 'example:import';

    protected function configure(): void
    {
        $this->setDescription('Import example data from a CSV file');
        $this->setHelp('This command imports data from a specified CSV file into the example component.');

        $this->addArgument(
            'file',
            InputArgument::REQUIRED,
            'Path to the CSV file to import'
        );

        $this->addOption(
            'dry-run',
            null,
            InputOption::VALUE_NONE,
            'Simulate the import without making changes'
        );

        $this->addOption(
            'batch-size',
            'b',
            InputOption::VALUE_REQUIRED,
            'Number of records per batch',
            '100'
        );
    }

    protected function doExecute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        $file = $input->getArgument('file');
        $dryRun = $input->getOption('dry-run');
        $batchSize = (int) $input->getOption('batch-size');

        if (!file_exists($file)) {
            $io->error(sprintf('File not found: %s', $file));
            return Command::FAILURE;
        }

        $io->title('Example Data Import');

        if ($dryRun) {
            $io->warning('Running in dry-run mode. No changes will be made.');
        }

        // Processing with progress bar
        $io->progressStart($totalRecords);

        foreach ($batches as $batch) {
            // Process batch
            $io->progressAdvance($batchSize);
        }

        $io->progressFinish();

        $io->success(sprintf('Successfully imported %d records.', $count));

        return Command::SUCCESS;
    }
}
```

#### Registration via Component Service Provider
```php
// In services/provider.php, register commands in the boot() method
public function boot(ContainerInterface $container): void
{
    // Register CLI commands
    if ($container->has(ConsoleApplication::class)) {
        $app = $container->get(ConsoleApplication::class);
        $app->addCommand(new ExampleImportCommand());
        $app->addCommand(new ExampleExportCommand());
    }
}
```

#### Registration via Console Plugin
```php
<?php

namespace Vendor\Plugin\Console\Example\Extension;

defined('_JEXEC') or die;

use Joomla\Application\ApplicationEvents;
use Joomla\CMS\Plugin\CMSPlugin;
use Joomla\Event\SubscriberInterface;
use Vendor\Plugin\Console\Example\Console\ExampleCommand;

final class ExampleConsolePlugin extends CMSPlugin implements SubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ApplicationEvents::BEFORE_EXECUTE => 'registerCommands',
        ];
    }

    public function registerCommands(): void
    {
        $this->getApplication()->addCommand(new ExampleCommand());
    }
}
```

### CLI Command Conventions

#### Command Naming
- Use colon-separated namespaces: `component:action` (e.g., `example:import`, `example:export`)
- Group related commands under the same prefix
- Use lowercase with hyphens for multi-word actions: `example:clear-cache`

#### Exit Codes
- `Command::SUCCESS` (0) - Command completed successfully
- `Command::FAILURE` (1) - Command failed with an error
- `Command::INVALID` (2) - Invalid input/arguments

#### Output Levels
- Normal output: Always shown
- Verbose (`-v`): Additional details
- Very verbose (`-vv`): Debug-level information
- Debug (`-vvv`): Full trace information

```php
if ($output->isVerbose()) {
    $io->info(sprintf('Processing record %d of %d', $current, $total));
}

if ($output->isVeryVerbose()) {
    $io->writeln(sprintf('  Record data: %s', json_encode($record)));
}
```

#### Progress Indicators
- Use `SymfonyStyle::progressStart/Advance/Finish` for batch operations
- Use `SymfonyStyle::createTable()` for tabular output
- Use `$io->section()` to break up long output

### Task Scheduler Integration
```php
// Register as a Joomla Task Scheduler task type via a task plugin
// Plugin group: task
// Allows CLI commands to be scheduled through Joomla's built-in scheduler
```

### Best Practices
- Always validate input arguments and options early
- Provide meaningful error messages with `$io->error()`
- Support `--dry-run` for destructive operations
- Use progress bars for long-running operations
- Return appropriate exit codes
- Access Joomla services via `Factory::getContainer()->get()`
- Never use `echo` directly; always use Symfony Console output methods

## Joomla 5+ Web Services API structure as part of a Component Structure

### Directory and File Structure for Web Services API application of a component.
```
/
└── api/
    └── components/com_example/
        ├── language/en-GB/
        └── src/
            ├── Controller
            ├── Serializer/
            └── View/
```

### Webservices Plugin Directory and File Structure
```
/plugins/
└── webservices/example/
    ├── example.xml
    ├── language/en-GB/
    ├── services/
    │   └── provider.php
    └── src/
       └── Extension
           └── Example.php
```
### JsonApiView Property Types

The base class `Joomla\CMS\MVC\View\JsonApiView` declares `$fieldsToRenderItem` and
`$fieldsToRenderList` **without** a type declaration. Child classes **MUST NOT** add
the `array` type — PHP forbids adding a type to an untyped parent property.

```php
// CORRECT — no type declaration
protected $fieldsToRenderItem = ['id', 'title', 'state'];
protected $fieldsToRenderList = ['id', 'title'];

// WRONG — will cause a fatal error
protected array $fieldsToRenderItem = ['id', 'title', 'state'];
```

### Component Key Files
- `/language` - Language files are installed within the component.

