"""
Geodesy Subpackage
==================
Contains primitives for handling Earth Orientation Parameters
and performing related spectral or time analyses.
"""

from .eop import EOPManager, EOPAnalyzer

__all__ = ['EOPManager', 'EOPAnalyzer']
