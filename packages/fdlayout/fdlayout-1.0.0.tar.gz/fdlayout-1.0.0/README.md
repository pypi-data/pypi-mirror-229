# fdlayout

Python library for creating force-directed graph layouts.

## Usage

```python
import fdlayout.networkx as fd
import networkx as nx

g = nx.generators.karate_club_graph()
nx.drawing.draw(g, pos=fd.layout(g))
```
