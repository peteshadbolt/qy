""" pete.shadbolt@gmail.com """

import numpy as np
import itertools as it
from collections import defaultdict
from operator import add
try:
    from permanent import permanent
except ImportError:
    print "Fell back to a slow implementation of the permanent.\nSee http://github.com/peteshadbolt/permanent"

    def permanent(a):
        r = range(len(a))
        return sum([np.prod(a[r, p]) for p in it.permutations(r)])

ir2 = 1 / np.sqrt(2)
factorial = (1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800, 39916800)
precision = 1e-6

# TODO: these should be namedtuples for extra badass
spec = {
    "coupler":      {"size": 2,  "unitary": lambda p: directional_coupler(p["ratio"])},
    "phaseshifter": {"size": 1,  "unitary": lambda p: phase_shifter(p["phase"])},
    "crossing":     {"size": 2,  "unitary": lambda p: np.array([[0, 1], [1, 0]])},
    "source":       {"size": 1,  "state": lambda p: {(p["y"],): 1}},
    "bellpair":     {"size": 4,  "state": lambda p: bell_state(p["y"])},
    "detector":     {"size": 1, "pattern": lambda p: p["y"]}}

prototype = {"bottom": lambda p: p["y"] + p["size"],
             "x": lambda p: p["x"], "y": lambda p: p["y"]}


def directional_coupler(ratio):
    r = 1j * np.sqrt(ratio)
    t = np.sqrt(1 - ratio)
    return np.array([[t, r], [r, t]])


def phase_shifter(phase):
    return np.array([[np.exp(1j * phase)]])


def bell_state(y):
    return {(y, y + 2): ir2, (y + 1, y + 3): ir2}


def choose(n, k):
    return 0 if n < k else int(np.prod([(i + k) / i for i in range(1, n - k + 1)]) + .5)


def normalization(modes):
    """ Compute the normalization constant """
    table = defaultdict(int)
    for mode in modes:
        table[mode] += 1
    return np.prod([factorial[t] for t in table.values()])


def modes_to_index(modes, p, m):
    """ Maps a list of positions of p photons in m modes to an index.  After Nick Russell.  """
    mx = choose(m + p - 1, p)
    out = sum([choose(m - modes[p - i] + i - 2, i) for i in range(1, p + 1)])
    return mx - out - 1


def dtens(*terms):
    """ The tensor product, defined for states represented as dicts """
    output = defaultdict(complex)
    for q in it.product(*(t.items() for t in terms)):
        keys, amps = zip(*q)
        newkey = tuple(sorted(reduce(add, keys)))
        output[newkey] = np.prod(amps)
    return output


def dinner(a, b):
    """ Inner product of states represented as dicts """
    return sum([a[key] * b[key] for key in set(a.keys() + b.keys())])


def fill_gaps(component):
    """ Fills the gaps (size, unitary, state) in a dictionary representing a component. """
    c = component.copy()
    ctype = c["type"]
    for key, value in spec[ctype].items():
        c[key] = value(c) if callable(value) else value
    for key, value in prototype.items():
        c[key] = value(c) if callable(value) else value
    return c


def compile(json):
    """ Compiles a JSON description of a circuit to a state, unitary and a bunch of detection patterns """
    components = map(fill_gaps, json)
    components.sort(key=lambda c: c["x"])
    nmodes = max([c["bottom"] for c in components])

    # Compute the linear-optical unitary matrix
    unitary = np.eye(nmodes, dtype=complex)
    for key, column in it.groupby(components, key=lambda c: c["x"]):
        cu = np.eye(nmodes, dtype=complex)
        for component in [c for c in column if "unitary" in c]:
            p1 = component["y"]
            p2 = component["bottom"]
            cu[p1:p2, p1:p2] = component["unitary"]
        unitary = np.dot(cu, unitary)

    # Parse input states
    s = [c["state"] for c in components if "state" in c]
    input_state = dtens(*s)
    nphotons = 0 if len(input_state) == 0 else len(input_state.keys()[0])

    # TODO: Find all nonzero patterns by classical (fast) means
    p = [c["pattern"] for c in components if "pattern" in c]
    if p == []:
        p = range(nmodes)
    patterns = tuple(it.combinations_with_replacement(p, nphotons))

    # Return a compiled representation of the state
    return {"input_state": input_state, "unitary": unitary, "patterns": patterns, "nmodes": nmodes, "nphotons": nphotons}


def simulate(input_state, unitary, patterns, mode="probability", **kwargs):
    """ Simulates a given circuit, for a given input state, looking at certain terms in the output state """
    output_state = defaultdict(complex)
    u2 = np.abs(unitary) ** 2
    for cols, amplitude in input_state.items():
        cols = list(cols)
        n1 = normalization(cols)
        for rows in patterns:
            n2 = normalization(rows)
            perm = permanent(unitary[list(rows)][:, cols])
            value = amplitude * perm / np.sqrt(n1 * n2)
            if value != 0:
                output_state[rows] += value

    if mode == "probability":
        for key, value in output_state.items():
            output_state[key] = np.abs(value) ** 2
    return output_state

if __name__ == "__main__":
    import test
    test.test()
