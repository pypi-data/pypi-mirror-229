use pyo3::{pyfunction, pymodule, PyResult, Python, wrap_pyfunction};
use pyo3::types::PyModule;

#[pyfunction]
fn convert_file(source_file: String, depth_file: String, infrared_file: String, alpha: f64, beta: f64) {
    dc_converter_tof::convert_file(source_file, depth_file, infrared_file, alpha, beta);
}


#[pymodule]
fn dc_converter(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(convert_file, m)?)?;
    Ok(())
}
