from typing import Optional

from tecoradors import stringable

from node import Node


@stringable
class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}

    def create(self, ltr: str):
        self.nodes[ltr] = Node(ltr)

    def reset(self):
        for node in self.nodes.values():
            node.reset()

    def satisfied(self):
        return all(i.used for i in self.nodes.values())

    def is_connected(self, ltr1: str, ltr2: str) -> bool:
        return self.nodes[ltr2] in self.nodes[ltr1].connections

    def connect(self, ltr1: str, ltr2: str):
        self.nodes[ltr1].connect(self.nodes[ltr2])

    def word_priority(self, word):
        try:
            return sum(self.nodes[l].priority for l in word)
        except KeyError:
            print(word)
            raise

    def accepts(self, word: str, index: int = 0, starting: Optional[str] = None,
                remaining: Optional[str] = None) -> bool:
        def connected(word, index=0, starting=None, remaining=None):
            if starting is not None and word[0] != starting:
                return False
            if index >= len(word) - 1:
                return True

            i, j = word[index], word[index + 1]

            if i not in self.nodes or j not in self.nodes:
                return False

            ok = self.is_connected(i, j)
            return ok and connected(word, index + 1, starting, remaining)

        satisfactory = any(remaining is None or i in remaining for i in word)
        return satisfactory and connected(word, index, starting, remaining)

    @classmethod
    def fromboard(cls, board: list[list[str]]) -> 'Graph':
        graph = cls()
        for side in board:
            for letter in side:
                graph.create(letter)

        for index, side in enumerate(board):
            for other_index, other_side in enumerate(board):
                if other_index == index:
                    continue
                for letter in side:
                    for other in other_side:
                        graph.connect(letter.lower(), other.lower())

        return graph

    @classmethod
    def fromstring(cls, string: str) -> 'Graph':
        return cls.fromboard([[j for j in i] for i in string.split(':')])
