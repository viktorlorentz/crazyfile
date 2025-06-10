# crazyfile

A tiny Python tool to “crazy-compress” large lists inside YAML while leaving the rest human-readable.
It turns .yaml -> .crazy.yaml and .crazy.yaml -> .yaml.

In our tests, it can reduce the size of e.g. a yaml file with a list of 50000 states from 7,6 MB to 730KB, which is a 10x reduction in size with float16 precision and 1,5 MB with float32 precision.

It is useful for large lists that you want to keep in a human-readable format, but also want to compress for storage. We use numpy to compress numerical arrays to a given float precision.


It was designed for experiments with the crazyflie quadrotors at [IMRC LAB](https://imrclab.github.io), but can be used for any YAML files with large arrays with floating point values like this:

```yaml
readable_number: 42
some_text: "This is a human-readable text."
large_list:
  - 1.0
  - 2.0
  - 3.0
  - ...
  - 100.0
```
This will be compressed to a `.crazy.yaml` file like this keeping the human-readable parts intact, while drastically reducing the size of large lists:

```yaml
readable_number: 42
some_text: "This is a human-readable text."
large_list: !!binary |
    H4sIAH1ASGgC/5yb83tc69vFa7enZtomaTDaMxsPbtS2bdu2bds6tW0rtW2bp27f/f0X3vyUmcy1
    935urPVZuZIp5auVq1g....
```

## Installation
Install from local source:
```bash
pip install .
```
You can also just copy the `crazyfile.py` file into your project and use it directly.

For development dependencies and tests:
```bash
pip install -r requirements.txt pytest
```

## Usage

Convert a normal YAML to a `.crazy.yaml` (compressing lists >20 elements with numpy) via the `crazyfile` CLI:

```bash
crazyfile --to-crazy input.yaml output.crazy.yaml
```

Restore a `.crazy.yaml` back to plain YAML:

```bash
crazyfile --decompress output.crazy.yaml restored.yaml
```

You can override the default compression threshold of minimum list length:

```bash
crazyfile --to-crazy in.yaml out.crazy.yaml --threshold 50
```

## Custom float precision (dtype)

By default, crazyfile compresses numerical arrays using `float16`, which can shrink blob sizes by 5x - 15x compared to `float32` or `float64`. You can select the precision with the `--dtype` option:

```bash
crazyfile --to-crazy input.yaml output.crazy.yaml --dtype float16
crazyfile --to-crazy input.yaml output.crazy.yaml --dtype float32
```

## Use Crazyfile in Your Project

You can import `crazyfile` in your Python code to programmatically export `.crazy.yaml` files. Ensure the repository (or installed package) is on your `PYTHONPATH`. 

If you want you can also just copy the `crazyfile.py` file into your project and use it directly.

```python
from crazyfile import yaml_to_crazy, store_data_to_crazy

# Compress an existing YAML file to crazy format
yaml_to_crazy(
    "path/to/input.yaml",
    "path/to/output.crazy.yaml",
    threshold=30,            # minimum list length to compress
    dtype="float32"  # choose precision
)

# Compress an in-memory Python data structure
data = {
    "values": [1, 2, 3, ...],
    "np_array": np.array([1.0, 2.0, 3.0, ...])
}
store_data_to_crazy(
    data,
    "path/to/data.crazy.yaml",
    threshold=20,
    dtype="float16"
)
```

Adjust `threshold` and `dtype` as needed for your data.