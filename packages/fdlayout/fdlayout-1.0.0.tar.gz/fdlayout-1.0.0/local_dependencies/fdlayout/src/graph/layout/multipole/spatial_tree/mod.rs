mod morton;

use morton::MortonCode;
use nalgebra::SVector;

type Point<const D: usize> = SVector<f32, D>;

#[derive(Clone, Default, Debug)]
pub struct SpatialTreeNode {
    pub level: u32,
    pub n_children: u32,
    pub i_first_point_ref: u32,
    pub n_points: u32,
    i_next: u32,
}

#[derive(Default, Clone)]
pub struct PointRef<const D: usize> {
    morton: MortonCode<D>,
    pub i_point: u32,
    pub i_node: u32,
}

fn restore_chain<const D: usize>(tree: &mut SpatialTree<D>) -> usize {
    #[derive(Default)]
    struct ChainRestorationContext {
        i_last_inner_node: usize,
        i_first_inner_node: usize,
        n_inner_nodes: u32,
    }

    fn restore_chain_recursive<const D: usize>(
        ctx: &mut ChainRestorationContext,
        tree: &mut SpatialTree<D>,
        i_node: usize,
    ) {
        if tree.nodes[i_node].n_children == 0 {
            return;
        }

        let i_first_child = tree.node_slots(i_node)[0] as usize;
        restore_chain_recursive(ctx, tree, i_first_child);

        tree.nodes[i_node].i_first_point_ref = tree.nodes[i_first_child].i_first_point_ref;

        if ctx.i_last_inner_node > 0 {
            tree.nodes[ctx.i_last_inner_node].i_next = i_node as u32;
        } else {
            ctx.i_first_inner_node = i_node;
        }
        ctx.i_last_inner_node = i_node;
        ctx.n_inner_nodes += 1;

        for i in 1..tree.nodes[i_node].n_children as usize {
            restore_chain_recursive(ctx, tree, tree.node_slots(i_node)[i] as usize);
        }

        let i_last_slot = tree.nodes[i_node].n_children as usize - 1;
        let i_last_child = tree.node_slots(i_node)[i_last_slot] as usize;
        let last_child = &tree.nodes[i_last_child];
        let i_last_point_of_last_child = last_child.i_first_point_ref as u32 + last_child.n_points;
        tree.nodes[i_node].n_points =
            i_last_point_of_last_child - tree.nodes[i_node].i_first_point_ref as u32;
    }

    let mut ctx = ChainRestorationContext::default();
    restore_chain_recursive(&mut ctx, tree, tree.i_root);

    if ctx.i_last_inner_node > 0 {
        tree.nodes[ctx.i_last_inner_node].i_next = 0;
    }

    ctx.n_inner_nodes as usize
}

#[derive(Default)]
pub struct SpatialTree<const D: usize> {
    nodes: Vec<SpatialTreeNode>,
    node_slots: Vec<u32>,
    point_refs: Vec<PointRef<D>>,
    node_sizes: Vec<f32>,
    node_positions: Vec<Point<D>>,
    i_root: usize,
    n_inner_nodes: usize,
}

impl<const D: usize> SpatialTree<D> {
    pub const MAX_CHILDREN_PER_NODE: usize = 1 << D;

    fn node_slots_mut(&mut self, i_node: usize) -> &mut [u32] {
        let i_start = i_node * Self::MAX_CHILDREN_PER_NODE;
        &mut self.node_slots[i_start..i_start + Self::MAX_CHILDREN_PER_NODE]
    }

    fn node_slots(&self, i_node: usize) -> &[u32] {
        let i_start = i_node * Self::MAX_CHILDREN_PER_NODE;
        &self.node_slots[i_start..i_start + Self::MAX_CHILDREN_PER_NODE]
    }

    fn prepare_tree(&mut self, n_points: usize) -> (usize, usize) {
        let mut n_leaves = 0usize;
        let mut i_leaf;
        let mut i_inner = 0usize;
        let mut i_point = 0usize;

        while i_point < n_points {
            i_leaf = i_point;
            i_inner = n_points + i_leaf;

            while i_point < n_points
                && *self.point_refs[i_point].morton == *self.point_refs[i_leaf].morton
            {
                self.point_refs[i_point].i_node = i_leaf as u32;
                i_point += 1;
            }

            n_leaves += 1;

            {
                let n_node_points = (i_point - i_leaf) as u32;

                self.nodes[i_leaf] = SpatialTreeNode {
                    level: 0,
                    i_next: i_point as u32,
                    n_children: 0,
                    i_first_point_ref: i_leaf as u32,
                    n_points: n_node_points,
                };

                self.nodes[i_inner] = SpatialTreeNode {
                    level: {
                        if i_point >= n_points {
                            64
                        } else {
                            self.point_refs[i_leaf]
                                .morton
                                .parent_level(&self.point_refs[i_point].morton)
                        }
                    },
                    i_next: (n_points + i_point) as u32,
                    n_children: 2,
                    i_first_point_ref: i_leaf as u32,
                    n_points: n_node_points,
                };
                self.node_slots[i_inner * Self::MAX_CHILDREN_PER_NODE] = i_leaf as u32;
                self.node_slots[i_inner * Self::MAX_CHILDREN_PER_NODE + 1] = i_point as u32;
            }
        }

        (n_leaves, i_inner)
    }

    fn build_hierarchy(
        &mut self,
        mut i_node: usize,
        max_level: u32,
        i_last_inner_node: usize,
    ) -> usize {
        let mut i_next_node: usize;

        while {
            i_next_node = self.nodes[i_node].i_next as usize;
            i_next_node != i_last_inner_node && self.nodes[i_next_node].level < max_level
        } {
            let level = self.nodes[i_node].level;
            let next_level = self.nodes[i_next_node].level;
            if level == next_level {
                for i_next_node_slot in 1..self.nodes[i_next_node].n_children as usize {
                    let i_next_node_child = self.node_slots(i_next_node)[i_next_node_slot];
                    let i_slot = self.nodes[i_node].n_children as usize;
                    self.node_slots_mut(i_node)[i_slot] = i_next_node_child;
                    self.nodes[i_node].n_children += 1;
                }
                self.nodes[i_node].i_next = self.nodes[i_next_node].i_next;
            } else if level < next_level {
                self.node_slots_mut(i_next_node)[0] = i_node as u32;
                i_node = i_next_node;
            } else {
                let i_right_child = self.build_hierarchy(i_next_node, level, i_last_inner_node);
                let i_slot = self.nodes[i_node].n_children as usize - 1;
                self.node_slots_mut(i_node)[i_slot] = i_right_child as u32;
                self.nodes[i_node].i_next = self.nodes[i_right_child].i_next;
            }
        }

        i_node
    }

    fn compute_coords(
        &mut self,
        mut i_node: usize,
        n_nodes: usize,
        grid_extent: f32,
        points_extent: f32,
        points_origin: &Point<D>,
    ) {
        let cell_size = points_extent / grid_extent;
        let mut node_position = [0u32; D];

        for _ in 0..n_nodes {
            let node = &self.nodes[i_node];
            let node_size = cell_size * (1u32 << node.level) as f32;
            self.node_sizes[i_node] = node_size;
            self.point_refs[node.i_first_point_ref as usize]
                .morton
                .decode_at_level(node.level, &mut node_position);

            for ((x, x_node), x_origin) in self.node_positions[i_node]
                .iter_mut()
                .zip(node_position)
                .zip(points_origin)
            {
                *x = x_node as f32 * cell_size - 0.5 / grid_extent + x_origin + 0.5 * node_size;
            }

            i_node = node.i_next as usize;
        }
    }

    pub fn build(&mut self, positions: &[Point<D>]) {
        assert!(D > 1);

        let min_max = (0..D)
            .map(|d| {
                positions
                    .iter()
                    .map(|p| p[d])
                    .fold::<Option<[f32; 2]>, _>(None, |acc, elem| match acc {
                        Some([min, max]) => Some([min.min(elem), max.max(elem)]),
                        None => Some([elem, elem]),
                    })
                    .unwrap()
            })
            .collect::<Vec<_>>();

        let points_origin =
            Point::<D>::from_column_slice(&min_max.iter().map(|b| b[0]).collect::<Vec<_>>());

        let grid_extent = ((1u32 << (64 / D).min(24)) - 1) as f32;
        let points_extent = min_max
            .iter()
            .map(|[min, max]| max - min)
            .fold(f32::MIN, |max, value| max.max(value));
        let n_points = positions.len();

        if self.point_refs.len() != n_points {
            self.point_refs.resize(n_points, PointRef::default());
        }

        {
            let mut t = [0u32; D];
            for (i_point, (point_ref, point)) in
                self.point_refs.iter_mut().zip(positions).enumerate()
            {
                let point_in_grid = (point - points_origin) * grid_extent / points_extent;

                for (i, x) in t.iter_mut().enumerate() {
                    *x = point_in_grid[i] as u32;
                }

                *point_ref = PointRef {
                    i_node: 0,
                    i_point: i_point as u32,
                    morton: MortonCode::encode(&t),
                };
            }
        }
        self.point_refs.sort_by(|a, b| a.morton.cmp(&b.morton));

        let max_n_nodes = 2 * n_points;

        if self.nodes.len() != max_n_nodes {
            self.nodes.resize(max_n_nodes, SpatialTreeNode::default());
            self.node_sizes.resize(max_n_nodes, 0.0);
            self.node_positions.resize(max_n_nodes, Point::zeros());
            self.node_slots
                .resize(max_n_nodes * Self::MAX_CHILDREN_PER_NODE, 0);
        }
        self.nodes.fill(SpatialTreeNode::default());

        let (n_leaves, i_last_inner_node) = self.prepare_tree(n_points);
        self.i_root = self.build_hierarchy(n_points, 128, i_last_inner_node);

        {
            self.n_inner_nodes = restore_chain(self);

            self.compute_coords(
                n_points,
                self.n_inner_nodes,
                grid_extent,
                points_extent,
                &points_origin,
            );

            self.compute_coords(0, n_leaves, grid_extent, points_extent, &points_origin);
        }
    }

    pub fn i_children(&self, i_node: usize) -> &[u32] {
        let i_start = i_node * Self::MAX_CHILDREN_PER_NODE;
        &self.node_slots[i_start..i_start + self.nodes[i_node].n_children as usize]
    }

    pub fn node(&self, i_node: usize) -> &SpatialTreeNode {
        &self.nodes[i_node]
    }

    pub fn point_ref(&self, i_point_ref: usize) -> &PointRef<D> {
        &self.point_refs[i_point_ref]
    }

    pub fn node_center(&self, i_node: usize) -> &Point<D> {
        &self.node_positions[i_node]
    }

    pub fn node_size(&self, i_node: usize) -> f32 {
        self.node_sizes[i_node]
    }

    pub fn i_root(&self) -> usize {
        self.i_root
    }

    pub fn n_nodes(&self) -> usize {
        self.nodes.len() / 2 + self.n_inner_nodes
    }

    pub fn traverse_bottom_up<F: FnMut(usize)>(&self, kernel: &mut F, i_node: Option<usize>) {
        let i_node = i_node.unwrap_or(self.i_root);

        if self.nodes[i_node].n_children > 0 {
            for i_child in self.i_children(i_node) {
                self.traverse_bottom_up(kernel, Some(*i_child as usize));
            }
        }

        kernel(i_node);
    }

    pub fn is_empty(&self) -> bool {
        self.nodes.is_empty()
    }

    pub fn clear(&mut self) {
        self.n_inner_nodes = 0;
        self.nodes.clear();
        self.node_slots.clear();
        self.node_positions.clear();
        self.node_sizes.clear();
        self.point_refs.clear();
        self.i_root = 0;
    }

    pub fn traverse_top_down<F: FnMut(usize)>(&self, kernel: &mut F, i_node: Option<usize>) {
        let i_node = i_node.unwrap_or(self.i_root);

        kernel(i_node);

        if self.nodes[i_node].n_children > 0 {
            for i_child in self.i_children(i_node) {
                self.traverse_top_down(kernel, Some(*i_child as usize));
            }
        }
    }

    pub fn forall_ordered_pairs_of_children<F: FnMut(usize, usize)>(
        &self,
        kernel: &mut F,
        i_node: usize,
    ) {
        let n_children = self.node(i_node).n_children as usize;
        if n_children > 0 {
            let start = Self::MAX_CHILDREN_PER_NODE * i_node;
            let end = start + n_children;
            for i in start..end {
                for j in (i + 1)..end {
                    kernel(self.node_slots[i] as usize, self.node_slots[j] as usize);
                }
            }
        }
    }
}
