import os
import numpy as np
import tempfile
import pytest
from ruamel.yaml import YAML

from crazyyaml import yaml_to_crazy, crazy_to_yaml, load_crazy, store_data_to_crazy
from testdata import generate_data

yaml = YAML()

def test_store_and_load_crazy(tmp_path):
    # Generate sample data and store to .crazy.yaml
    data = generate_data(10, 0.1, 0.2, 0.3)
    crazy_file = tmp_path / "data.crazy.yaml"
    store_data_to_crazy(data, str(crazy_file), threshold=5, dtype=np.dtype("float32"))

    # Load back and compare
    loaded = load_crazy(str(crazy_file))
    assert loaded == data


def test_yaml_to_crazy_and_back(tmp_path):
    # Generate larger data for compression
    data = generate_data(30, 1.1, 2.2, 3.3)
    input_yaml = tmp_path / "input.yaml"
    # Write normal YAML
    with open(input_yaml, 'w') as f:
        yaml.dump(data, f)

    # Compress to crazy YAML
    crazy_yaml = tmp_path / "input.crazy.yaml"
    yaml_to_crazy(str(input_yaml), str(crazy_yaml), threshold=10, dtype=np.dtype("float16"))
    text = crazy_yaml.read_text()
    # Ensure compression occurred
    assert "!!binary" in text

    # Decompress back to normal YAML
    output_yaml = tmp_path / "output.yaml"
    crazy_to_yaml(str(crazy_yaml), str(output_yaml))
    with open(output_yaml) as f:
        data_roundtrip = yaml.load(f)
    assert data_roundtrip == data


def test_threshold_effect(tmp_path):
    # With high threshold, no compression
    data = generate_data(3, 0.0, 0.0, 0.0)
    input_yaml = tmp_path / "small.yaml"
    with open(input_yaml, 'w') as f:
        yaml.dump(data, f)

    crazy_yaml = tmp_path / "small.crazy.yaml"
    yaml_to_crazy(str(input_yaml), str(crazy_yaml), threshold=100, dtype=np.dtype("float16"))
    text = crazy_yaml.read_text()
    # No binary blobs when threshold not reached
    assert "!!binary" not in text


def test_dtype_change(tmp_path):
    # Test that changing dtype still yields correct data
    data = generate_data(25, 5.5, 6.6, 7.7)
    input_yaml = tmp_path / "dtype.yaml"
    with open(input_yaml, 'w') as f:
        yaml.dump(data, f)

    crazy_yaml = tmp_path / "dtype.crazy.yaml"
    yaml_to_crazy(str(input_yaml), str(crazy_yaml), threshold=10, dtype=np.dtype("float32"))

    output_yaml = tmp_path / "dtype_out.yaml"
    crazy_to_yaml(str(crazy_yaml), str(output_yaml))
    with open(output_yaml) as f:
        data_out = yaml.load(f)
    assert data_out == data
