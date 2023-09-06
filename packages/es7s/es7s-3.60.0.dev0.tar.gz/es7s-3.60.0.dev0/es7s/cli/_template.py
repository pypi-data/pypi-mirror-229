# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from __future__ import annotations

import re

import pytermor as pt

from es7s.shared import get_logger, get_stdout


class TemplateCommand:
    REGEX_SECTION_START = '\x1b\x1e'
    REGEX_SUBSTITUTE_SEP = '\x1f'

    def __init__(self, filepath: str):
        get_logger().debug(f"Input filepath: '{filepath}'")
        with open(filepath, "rt") as f:
            self._tpl = f.read()
        get_logger().debug(f"Input size: " + pt.format_si_binary(len(self._tpl)))

    def run(self):
        engine = pt.TemplateEngine()
        substituted = engine.substitute(self._tpl)
        rendered = substituted.render(get_stdout().renderer)
        postprocessed = self._postprocess(rendered)

        get_stdout().echo(postprocessed, nl=False)

    def _postprocess(self, rendered: str) -> str:
        if self.REGEX_SECTION_START not in rendered:
            return rendered

        rendered, _, preprocessors = rendered.partition(self.REGEX_SECTION_START)
        for pp in preprocessors.splitlines():
            if not pp:
                continue
            sub_args = [*pp.split(self.REGEX_SUBSTITUTE_SEP, 1)]
            if len(sub_args) != 2:
                get_logger().warning(f"Invalid substitute directive: {pp!r}")
                continue
            rendered = re.sub(*sub_args, rendered)

        return rendered
