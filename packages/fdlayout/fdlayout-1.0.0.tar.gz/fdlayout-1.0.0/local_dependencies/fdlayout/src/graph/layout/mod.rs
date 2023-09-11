pub mod fruchterman_reingold;
pub mod iteration;
pub mod multilevel;
pub mod multipole;

use super::{Graph, NodePosition};
use rand::Rng;

pub const DEFAULT_NODE_SIZE: f32 = 1.0 / 50.0;

pub struct GraphLayoutAttributes {
    pub node_sizes: Vec<f32>,
    pub edge_lengths: Vec<f32>,
    pub desired_edge_length: f32,
}

impl From<&Graph> for GraphLayoutAttributes {
    fn from(value: &Graph) -> Self {
        Self::new(value, None, None)
    }
}

impl GraphLayoutAttributes {
    pub fn new(
        graph: &Graph,
        node_sizes: Option<Vec<f32>>,
        edge_lengths: Option<Vec<f32>>,
    ) -> Self {
        fn get_edge_lengths_from_node_sizes(graph: &Graph, sizes: &[f32]) -> Vec<f32> {
            graph
                .edges()
                .iter()
                .map(|[a, b]| 0.5 * (sizes[*a as usize] + sizes[*b as usize]))
                .collect()
        }

        let (node_sizes, edge_lengths) = match (node_sizes, edge_lengths) {
            (None, None) => {
                let sizes = vec![DEFAULT_NODE_SIZE; graph.n_nodes()];
                let lengths = get_edge_lengths_from_node_sizes(graph, &sizes);
                (sizes, lengths)
            }
            (Some(sizes), None) => {
                let lengths = get_edge_lengths_from_node_sizes(graph, &sizes);
                (sizes, lengths)
            }
            (None, Some(lengths)) => {
                let avg_length = lengths.iter().sum::<f32>() / lengths.len() as f32;
                (vec![avg_length; graph.n_nodes()], lengths)
            }
            (Some(sizes), Some(lengths)) => (sizes, lengths),
        };

        Self {
            desired_edge_length: edge_lengths.iter().sum::<f32>() / graph.edges().len() as f32,
            node_sizes,
            edge_lengths,
        }
    }
}

pub trait LayoutAlgorithm<const D: usize> {
    fn run(
        &mut self,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        attributes: &GraphLayoutAttributes,
    );
}

pub struct RandomLayout<'a, R: Rng> {
    rng: &'a mut R,
    scale: f32,
}

impl<'a, R: Rng> RandomLayout<'a, R> {
    pub fn new(rng: &'a mut R, scale: Option<f32>) -> Self {
        Self {
            rng,
            scale: scale.unwrap_or(1.0),
        }
    }
}

impl<'a, const D: usize, R: Rng> LayoutAlgorithm<D> for RandomLayout<'a, R> {
    fn run(
        &mut self,
        _graph: &Graph,
        positions: &mut [NodePosition<D>],
        _attributes: &GraphLayoutAttributes,
    ) {
        for p in positions {
            self.rng.fill(p.as_mut_slice());
            *p *= self.scale;
        }
    }
}
