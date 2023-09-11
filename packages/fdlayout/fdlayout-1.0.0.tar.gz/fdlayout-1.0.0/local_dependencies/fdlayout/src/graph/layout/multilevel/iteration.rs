use super::MultilevelLayout;
use crate::graph::{
    layout::{
        iteration::{AlgorithmIterationBundleImpl, LayoutAlgorithmIterator},
        multilevel::place_child_nodes,
        LayoutAlgorithm, RandomLayout,
    },
    Graph, NodePosition,
};
use rand::Rng;

#[derive(PartialEq)]
enum IterationState<const D: usize> {
    Setup(Option<(usize, Vec<NodePosition<D>>)>),
    Running(usize),
}

impl<const D: usize> Default for IterationState<D> {
    fn default() -> Self {
        Self::Setup(None)
    }
}

#[derive(Default)]
pub struct MultilevelLayoutIterator<const D: usize> {
    state: IterationState<D>,
}

impl<const D: usize> MultilevelLayoutIterator<D> {
    pub fn next<
        R: Rng,
        A: LayoutAlgorithm<D>,
        I: LayoutAlgorithmIterator<D, Algorithm = A>,
        T: AlgorithmIterationBundleImpl<D, A, I>,
    >(
        &mut self,
        mll: &mut MultilevelLayout,
        algorithm_bundle: &mut T,
        rng: &mut R,
        positions: &mut [NodePosition<D>],
    ) -> bool {
        assert!(!mll.levels.is_empty());

        match &self.state {
            IterationState::Setup(state) => {
                let i_level = state.as_ref().map(|s| s.0).unwrap_or(mll.levels.len() - 1);
                let level = &mll.levels[i_level];

                if let Some((_, prev_positions)) = state {
                    positions.copy_from_slice(&place_child_nodes(
                        rng,
                        level,
                        &prev_positions,
                        &level.attributes.node_sizes,
                    ));
                } else {
                    RandomLayout::new(rng, None).run(&level.graph, positions, &level.attributes);
                }

                self.state = IterationState::Running(i_level);
            }
            IterationState::Running(i_level) => {
                let i_level = *i_level;
                let level = &mll.levels[i_level];

                let level_is_done =
                    algorithm_bundle.next(&level.graph, positions, &level.attributes);

                if level_is_done {
                    self.state = IterationState::Setup({
                        if i_level > 0 {
                            Some((i_level - 1, positions.iter().cloned().collect()))
                        } else {
                            None
                        }
                    });
                }
            }
        }

        match &self.state {
            IterationState::Setup(state) => state.is_none(),
            _ => false,
        }
    }

    pub fn i_level(&self, mll: &MultilevelLayout) -> usize {
        assert!(!mll.levels.is_empty());
        match &self.state {
            IterationState::Setup(state) => {
                state.as_ref().map(|s| s.0).unwrap_or(mll.levels.len() - 1)
            }
            IterationState::Running(i) => *i,
        }
    }

    pub fn get_current_graph<'a>(&self, mll: &'a MultilevelLayout) -> &'a Graph {
        assert!(!mll.levels.is_empty());
        &mll.levels[self.i_level(mll)].graph
    }
}
