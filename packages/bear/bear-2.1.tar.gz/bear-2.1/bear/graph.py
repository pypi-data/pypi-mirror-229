import graphviz
import yaml
from bear.pipeline import Pipeline
import inspect

from itertools import permutations


def words(letters):
    yield from map(''.join, permutations(letters, len(letters)))


def get_perms(word):
    result = set()
    for word in words(word):
        result.add(word)

    return result


def add_prefix(word, pre):
    return pre + '_' + word


def add_postfix(word, post):
    return word + '_' + post

def combine(w1, w2):
    return w1 + w2


path = 'C:/Users/Kourosh/AppData/Local/Temp/data.yaml'
with open(path, 'r') as file:
    data = yaml.safe_load(file)

dot = graphviz.Digraph()


# for name in data['inputs']:
#     dot.node(name, name)
#
# for name, task in data['tasks'].items():
#     dot.node(name, name)
#
# for name in data['outputs']:
#     dot.node(name, name)

def get_all_functions():
    current_module = inspect.getmodule(inspect.currentframe())
    module_attributes = dir(current_module)

    all_functions = {}
    for attr in module_attributes:
        if inspect.isfunction(getattr(current_module, attr)):
            all_functions[attr] = getattr(current_module, attr)

    # Initialize a dictionary to store imported module functions
    imported_functions = {}

    # Loop through imported modules
    for name, module in list(current_module.__dict__.items()):
        if inspect.ismodule(module):
            # Get all attributes (including functions) of the imported module
            module_attributes = dir(module)

            # Filter attributes to select only functions (methods) from the imported module
            for attr in module_attributes:
                if inspect.isfunction(getattr(module, attr)):
                    all_functions[attr] = getattr(module, attr)

    print(all_functions)
    return all_functions


def get_interface(data):
    inputs = set()
    outputs = set()
    all_functions = get_all_functions()

    for key, val in data['relationships'].items():
        if key not in all_functions:
            #import pdb;pdb.set_trace()
            inputs.add(key)

        if isinstance(val, list):
            for v in val:
                if v not in all_functions:
                    outputs.add(v)
                dot.edge(key, v)
        else:
            if val not in all_functions:
                outputs.add(val)
            dot.edge(key, val)

    # dot.render('graph', view=True)
    return inputs, outputs, all_functions


def runit(data, input_params):
    inputs, outputs, all_functions = get_interface(data)
    for params in input_params:
        if len(inputs) != len(params):
            raise Exception('Invalid number inputs. Data file expects {} inputs while you passed {} inputs. ' \
                            'Expected inputs: {}'.format(len(inputs), len(params), inputs
                                                         ))

    pipe = Pipeline()
    rels = data['relationships']
    for input in inputs:
        func_name = rels[input]
        func = all_functions[func_name]
        tasks = pipe.parallel_async(func, input_params)
        pipe.wait()
        for child in rels[func_name]:
            func = all_functions[child]
            input_params = []
            for task in tasks:
                for val in task.result:
                    print(val)
                    input_params.append((val, '?')) ################## ?
            # tasks = pipe.parallel_async(func, input_params)
            # pipe.wait()
            # for task in tasks:
            #     print(task.result)


if __name__ == '__main__':
    res = runit(data, [('abcd',), ('qwer',)])
    print(res)
