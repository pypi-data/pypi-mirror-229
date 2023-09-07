# MKDocs Gitlinks
This is a simple plugin for MKDocs that creates links to git projects easier.

# Usage

To use the plugin you need to set it up

### Config
In the mkdocs.yml add:

```yaml
plugins:
  - mkdocs_gitlinks:
```

### Markdown
Then in the markdown you can link to git projects (currently only Github is supported) by using the syntax below:

```markdown
[github](orginisation/project)
```

For example to link to this project use:

```markdown
[github](umaaz/mkdocs_gitlinks)
```

### Output

The result of this is to change the link to:

![img.png](img.png)


# Options
There are a few options available

```yaml
plugins:
  - mkdocs_gitlinks:
      show_docs: false # setting this to true will include a link to the github pages for the project
      github_host: github.com # this allows for changing the github host name
```
