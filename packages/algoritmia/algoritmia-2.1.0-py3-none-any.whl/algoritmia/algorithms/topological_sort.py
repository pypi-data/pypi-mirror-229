from collections.abc import Iterator
from collections import deque
from algoritmia.datastructures.graphs import Digraph, TVertex

# Ordenación topológica de un digrafo acíclico
# Si el grafo tiene algún ciclo, el algoritmo lanza una excepción
def topological_sort(g: Digraph[TVertex]) -> deque[TVertex]:
    def traverse_from(v: TVertex, used: set[TVertex]):
        seen.add(v)
        for suc_v in g.succs(v):
            if suc_v in used:   # Cycle detection
                raise Exception("The graph has at least one cycle")
            used.add(suc_v)     # Cycle detection
            if suc_v not in seen:
                yield from traverse_from(suc_v, used)
            used.remove(suc_v)  # Cycle detection
        yield v

    lv = []
    seen = set()
    for v in g.V:
        if len(g.preds(v)) == 0:
            lv.extend(traverse_from(v, set()))
    lv.reverse()
    return lv

def topological_sort2(g: Digraph[TVertex]) -> list[TVertex]:
    def traverse_from(v: TVertex, used) -> Iterator[TVertex]:
        if v not in seen:
            seen.add(v)
            if v in used:   # Cycle detection
                raise Exception("The graph has at least one cycle")
            used.add(v)     # Cycle detection
            for suc_v in g.succs(v):
                yield from traverse_from(suc_v, used)
            used.remove(v)  # Cycle detection
            yield v

    lv: list[TVertex] = []
    seen = set()
    for v in g.V:
        if len(g.preds(v)) == 0:
            lv.extend(traverse_from(v, set()))
    lv.reverse()
    return lv


if __name__ == '__main__':
    edges = [('C', 'C++'), ('C', 'Java'), ('C', 'Objective-C'), ('C', 'C#'),
             ('C++', 'Java'), ('C++', 'C#'), ('Java', 'C#'),
             ('MT', 'Haskell'), ('Haskell', 'C#')]
    my_graph = Digraph(E=edges)
    print(topological_sort(my_graph))
