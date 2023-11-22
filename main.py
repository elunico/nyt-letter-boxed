import functools

from graph import Graph


class NoMoreBacktrackingError(ValueError):
    pass


@functools.lru_cache
def uniqueness(word):
    return len(set(word))

def nullout(*args, **kwargs):
    pass

def main():
    # graph = Graph.fromstring('jcp:aoe:irh:fbt')
    graph = Graph.fromstring('ath:rpi:eou:flg')

    with open('/usr/share/dict/words') as f:
        words = [i.strip().lower() for i in f]

    with open('./invalid-words.txt') as f:
        illegal = [i.strip() for i in f]

    for i in illegal:
        words.remove(i)

    shortest_words = [None] * 100
    shortest_count = None
    shortest_both = None

    while True:
        try:
            chain = find_chain(graph, words, nullout)
            print("Chain of {}".format(chain))
            for word in chain:
                words.remove(word)
            if len(chain) < len(shortest_words):
                shortest_words = chain
                print("SHORTEST WORDS: {}".format(chain))
            graph.reset()
        except NoMoreBacktrackingError:
            break



def find_chain(graph, words, output=print):
    chain_breakers: set[str] = set()
    chain: list[str] = []
    while not graph.satisfied():
        acceptables: list[str] = []
        for word in words:
            unused_letters = ''.join(n.letter for n in graph.nodes.values() if not n.used)
            first_letter = chain[-1][-1] if len(chain) > 0 else None
            if graph.accepts(word, starting=first_letter, remaining=unused_letters) and word not in chain_breakers:
                acceptables.append(word)

        acceptables.sort(key=lambda w: uniqueness(w) + graph.word_priority(w))

        if not acceptables and not chain:
            raise NoMoreBacktrackingError("No solution found! ")
        elif not acceptables:
            # acceptable words must contain at least 1 unused letter
            # if no words do we backtrack because we do not want to add words
            # to the chain that only use already used letters—that makes no progress
            backer = chain.pop()
            output("Backtracking... removing {}".format(backer))
            chain_breakers.add(backer)
            for letter in backer:
                if not any(letter in w for w in chain):
                    graph.nodes[letter].used = False
                    graph.nodes[letter].more_important()
        else:
            candidate = acceptables.pop()
            output("Testing highest priority word: {}...".format(candidate))
            # if candidate in chain_breakers:
            #     output("Chainbreaker! restarting...")
            #     continue
            for letter in candidate:
                graph.nodes[letter].used = True
                graph.nodes[letter].less_important()
            for node in graph.nodes.values():
                if node.letter not in candidate:
                    node.more_important()
            chain.append(candidate)
    output("\nSOLVED! Chain is '{}'".format('->'.join(chain)))
    output("Trying to optimize...")
    output('Optimizing chain start...')
    if all(i in ''.join(i for i in chain[1:]) for i in chain[0]):
        output("dropped first word")
        chain = chain[1:]
    output("\nChain is now '{}'".format('->'.join(chain)))
    return chain


if __name__ == '__main__':
    raise SystemExit(main())
