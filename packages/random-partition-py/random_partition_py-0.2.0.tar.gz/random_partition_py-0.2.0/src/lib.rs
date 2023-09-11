use numpy::PyArray2;
use pyo3::prelude::*;
use rand::Rng;
use random_partition as rs;
use rug::rand::RandState;

/// Generate a collection of uniformly distributed random integer partitions; optionally seed the RNG using the given seed.
///
/// # Returns
/// 2D array where each row represents a partition *with elements ordered in descending order*.
#[pyfunction]
#[pyo3(signature = (total, number_of_parts, number_of_partitions=1, *, seed=None))]
fn random_partitions(
    total: usize,
    number_of_parts: usize,
    number_of_partitions: usize,
    seed: Option<usize>,
) -> Py<PyArray2<usize>> {
    let mut rng = RandState::new();
    rng.seed(&seed.unwrap_or_else(|| rand::thread_rng().gen()).into());
    let parts = rs::random_partitions(&mut rng, total, number_of_parts, number_of_partitions);
    Python::with_gil(|py| PyArray2::from_owned_array(py, parts).into())
}

/// Generate approximately uniformly distributed random integer partitions
#[pymodule]
fn random_partition_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(random_partitions, m)?)?;
    Ok(())
}
