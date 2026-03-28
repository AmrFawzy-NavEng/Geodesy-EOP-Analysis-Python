"""
Example 02: Geodesy - Earth Orientation Parameters (EOP) Analysis
=================================================================
Demonstrates the use of the `naveng.geodesy.eop` module for downloading IERS C04 data,
extracting the Chandler wobble using FFT, and converting time scales.
"""

import sys
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from datetime import datetime
import numpy as np

# Add the parent directory to the path so we can import naveng
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geodesy_eop import EOPManager, EOPAnalyzer

def main():
    print("--- 1. Initializing EOP Manager ---")
    eop_mgr = EOPManager(cache_file="eopc04_IAU2000.txt")
    
    print("Downloading / Loading IERS C04 EOP Data...")
    try:
        data = eop_mgr.load(max_year=2024)
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
    target_mjd = 57754.5 # Example epoch
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
    plt.savefig('polar_motion_trajectory.png', dpi=300)
    print("Saved 'polar_motion_trajectory.png'")

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
    plt.savefig('polar_motion_spectrum.png', dpi=300)
    print("Saved 'polar_motion_spectrum.png'")

if __name__ == "__main__":
    main()
