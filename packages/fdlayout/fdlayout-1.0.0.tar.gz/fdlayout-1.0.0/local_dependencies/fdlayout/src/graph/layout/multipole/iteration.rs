use super::{move_to_zero, MultipoleLayout, PREPROCESSING_TIME_STEP, TIME_STEP};
use crate::graph::{
    layout::{iteration::LayoutAlgorithmIterator, GraphLayoutAttributes},
    Graph, NodePosition,
};

#[derive(Default)]
pub struct MultipoleLayoutIterator<const D: usize> {
    initialized: bool,
    temparature: f32,
    i_iteration: usize,
    i_preproc_iteration: usize,
    degrees: Vec<u32>,
    prev_n_points: usize,
}

impl<const D: usize> LayoutAlgorithmIterator<D> for MultipoleLayoutIterator<D> {
    type Algorithm = MultipoleLayout<D>;

    fn next(
        &mut self,
        ml: &mut Self::Algorithm,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) -> bool {
        let n_points = positions.len();

        if !self.initialized {
            self.initialized = true;
            self.temparature = 1.0;
            self.i_iteration = 0;
            self.i_preproc_iteration = 0;

            if self.degrees.len() != n_points {
                self.degrees = graph.collect_degrees();
            }
        }

        ml.tree.clear();

        if self.i_preproc_iteration < ml.n_preprocessing_iterations {
            ml.reset_displacements(n_points);
            ml.evaluate_edge_forces(graph.edges(), positions, &self.degrees, &atts.edge_lengths);
            ml.apply_displacements(positions, PREPROCESSING_TIME_STEP);

            self.i_preproc_iteration += 1;
        } else if self.i_iteration < ml.max_n_iterations {
            ml.reset_displacements(n_points);

            self.temparature *= ml.cooling_rate;

            ml.evaluate_repulsive_forces(positions, &atts.node_sizes);
            ml.evaluate_edge_forces(graph.edges(), positions, &self.degrees, &atts.edge_lengths);

            let max_force_sq = ml.apply_displacements(positions, TIME_STEP * self.temparature);

            self.initialized =
                !ml.should_stop_early(self.i_iteration, max_force_sq, atts.desired_edge_length);

            self.i_iteration += 1;
            self.initialized &= self.i_iteration < ml.max_n_iterations;
        }

        move_to_zero(positions);
        self.prev_n_points = n_points;

        !self.initialized
    }
}
