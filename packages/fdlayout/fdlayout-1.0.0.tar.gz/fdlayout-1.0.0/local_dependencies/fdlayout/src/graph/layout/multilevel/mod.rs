pub mod iteration;

use super::LayoutAlgorithm;
use crate::graph::{
    layout::{GraphLayoutAttributes, RandomLayout},
    Graph, NodePosition,
};
use rand::{seq::SliceRandom, Rng};
use std::collections::{HashMap, HashSet};

fn place_child_nodes<const D: usize, T: Rng>(
    rng: &mut T,
    level: &LayoutLevel,
    parent_positions: &[NodePosition<D>],
    node_sizes: &[f32],
) -> Vec<NodePosition<D>> {
    let mut placed_nodes: Vec<Option<NodePosition<D>>> = vec![None; level.graph.n_nodes()];
    let link = level.link.as_ref().unwrap();
    let adjacency = level.graph.collect_adjacency();
    for (i_parent, i_first_child) in link.parent_to_first_child.iter().cloned().enumerate() {
        placed_nodes[i_first_child as usize] = Some(parent_positions[i_parent]);
    }

    let randomized_children = {
        let mut v = (0..level.graph.n_nodes() as u32).collect::<Vec<_>>();
        v.shuffle(rng);
        v
    };

    for i_child in randomized_children {
        let i_child = i_child as usize;
        let placement = &mut placed_nodes[i_child];
        if placement.is_none() {
            let neighbors = &adjacency[i_child];
            let mut sum = NodePosition::<D>::zeros();
            let mut parent_set = HashSet::<usize>::new();
            let mut count = 0u32;
            for i_neighbor in neighbors.iter().cloned() {
                if let Some(p) = placed_nodes[i_neighbor as usize].or_else(|| {
                    let i = link.child_to_parent[i_neighbor as usize];
                    if parent_set.insert(i as usize) {
                        Some(parent_positions[i as usize])
                    } else {
                        None
                    }
                }) {
                    sum += p;
                    count += 1;
                }
            }

            let max_offset = 2.0 * node_sizes[i_child];
            let offset_origin = NodePosition::<D>::from_element(max_offset);

            let mut random_offset = NodePosition::<D>::zeros();
            rng.fill(random_offset.as_mut_slice());

            placed_nodes[i_child] =
                Some(sum / count as f32 - 0.5 * offset_origin + max_offset * random_offset);
        }
    }
    placed_nodes.iter().map(|p| p.unwrap()).collect()
}

struct GraphTopology {
    edges: Vec<[u32; 2]>,
    edge_lengths: Vec<f32>,
}

fn build_parent_topology(
    child_adjacency: &[Vec<u32>],
    parent_to_children: &[Vec<u32>],
    child_to_parent: &[u32],
    child_edges: &[[u32; 2]],
    child_edge_lengths: &[f32],
) -> GraphTopology {
    let mut edges = Vec::new();
    let mut edge_lengths = Vec::<(u32, f32)>::new();
    let child_edge_map = {
        let mut m = HashMap::<EdgeKey, u32>::new();
        for (i, edge) in child_edges.iter().cloned().enumerate() {
            m.insert(edge.into(), i as u32);
        }
        m
    };
    let mut parent_edge_map = HashMap::new();

    for (i_parent, i_children) in parent_to_children.iter().enumerate() {
        let i_parent = i_parent as u32;
        for i_child in i_children {
            let i_child = *i_child as usize;
            for i_child_neighbor in &child_adjacency[i_child] {
                let i_parent_neighbor = child_to_parent[*i_child_neighbor as usize];
                if i_parent_neighbor == i_parent {
                    continue;
                }

                let parent_edge_key = EdgeKey::from([i_parent, i_parent_neighbor]);
                let child_edge_length = {
                    let i_child_edge = child_edge_map
                        .get(&EdgeKey::from([i_child as u32, *i_child_neighbor as u32]))
                        .unwrap();
                    child_edge_lengths[*i_child_edge as usize]
                };

                if let Some(i_parent_edge) = parent_edge_map.get(&parent_edge_key) {
                    let l = &mut edge_lengths[*i_parent_edge as usize];
                    l.0 += 1;
                    l.1 += child_edge_length;
                } else {
                    parent_edge_map.insert(parent_edge_key, edges.len() as u32);

                    edges.push(parent_edge_key.0);
                    edge_lengths.push((1, child_edge_length));
                }
            }
        }
    }

    GraphTopology {
        edges,
        edge_lengths: edge_lengths
            .into_iter()
            .map(|(n, v)| v / n as f32)
            .collect(),
    }
}

#[derive(Hash, PartialEq, Eq, Clone, Copy)]
struct EdgeKey([u32; 2]);
impl From<[u32; 2]> for EdgeKey {
    fn from([a, b]: [u32; 2]) -> Self {
        Self(if a < b { [a, b] } else { [b, a] })
    }
}

#[derive(Debug)]
struct LevelLink {
    child_to_parent: Vec<u32>,
    parent_to_first_child: Vec<u32>,
}

pub struct LayoutLevel {
    graph: Graph,
    weights: Vec<u32>,
    link: Option<LevelLink>,
    attributes: GraphLayoutAttributes,
}

impl LayoutLevel {
    pub fn graph(&self) -> &Graph {
        &self.graph
    }

    pub fn child_to_parent(&self) -> Option<&[u32]> {
        self.link.as_ref().map(|l| l.child_to_parent.as_slice())
    }

    pub fn attributes(&self) -> &GraphLayoutAttributes {
        &self.attributes
    }
}

#[derive(Default)]
pub struct MultilevelLayout {
    levels: Vec<LayoutLevel>,
}

impl MultilevelLayout {
    fn build_recursive<T: Rng>(
        &mut self,
        rng: &mut T,
        graph: Graph,
        weights: Vec<u32>,
        attributes: GraphLayoutAttributes,
    ) {
        {
            let n_nodes = graph.n_nodes();
            self.levels.push(LayoutLevel {
                graph,
                weights,
                attributes,
                link: None,
            });

            if n_nodes < 3 {
                return;
            }
        }

        let prev = self.levels.last_mut().unwrap();

        let mut node_markings = vec![false; prev.graph.n_nodes()];

        let edges = prev
            .graph
            .edges()
            .iter()
            .cloned()
            .enumerate()
            .collect::<Vec<_>>();

        macro_rules! randomize {
            ($vec:expr) => {{
                let mut t = $vec.clone();
                t.shuffle(rng);
                t
            }};
        }

        let mut primary_merges = Vec::<usize>::new();
        let mut edge_stash = Vec::<usize>::new();
        for (i, [a, b]) in randomize!(edges) {
            if !node_markings[a as usize] && !node_markings[b as usize] {
                node_markings[a as usize] = true;
                node_markings[b as usize] = true;
                primary_merges.push(i);
            } else {
                edge_stash.push(i);
            }
        }

        let mut secondary_merges = Vec::<usize>::new();
        for (i, [a, b]) in randomize!(edge_stash).iter().map(|i| edges[*i]) {
            if !node_markings[a as usize] || !node_markings[b as usize] {
                node_markings[a as usize] = true;
                node_markings[b as usize] = true;
                secondary_merges.push(i);
            }
        }

        assert!(node_markings.iter().all(|marked| *marked));

        let mut parent_to_children = Vec::<Vec<u32>>::new();
        let mut child_to_parent: Vec<Option<u32>> = vec![None; prev.graph.n_nodes()];

        for [a, b] in primary_merges.iter().map(|i| prev.graph.edges()[*i]) {
            let i_parent = parent_to_children.len() as u32;
            child_to_parent[a as usize] = Some(i_parent);
            child_to_parent[b as usize] = Some(i_parent);
            parent_to_children.push(vec![a, b]);
        }

        for [a, b] in secondary_merges.iter().map(|i| prev.graph.edges()[*i]) {
            let (i_parent, i_child) = if let Some(i_parent) = child_to_parent[a as usize] {
                (i_parent, b)
            } else {
                let i_parent = child_to_parent[b as usize].unwrap();
                (i_parent, a)
            };

            child_to_parent[i_child as usize] = Some(i_parent);
            parent_to_children[i_parent as usize].push(i_child);
        }

        let child_to_parent = child_to_parent
            .iter()
            .map(|i| i.unwrap())
            .collect::<Vec<_>>();
        let child_adjacency = prev.graph.collect_adjacency();

        let next_n_nodes = parent_to_children.len();
        if next_n_nodes < 3 {
            return;
        }

        let mut weights = vec![0u32; next_n_nodes];
        let mut node_sizes = vec![0.0; next_n_nodes];

        for (i_parent, i_children) in parent_to_children.iter().enumerate() {
            for i_child in i_children {
                let i_child = *i_child as usize;
                weights[i_parent] += prev.weights[i_child];
                node_sizes[i_parent] = prev.attributes.node_sizes[i_child];
            }
        }

        let parent_topology = build_parent_topology(
            &child_adjacency,
            &parent_to_children,
            &child_to_parent,
            prev.graph.edges(),
            &prev.attributes.edge_lengths,
        );

        for children in &mut parent_to_children {
            children.sort_by(|i, j| {
                child_adjacency[*j as usize]
                    .len()
                    .cmp(&child_adjacency[*i as usize].len())
            });
        }

        prev.link = Some(LevelLink {
            child_to_parent,
            parent_to_first_child: parent_to_children
                .iter_mut()
                .map(|children| {
                    children.sort_by(|i, j| {
                        child_adjacency[*j as usize]
                            .len()
                            .cmp(&child_adjacency[*i as usize].len())
                    });
                    children[0]
                })
                .collect(),
        });

        let next_graph = Graph::new(next_n_nodes as u32, parent_topology.edges).unwrap();
        let next_atts = GraphLayoutAttributes::new(
            &next_graph,
            Some(node_sizes),
            Some(parent_topology.edge_lengths),
        );
        self.build_recursive(rng, next_graph, weights, next_atts);
    }

    pub fn build<T: Rng>(&mut self, rng: &mut T, graph: Graph, attributes: GraphLayoutAttributes) {
        if !self.levels.is_empty() {
            self.levels.clear();
        }
        let weights = vec![1; graph.n_nodes as usize];
        self.build_recursive(rng, graph, weights, attributes);
    }

    pub fn run<const D: usize, T: Rng, A: LayoutAlgorithm<D>>(
        &mut self,
        single_level_algorithm: &mut A,
        rng: &mut T,
        positions: &mut [NodePosition<D>],
    ) {
        assert!(!self.levels.is_empty());
        assert!(self.levels[0].graph.n_nodes == positions.len() as u32);

        let layout = self
            .levels
            .iter()
            .rev()
            .fold::<Option<Vec<NodePosition<D>>>, _>(None, |prev_layout, level| {
                let mut positions = match prev_layout {
                    None => {
                        let mut positions = vec![NodePosition::zeros(); level.graph.n_nodes()];
                        RandomLayout::new(rng, None).run(
                            &level.graph,
                            &mut positions,
                            &level.attributes,
                        );
                        positions
                    }
                    Some(layout) => {
                        place_child_nodes(rng, level, &layout, &level.attributes.node_sizes)
                    }
                };

                single_level_algorithm.run(&level.graph, &mut positions, &level.attributes);

                Some(positions)
            })
            .unwrap();

        positions.copy_from_slice(&layout);
    }

    pub fn levels(&self) -> &[LayoutLevel] {
        &self.levels
    }
}
