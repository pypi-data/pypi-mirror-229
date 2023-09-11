use pyo3::{
    prelude::pymodule,
    pyfunction,
    types::{PyDict, PyList, PyModule, PySequence, PySet, PyString, PyTuple},
    wrap_pyfunction, IntoPy, Py, PyAny, PyObject, PyResult, Python,
};

#[pyfunction]
#[pyo3(signature = (obj, by_alias = false))]
fn make_mapping(py: Python, obj: PyObject, by_alias: Option<bool>) -> PyResult<Py<PyDict>> {
    let gyver_attrs = match obj.getattr(py, "__gyver_attrs__") {
        Ok(x) => x.extract::<Py<PyDict>>(py)?,
        Err(err) => return Err(err),
    };
    let should_alias = by_alias.unwrap_or(false);
    if let Ok(parser) = obj.getattr(py, "__parse_dict__") {
        let output = parser.call1(py, (by_alias,))?;
        let result = output.downcast::<PyDict>(py);
        return Ok(result?.into());
    }
    let result = PyDict::new(py);

    Python::with_gil(|py| {
        for (key, field) in gyver_attrs.into_ref(py) {
            let field_key = if should_alias {
                field.getattr("alias").unwrap().extract::<&PyString>()
            } else {
                key.extract::<&PyString>()
            }
            .unwrap();
            match obj.getattr(py, key.extract::<&PyString>().unwrap()) {
                Ok(value) => result.set_item(field_key, value).unwrap(),
                _ => (),
            };
        }
    });
    Ok(result.into())
}

#[pyfunction]
#[pyo3(signature = (value, by_alias = false))]
fn deserialize(py: Python, value: &PyAny, by_alias: bool) -> PyResult<PyObject> {
    if let Ok(parser) = value.getattr("__parse_dict__") {
        let result = parser.call1((by_alias,))?;
        Ok(result.into())
    } else if let Ok(sequence) = value.extract::<&PySequence>() {
        let result: &PyAny = if sequence.is_instance_of::<PyList>()? {
            let items = sequence
                .iter()?
                .map(|item| deserialize(py, item.unwrap(), by_alias))
                .collect::<PyResult<Vec<_>>>()?;
            PyList::new(py, items)
        } else if sequence.is_instance_of::<PyTuple>()? {
            let items = sequence
                .iter()?
                .map(|item| deserialize(py, item.unwrap(), by_alias))
                .collect::<PyResult<Vec<_>>>()?;
            PyTuple::new(py, items)
        } else if sequence.is_instance_of::<PySet>()? {
            let items = sequence
                .iter()?
                .map(|item| deserialize(py, item?, by_alias))
                .collect::<PyResult<Vec<_>>>()?;
            PySet::new(py, items.as_slice()).unwrap()
        } else {
            sequence
        };
        Ok(result.into())
    } else if let Ok(mapping) = value.extract::<&PyDict>() {
        let result = deserialize_mapping(py, mapping.into(), Some(by_alias))?;
        Ok(result.into())
    } else if let Ok(_) = value.getattr("__gyver_attrs__") {
        let mapping = make_mapping(py, value.into_py(py), Some(by_alias))?;
        let result = deserialize(py, mapping.extract(py)?, by_alias)?;
        Ok(result.into())
    } else {
        Ok(value.into())
    }
}
#[pyfunction]
fn deserialize_mapping(
    py: Python,
    mapping: &PyDict,
    by_alias: Option<bool>,
) -> PyResult<Py<PyDict>> {
    let result = PyDict::new(py);
    let should_alias = by_alias.unwrap_or(false);

    for (key, value) in mapping.iter() {
        let unwrapped = deserialize(py, value, should_alias)?;
        result.set_item(key, unwrapped)?;
    }

    Ok(result.into())
}

#[pymodule]
#[pyo3(name = "gattrs_converter")]
fn gyver_attrs_extras(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(make_mapping, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_mapping, m)?)?;

    Ok(())
}
