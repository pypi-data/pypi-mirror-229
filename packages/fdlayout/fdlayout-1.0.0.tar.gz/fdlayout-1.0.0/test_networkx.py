import fdlayout.networkx as fd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

g = nx.generators.karate_club_graph()

fig = plt.figure(figsize=(12, 6))
r = 1
c = 2
i_ax = 0


def ax(title: str):
    global i_ax
    i_ax += 1
    a = fig.add_subplot(r, c, i_ax)
    a.title.set_text(title)
    return a


opt = {
    "node_color": "black",
    "node_size": 100,
    "width": 3,
}

nx.drawing.draw(g, pos=fd.layout(g), ax=ax("fdlayout.layout()"), **opt)
nx.drawing.draw(
    g, pos=nx.layout.spring_layout(g), ax=ax("networkx.spring_layout()"), **opt
)

out_dir = "tmp"
Path(out_dir).mkdir(exist_ok=True, parents=True)
plt.savefig("{}/networkx.png".format(out_dir))
