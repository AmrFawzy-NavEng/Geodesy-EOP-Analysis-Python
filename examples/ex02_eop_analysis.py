"""
Example 02: Geodesy - Earth Orientation Parameters (EOP) Analysis
=================================================================
Demonstrates using the `geodesy_eop` package to download IERS C04 data,
extract the Chandler wobble frequency via FFT, and convert time scales.

This example is fully self-contained — it automatically downloads data
from the IERS servers on first run.
"""

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from datetime import datetime
import numpy as np

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geodesy_eop import EOPManager, EOPAnalyzer

def main():
    print("--- 1. Initializing EOP Manager ---")
    cache_path = os.path.join(os.path.dirname(__file__), "eopc04_IAU2000.txt")
    eop_mgr = EOPManager(cache_file=cache_path)
    
    print("Downloading / Loading IERS C04 EOP Data...")
    try:
        data = eop_mgr.load()
        print(f"Successfully loaded {len(data)} daily epochs.")
    except Exception as e:
        print(f"Failed to load EOP data: {e}")
        return

    print("\n--- 2. Spectral Analysis ---")
    analyzer = EOPAnalyzer(eop_data=data)
    spectrum = analyzer.polar_motion_spectrum()
    
    print(f"Chandler Wobble Period: {spectrum['chandler_period_days']:.2f} days")
    print(f"Chandler Wobble Amplitude: {spectrum['chandler_amp_arcsec']:.6f} arcsec")
    print(f"Chandler Wobble Amplitude: {spectrum['chandler_amp_rad']:.10f} rad")

    print("\n--- 3. Time Scale Conversion ---")
    target_mjd = 57754.5  # Example epoch
    mjd_ut1, offset = analyzer.convert_utc_to_ut1(target_mjd)
    print(f"Target Epoch MJD (UTC): {target_mjd}")
    print(f"UT1 - UTC Offset:       {offset:.6f} s")
    print(f"Target Epoch MJD (UT1): {mjd_ut1:.6f}")

    print("\n--- 4. Visualizations ---")
    # 4.1 Plot Polar Motion Trajectory
    years = np.array([datetime.fromordinal(int(m - 2400000.5 + 2400001)) for m in analyzer.mjd])
    years_float = np.array([y.year + y.timetuple().tm_yday/365.25 for y in years])

    plt.figure(figsize=(10, 6))
    plt.plot(years_float, analyzer.xp, 'b-', label='xp', alpha=0.7)
    plt.plot(years_float, analyzer.yp, 'r-', label='yp', alpha=0.7)
    plt.title('Polar Motion Trajectory Tracking (IERS C04)')
    plt.xlabel('Year')
    plt.ylabel('Deviation (arcsec)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    out1 = os.path.join(os.path.dirname(__file__), 'polar_motion_trajectory.png')
    plt.savefig(out1, dpi=300)
    print(f"Saved '{out1}'")

    # 4.2 Plot FFT Spectrum
    plt.figure(figsize=(10, 6))
    plt.loglog(spectrum['freq_cpy'], spectrum['xp_amp'], 'b-', label='xp')
    plt.loglog(spectrum['freq_cpy'], spectrum['yp_amp'], 'r-', label='yp')
    plt.xlabel('Frequency (cycles per year)')
    plt.ylabel('Amplitude (arcsec)')
    plt.title('Single-Sided Amplitude Spectrum of Polar Motion')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    
    for axis in [plt.gca().xaxis, plt.gca().yaxis]:
        axis.set_major_formatter(ScalarFormatter())
        
    plt.tight_layout()
    out2 = os.path.join(os.path.dirname(__file__), 'polar_motion_spectrum.png')
    plt.savefig(out2, dpi=300)
    print(f"Saved '{out2}'")

if __name__ == "__main__":
    main()
