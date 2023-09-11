pub mod graph;

use graph::{
    layout::{
        multilevel::MultilevelLayout, multipole::MultipoleLayout, GraphLayoutAttributes,
        LayoutAlgorithm, RandomLayout,
    },
    Graph, NodePosition,
};
use rand::{rngs::StdRng, SeedableRng};

pub struct LayoutProps {
    pub lengths: Option<Vec<f32>>,
    pub random_seed: Option<u64>,
}

fn layout_connected_graph<const D: usize>(
    graph: Graph,
    LayoutProps {
        lengths,
        random_seed,
    }: LayoutProps,
) -> Vec<[f32; D]> {
    let mut rng = StdRng::seed_from_u64(random_seed.unwrap_or(42));
    let mut positions = vec![NodePosition::<D>::zeros(); graph.n_nodes()];

    let graph_attributes = GraphLayoutAttributes::new(&graph, None, lengths);

    RandomLayout::new(&mut rng, None).run(&graph, &mut positions, &graph_attributes);

    let mut mll = MultilevelLayout::default();
    mll.build(&mut rng, graph, graph_attributes);

    let mut mpl = MultipoleLayout::<D>::new(None, None, None, None, None);
    mll.run(&mut mpl, &mut rng, &mut positions);

    positions
        .iter()
        .map(|p| p.as_slice().try_into().unwrap())
        .collect()
}

#[derive(Clone, Default)]
struct RowInfo {
    width: f32,
    max_height: f32,
    boxes: Vec<usize>,
}

fn find_best_row<const D: usize>(rows: &mut [RowInfo], size: &[f32; D]) -> i32 {
    let mut total_width = 0.0;
    let mut total_height = 0.0;

    for row in rows.iter_mut() {
        if row.width > total_width {
            total_width = row.width;
        }
        total_height += row.max_height;
    }

    let mut best_row = -1;
    total_width = total_width.max(size[0]);
    total_height += size[1];

    let page_ratio = 1.0;
    let mut best_area = (page_ratio * total_height.powi(2)).max(total_width.powi(2) / page_ratio);

    for (i, row) in rows.iter().enumerate() {
        let w = row.width + size[0];
        let h = row.max_height.max(size[1]);
        let area = (page_ratio * h.powi(2)).max(w.powi(2) / page_ratio);

        if area < best_area {
            best_area = area;
            best_row = i as i32;
        }
    }

    best_row
}

fn get_box_offsets<const D: usize>(n_components: usize, sizes: &[[f32; D]]) -> Vec<[f32; 2]> {
    // Sort size indices in height descending order
    let mut size_ids_sorted = (0..sizes.len()).collect::<Vec<_>>();
    size_ids_sorted.sort_by(|a, b| sizes[*b][1].partial_cmp(&sizes[*a][1]).unwrap());

    let mut rows = Vec::<RowInfo>::with_capacity(n_components);
    for id in size_ids_sorted {
        let size = sizes[id];
        let i_best_row = find_best_row::<D>(&mut rows, &size);

        if i_best_row < 0 {
            rows.push(RowInfo {
                width: size[0],
                max_height: size[1],
                boxes: vec![id],
            });
        } else {
            let r = &mut rows[i_best_row as usize];
            r.boxes.push(id);
            r.width += size[0];
            r.max_height = r.max_height.max(size[1]);
        }
    }

    {
        let mut offsets = vec![[0.0, 0.0]; n_components];
        let mut y = 0.0;
        for row in rows {
            let mut x = 0.0;
            for i_box in row.boxes {
                offsets[i_box] = [x, y];
                x += sizes[i_box][0];
            }
            y += row.max_height;
        }
        offsets
    }
}

fn layout_disconnected_graph<const D: usize>(
    n_components: usize,
    nodes_to_components: Vec<u32>,
    graph: Graph,
    LayoutProps {
        lengths,
        random_seed,
    }: LayoutProps,
) -> Vec<[f32; D]> {
    #[derive(Clone)]
    struct GraphComponent {
        edges: Vec<[u32; 2]>,
        lengths: Option<Vec<f32>>,
    }

    let n_nodes = graph.n_nodes() as usize;

    let mut nodes_to_component_nodes = vec![0u32; n_nodes];
    let comp = GraphComponent {
        edges: Vec::new(),
        lengths: lengths.as_ref().map(|_| Vec::new()),
    };
    let mut components = vec![comp; n_components];
    let mut component_nodes_to_main_nodes: Vec<Vec<u32>> = vec![Vec::new(); n_components];

    for i_node in 0..n_nodes {
        let i_component = nodes_to_components[i_node] as usize;
        let to_main_nodes = &mut component_nodes_to_main_nodes[i_component];
        nodes_to_component_nodes[i_node] = to_main_nodes.len() as u32;
        to_main_nodes.push(i_node as u32);
    }

    for (i_edge, [i_a, i_b]) in graph.edges().iter().enumerate() {
        let i_component = nodes_to_components[*i_a as usize] as usize;
        let component = &mut components[i_component];
        component.edges.push([
            nodes_to_component_nodes[*i_a as usize],
            nodes_to_component_nodes[*i_b as usize],
        ]);
        if let Some(lengths) = lengths.as_ref() {
            component.lengths.as_mut().unwrap().push(lengths[i_edge]);
        }
    }

    let mut layouts = components
        .into_iter()
        .zip(&component_nodes_to_main_nodes)
        .map(|(component, to_main_nodes)| {
            layout_connected_graph::<D>(
                Graph::new(to_main_nodes.len() as u32, component.edges).unwrap(),
                LayoutProps {
                    lengths: component.lengths,
                    random_seed,
                },
            )
        })
        .collect::<Vec<_>>();

    let dim_bounds: Vec<[[f32; 2]; D]> = layouts
        .iter()
        .map(|layout| {
            (0..D)
                .map(|d| {
                    layout
                        .iter()
                        .map(|p| p[d])
                        .fold([f32::MAX, f32::MIN], |[min, max], v| {
                            [min.min(v), max.max(v)]
                        })
                })
                .collect::<Vec<_>>()
                .try_into()
                .unwrap()
        })
        .collect();

    let box_sizes = dim_bounds
        .iter()
        .map(|dims| dims.map(|[min, max]| max - min))
        .collect::<Vec<_>>();

    let pad_size = 0.01
        * box_sizes
            .iter()
            .map(|s| (0..D).map(|d| s[d] * s[d]).sum::<f32>().sqrt())
            .sum::<f32>();

    let padded_box_sizes: Vec<[f32; D]> = box_sizes
        .into_iter()
        .map(|s| {
            s.iter()
                .map(|x| x + 2.0 * pad_size)
                .collect::<Vec<_>>()
                .try_into()
                .unwrap()
        })
        .collect();

    let layout_mins: Vec<[f32; D]> = dim_bounds
        .iter()
        .map(|bounds| {
            bounds
                .iter()
                .map(|[min, ..]| *min)
                .collect::<Vec<_>>()
                .try_into()
                .unwrap()
        })
        .collect();

    for ((layout, offset), min) in layouts
        .iter_mut()
        .zip(get_box_offsets(n_components, &padded_box_sizes))
        .zip(layout_mins)
    {
        for p in layout {
            for d in 0..D {
                p[d] += pad_size + offset[d] - min[d];
            }
        }
    }

    {
        let mut positions = vec![[0f32; D]; graph.n_nodes()];
        for (to_main_nodes, layout) in component_nodes_to_main_nodes.into_iter().zip(layouts) {
            for (i_component_node, i_node) in to_main_nodes.iter().enumerate() {
                positions[*i_node as usize] = layout[i_component_node];
            }
        }
        positions
    }
}

pub fn layout<const D: usize>(
    n_nodes: u32,
    edges: Vec<[u32; 2]>,
    props: LayoutProps,
) -> Result<Vec<[f32; D]>, String> {
    let graph = Graph::new(n_nodes, edges)?;
    let (n_components, nodes_to_components) = graph.get_node_to_component_map();

    let layout = if n_components > 1 {
        layout_disconnected_graph(n_components, nodes_to_components, graph, props)
    } else {
        layout_connected_graph(graph, props)
    };

    Ok(layout)
}
