from typing import Optional

def layout(
    n_nodes: int,
    edges: list[tuple[int, int]],
    lengths: Optional[list[float]] = None,
    random_seed: Optional[int] = None,
) -> tuple[list[float], list[float]]:
    """Execute 2D force-directed layout"""
