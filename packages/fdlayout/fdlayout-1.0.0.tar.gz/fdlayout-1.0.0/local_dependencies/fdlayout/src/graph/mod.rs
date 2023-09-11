pub mod layout;

use nalgebra::SVector;
use std::collections::HashMap;

pub type NodePosition<const D: usize> = SVector<f32, D>;

#[derive(Default, Clone, Debug)]
pub struct Graph {
    n_nodes: u32,
    edges: Vec<[u32; 2]>,
}

pub fn collect_adjacency(n_nodes: usize, edges: &[[u32; 2]]) -> Vec<Vec<u32>> {
    let mut adjacency: Vec<Vec<u32>> = vec![vec![]; n_nodes];
    for [a, b] in edges.iter().cloned() {
        adjacency[a as usize].push(b);
        adjacency[b as usize].push(a);
    }
    adjacency
}

impl Graph {
    pub fn new(n_nodes: u32, edges: Vec<[u32; 2]>) -> Result<Self, String> {
        let mut set = HashMap::<[u32; 2], u32>::new();

        for (i, e) in edges.iter().enumerate() {
            let key = if e[0] < e[1] { *e } else { [e[1], e[0]] };
            if let Some(j) = set.get(&key) {
                return Err(format!(
                    "Only undirected graphs are allowed. Edges {} and {} have the same start and end nodes.",
                    j, i
                ));
            }
            set.insert(key, i as u32);

            for j in e {
                let j = *j;
                if j >= n_nodes {
                    return Err(format!(
                        "Edge {} references node {}, which does not exist.",
                        i, j
                    ));
                }
            }
        }

        Ok(Self { n_nodes, edges })
    }

    pub fn n_nodes(&self) -> usize {
        self.n_nodes as usize
    }

    pub fn edges(&self) -> &[[u32; 2]] {
        &self.edges
    }

    pub fn collect_adjacency(&self) -> Vec<Vec<u32>> {
        collect_adjacency(self.n_nodes(), self.edges())
    }

    pub fn collect_degrees(&self) -> Vec<u32> {
        self.collect_adjacency()
            .iter()
            .map(|adj| adj.len() as u32)
            .collect()
    }

    pub fn get_node_to_component_map(&self) -> (usize, Vec<u32>) {
        let mut labels: Vec<Option<u32>> = vec![None; self.n_nodes as usize];
        let mut n_components = 0usize;
        let mut stack = Vec::<usize>::new();
        let adjacency = self.collect_adjacency();

        for i in 0..self.n_nodes as usize {
            if labels[i].is_some() {
                continue;
            }
            labels[i] = Some(n_components as u32);
            stack.push(i);

            while !stack.is_empty() {
                let i_last = stack.pop().unwrap();
                for i_neighbor in &adjacency[i_last] {
                    let i_neighbor = *i_neighbor as usize;
                    if labels[i_neighbor].is_none() {
                        labels[i_neighbor] = Some(n_components as u32);
                        stack.push(i_neighbor);
                    }
                }
            }

            n_components += 1;
        }

        (n_components, labels.iter().map(|l| l.unwrap()).collect())
    }
}
