use super::{
    move_to_zero, FruchtermanReingoldLayout, DEFAULT_MAX_ITERATIONS, DEFAULT_STOP_TOLERANCE,
};
use crate::graph::{
    layout::{iteration::LayoutAlgorithmIterator, GraphLayoutAttributes},
    Graph, NodePosition,
};

#[derive(Default)]
pub struct FruchtermanReingoldLayoutIterator<const D: usize> {
    temparature: f32,
    i_iteration: u32,
    i_preproc_iteration: u32,
    degrees: Vec<u32>,
    initialized: bool,
}

impl<const D: usize> LayoutAlgorithmIterator<D> for FruchtermanReingoldLayoutIterator<D> {
    type Algorithm = FruchtermanReingoldLayout<D>;

    fn next(
        &mut self,
        fdl: &mut Self::Algorithm,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) -> bool {
        let optimal_distance =
            fdl.evaluate_optimal_distance(atts.desired_edge_length, graph.n_nodes());
        let stop_threshold = DEFAULT_STOP_TOLERANCE * optimal_distance;
        let n_nodes = graph.n_nodes();

        if !self.initialized {
            self.initialized = true;

            self.temparature = optimal_distance;
            self.i_iteration = 0;
            self.i_preproc_iteration = 0;

            if self.degrees.len() != n_nodes {
                self.degrees = graph.collect_degrees();
            }
        }

        fdl.reset_displacements(n_nodes);
        fdl.evaluate_edge_forces(graph, positions, 0.5 * optimal_distance, &self.degrees);

        if self.i_preproc_iteration < fdl.n_preprocessing_iterations {
            fdl.apply_displacements(
                positions,
                0.5 * optimal_distance / fdl.n_preprocessing_iterations as f32,
            );
            self.i_preproc_iteration += 1;
        } else {
            fdl.evaluate_repulsive_forces(positions, optimal_distance);
            let disp_max = fdl.apply_displacements(positions, self.temparature);
            self.temparature *= fdl.cooling_rate;
            self.i_iteration += 1;
            self.initialized =
                self.i_iteration < DEFAULT_MAX_ITERATIONS && disp_max >= stop_threshold;
        }

        move_to_zero(positions);

        !self.initialized
    }
}
