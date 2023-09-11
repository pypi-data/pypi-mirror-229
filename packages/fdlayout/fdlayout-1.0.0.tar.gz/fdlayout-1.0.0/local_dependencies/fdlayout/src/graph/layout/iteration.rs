use super::{GraphLayoutAttributes, LayoutAlgorithm};
use crate::graph::{Graph, NodePosition};

pub trait LayoutAlgorithmIterator<const D: usize> {
    type Algorithm: LayoutAlgorithm<D>;

    fn next(
        &mut self,
        algorithm: &mut Self::Algorithm,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) -> bool;
}

pub struct AlgorithmIterationBundle<A, I> {
    pub algorithm: A,
    pub iterator: I,
}

impl<A, I> From<(A, I)> for AlgorithmIterationBundle<A, I> {
    fn from((algorithm, iterator): (A, I)) -> Self {
        Self {
            algorithm,
            iterator,
        }
    }
}

pub trait AlgorithmIterationBundleImpl<const D: usize, A, I> {
    fn algorithm(&self) -> &A;
    fn iterator(&self) -> &I;
    fn next(
        &mut self,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        attributes: &GraphLayoutAttributes,
    ) -> bool;
}

impl<const D: usize, A, I> AlgorithmIterationBundleImpl<D, A, I> for AlgorithmIterationBundle<A, I>
where
    A: LayoutAlgorithm<D>,
    I: LayoutAlgorithmIterator<D, Algorithm = A>,
{
    fn algorithm(&self) -> &A {
        &self.algorithm
    }

    fn iterator(&self) -> &I {
        &self.iterator
    }

    fn next(
        &mut self,
        graph: &Graph,
        positions: &mut [NodePosition<D>],
        atts: &GraphLayoutAttributes,
    ) -> bool {
        self.iterator
            .next(&mut self.algorithm, graph, positions, atts)
    }
}
