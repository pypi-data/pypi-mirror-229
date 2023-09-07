import os.path
from typing import Set, Optional

from fictus.data import Data

from .fictusexception import FictusException
from .file import File
from .folder import Folder


DEFAULT_ROOT_NAME = "\\"


class FictusFileSystem:
    """
    A FictusFileSystem (FFS) simulates the creation and traversal of a file system.
    The FFS allows for the creation and removal of files and folders,
    """

    def __init__(self, name=DEFAULT_ROOT_NAME) -> None:
        self._root: Folder = Folder(name)
        self._current: Folder = self._root

    def current(self) -> Folder:
        return self._current

    @staticmethod
    def _normalize(path: str) -> str:
        return os.path.normpath(path.replace(DEFAULT_ROOT_NAME, "/"))

    def mkdir(self, path: str) -> None:
        """Takes a string of a normalized relative to cwd and adds the directories
        one at a time."""
        if not path:
            raise FictusException("A Folder must contain a non-empty string.")

        # hold onto the current directory
        current = self._current

        normalized_path = self._normalize(path)
        if normalized_path.startswith(os.sep):
            self._to_root()

        folders = {d.name: d for d in self._current.folders()}

        for part in normalized_path.split(os.sep):
            if not part:
                continue

            if part not in folders:
                folders[part] = Folder(part)
                self._current.folder(folders[part])

            self.cd(folders[part].name)
            folders = {d.name: d for d in self._current.folders()}

        # return to starting directory
        self._current = current

    def mkfile(self, *files: str) -> None:
        """Takes one or more filenames and adds them to the cwd."""
        visited: Set[str] = {f.name for f in self._current.files()}
        for file in files:
            if not file:
                raise FictusException("A File must contain a non-empty string.")

            if file not in visited:
                visited.add(file)
                self._current.file(File(file))

    def rename(self, old: str, new: str) -> None:
        """Renames a File or Folder based on its name."""
        for content in self._current.contents():
            if content.name == old:
                content.name = new
                break

    def cwd(self) -> str:
        """Prints the current working directory."""
        r = []

        node: Optional[Data] = self._current
        while node is not None:
            r.append(node.name)
            node = node.parent

        return f"{os.sep}".join(reversed(r))

    def _to_root(self) -> None:
        self._current = self._root

    def cd(self, path: str) -> None:
        """Takes a string of a normalized relative to cwd and changes the current"""
        # Return to the current dir if something goes wrong
        current = self._current

        normalized_path = self._normalize(path)
        if normalized_path.startswith(os.sep):
            self._to_root()

        for index, part in enumerate(normalized_path.split(os.sep)):
            if not part:
                continue

            if index == 0 and part == self._root.name:
                self._to_root()
                continue

            if part == "..":
                # looking at the parent here, so ensure its valid.
                parent = self._current.parent

                if parent is None or isinstance(parent, Folder) is False:
                    self._current = current
                    raise FictusException(
                        f"Could not path to {normalized_path} from {self.cwd()}."
                    )

                self._current = parent

            else:
                hm = {f.name: f for f in self._current.folders()}
                if part not in hm:
                    self._current = current
                    raise FictusException(
                        f"Could not path to {normalized_path} from {self.cwd()}."
                    )
                self._current = hm[part]

        return None
