from __future__ import annotations

import re
import sys
from typing import List, Set, Optional

from .fictusfilesystem import FictusFileSystem
from .constants import PIPE, SPACER_PREFIX, ELBOW, TEE, SPACER
from .data import Data
from .folder import Folder
from .renderer import Renderer, defaultRenderer, RenderTagEnum

pattern = re.compile(r"[^\\]")


class FictusDisplay:
    def __init__(self, ffs: FictusFileSystem):
        self._ffs = ffs
        self._renderer = defaultRenderer
        self._ignore: Set[int] = set()

    @property
    def renderer(self) -> Renderer:
        return self._renderer

    @renderer.setter
    def renderer(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def _wrap_node_name_with_tags(self, node: Data):
        # setup defaults
        key = RenderTagEnum.FILE

        # account for the distinction between root and all other folders
        if isinstance(node, Folder):
            if node == self._ffs.root():
                key = RenderTagEnum.ROOT
            else:
                key = RenderTagEnum.FOLDER

        tags = self.renderer.tags(key)

        return f"{tags.open}{node.name}{tags.close}"

    def _display_node(self, node: Data, node_level_start: int) -> str:
        """
        Bookkeeping of nested node depth, node siblings, and order in the queue are
        used to present the FicusSystem in an aesthetic way.
        """

        parts = [PIPE + SPACER_PREFIX for _ in range(node_level_start, node.level)]
        for index in self._ignore:
            if 0 < len(parts) > index - 1:
                parts[index - 1] = SPACER + SPACER_PREFIX

        if parts:
            parts[-1] = ELBOW if node.last is True else TEE

        return f'{"".join(parts)}{self._wrap_node_name_with_tags(node)}'

    def pprint(self, renderer: Optional[Renderer] = None) -> None:
        """Displays the file system structure to stdout."""

        old_renderer, self._renderer = self._renderer, renderer or self._renderer

        node = self._ffs.current()
        node.last = True
        node_level_start = node.level

        self._ignore = {i for i in range(node.level)}

        prefix: int = -1  # not set

        buffer: List[str] = []

        q: List[Data] = [node]
        while q:
            node = q.pop()
            if node.last is False:
                if node.level in self._ignore:
                    self._ignore.remove(node.level)
            line = self._display_node(node, node_level_start)

            # This needs to happen only once and applied
            # thereafter to each subsequent line.
            prefix = len(line) - len(line.lstrip()) if prefix == -1 else prefix

            buffer.append(f"{line[prefix:]}\n")
            if node.last is True:
                # track nodes without children.
                self._ignore.add(node.level)

            if isinstance(node, Folder):
                q += node.contents()

            # clear flag for next run
            node.last = False

        # output data
        sys.stdout.write(self._renderer.tags(RenderTagEnum.DOC).open)
        sys.stdout.writelines(buffer)
        sys.stdout.write(self._renderer.tags(RenderTagEnum.DOC).close)

        # reset renderer to what it was
        self._renderer = old_renderer
