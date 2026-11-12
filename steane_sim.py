"""Steane [[7,1,3]] code: check that its 3 parity checks name the broken qubit, then simulate how
often the protected (logical) qubit fails versus a bare qubit.

Noise model (code capacity): each of the 7 qubits gets a depolarizing error with probability p,
stabilizers are measured perfectly, a lookup decoder fixes the qubit named by the syndrome.
One stim circuit per p: the logical qubit is entangled with a reference qubit, so bit-flip and phase-flip
failures are read from the same error pattern. The logical qubit fails if either happens.
Cross-check: exact enumeration of all 4^7 Pauli errors (exact_logical_error) gives the same curve.

Usage: python3 steane_sim.py [--json steane.json]
"""
import argparse, json

import numpy as np
import stim

# Hamming [7,4,3] checks; qubit k (1..7) is in check j if bit j of k is set -> syndrome = k in binary
CHECKS = [[k for k in range(1, 8) if k & bit] for bit in (4, 2, 1)]


def syndrome_names_qubit():
    """Every single-qubit flip gives a different 3-bit syndrome equal to its index."""
    out = {}
    for k in range(1, 8):
        s = [int(k in c) for c in CHECKS]
        out[k] = s
        assert s[0] * 4 + s[1] * 2 + s[2] == k
    return out


def pauli_product(P, qubits):
    return stim.target_combined_paulis([stim.target_x(q) if P == "X" else stim.target_z(q) for q in qubits])


def memory_circuit(p):
    """One circuit, one error pattern, both kinds of logical failure.
    Qubits 0-6 hold the code; qubit 7 is a reference that is entangled with the logical qubit by
    measuring X_L X_R and Z_L Z_R (X_L = X on all 7, Z_L = Z on all 7). After the noise we measure
    the 6 checks and the 2 logical pairs again: a change in Z_L Z_R is a logical bit flip, a change
    in X_L X_R a logical phase flip."""
    meas = []
    for P in ("X", "Z"):
        for ch in CHECKS:
            meas += pauli_product(P, [q - 1 for q in ch])
    meas += pauli_product("X", list(range(8)))         # X_L X_R
    meas += pauli_product("Z", list(range(8)))         # Z_L Z_R
    c = stim.Circuit()
    c.append("R", range(8))
    c.append("MPP", meas)                               # round 1: projects into the code (reference values)
    c.append("DEPOLARIZE1", range(7), p)                # noise on the 7 code qubits only
    c.append("MPP", meas)                               # round 2
    for j in range(6):                                  # detectors 0-2: X checks (see Z errors), 3-5: Z checks (see X errors)
        c.append("DETECTOR", [stim.target_rec(-8 + j), stim.target_rec(-16 + j)])
    c.append("OBSERVABLE_INCLUDE", [stim.target_rec(-1), stim.target_rec(-9)], 0)   # Z_L Z_R changed: bit flip
    c.append("OBSERVABLE_INCLUDE", [stim.target_rec(-2), stim.target_rec(-10)], 1)  # X_L X_R changed: phase flip
    return c


def logical_error(p, shots, seed):
    det, obs = memory_circuit(p).compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    # lookup decoder: flip the qubit the syndrome names; any single-qubit flip changes the 7-qubit logical
    guess_bit = det[:, 3:6].any(axis=1)                 # Z checks fired -> fix an X error
    guess_phase = det[:, 0:3].any(axis=1)               # X checks fired -> fix a Z error
    fail = (guess_bit != obs[:, 0]) | (guess_phase != obs[:, 1])
    return float(fail.mean()), int(fail.sum())


def exact_logical_error(p):
    """Exact failure probability: sum over all 4^7 Pauli errors with the same lookup decoder."""
    import itertools

    def fails(v):
        s = sum(b for b, ch in zip((4, 2, 1), CHECKS) if sum(v[q - 1] for q in ch) % 2)
        v = list(v)
        if s:
            v[s - 1] ^= 1
        return sum(v) % 2                               # zero syndrome left: odd weight = logical operator
    tot = 0.0
    for err in itertools.product(range(4), repeat=7):   # 0 I, 1 X, 2 Y, 3 Z
        w = sum(1 for e in err if e)
        if fails([e in (1, 2) for e in err]) or fails([e in (2, 3) for e in err]):
            tot += (1 - p) ** (7 - w) * (p / 3) ** w
    return tot


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json"); args = ap.parse_args()
    table = syndrome_names_qubit()
    print("1. syndrome = qubit number:", {k: "".join(map(str, v)) for k, v in table.items()})
    ps = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3]
    rows = []
    for i, p in enumerate(ps):
        shots = 2_000_000 if p < 0.01 else 400_000
        pl, k = logical_error(p, shots, seed=11 + i)
        ex = exact_logical_error(p)
        z = (pl - ex) / np.sqrt(ex * (1 - ex) / shots)
        rows.append({"p": p, "p_logical": pl, "failures": k, "shots": shots, "p_logical_exact": ex})
        print(f"   p = {p:<6} logical = {pl:.3e}  ({k} failures / {shots:,})  exact {ex:.3e}  "
              f"({z:+.1f} sigma)  pL/p^2 = {pl / p**2:.1f}")
    # break-even: where the protected qubit fails as often as a bare one, by bisection on the exact curve
    lo, hi = 0.02, 0.3
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if exact_logical_error(mid) < mid else (lo, mid)
    pbe = (lo + hi) / 2
    print(f"2. break-even (logical = bare) at p ~ {pbe:.3f}")
    if args.json:
        json.dump({"checks": CHECKS, "syndromes": table, "rows": rows, "break_even": pbe}, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
