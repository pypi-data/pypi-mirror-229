# MkDocs Embed Markdown Plugin

[![MIT license][license-image]][license-url]

[license-image]: https://img.shields.io/badge/License-MIT-blue.svg
[license-url]: https://mit-license.org/

## About

Fork from [MkDocs Embed External Markdown Plugin](https://github.com/fire1ce/mkdocs-embed-external-markdown) and fix the conflict with mkdocs-macros plugin and support access of Gitea private repo by token. The basic functionality is the same as the original plugin. But when rendering markdown, it search the opening tag (@include) in the whole text and replace it with the content of the included file.

## Installation

Install the package with pip:

```shell
pip install mkdocs-embed-markdown
```

## Configuration

Enable the plugin in your `mkdocs.yml` file:

```yaml
plugins:
  - external-markdown
```

## Compatibility with Github/Gitea Private Repository

If the GH_TOKEN environment variable is set with an authorized personal access token then the authorization header will be added to the request and content from private repositories can be fetched.

For Gitea users, the GT_TOKEN environment variable can be used instead. You may need to go to profile > settings > applications > Manage Access Tokens, and add your token to the environment variable. The key is GT_TOKEN, and the value is your token.

## Usage

- Section defined by **"##/###/####..."** header (h2/h3/h4...)
- **"#"** header (h1) will be **removed** from source content so you can use use your own header
- **"##/###/####..."** header (h2/h3/h4...) will be **removed** from source **section** content so you can use use your own header
- Supports multiple **sections** from any source

`@include` requires 2 parameters: **url** and **section name**.

```makrdown
@include('url', '## section name')
```

### Full Markdown Content

Embed full markdown content from a given url, you can use the following example:

```markdown
@include('https://raw.githubusercontent.com/fire1ce/DDNS-Cloudflare-Bash/main/README.md', '')
```

### Specific Section

Embed markdown section from a given url, you can use the following example:

```markdown
@include('https://raw.githubusercontent.com/fire1ce/DDNS-Cloudflare-Bash/main/README.md', '## Installation')
```

## MkDocs Example

The following example shows how to use the plugin in mkdocs project:

````markdown
# Example Page

This is an example page.

## Embedding Multiple Markdown Sections From Different URLs

### First Embedded Section

```markdown
@include('https://raw.githubusercontent.com/mkdocs/mkdocs/master/README.md', '## Features')
```

### Second Embedded Section

```markdown
@include('https://raw.githubusercontent.com/squidfunk/mkdocs-material/master/README.md', '## Quick start')
```
````

Will produce the following page:

![MkDocs Embed External Markdown Plugin](https://user-images.githubusercontent.com/16795594/155761254-17b47e65-d27e-438b-a476-15bd04fdc3ec.jpg)

## Known Issues

- [ ]

## Changelog

See [https://github.com/fire1ce/mkdocs-embed-external-markdown#changelog](https://github.com/fire1ce/mkdocs-embed-external-markdown#changelog)

## License

This project is licensed under the terms of the [MIT License](LICENSE.md).
