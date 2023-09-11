from . import layout as layout_core
import networkx as nx
import numpy as np
from numpy._typing import NDArray


def layout(graph: nx.Graph) -> dict[int, NDArray]:
    n_nodes = len(graph)
    edges = []
    for u, v in graph.edges():  # type: ignore
        edges.append([u, v])

    positions = [np.asarray(i) for i in zip(*layout_core(n_nodes, edges))]

    return dict(zip(range(n_nodes), positions))
