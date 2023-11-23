class Node:
    def __init__(self, letter: str) -> None:
        self.letter: str = letter
        self.connections: 'list[Node]' = []
        self.priority: int = 1
        self.used: bool = False

    def prioritize(self):
        self.priority += 10  # priority is 10x more important than length

    def deprioritize(self):
        self.priority -= 10  # priority is 10x more important than length

    def connect(self, other: 'Node'):
        self.connections.append(other)

    def reset(self):
        self.priority = 1
        self.used = False

    def __str__(self) -> str:
        return 'Node({})[{}]'.format(self.letter, ', '.join(i.letter for i in self.connections))

    def __repr__(self) -> str:
        return str(self)
