"""Backward-compatible import for the generated CMS project generator.

The implementation now lives in ``builder.generators`` so callers can keep
using ``builder.project_generator.GeneratedCMSProjectGenerator`` unchanged.
"""

from .generators import GeneratedCMSProjectGenerator

__all__ = ['GeneratedCMSProjectGenerator']
