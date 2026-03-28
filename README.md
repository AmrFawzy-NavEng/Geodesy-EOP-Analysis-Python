# Geodesy-EOP-Analysis-Python

# Geodetic Tools (`naveng.geodesy`)

This module deals with complex Earth Observation primitives, focusing on the dynamic nature of Earth's rotation and orientation in space. 

## Earth Orientation Parameters (EOP)

The Earth's orientation is not strictly fixed relative to inertial space or even its own crust. The `EOPManager` and `EOPAnalyzer` classes abstract the retrieval and analysis of the IERS C04 celestial reference frame datasets.

### Mathematical & Physical Principles

**1. Polar Motion ($x_p, y_p$)**
Polar motion describes the movement of Earth's rotational axis relative to the crust. The two dominant periodic signals in this motion are the Annual Wobble (due to seasonal mass distributions) and the Chandler Wobble.
The analyzer isolates the **Chandler Wobble** by applying a Fast Fourier Transform (FFT). It isolates the frequency band $f \in [0.7, 1.0]$ cycles/year (corresponding to a period of ~433 days) to determine the Earth's free nutation amplitude.

**2. Time Scales ($UT1 - UTC$)**
Because the Earth's rotation rate fluctuates, Universal Time ($UT1$) slowly drifts from Coordinated Universal Time ($UTC$). The analyzer interpolates the $UT1-UTC$ offset from IERS datasets to accurately convert observation epochs into dynamically correct timeframes. This is absolutely critical for high-precision GNSS processing or orbit determination.

### Usage
Run `examples/ex02_eop_analysis.py` to seamlessly download the historical IERS dataset, plot the polar trajectories, and isolate the Chandler wobble frequency mathematically.
