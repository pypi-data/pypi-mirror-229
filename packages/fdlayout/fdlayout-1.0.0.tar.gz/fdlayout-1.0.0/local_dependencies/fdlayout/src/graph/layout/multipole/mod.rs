mod expansion;
pub mod iteration;
mod spatial_tree;

use self::expansion::evaluate_displacement;

use super::{GraphLayoutAttributes, LayoutAlgorithm};
use crate::graph::{Graph, NodePosition};
use expansion::Expansion;
use spatial_tree::SpatialTree;

pub const DEFAULT_COOLING_RATE: f32 = 0.999;
pub const DEFAULT_MAX_ITERATIONS: usize = 1000;
pub const DEFAULT_PREPROCESSING_ITERATIONS: usize = 20;
pub const DEFAULT_SIMPLE_APPROACH_POINT_LIMIT: usize = 150;
pub const DEFAULT_STOP_THRESHOLD: f32 = 0.00005;

const TIME_STEP: f32 = 0.25;
const PREPROCESSING_TIME_STEP: f32 = 0.5;

fn move_to_zero<const D: usize>(positions: &mut [NodePosition<D>]) {
    let avg = positions.iter().sum::<NodePosition<D>>() / positions.len() as f32;
    for p in positions {
        *p -= avg;
    }
}

pub struct MultipoleLayout<const D: usize> {
    tree: SpatialTree<D>,
    displacements: Vec<NodePosition<D>>,
    expansion: Expansion<D, 4>,
    cooling_rate: f32,
    max_n_iterations: usize,
    n_preprocessing_iterations: usize,
    simple_approach_limit: usize,
    stop_threshold: f32,
}

impl<const D: usize> Default for MultipoleLayout<D> {
    fn default() -> Self {
        Self::new(None, None, None, None, None)
    }
}

impl<const D: usize> MultipoleLayout<D> {
    pub fn new(
        max_n_iterations: Option<usize>,
        n_preprocessing_iterations: Option<usize>,
        cooling_rate: Option<f32>,
        simple_approach_limit: Option<usize>,
        stop_threshold: Option<f32>,
    ) -> Self {
        Self {
            tree: SpatialTree::default(),
            displacements: Vec::new(),
            expansion: Expansion::default(),
            cooling_rate: cooling_rate.unwrap_or(DEFAULT_COOLING_RATE),
            max_n_iterations: max_n_iterations.unwrap_or(DEFAULT_MAX_ITERATIONS),
            n_preprocessing_iterations: n_preprocessing_iterations
                .unwrap_or(DEFAULT_PREPROCESSING_ITERATIONS),
            simple_approach_limit: simple_approach_limit
                .unwrap_or(DEFAULT_SIMPLE_APPROACH_POINT_LIMIT),
            stop_threshold: stop_threshold.unwrap_or(DEFAULT_STOP_THRESHOLD),
        }
    }

    fn evaluate_edge_forces(
        &mut self,
        edges: &[[u32; 2]],
        positions: &[NodePosition<D>],
        degrees: &[u32],
        edge_lengths: &[f32],
    ) {
        for (i_edge, [i_a, i_b]) in edges.iter().enumerate() {
            let i_a = *i_a as usize;
            let i_b = *i_b as usize;
            let difference = positions[i_b] - positions[i_a];
            let distance_sq = difference.magnitude_squared();
            if distance_sq > 0.0 {
                let strength = 0.25 * (0.5 * distance_sq.ln() - edge_lengths[i_edge].ln());
                let mut disp = strength * difference;
                disp *= 0.5;

                self.displacements[i_a] += disp / degrees[i_a] as f32;
                self.displacements[i_b] -= disp / degrees[i_b] as f32;
            }
        }
    }

    fn reset_displacements(&mut self, n: usize) {
        let init = NodePosition::zeros();
        if self.displacements.len() != n {
            self.displacements.resize(n, init);
        }
        self.displacements.fill(init);
    }

    fn apply_displacements(&self, positions: &mut [NodePosition<D>], time_step: f32) -> f32 {
        let mut max_force_sq = 0.0f32;
        for (displacement, point) in self.displacements.iter().zip(positions) {
            let disp = time_step * displacement;
            let distance_sq = disp.magnitude_squared();
            if distance_sq < f32::MAX {
                max_force_sq = max_force_sq.max(distance_sq);
                *point += disp;
            }
        }

        max_force_sq
    }

    fn evaluate_multipole_expansion(&mut self, points: &[NodePosition<D>], point_sizes: &[f32]) {
        self.tree.build(points);
        self.expansion.setup(points.len());

        self.tree.traverse_bottom_up(
            &mut |i_node| {
                let node = self.tree.node(i_node);
                let node_center = self.tree.node_center(i_node);
                if node.n_children > 0 {
                    for i_child in self.tree.i_children(i_node) {
                        let i_child = *i_child as usize;
                        let child_center = self.tree.node_center(i_child);
                        self.expansion
                            .m2m(child_center, node_center, i_child, i_node);
                    }
                } else {
                    for i_point_ref in
                        node.i_first_point_ref..(node.i_first_point_ref + node.n_points)
                    {
                        let i_point = self.tree.point_ref(i_point_ref as usize).i_point as usize;
                        self.expansion.p2m(
                            &points[i_point],
                            point_sizes[i_point],
                            node_center,
                            i_node,
                        );
                    }
                }
            },
            None,
        );

        self.expansion.handle_pairs(
            &self.tree,
            points,
            point_sizes,
            &mut self.displacements,
            None,
        );

        self.tree.traverse_top_down(
            &mut |i_node| {
                if self.tree.node(i_node).n_children > 0 {
                    for i_child in self.tree.i_children(i_node) {
                        let i_child = *i_child as usize;
                        self.expansion.l2l(
                            self.tree.node_center(i_node),
                            self.tree.node_center(i_child),
                            i_node,
                            i_child,
                        );
                    }
                }
            },
            None,
        );

        for i_point_ref in 0..points.len() {
            let point_ref = self.tree.point_ref(i_point_ref);
            let i_point = point_ref.i_point as usize;
            let i_leaf = point_ref.i_node as usize;
            self.expansion.l2p(
                &mut self.displacements[i_point],
                self.tree.node_center(i_leaf),
                &points[i_point],
                i_leaf,
            );

            self.displacements[i_point] *= 2.0;
        }
    }

    fn evaluate_repulsive_forces(&mut self, points: &[NodePosition<D>], graph_node_sizes: &[f32]) {
        let n_points = points.len();
        if n_points < self.simple_approach_limit {
            for i in 0..n_points {
                for j in (i + 1)..n_points {
                    let disp = evaluate_displacement(
                        &points[i],
                        &points[j],
                        graph_node_sizes[i],
                        graph_node_sizes[j],
                    );
                    self.displacements[i] += disp;
                    self.displacements[j] -= disp;
                }
            }
        } else {
            self.evaluate_multipole_expansion(points, &graph_node_sizes);
        }
    }

    fn should_stop_early(
        &self,
        i_iteration: usize,
        max_force_sq: f32,
        desired_edge_length: f32,
    ) -> bool {
        i_iteration > 4 && max_force_sq / desired_edge_length < self.stop_threshold
    }

    pub fn tree(&self) -> &SpatialTree<D> {
        &self.tree
    }
}

impl<const D: usize> LayoutAlgorithm<D> for MultipoleLayout<D> {
    fn run(
        &mut self,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) {
        let degrees = graph.collect_degrees();
        let n_points = graph.n_nodes();

        for _ in 0..self.n_preprocessing_iterations {
            self.reset_displacements(n_points);
            self.evaluate_edge_forces(graph.edges(), positions, &degrees, &atts.edge_lengths);
            self.apply_displacements(positions, PREPROCESSING_TIME_STEP);
        }

        let mut temparature: f32 = 1.0;

        for i_iteration in 0..self.max_n_iterations {
            self.reset_displacements(n_points);

            temparature *= self.cooling_rate;

            self.evaluate_repulsive_forces(positions, &atts.node_sizes);
            self.evaluate_edge_forces(graph.edges(), positions, &degrees, &atts.edge_lengths);

            let max_force_sq = self.apply_displacements(positions, TIME_STEP * temparature);

            if self.should_stop_early(i_iteration, max_force_sq, atts.desired_edge_length) {
                break;
            }
        }

        move_to_zero(positions);
    }
}
