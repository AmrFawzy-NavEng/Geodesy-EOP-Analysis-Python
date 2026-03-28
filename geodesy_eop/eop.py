"""
Earth Orientation Parameters (EOP) Module
=========================================
Object-oriented primitives for downloading, parsing, and analyzing
IERS Earth Orientation Parameters (Polar Motion, UT1-UTC).
"""

import os
import requests
import numpy as np

class EOPManager:
    """
    Manages the retrieval and parsing of IERS EOP C04 data.
    """
    IERS_C04_URL = "https://hpiers.obspm.fr/iers/eop/eopc04/eopc04_IAU2000.62-now"

    def __init__(self, cache_file: str = "eopc04_IAU2000.txt"):
        self.cache_file = cache_file
        self.data: np.ndarray = np.array([])
        
    def download(self, force: bool = False) -> bool:
        """Downloads EOP data from IERS if not cached or forced."""
        if not force and os.path.exists(self.cache_file):
            return True
        
        response = requests.get(self.IERS_C04_URL)
        if response.status_code == 200:
            with open(self.cache_file, "w") as f:
                f.write(response.text)
            return True
        return False

    def load(self, max_year: int = 2100) -> np.ndarray:
        """
        Parses the cached EOP file up to a maximum year.
        Returns array columns: [MJD, xp, yp, UT1-UTC].
        """
        if not os.path.exists(self.cache_file):
            if not self.download():
                raise FileNotFoundError("Could not download EOP data.")

        parsed_data = []
        with open(self.cache_file, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 12 and parts[0].isdigit():
                    year = int(parts[0])
                    if year <= max_year:
                        mjd = float(parts[3])
                        xp = float(parts[4])
                        yp = float(parts[5])
                        ut1_utc = float(parts[6])
                        parsed_data.append([mjd, xp, yp, ut1_utc])
        
        self.data = np.array(parsed_data)
        return self.data


class EOPAnalyzer:
    """
    Performs spectral analysis and time conversions on EOP data.
    """
    def __init__(self, eop_data: np.ndarray):
        """
        Args:
            eop_data: Numpy array of shape (N, 4) -> [MJD, xp, yp, UT1-UTC].
        """
        self.mjd = eop_data[:, 0]
        self.xp = eop_data[:, 1]
        self.yp = eop_data[:, 2]
        self.ut1_utc = eop_data[:, 3]

    def convert_utc_to_ut1(self, target_mjd: float) -> tuple[float, float]:
        """
        Converts a given MJD from UTC to UT1.
        Returns: (mjd_ut1, offset_seconds)
        """
        idx = np.argmin(np.abs(self.mjd - target_mjd))
        offset_sec = self.ut1_utc[idx]
        mjd_ut1 = target_mjd + (offset_sec / 86400.0)
        return mjd_ut1, offset_sec

    def polar_motion_spectrum(self) -> dict:
        """
        Computes the single-sided amplitude spectrum of polar motion.
        Returns dictionary with frequencies, amplitudes, and Chandler parameters.
        """
        dt = np.mean(np.diff(self.mjd))
        n_samples = len(self.xp)
        
        xp_fft = np.fft.fft(self.xp)
        yp_fft = np.fft.fft(self.yp)
        
        freq = np.fft.fftfreq(n_samples, d=dt)
        cycles_per_year = freq * 365.25
        
        xp_amp = np.abs(xp_fft) / (n_samples / 2.0)
        yp_amp = np.abs(yp_fft) / (n_samples / 2.0)
        
        pos_idx = np.where(cycles_per_year > 0)
        cpy_pos = cycles_per_year[pos_idx]
        xp_amp_pos = xp_amp[pos_idx]
        yp_amp_pos = yp_amp[pos_idx]
        
        # Chandler wobble isolation (~1.2 years -> 0.7 to 1.0 cycles/year)
        mask = (cpy_pos > 0.7) & (cpy_pos < 1.0)
        if np.any(mask):
            chandler_idx = np.argmax(xp_amp_pos[mask])
            chandler_freq = cpy_pos[mask][chandler_idx]
            chandler_period_days = (1.0 / chandler_freq) * 365.25
            chandler_amp_arcsec = xp_amp_pos[mask][chandler_idx]
            chandler_amp_rad = chandler_amp_arcsec * (np.pi / (180.0 * 3600.0))
        else:
            chandler_period_days, chandler_amp_arcsec, chandler_amp_rad = 0, 0, 0
            
        return {
            'freq_cpy': cpy_pos,
            'xp_amp': xp_amp_pos,
            'yp_amp': yp_amp_pos,
            'chandler_period_days': float(chandler_period_days),
            'chandler_amp_arcsec': float(chandler_amp_arcsec),
            'chandler_amp_rad': float(chandler_amp_rad)
        }
