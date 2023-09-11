use fdlayout::LayoutProps;
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

#[pyfunction]
fn layout(
    py: Python,
    n_nodes: u32,
    edges: Vec<[u32; 2]>,
    lengths: Option<Vec<f32>>,
    random_seed: Option<u64>,
) -> PyResult<&PyTuple> {
    fdlayout::layout::<2>(
        n_nodes,
        edges,
        LayoutProps {
            lengths,
            random_seed,
        },
    )
    .map(|data| {
        PyTuple::new(
            py,
            &[
                data.iter().map(|p| p[0]).collect::<Vec<_>>(),
                data.iter().map(|p| p[1]).collect::<Vec<_>>(),
            ],
        )
    })
    .map_err(|msg| PyTypeError::new_err(msg))
}

#[pymodule]
#[pyo3(name = "fdlayout")]
fn module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(layout, m)?)?;
    Ok(())
}
