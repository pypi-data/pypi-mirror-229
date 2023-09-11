mod grid;
pub mod iteration;

use super::{GraphLayoutAttributes, LayoutAlgorithm};
use crate::graph::{layout::fruchterman_reingold::grid::Grid, Graph, NodePosition};

pub const DEFAULT_COOLING_RATE: f32 = 0.99;
pub const DEFAULT_STOP_TOLERANCE: f32 = 0.01;
pub const DEFAULT_MAX_ITERATIONS: u32 = 1000;

fn move_to_zero<const D: usize>(positions: &mut [NodePosition<D>]) {
    let avg = positions.iter().sum::<NodePosition<D>>() / positions.len() as f32;
    for p in positions {
        *p -= avg;
    }
}

pub struct FruchtermanReingoldLayout<const D: usize> {
    displacements: Vec<NodePosition<D>>,
    n_preprocessing_iterations: u32,
    edge_length_multiplicator: Option<f32>,
    cooling_rate: f32,
    grid: Grid<D>,
}

impl<const D: usize> Default for FruchtermanReingoldLayout<D> {
    fn default() -> Self {
        Self::new(None, None, None)
    }
}

impl<const D: usize> FruchtermanReingoldLayout<D> {
    pub fn new(
        n_preprocessing_iterations: Option<u32>,
        edge_length_multiplicator: Option<f32>,
        cooling_rate: Option<f32>,
    ) -> Self {
        Self {
            displacements: Vec::new(),
            edge_length_multiplicator,
            cooling_rate: cooling_rate.unwrap_or(DEFAULT_COOLING_RATE),
            n_preprocessing_iterations: n_preprocessing_iterations.unwrap_or(0),
            grid: Grid::default(),
        }
    }

    fn evaluate_edge_forces(
        &mut self,
        graph: &Graph,
        positions: &[NodePosition<D>],
        mut optimal_distance: f32,
        degrees: &[u32],
    ) {
        optimal_distance *= 0.25;
        for [i_start, i_end] in &graph.edges {
            let i_start = *i_start;
            let i_end = *i_end;
            let difference = positions[i_end as usize] - positions[i_start as usize];
            let mag = difference.magnitude();
            if mag > 0.25 * optimal_distance {
                let force = difference * (mag / optimal_distance);
                self.displacements[i_start as usize] += force / degrees[i_start as usize] as f32;
                self.displacements[i_end as usize] -= force / degrees[i_end as usize] as f32;
            }
        }
    }

    fn evaluate_repulsive_forces(&mut self, positions: &[NodePosition<D>], optimal_distance: f32) {
        self.grid.build(positions, optimal_distance);
        let optimal_distance_sq = optimal_distance * optimal_distance;

        for ((i, p), disp) in positions.iter().enumerate().zip(&mut self.displacements) {
            *disp += 0.2
                * self.grid.query_sum(NodePosition::<D>::zeros(), p, |j| {
                    if j != i {
                        let diff = p - positions[j];
                        let distance_sq = diff.magnitude_squared();
                        if distance_sq > 0.0 {
                            return Some(diff * optimal_distance_sq / distance_sq);
                        }
                    }
                    None
                });
        }
    }

    fn reset_displacements(&mut self, n_nodes: usize) {
        if self.displacements.len() != n_nodes {
            self.displacements.resize(n_nodes, NodePosition::zeros());
        }
        self.displacements.fill(NodePosition::zeros());
    }

    fn apply_displacements(&self, positions: &mut [NodePosition<D>], temparature: f32) -> f32 {
        let mut disp_mag_sq_max = 0.0f32;
        for (disp, point) in self.displacements.iter().zip(positions) {
            let cooled_disp = disp.cap_magnitude(temparature);
            disp_mag_sq_max = disp_mag_sq_max.max(cooled_disp.magnitude_squared());
            *point += cooled_disp;
        }

        disp_mag_sq_max.sqrt()
    }

    fn evaluate_optimal_distance(&self, desired_edge_length: f32, n_nodes: usize) -> f32 {
        desired_edge_length * self.edge_length_multiplicator.unwrap_or(1.0) / n_nodes as f32
    }

    pub fn grid(&self) -> &Grid<D> {
        &self.grid
    }
}

impl<const D: usize> LayoutAlgorithm<D> for FruchtermanReingoldLayout<D> {
    fn run(
        &mut self,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) {
        let optimal_distance =
            self.evaluate_optimal_distance(atts.desired_edge_length, graph.n_nodes());
        let stop_threshold = DEFAULT_STOP_TOLERANCE * atts.desired_edge_length;
        let degrees = graph
            .collect_adjacency()
            .iter()
            .map(|adj| adj.len() as u32)
            .collect::<Vec<_>>();
        let n_nodes = graph.n_nodes();

        for _ in 0..self.n_preprocessing_iterations {
            self.reset_displacements(n_nodes);
            self.evaluate_edge_forces(graph, positions, optimal_distance, &degrees);
            self.apply_displacements(
                positions,
                optimal_distance / self.n_preprocessing_iterations as f32,
            );
        }

        let mut temparature = optimal_distance;
        for _ in 0..DEFAULT_MAX_ITERATIONS {
            self.reset_displacements(n_nodes);
            self.evaluate_repulsive_forces(positions, optimal_distance);
            self.evaluate_edge_forces(graph, positions, optimal_distance, &degrees);
            if self.apply_displacements(positions, temparature) < stop_threshold {
                break;
            }
            temparature *= self.cooling_rate;
        }

        move_to_zero(positions);
    }
}
