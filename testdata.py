import argparse
import numpy as np
from ruamel.yaml import YAML

def generate_data(n, delta, epsilon, cost):
    states = np.random.random((n, 4)).tolist()
    actions = np.random.random((n, 2)).tolist()
    return {
        'delta': delta,
        'epsilon': epsilon,
        'cost': cost,
        'result': [{
            'states': states,
            'actions': actions
        }]
    }

def main():
    parser = argparse.ArgumentParser(description="Generate test.yaml with random states/actions")
    parser.add_argument('-n','--num-states', type=int, required=True, help="Number of states to generate")
    parser.add_argument('-o','--output', default='test.yaml', help="Output YAML file path")
    parser.add_argument('--delta', type=float, default=0.5)
    parser.add_argument('--epsilon', type=float, default=1.0)
    parser.add_argument('--cost', type=float, default=11.0)
    args = parser.parse_args()

    data = generate_data(args.num_states, args.delta, args.epsilon, args.cost)
    yaml = YAML()
    yaml.default_flow_style = False
    with open(args.output, 'w') as f:
        yaml.dump(data, f)

if __name__ == "__main__":
    main()
