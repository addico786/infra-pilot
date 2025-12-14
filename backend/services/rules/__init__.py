"""
Rule engine for drift detection.

This module provides rule-based analysis for Terraform and Kubernetes configurations.
Rules are modular and easily extensible - add new rules by creating functions
that accept content (str) and return a list of issue dictionaries.
"""

from .terraform_rules import analyze_terraform
from .k8s_rules import analyze_kubernetes

__all__ = ["analyze_terraform", "analyze_kubernetes"]

