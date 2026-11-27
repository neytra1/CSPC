import pandas as pd

ev = pd.read_csv("results/events.csv")
lines = []
for _, r in ev.iterrows():
    lines.append(f"{r['file']}: P at {r['tP_s']:.1f} s, S at {r['tS_s']:.1f} s, "
                 f"distance {r['R_km']:.0f} km, magnitude {r['M']:.1f}.")
lines.append(f"Closer: {ev.loc[ev['R_km'].idxmin(), 'file']}")
lines.append(f"Stronger: {ev.loc[ev['M'].idxmax(), 'file']}")
open("results/report.txt", "w").write("\n".join(lines) + "\n")