import os
import numpy as np
import tempfile
import pytest
from ruamel.yaml import YAML

from crazyfile import yaml_to_crazy, crazy_to_yaml, load_crazy, store_data_to_crazy
from testdata import generate_data

yaml = YAML()

def assert_data_equal(orig, loaded, rtol=1e-3, atol=1e-3):
    # Compare scalar fields exactly
    for key in ('delta', 'human_readable'):
        assert orig[key] == loaded[key]
    # Compare array fields with tolerance
    orig_states = np.array(orig['result'][0]['states'], dtype=float)
    loaded_states = np.array(loaded['result'][0]['states'], dtype=float)
    assert np.allclose(orig_states, loaded_states, rtol=rtol, atol=atol)
    orig_actions = np.array(orig['result'][0]['actions'], dtype=float)
    loaded_actions = np.array(loaded['result'][0]['actions'], dtype=float)
    assert np.allclose(orig_actions, loaded_actions, rtol=rtol, atol=atol)

def test_store_and_load_crazy(tmp_path):
    # Generate sample data and store to .crazy.yaml
    data = generate_data(10)
    crazy_file = tmp_path / "data.crazy.yaml"
    store_data_to_crazy(data, str(crazy_file), threshold=5, dtype=np.dtype("float32"))

    # Load back and compare
    loaded = load_crazy(str(crazy_file))
    # float32 precision => use tolerance
    assert_data_equal(data, loaded, rtol=1e-5, atol=1e-8)


def test_yaml_to_crazy_and_back(tmp_path):
    # Generate larger data for compression
    data = generate_data(30)
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
    # float16 precision => looser tolerance
    assert_data_equal(data, data_roundtrip, rtol=1e-2, atol=1e-3)


def test_threshold_effect(tmp_path):
    # With high threshold, no compression
    data = generate_data(3)
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
    data = generate_data(1000)
    input_yaml = tmp_path / "dtype.yaml"
    with open(input_yaml, 'w') as f:
        yaml.dump(data, f)

    crazy_yaml = tmp_path / "dtype.crazy.yaml"
    yaml_to_crazy(str(input_yaml), str(crazy_yaml), threshold=10, dtype=np.dtype("float32"))

    output_yaml = tmp_path / "dtype_out.yaml"
    crazy_to_yaml(str(crazy_yaml), str(output_yaml))
    with open(output_yaml) as f:
        data_out = yaml.load(f)
    # float32 precision => use tolerance
    assert_data_equal(data, data_out, rtol=1e-5, atol=1e-8)


def test_human_readable_and_delta_in_crazy_yaml(tmp_path):
    """Ensure human_readable text and delta value are present in .crazy.yaml"""
    data = generate_data(5)
    input_yaml = tmp_path / "input.yaml"
    with open(input_yaml, 'w') as f:
        yaml.dump(data, f)
    crazy_yaml = tmp_path / "input.crazy.yaml"
    yaml_to_crazy(str(input_yaml), str(crazy_yaml), threshold=1, dtype=np.dtype("float16"))
    text = crazy_yaml.read_text()
    assert data['human_readable'] in text
    assert f"delta: {data['delta']}" in text
