# The Steane Code in 10 Questions

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MaldoAlberto/steane-code/blob/main/steane_demo.ipynb)

A hands-on, beginner-friendly demo of quantum error correction with the Steane [[7,1,3]] code.
No previous knowledge of error correction is needed: each new idea is explained the first time it appears.

**[Open the notebook](steane_demo.ipynb)**

## The 10 questions

1. Why can't we just copy the qubit and compare?
2. Then how do we find an error without looking?
3. How do we put one qubit into seven?
4. How do we ask the checks without measuring the data?
5. Does it really fix any single error?
6. And if two errors happen?
7. How much does it help with random noise?
8. Is there a point where the code stops helping?
9. Can we compute on the encoded qubit?
10. So why don't we have error-free quantum computers yet?

## What you will see

- The 4 + 1 = 5 trick: three parity checks name the broken qubit.
- A dynamic circuit (Qiskit) that finds and fixes all 21 single-qubit errors, tested from both |0_L⟩ and |+_L⟩.
- A stim simulation checked against an exact count: about 16 p² failures, helping below about 8 % noise
  (perfect checks).
- Noisy checks in a small memory experiment, with two decoders: the code still helps below about 5 %, and at low
  noise the decoder that reads the rounds together fails about half as often.
- Transversal H, S and CNOT, and why the T gate needs magic states.

The models are deliberately simple (noise on data qubits, noisy check answers). Errors spreading inside the
check circuits are explained but not simulated; see the notebook for the details.

## Run it

```bash
pip install -r requirements.txt
jupyter notebook steane_demo.ipynb
```

In Colab, the first code cell installs the missing packages automatically.
The notebook was tested with qiskit 2.2.3, qiskit-aer 0.17.2 and stim 1.14.0 (Python 3.9), and with qiskit 2.6.2,
qiskit-aer 0.18.2 and stim 1.16.0 (Python 3.11); all cells run in about 10 seconds. Newer stim versions draw
different random samples, so the simulated points move slightly; the exact curve and the conclusions do not.

## Files

| File | What it is |
|---|---|
| `steane_demo.ipynb` | The notebook (executed, with outputs). |
| `build_demo.py` | Generates the notebook; `python3 build_demo.py --execute` rebuilds and runs it. |
| `steane_sim.py` | Stand-alone simulation (stim + exact count) that writes `steane.json`. |
| `steane.json` | Data behind the social-media figure: failure rate versus noise and break-even point. |
| `figures/` | The social-media figure (`figures/images/`) and its script: `python3 figures/make_steane_beginner.py out`. |

## Related

- [shor-resource-estimate](https://github.com/MaldoAlberto/shor-resource-estimate): how many physical qubits
  Shor's algorithm needs, and why almost all of them go to error correction.

## References

- A. M. Steane, Phys. Rev. Lett. 77, 793 (1996).
- R. W. Hamming, Bell Syst. Tech. J. 29, 147 (1950).
- L. Postler et al., Nature 605, 675 (2022).
- Google Quantum AI and collaborators, Nature 638, 920 (2025).
- C. Gidney, Quantum 5, 497 (2021).

## License

MIT. Created by Alberto Maldonado Romo (@qalycat).
