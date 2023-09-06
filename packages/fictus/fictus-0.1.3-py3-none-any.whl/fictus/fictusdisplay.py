from __future__ import annotations

import os
import re
import sys
from typing import List, Set, Optional

from .fictusfilesystem import FictusFileSystem
from .constants import PIPE, SPACER_PREFIX, ELBOW, TEE, SPACER
from .data import Data
from .file import File
from .folder import Folder
from .renderer import Renderer, defaultRenderer

pattern = re.compile(r"[^\\]")


class FictusDisplay:
    def __init__(self, ffs: FictusFileSystem):
        self._ffs = ffs
        self._renderer = defaultRenderer
        self._ignore: Set[int] = set()

    def set_renderer(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def _display_node(self, node: Data) -> str:
        """
        Bookkeeping of nested node depth, node siblings, and order in the queue are
        used to present the FicusSystem in an aesthetic way.
        """

        parts = [PIPE + SPACER_PREFIX for _ in range(node.level)]
        for index in self._ignore:
            if len(parts) > index - 1:
                parts[index - 1] = SPACER + SPACER_PREFIX

        if parts:
            parts[-1] = ELBOW if node.last is True else TEE

        is_file = isinstance(node, File)
        file_open = self._renderer.file_open if is_file else self._renderer.folder_open
        file_close = (
            self._renderer.file_close if is_file else self._renderer.folder_close
        )

        # checking for Folder type
        end = "\\" if not is_file else ""

        return f'{"".join(parts)}{file_open}{node.name}{file_close}{end}'

    @staticmethod
    def _pprint_header(header: str) -> int:
        """Writes the CWD to stdout with forward slashes and its length."""

        parts = header.split(os.sep)
        if len(parts) <= 1:
            # when _root is passed in
            return 0

        header = f"\\".join(parts[:-1])
        sys.stdout.write(f"{header}\\\n")
        return header[:-1].rfind("\\") + 1  # one past found

    def pprint(self, renderer: Optional[Renderer] = None) -> None:
        """Displays the file system structure to stdout."""

        node = self._ffs.current()
        node.last = True
        self._ignore = {i for i in range(node.level)}
        header_length = self._pprint_header(self._ffs.cwd())

        prefix: int = -1  # not set
        buffer: List[str] = [self._renderer.doc_open]

        q: List[Data] = [node]
        while q:
            node = q.pop()
            if node.last is False:
                if node.level in self._ignore:
                    self._ignore.remove(node.level)
            line = self._display_node(node)

            # This needs to happen only once and applied
            # thereafter to each subsequent line.
            prefix = len(line) - len(line.lstrip()) if prefix == -1 else prefix

            buffer.append(f"{header_length * SPACER}{line[prefix:]}\n")

            if node.last is True:
                # track nodes without children.
                self._ignore.add(node.level)

            if isinstance(node, Folder):
                q += node.contents()

            # clear flag for next run
            node.last = False
        buffer.append(self._renderer.doc_close)

        sys.stdout.writelines(buffer)
