import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, spectrogram

os.makedirs("figures", exist_ok=True)

VP, VS = 6.2, 3.6         



d = pd.read_csv("data/seismogram_A.csv")
print("Columns:", list(d.columns))

t = d.iloc[:, 0].to_numpy()          
Z = d["Z"].to_numpy()
N = d["N"].to_numpy()
E = d["E"].to_numpy()
fs = 1 / (t[1] - t[0])              
print(f"fs = {fs:.1f} Hz, duration = {t[-1] - t[0]:.1f} s, samples = {len(t)}")

fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 7))
for a, x, name in zip(ax, [Z, N, E], ["Z", "N", "E"]):
    a.plot(t, x * 1000)              
    a.set_ylabel(f"{name} (mm/s)")
ax[-1].set_xlabel("time (s)")
fig.suptitle("Step 1: raw record")
fig.savefig("figures/step1_channels.png", dpi=150)


fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 7))
m = t < 60
for a, x, name in zip(ax, [Z, N, E], ["Z", "N", "E"]):
    a.plot(t[m], x[m] * 1000)
    a.set_ylabel(f"{name} (mm/s)")
ax[-1].set_xlabel("time (s)")
fig.suptitle("Step 1: first 60 s (is the station really still?)")
fig.savefig("figures/step1_zoom60s.png", dpi=150)



X = np.fft.fft(Z)
f = np.fft.fftfreq(len(Z), d=1 / fs)
amp = np.abs(X) / len(Z) * 2         # /N : average size, *2 : mirror holds half

plt.figure(figsize=(10, 4))
plt.plot(amp)
plt.xlabel("index of the array")
plt.ylabel("amplitude")
plt.title("Step 2a: spectrum against index")
plt.savefig("figures/step2a_index.png", dpi=150)

plt.figure(figsize=(10, 4))
plt.plot(f, amp)
plt.xlabel("frequency (Hz)")
plt.ylabel("amplitude")
plt.title("Step 2a: spectrum against frequency (mirrored around 0 Hz)")
plt.savefig("figures/step2a_freq.png", dpi=150)


def spectrum(x):
    """Positive frequencies and amplitudes of a real signal."""
    F = np.fft.fftfreq(len(x), 1 / fs)
    A = np.abs(np.fft.fft(x)) / len(x) * 2
    p = F > 0
    return F[p], A[p]




fq, Aq = spectrum(Z[t < 60])
fw, Aw = spectrum(Z)
plt.figure(figsize=(10, 5))
plt.loglog(fq, Aq, label="quiet part (first 60 s)")
plt.loglog(fw, Aw, label="whole record")
plt.xlabel("frequency (Hz)")
plt.ylabel("amplitude")
plt.legend()
plt.title("Step 2b: spectra on log-log axes")
plt.savefig("figures/step2b_loglog.png", dpi=150)



def bandpass(x, fs, a, b):
    """Keep only frequencies between a and b Hz."""
    X = np.fft.fft(x)
    f = np.fft.fftfreq(len(x), 1 / fs)
    X[(np.abs(f) < a) | (np.abs(f) > b)] = 0   # delete everything outside a..b
    return np.fft.ifft(X).real



print("ifft(fft(Z)) == Z ?", np.allclose(np.fft.ifft(np.fft.fft(Z)).real, Z))


A_CUT, B_CUT = 0.5, 10
Zf = bandpass(Z, fs, A_CUT, B_CUT)
Nf = bandpass(N, fs, A_CUT, B_CUT)
Ef = bandpass(E, fs, A_CUT, B_CUT)



plt.figure(figsize=(10, 4))
plt.plot(t, (Z - Zf) * 1000)
plt.xlabel("time (s)")
plt.ylabel("Z - clean (mm/s)")
plt.title("Step 3c: what the filter removed")
plt.savefig("figures/step3c_removed.png", dpi=150)



plt.figure(figsize=(10, 4))
plt.plot(t, Z * 1000, alpha=0.5, label="raw Z")
plt.plot(t, Zf * 1000, label="filtered Z")
plt.xlabel("time (s)")
plt.ylabel("mm/s")
plt.legend()
plt.title("Step 3b: Z before and after the band-pass 0.5-10 Hz")
plt.savefig("figures/step3b_filtered.png", dpi=150)



def envelope(x, fs, win_s):
    """Moving average of |x| with a window of win_s seconds."""
    w = int(win_s * fs)              # seconds x samples/second = samples
    return np.convolve(np.abs(x), np.ones(w) / w, mode="same")


H = np.sqrt(Nf**2 + Ef**2)          
envZ = envelope(Zf, fs, 0.5)
envH = envelope(H, fs, 0.5)

plt.figure(figsize=(10, 4))
plt.plot(t, envZ * 1000, label="Z envelope")
plt.plot(t, envH * 1000, label="horizontal envelope")
plt.xlabel("time (s)")
plt.ylabel("mm/s")
plt.legend()
plt.title("Step 4: envelopes (window 0.5 s)")
plt.savefig("figures/step4_envelopes.png", dpi=150)

plt.figure(figsize=(10, 4))
for w in (0.05, 0.5, 5):
    plt.plot(t, envelope(Zf, fs, w) * 1000, label=f"window {w} s")
plt.xlabel("time (s)")
plt.ylabel("mm/s")
plt.legend()
plt.title("Step 4: three window lengths on Z")
plt.savefig("figures/step4_windows.png", dpi=150)



iP = np.argmax(envZ > 0.05 * envZ.max())
tP = t[iP]

i0 = np.searchsorted(t, tP + 2)      # start looking 2 s after tP
iS = i0 + np.argmax(envH[i0:] > 0.10 * envH.max())
tS = t[iS]

peaks, _ = find_peaks(envH, height=0.5 * envH.max())
t_max = t[peaks[np.argmax(envH[peaks])]]

print(f"tP = {tP:.2f} s")
print(f"tS = {tS:.2f} s")
print(f"time of the horizontal maximum = {t_max:.2f} s (tS is {t_max - tS:.1f} s earlier)")



fig, ax = plt.subplots(3, 1, sharex=True, figsize=(10, 7))
for a, x, name in zip(ax, [Z, N, E], ["Z", "N", "E"]):
    a.plot(t, x * 1000)
    a.axvline(tP, color="red", label="tP")
    a.axvline(tS, color="green", label="tS")
    a.set_ylabel(f"{name} (mm/s)")
ax[0].legend()
ax[-1].set_xlabel("time (s)")
fig.suptitle("Step 5: P and S arrivals")
fig.savefig("figures/step5_arrivals.png", dpi=150)


slowness = 1 / VS - 1 / VP           # s/km
R = (tS - tP) / slowness             # km
dR = 1.0 / slowness                  # km of change for 1 s error in tS
t0 = tP - R / VP                     # origin time (s)

print(f"R = {R:.1f} km")
print(f"1 s error in tS changes R by {dR:.1f} km")
print(f"origin time = {t0:.2f} s")


fsp, tsp, S = spectrogram(Z, fs=fs, nperseg=256)
plt.figure(figsize=(10, 5))
plt.pcolormesh(tsp, fsp, 10 * np.log10(S), shading="auto")
plt.ylim(0, 10)
plt.xlabel("time (s)")
plt.ylabel("frequency (Hz)")
plt.colorbar(label="power (dB)")
plt.title("Step 7: spectrogram of raw Z")
plt.savefig("figures/step7_spectrogram.png", dpi=150)


PGV = np.max(np.sqrt(N**2 + E**2)) * 100      # RAW data, m/s -> cm/s
M = (np.log10(PGV) + np.log10(R) + 1.0) / 0.55

print(f"PGV = {PGV:.3f} cm/s")
print(f"M = {M:.2f}")
print(f"If ignoring log10(R) at twice the distance, M would be off by "
      f"{np.log10(2) / 0.55:.2f}")
print(f"PGV factor for M + 1 at same distance: {10 ** 0.55:.2f}")

plt.close("all")
print("Done. Figures are in the figures/ folder.")