use super::spatial_tree::SpatialTree;
use nalgebra::SVector;
use num::complex::Complex64;

type Point<const D: usize> = SVector<f32, D>;
type Complex = Complex64;

pub fn evaluate_displacement<const D: usize>(
    point_a: &Point<D>,
    point_b: &Point<D>,
    size_a: f32,
    size_b: f32,
) -> Point<D> {
    let d = point_a - point_b;
    let s = size_a + size_b;
    d * s / (0.25 * s).max(d.magnitude_squared())
}

fn p2p_evaluate_displacement<const D: usize>(
    displacements: &mut [Point<D>],
    tree: &SpatialTree<D>,
    points: &[Point<D>],
    point_sizes: &[f32],
    i_p_ref: usize,
    i_q_ref: usize,
) {
    let i_p = tree.point_ref(i_p_ref).i_point as usize;
    let i_q = tree.point_ref(i_q_ref).i_point as usize;

    let disp = evaluate_displacement(
        &points[i_p],
        &points[i_q],
        point_sizes[i_p],
        point_sizes[i_q],
    );

    displacements[i_p] += disp;
    displacements[i_q] -= disp;
}

fn is_well_separated<const D: usize>(tree: &SpatialTree<D>, i_a: usize, i_b: usize) -> bool {
    let delta = tree.node_center(i_a) - tree.node_center(i_b);
    let extent = tree.node_size(i_a).max(tree.node_size(i_b));
    let bias: f32 = 0.00000001;
    let b = 1.0 + 0.5 * bias;
    delta.magnitude_squared() > 2.0 * b * b * extent * extent
}

struct BinCoeff {
    coeffs: Vec<f64>,
    extent: usize,
}

impl BinCoeff {
    fn new(max_n: usize) -> Self {
        let extent = max_n + 1;
        let mut coeffs = vec![0.0; extent * extent];

        for i in 0..extent {
            coeffs[i * extent] = 1.0;
            coeffs[i * extent + i] = 1.0;
        }

        for i_row in 2..extent {
            for i_col in 1..i_row {
                let i_top = (i_row - 1) * extent + i_col;
                coeffs[i_row * extent + i_col] = coeffs[i_top - 1] + coeffs[i_top];
            }
        }

        Self { coeffs, extent }
    }

    fn value(&self, n: usize, k: usize) -> f64 {
        self.coeffs[n * self.extent + k]
    }
}

#[derive(Default)]
pub struct Expansion<const D: usize, const P: usize> {
    expansions: Vec<[Complex; P]>,
    local_expansions: Vec<[Complex; P]>,
    bin_coeff: Option<BinCoeff>,
}

impl<const D: usize, const P: usize> Expansion<D, P> {
    pub fn setup(&mut self, n_points: usize) {
        self.bin_coeff = Some(BinCoeff::new(2 * P));

        {
            let init = [Complex::default(); P];
            let max_n_nodes = 2 * n_points;
            if self.expansions.len() != max_n_nodes {
                self.expansions.resize(max_n_nodes, init);
                self.local_expansions.resize(max_n_nodes, init);
            }
            self.expansions.fill(init);
            self.local_expansions.fill(init);
        }
    }

    pub fn p2m(
        &mut self,
        point: &Point<D>,
        point_size: f32,
        receiver_center: &Point<D>,
        i_receiver: usize,
    ) {
        let coeff = &mut self.expansions[i_receiver];
        let q = point_size as f64;
        coeff[0].re += q;

        let delta = point - receiver_center;
        let delta = Complex::new(delta[0] as f64, delta[1] as f64);
        let mut delta_k = delta;

        for k in 1..P {
            coeff[k] -= (q / k as f64) * delta_k;
            delta_k *= delta;
        }
    }

    pub fn m2m(
        &mut self,
        source_center: &Point<D>,
        receiver_center: &Point<D>,
        i_source: usize,
        i_receiver: usize,
    ) {
        let source_coeff = self.expansions[i_source];
        let receiver_coeff = &mut self.expansions[i_receiver];
        let bin_coeff = self.bin_coeff.as_ref().unwrap();

        let delta = source_center - receiver_center;
        let delta = Complex::new(delta[0] as f64, delta[1] as f64);
        receiver_coeff[0] += source_coeff[0];

        for j in 1..P {
            let c_rec = &mut receiver_coeff[j];
            let mut delta_k = Complex::new(1.0, 0.0);
            for k in 0..j {
                let c_src = source_coeff[j - k];
                *c_rec += c_src * delta_k * bin_coeff.value(j - 1, k);
                delta_k *= delta;
            }
            *c_rec -= source_coeff[0] * delta_k / j as f64;
        }
    }

    pub fn l2l(
        &mut self,
        source_center: &Point<D>,
        receiver_center: &Point<D>,
        i_source: usize,
        i_receiver: usize,
    ) {
        let source_coeff = self.local_expansions[i_source];
        let receiver_coeff = &mut self.local_expansions[i_receiver];
        let bin_coeff = self.bin_coeff.as_ref().unwrap();

        let delta = source_center - receiver_center;
        let delta = Complex::new(delta[0] as f64, delta[1] as f64);

        for j in 0..P {
            let c_rec = &mut receiver_coeff[j];
            let mut delta_k = Complex::new(1.0, 0.0);
            for k in j..P {
                *c_rec += source_coeff[k] * delta_k * bin_coeff.value(k, j);
                delta_k *= delta;
            }
        }
    }

    pub fn l2p(
        &self,
        displacement: &mut Point<D>,
        node_center: &Point<D>,
        point: &Point<D>,
        i_node: usize,
    ) {
        let coeff = &self.local_expansions[i_node];

        let delta = point - node_center;
        let delta = Complex::new(delta[0] as f64, delta[1] as f64);
        let mut delta_k = Complex::new(1.0, 0.0);

        let mut res = Complex::default();

        for k in 1..P {
            res += coeff[k] * delta_k * k as f64;
            delta_k *= delta;
        }
        res = res.conj();

        displacement[0] -= res.re as f32;
        displacement[1] -= res.im as f32;
    }

    pub fn m2l(
        &mut self,
        source_center: &Point<D>,
        receiver_center: &Point<D>,
        i_source: usize,
        i_receiver: usize,
    ) {
        let source_coeff = self.expansions[i_source];
        let receiver_coeff = &mut self.local_expansions[i_receiver];
        let bin_coeff = self.bin_coeff.as_ref().unwrap();

        let delta0 = source_center - receiver_center;
        let delta0 = Complex::new(delta0[0] as f64, delta0[1] as f64);
        let delta1 = -delta0;
        let mut delta1_l = delta1;

        for j in 1..P {
            let c_rec = &mut receiver_coeff[j];
            let mut sum = source_coeff[0] * (-1.0 / j as f64);
            let mut delta0_k = delta0;
            for k in 1..P {
                let c_src = &source_coeff[k];
                sum += (c_src * bin_coeff.value(j + k - 1, k - 1)) / delta0_k;
                delta0_k *= delta0;
            }
            *c_rec += sum / delta1_l;
            delta1_l *= delta1;
        }

        receiver_coeff[0] += source_coeff[0]
            * Complex::new(
                (delta1.re * delta1.re + delta1.im * delta1.im).sqrt().ln(),
                ((receiver_center[0] - source_center[0]) / (receiver_center[1] - source_center[1]))
                    .atan() as f64,
            );

        delta1_l = delta1;
        for k in 1..P {
            receiver_coeff[0] += source_coeff[k] / delta1_l;
            delta1_l *= delta1;
        }
    }

    fn p2p_pair(
        &self,
        displacements: &mut [Point<D>],
        tree: &SpatialTree<D>,
        points: &[Point<D>],
        point_sizes: &[f32],
        i_a: usize,
        i_b: usize,
    ) {
        let a = tree.node(i_a);
        let b = tree.node(i_b);
        for i_p_ref in a.i_first_point_ref..(a.i_first_point_ref + a.n_points) {
            for i_q_ref in b.i_first_point_ref..(b.i_first_point_ref + b.n_points) {
                p2p_evaluate_displacement(
                    displacements,
                    tree,
                    points,
                    point_sizes,
                    i_p_ref as usize,
                    i_q_ref as usize,
                );
            }
        }
    }

    fn handle_pair(
        &mut self,
        displacements: &mut [Point<D>],
        tree: &SpatialTree<D>,
        points: &[Point<D>],
        point_sizes: &[f32],
        i_a: usize,
        i_b: usize,
    ) {
        let node_a = tree.node(i_a);
        let node_b = tree.node(i_b);

        const M2L_MIN_BOUND: u32 = 8;
        const WSPD_BRANCH_BOUND: u32 = 16;

        if is_well_separated(tree, i_a, i_b) {
            if node_a.n_points < M2L_MIN_BOUND && node_b.n_points < M2L_MIN_BOUND {
                self.p2p_pair(displacements, tree, points, point_sizes, i_a, i_b)
            } else {
                let center_a = tree.node_center(i_a);
                let center_b = tree.node_center(i_b);
                self.m2l(&center_a, &center_b, i_a, i_b);
                self.m2l(&center_b, &center_a, i_b, i_a);
            }
        } else if node_a.n_children == 0
            || node_b.n_children == 0
            || (node_a.n_points <= WSPD_BRANCH_BOUND && node_b.n_points <= WSPD_BRANCH_BOUND)
        {
            self.p2p_pair(displacements, tree, points, point_sizes, i_a, i_b)
        } else {
            let (i, j) = if node_a.level >= node_b.level {
                (i_a, i_b)
            } else {
                (i_b, i_a)
            };

            for i_child in tree.i_children(i) {
                self.handle_pair(
                    displacements,
                    tree,
                    points,
                    point_sizes,
                    j,
                    *i_child as usize,
                );
            }
        }
    }

    pub fn handle_pairs(
        &mut self,
        tree: &SpatialTree<D>,
        points: &[Point<D>],
        point_sizes: &[f32],
        displacements: &mut [Point<D>],
        i_node: Option<usize>,
    ) {
        let i_node = i_node.unwrap_or(tree.i_root());
        let node = tree.node(i_node);

        if node.n_children > 0 && node.n_points > 25 {
            for i_child in tree.i_children(i_node) {
                let i_child: usize = *i_child as usize;
                self.handle_pairs(tree, points, point_sizes, displacements, Some(i_child));
            }
            tree.forall_ordered_pairs_of_children(
                &mut |i_child_a, i_child_b| {
                    self.handle_pair(
                        displacements,
                        tree,
                        points,
                        point_sizes,
                        i_child_a,
                        i_child_b,
                    );
                },
                i_node,
            );
        } else if node.n_points > 1 {
            let i_end = node.i_first_point_ref + node.n_points;
            for i_p_ref in node.i_first_point_ref..i_end {
                for i_q_ref in (i_p_ref + 1)..i_end {
                    p2p_evaluate_displacement(
                        displacements,
                        tree,
                        points,
                        point_sizes,
                        i_p_ref as usize,
                        i_q_ref as usize,
                    );
                }
            }
        }
    }
}
