# Search helper

User-configurable, cross-platform Python script using a Tk GUI
for opening predefined search URLs in the web browser.


## Prerequisites

* Python 3.8 or greater
* [serializable-trees](https://pypi.org/project/serializable-trees/)
    * transitive dependency: [PyYAML](https://pypi.org/project/PyYAML/)


## Invocation

Choose the configuration file via a dialog:

```
python -m search_helper
```

Use a configuration file:

```
python -m search_helper configfile.yaml
```


## User interface

![UI on Windows using example.yaml](./docs/examples/example-screenshot.png)

When you have entered a search string, you can open it in the selected
category or categories using the "Open" button or the **Return** key.
This will open the URLs of each category in webbrowser tabs.
If possible, each category is opened in a separate browser window.

The first up to 12 category selections can be toggled using the function keys
as displayed (**F1** through **F12** from top down).

Pressing **Escape** or clicking the "Quit" button exits the program.

You can delete the search term by pressing **Ctrl-D** or by clicking
the "Clear" button. **Ctrl-X** will copy the search term to the clipboard
and then clear the search term entry field.

For single-URL categories, the "Copy URL" button will copy a URL
(which is generated from the search term in combination with the category
written before the button) to the clipboard.

Categories with multiple URLs have a "List URL names" button instead.
Clicking on that button will open a popup window containing a list of all
URL names/identifiers that belong to the category written before the button.

Other key combinations selecting multiple categories can be configured
in the configuration files. In the example above
(which uses [example.yaml](./docs/examples/example.yaml)), that is **Ctrl-Shift-A**
selecting the first and third category.


## Configuration files

The configuration file can be in YAML or JSON format.
It contains a data structure as described in
[config\_file\_structure.md](./docs/config_file_structure.md).
