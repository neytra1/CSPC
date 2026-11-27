import numpy as np, pandas as pd

VP, VS = 6.2, 3.6

def bandpass(x, fs, a, b):
    X = np.fft.fft(x)
    f = np.fft.fftfreq(len(x), 1/fs)
    X[(np.abs(f) < a) | (np.abs(f) > b)] = 0
    return np.fft.ifft(X).real

def envelope(x, fs, win_s):
    w = int(win_s * fs)
    return np.convolve(np.abs(x), np.ones(w) / w, mode="same")

def analyse(csv_file):
    d = pd.read_csv(csv_file)
    t = d["time_s"].to_numpy()
    Z, N, E = (d[c].to_numpy() for c in ["Z", "N", "E"])
    fs = 1 / (t[1] - t[0])

    Zf, Nf, Ef = (bandpass(x, fs, 0.5, 10) for x in (Z, N, E))
    envZ = envelope(Zf, fs, 0.5)
    envH = envelope(np.sqrt(Nf**2 + Ef**2), fs, 0.5)

    iP = np.argmax(envZ > 0.05 * envZ.max());  tP = t[iP]
    i0 = np.searchsorted(t, tP + 2)
    iS = i0 + np.argmax(envH[i0:] > 0.10 * envH.max());  tS = t[iS]

    R = (tS - tP) / (1/VS - 1/VP)
    PGV = np.max(np.sqrt(N**2 + E**2)) * 100
    M = (np.log10(PGV) + np.log10(R) + 1.0) / 0.55
    return {"file": csv_file, "tP_s": tP, "tS_s": tS, "R_km": R,
            "PGV_cm_s": PGV, "M": M}

if __name__ == "__main__":
    rows = [analyse("data/seismogram_A.csv"), analyse("data/seismogram_B.csv")]
    pd.DataFrame(rows).to_csv("results/events.csv", index=False)