import io
import gzip
import base64
import argparse
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq
import numpy as np
import os

yaml = YAML()

# Default threshold above which lists get compressed
DEFAULT_THRESHOLD = 20
DEFAULT_DTYPE = 'float16'


def _compress_list(lst, threshold, dtype=DEFAULT_DTYPE):
    """
    Recursively compress lists longer than threshold into binary blobs.
    """
    if isinstance(lst, list):
        # First transform sub-elements
        new_list = []
        for item in lst:
            new_list.append(_compress_list(item, threshold, dtype))
        # If this list is large, compress it
        if len(new_list) > threshold:
            # Only compress if elements are not already compressed (bytes)
            if any(isinstance(item, bytes) for item in new_list):
                return new_list
            # apply requested dtype here
            arr = np.array(new_list, dtype=dtype)
            buf = io.BytesIO()
            # Save numpy array to buffer
            np.save(buf, arr, allow_pickle=False)
            comp = gzip.compress(buf.getvalue())
            return comp  # bytes -> emitted as !!binary
        return new_list
    elif isinstance(lst, dict):
        new_dict = {}
        for k, v in lst.items():
            new_dict[k] = _compress_list(v, threshold, dtype)
        return new_dict
    else:
        return lst


def _decompress_structure(node):
    """
    Recursively decompress binary blobs back into numpy arrays.
    """
    if isinstance(node, bytes):
        raw = gzip.decompress(node)
        arr = np.load(io.BytesIO(raw), allow_pickle=False)
        return arr.tolist()
    elif isinstance(node, list):
        return [_decompress_structure(v) for v in node]
    elif isinstance(node, dict):
        return {k: _decompress_structure(v) for k, v in node.items()}
    else:
        return node


def _apply_flow_style(node, flow_threshold=10):
    """
    Recursively wrap flat lists shorter than flow_threshold into flow-style sequences.
    """
    if isinstance(node, list):
        new_list = [_apply_flow_style(item, flow_threshold) for item in node]
        if all(not isinstance(item, (list, dict)) for item in new_list) and len(new_list) < flow_threshold:
            seq = CommentedSeq(new_list)
            seq.fa.set_flow_style()  # force [a, b, c] style
            return seq
        return new_list
    elif isinstance(node, dict):
        return {k: _apply_flow_style(v, flow_threshold) for k, v in node.items()}
    else:
        return node


def yaml_to_crazy(input_path, output_path, threshold=DEFAULT_THRESHOLD, dtype=DEFAULT_DTYPE):
    # Load normal YAML
    data = yaml.load(open(input_path))
    # Compress large lists
    cdata = _compress_list(data, threshold, dtype)
    # Write comment + crazy YAML
    with open(output_path, 'w') as f:
        f.write('# .crazy.yaml file. Use crazyfile.py --decompress to restore to normal YAML\n')
        yaml.dump(cdata, f)


def store_data_to_crazy(data, output_path, threshold=DEFAULT_THRESHOLD, dtype=DEFAULT_DTYPE):
    # Compress provided data structure
    cdata = _compress_list(data, threshold, dtype)
    with open(output_path, 'w') as f:
        f.write('# .crazy.yaml file. Use crazyfile.py --decompress to restore to normal YAML\n')
        yaml.dump(cdata, f)


def load_crazy(input_path):
    # Load .crazy.yaml including binary blobs
    data = yaml.load(open(input_path))
    return _decompress_structure(data)


def crazy_to_yaml(input_path, output_path):
    # Decompress then dump as regular YAML
    data = load_crazy(input_path)
    data = _apply_flow_style(data)                  # apply flow style to small lists
    with open(output_path, 'w') as f:
        yaml.dump(data, f)


def main():
    parser = argparse.ArgumentParser(description='Process .yaml and .crazy.yaml files.')
    parser.add_argument('--to-crazy', nargs='*', metavar=('IN', 'OUT'),
                        help='Convert normal YAML IN to crazy YAML OUT; if OUT omitted, auto-add .crazy before extension')
    parser.add_argument('--store-crazy', nargs=2, metavar=('IN_PY', 'OUT'),
                        help='Store Python data structure IN_PY to crazy YAML OUT')
    parser.add_argument('--load-crazy', metavar='IN',
                        help='Load crazy YAML IN and print Python representation')
    parser.add_argument('--decompress', nargs='*', metavar=('IN', 'OUT'),
                        help='Convert .crazy.yaml IN back to normal YAML OUT; if OUT omitted, auto-remove .crazy from name')
    parser.add_argument('--threshold', type=int, default=DEFAULT_THRESHOLD,
                        help=f'Array size threshold for compression (default {DEFAULT_THRESHOLD})')
    parser.add_argument('--dtype', default=DEFAULT_DTYPE,
                        help='NumPy dtype for floating point arrays (default float16)')
    args = parser.parse_args()
    # convert string name to actual NumPy dtype
    args.dtype = np.dtype(args.dtype)

    if args.to_crazy:
        if len(args.to_crazy) == 1:
            in_path = args.to_crazy[0]
            base, ext = os.path.splitext(in_path)
            out_path = f"{base}.crazy{ext}"
        elif len(args.to_crazy) == 2:
            in_path, out_path = args.to_crazy
        else:
            parser.error('argument --to-crazy: expected 1 or 2 arguments')

        if '.crazy' in os.path.basename(in_path):
            parser.error(f"Input '{in_path}' for --to-crazy must not contain '.crazy'")
        if '.crazy' not in os.path.basename(out_path):
            parser.error(f"Output '{out_path}' for --to-crazy must contain '.crazy'")
        yaml_to_crazy(in_path, out_path, args.threshold, args.dtype)

    elif args.store_crazy:
        # Expect a Python file IN_PY defining `data` variable
        module_path = args.store_crazy[0]
        spec = __import__(module_path.replace('.py', ''))
        data = getattr(spec, 'data')
        store_data_to_crazy(data, args.store_crazy[1], args.threshold, args.dtype)

    elif args.load_crazy:
        data = load_crazy(args.load_crazy)
        print(data)

    elif args.decompress:
        if len(args.decompress) == 1:
            in_path = args.decompress[0]
            out_path = in_path.replace('.crazy', '')
        elif len(args.decompress) == 2:
            in_path, out_path = args.decompress
        else:
            parser.error('argument --decompress: expected 1 or 2 arguments')

        if '.crazy' not in os.path.basename(in_path):
            parser.error(f"Input '{in_path}' for --decompress must contain '.crazy'")
        if '.crazy' in os.path.basename(out_path):
            parser.error(f"Output '{out_path}' for --decompress must not contain '.crazy'")
        crazy_to_yaml(in_path, out_path)

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
