import os
import re
from typing import Optional

from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

base_path = os.path.dirname(os.path.abspath(__file__))


def svg_icon():
    return """<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 496 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M165.9 397.4c0 2-2.3 3.6-5.2 3.6-3.3.3-5.6-1.3-5.6-3.6 0-2 2.3-3.6 5.2-3.6 3-.3 5.6 1.3 5.6 3.6zm-31.1-4.5c-.7 2 1.3 4.3 4.3 4.9 2.6 1 5.6 0 6.2-2s-1.3-4.3-4.3-5.2c-2.6-.7-5.5.3-6.2 2.3zm44.2-1.7c-2.9.7-4.9 2.6-4.6 4.9.3 2 2.9 3.3 5.9 2.6 2.9-.7 4.9-2.6 4.6-4.6-.3-1.9-3-3.2-5.9-2.9zM244.8 8C106.1 8 0 113.3 0 252c0 110.9 69.8 205.8 169.5 239.2 12.8 2.3 17.3-5.6 17.3-12.1 0-6.2-.3-40.4-.3-61.4 0 0-70 15-84.7-29.8 0 0-11.4-29.1-27.8-36.6 0 0-22.9-15.7 1.6-15.4 0 0 24.9 2 38.6 25.8 21.9 38.6 58.6 27.5 72.9 20.9 2.3-16 8.8-27.1 16-33.7-55.9-6.2-112.3-14.3-112.3-110.5 0-27.5 7.6-41.3 23.6-58.9-2.6-6.5-11.1-33.3 2.6-67.9 20.9-6.5 69 27 69 27 20-5.6 41.5-8.5 62.8-8.5s42.8 2.9 62.8 8.5c0 0 48.1-33.6 69-27 13.7 34.7 5.2 61.4 2.6 67.9 16 17.7 25.8 31.5 25.8 58.9 0 96.5-58.9 104.2-114.8 110.5 9.2 7.9 17 22.9 17 46.4 0 33.7-.3 75.4-.3 83.6 0 6.5 4.6 14.4 17.3 12.1C428.2 457.8 496 362.9 496 252 496 113.3 383.5 8 244.8 8zM97.2 352.9c-1.3 1-1 3.3.7 5.2 1.6 1.6 3.9 2.3 5.2 1 1.3-1 1-3.3-.7-5.2-1.6-1.6-3.9-2.3-5.2-1zm-10.8-8.1c-.7 1.3.3 2.9 2.3 3.9 1.6 1 3.6.7 4.3-.7.7-1.3-.3-2.9-2.3-3.9-2-.6-3.6-.3-4.3.7zm32.4 35.6c-1.6 1.3-1 4.3 1.3 6.2 2.3 2.3 5.2 2.6 6.5 1 1.3-1.3.7-4.3-1.3-6.2-2.2-2.3-5.2-2.6-6.5-1zm-11.4-14.7c-1.6 1-1.6 3.6 0 5.9 1.6 2.3 4.3 3.3 5.6 2.3 1.6-1.3 1.6-3.9 0-6.2-1.4-2.3-4-3.3-5.6-2z"/></svg>"""


def svg_docs():
    return """<svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512"><!--! Font Awesome Free 6.4.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path d="M249.6 471.5c10.8 3.8 22.4-4.1 22.4-15.5V78.6c0-4.2-1.6-8.4-5-11C247.4 52 202.4 32 144 32C93.5 32 46.3 45.3 18.1 56.1C6.8 60.5 0 71.7 0 83.8V454.1c0 11.9 12.8 20.2 24.1 16.5C55.6 460.1 105.5 448 144 448c33.9 0 79 14 105.6 23.5zm76.8 0C353 462 398.1 448 432 448c38.5 0 88.4 12.1 119.9 22.6c11.3 3.8 24.1-4.6 24.1-16.5V83.8c0-12.1-6.8-23.3-18.1-27.6C529.7 45.3 482.5 32 432 32c-58.4 0-103.4 20-123 35.6c-3.3 2.6-5 6.8-5 11V456c0 11.4 11.7 19.3 22.4 15.5z"/></svg>"""


class GitLinksPlugin(BasePlugin):
    config_scheme = (
        ('show_docs', config_options.Type(bool, default=False)),
        ('target', config_options.Type(str, default="_blank")),
        ('github_host', config_options.Type(str, default="github.com")),
        ('github_docs_host', config_options.Type(str, default="github.io")),
    )

    def create_link(self, config: MkDocsConfig, repo_name):
        return "<div><a target='%s' title='Open Github Project' href='https://%s/%s'><span class='gitlink-icon'>%s</span>%s</a>%s</div>" % (
            self.config['target'], self.config["github_host"], repo_name, svg_icon(), repo_name,
            self.docs_link(repo_name))

    def on_post_page(self, output: str, *, page: Page, config: MkDocsConfig) -> Optional[str]:
        # Define regular expressions for matching the relevant sections of the HTML code
        head_regex = re.compile(r"<head>(.*?)</head>", flags=re.DOTALL)

        # Modify the CSS link
        css_link = f'<link href="{utils.get_relative_url(utils.normalize_url("assets/stylesheets/gitlinks-styles.css"), page.url)}" rel="stylesheet"/>'
        output = head_regex.sub(f"<head>\\1 {css_link}</head>", output)

        return output

    def on_page_content(self, html: str, *, page: Page, config: MkDocsConfig, files: Files) -> Optional[str]:
        search = re.findall("<a.*>github</a>", html)
        for link in search:
            re_search = re.search("href=\".*\"", link)
            repo_name = link[re_search.start() + 6:re_search.end() - 1]
            html = html.replace(link, self.create_link(config, repo_name))
        return html

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        output_base_path = os.path.join(config["site_dir"], "assets")

        css_path = os.path.join(output_base_path, "stylesheets")
        utils.copy_file(
            os.path.join(base_path, "assets", "gitlinks-styles.css"),
            os.path.join(css_path, "gitlinks-styles.css"),
        )

    def docs_link(self, repo_name):
        if not self.config['show_docs']:
            return ""

        split = repo_name.split("/")

        return """ <a target="%s" title="Open Github Pages" href="https://%s.%s/%s"><span class="gitlink-docs-icon">%s</span></a>""" % (
            self.config['target'], split[0], self.config['github_docs_host'], split[1], svg_docs())
