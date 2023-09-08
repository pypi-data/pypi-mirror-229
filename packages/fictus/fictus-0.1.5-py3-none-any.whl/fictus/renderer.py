from collections import defaultdict
from dataclasses import field, dataclass
from enum import Enum, auto

"""A Renderer is a representation of how a fs should be printed."""


@dataclass
class RenderTags:
    open: str = field(default="")
    close: str = field(default="")


class RenderKeys(Enum):
    DOC = auto()
    FILE = auto()
    FOLDER = auto()


class Renderer:
    """A Renderer provides special instructions for how a fs is displayed."""

    def __init__(self):
        self._tags = defaultdict(RenderTags)

    def register(self, key: RenderKeys, tags: RenderTags):
        self._tags[key] = tags

    def tags(self, key: RenderKeys) -> RenderTags:
        return self._tags[key]


defaultRenderer = Renderer()

markdownRenderer = Renderer()
markdownRenderer.register(
    RenderKeys.DOC, RenderTags('<pre style="line-height:17px">', "</pre>")
)
markdownRenderer.register(
    RenderKeys.FILE, RenderTags('<span style="color:gray">', "</span>")
)


emojiRenderer = Renderer()
emojiRenderer.register(RenderKeys.FILE, RenderTags("📄", ""))
emojiRenderer.register(RenderKeys.FOLDER, RenderTags("📁", ""))
