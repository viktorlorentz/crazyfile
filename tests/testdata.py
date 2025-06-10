import argparse
import numpy as np
from ruamel.yaml import YAML

def generate_data(n):
    states = np.random.random((n, 4)).tolist()
    actions = np.random.random((n, 2)).tolist()
    return {
        'delta': 42.0, # Example fixed value
        'human_readable': "Example human readable text",
        'result': [{
            'states': states,
            'actions': actions
        }]
    }

def main():
    parser = argparse.ArgumentParser(description="Generate test.yaml with random states/actions")
    parser.add_argument('-n','--num-states', type=int, required=True, help="Number of states to generate")
    parser.add_argument('-o','--output', default='test.yaml', help="Output YAML file path")
    args = parser.parse_args()

    data = generate_data(args.num_states)
    yaml = YAML()
    yaml.default_flow_style = False
    with open(args.output, 'w') as f:
        yaml.dump(data, f)

if __name__ == "__main__":
    main()
