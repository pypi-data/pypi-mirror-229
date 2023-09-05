![Community-Project](https://gitlab.com/softbutterfly/open-source/open-source-office/-/raw/master/banners/softbutterfly-open-source--banner--community-project.png)

![PyPI - Supported versions](https://img.shields.io/pypi/pyversions/wagtail-sb-structblock)
![PyPI - Package version](https://img.shields.io/pypi/v/wagtail-sb-structblock)
![PyPI - Downloads](https://img.shields.io/pypi/dm/wagtail-sb-structblock)
![PyPI - MIT License](https://img.shields.io/pypi/l/wagtail-sb-structblock)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/00f3debb1fa94a51894b03ec2273fafa)](https://app.codacy.com/gl/softbutterfly/wagtail-sb-structblock/dashboard?utm_source=gl&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/00f3debb1fa94a51894b03ec2273fafa)](https://app.codacy.com/gl/softbutterfly/wagtail-sb-structblock/dashboard?utm_source=gl&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

# Wagtail SB Struct Block

Wagtail package to render render struct block with a tabbed interface to
distinguish between content fields an settings fields in struct blocks.

## Requirements

- Python 3.8.1 or higher
- Wagtail 3.0 or higher
- Django 3.2 or higher

## Install

```bash
pip install wagtail-sb-structblock
```

## Usage

Add `wagtail_sb_structblock` to your `INSTALLED_APPS` settings

```python
INSTALLED_APPS = [
  # ...
  "wagtail_sb_structblock",
  # ...
]
```

In your struct blocks must inherith from `StructBlock` and you must specify
the `settings_fields` ub your `Meta` class.

```python
from wagtail.blocks import StructBlock
from wagtail_sb_structblock.blocks import StructBlock

class EnhancedHTMLBlock(StructBlock):
    text = CharBlock()

    html_attrs = CharBlock()

    class Meta:
        settings_fields = [
            "html_attrs",
        ]
```

Include it in your stream file and your model so you can use a tabed interface
for your struct block.

![content tab](https://gitlab.com/softbutterfly/open-source/wagtail-sb-structblock/-/raw/master/_assets/content_tab.png)

![settings tab](https://gitlab.com/softbutterfly/open-source/wagtail-sb-structblock/-/raw/master/_assets/settings_tab.png)

## Docs

- [Ejemplos](https://gitlab.com/softbutterfly/open-source/wagtail-sb-structblock/-/wikis)
- [Wiki](https://gitlab.com/softbutterfly/open-source/wagtail-sb-structblock/-/wikis)

## Changelog

All changes to versions of this library are listed in the [change history](CHANGELOG.md).

## Development

Check out our [contribution guide](CONTRIBUTING.md).

## Contributors

See the list of contributors [here](https://gitlab.com/softbutterfly/open-source/wagtail-sb-structblock/-/graphs/develop).
