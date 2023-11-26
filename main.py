import argparse
import functools

from graph import Graph


class NoMoreBacktrackingError(ValueError):
    pass


def arg_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--board', help='String representing the board. Four sides should be separated by colons.')
    ap.add_argument('-v', '--verbose', action='store_true', help='More output')
    ap.add_argument('-q', '--quiet', action='store_true', help='Only print comma-separated accepted results')
    ap.add_argument('-Q', '--veryquiet', action='store_true',
                    help='Only print comma-separated accepted results when it is the shortest solution found so far')
    ap.add_argument('-w', '--wordfile', help='Path to file containing valid words')
    ap.add_argument('-i', '--illegals',
                    help='if starts with . or / path to illegal words file, otherwise comma-sep list of illegal words')
    return ap


@functools.lru_cache
def uniqueness(word):
    return len(set(word))


def nullout(*args, **kwargs):
    pass


def find_chain(graph: 'Graph', words: list[str], output=print):
    chain_breakers: set[str] = set()
    chain: list[str] = []
    iterations = 0
    while not graph.satisfied():
        acceptables: list[str] = []
        for word in words:
            unused_letters = ''.join(n.letter for n in graph.nodes.values() if not n.used)
            first_letter = chain[-1][-1] if chain else None
            if graph.accepts(word, starting=first_letter, remaining=unused_letters) and word not in chain_breakers:
                acceptables.append(word)

        acceptables.sort(key=lambda w: (-len(w) * iterations / 10) + uniqueness(w) + graph.word_priority(w))

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
                    graph.nodes[letter].prioritize()
        else:
            candidate = acceptables.pop()
            output("Testing highest priority word: {}...".format(candidate))
            # for letter in candidate:
            #     graph.nodes[letter].used = True
            #     graph.nodes[letter].deprioritize()
            for node in graph.nodes.values():
                if node.letter not in candidate:
                    node.prioritize()
                else:
                    node.deprioritize()
                    node.used = True
            chain.append(candidate)
        iterations += 1

    output("\nSOLVED! Chain is '{}'".format('->'.join(chain)))
    output("Trying to optimize...")
    output('Optimizing chain start...')
    if all(i in ''.join(i for i in chain[1:]) for i in chain[0]):
        output("dropped first word")
        chain = chain[1:]
    output("\nChain is now '{}'".format('->'.join(chain)))
    return chain


def interactive():
    board = input("Enter the board: ")
    wordfile = input("Enter file for words: ")
    illegals = input("Enter illegal words or path to file: ")
    verbose = input("Verbose (y/n)? ")

    graph = Graph.fromstring(board)
    if illegals:
        if illegals.startswith('.') or illegals.startswith('/'):
            with open(illegals) as f:
                illegal = set(i.strip() for i in f)
        else:
            illegal = set(i.strip() for i in illegals.split(','))
    else:
        illegal = set()

    with open(wordfile) as f:
        words = [i.strip() for i in f if i not in illegal]

    return graph, words, argparse.Namespace(verbose=verbose.strip().lower().startswith('y'), quiet=False,
                                            veryquiet=False)


def construct():
    parser = arg_parser()
    args = parser.parse_args()

    get_args = [i[1] for i in args._get_kwargs()]
    if not any(get_args):
        return interactive()

    if args.veryquiet:
        args.quiet = True

    if args.verbose and (args.quiet or args.veryquiet):
        parser.error("Invalid combination of output specifiers: verbose and quiet")

    if not args.board:
        parser.error("Must specify board in CMD line arguments")

    if not args.wordfile:
        parser.error("Must specify word file")

    graph = Graph.fromstring(args.board)

    if args.illegals:
        if args.illegals.startswith('.') or args.illegals.startswith('/'):
            with open(args.illegals) as f:
                illegal = set(i.strip() for i in f)
        else:
            illegal = set(i.strip() for i in args.illegals.split(','))
    else:
        illegal = set()

    with open(args.wordfile) as f:
        words = [i.strip() for i in f if i not in illegal]

    return graph, words, args


def main():
    graph, words, args = construct()

    if args.verbose:
        outdev = print
    else:
        outdev = nullout

    shortest_words = [None] * 100

    while True:
        try:
            chain = find_chain(graph, words, outdev)
            if args.quiet and not args.veryquiet:
                print(','.join(chain))
            elif not args.quiet:
                print("Chain of {}".format(chain))
            # for word in chain:
            #     words.remove(word)
            words.remove(chain[0])
            if len(chain) < len(shortest_words):
                shortest_words = chain
                if not args.quiet and not args.veryquiet:
                    print("SHORTEST WORDS: {}".format(chain))
                elif args.veryquiet:
                    print(','.join(chain))
            graph.reset()
        except NoMoreBacktrackingError:
            break


if __name__ == '__main__':
    raise SystemExit(main())
