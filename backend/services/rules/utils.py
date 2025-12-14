"""
Utility functions for rule-based analysis.

These functions provide common operations needed across multiple rules,
such as regex pattern matching, resource extraction, and severity calculation.
"""

import re
from typing import Optional


def extract_resource_name(content: str, resource_type: str, resource_id: str = None) -> str:
    """
    Extract the resource identifier from Terraform/K8s content.
    
    This is a helper to standardize how we identify resources in our rules.
    In production, you might want to use proper parsers (hcl2, pyyaml for K8s).
    
    Args:
        content: The configuration content
        resource_type: Type of resource (e.g., "aws_security_group", "Deployment")
        resource_id: Optional specific resource ID to search for
    
    Returns:
        A resource identifier string for use in issue reports
    """
    # Simple pattern matching - can be enhanced with proper parsers later
    if resource_id:
        return f"{resource_type}.{resource_id}"
    
    # Try to find resource block
    pattern = rf'resource\s+["\']?{re.escape(resource_type)}["\']?\s+["\']([^"\']+)["\']'
    match = re.search(pattern, content)
    if match:
        return f"{resource_type}.{match.group(1)}"
    
    return resource_type


def find_pattern_in_content(content: str, pattern: str, case_sensitive: bool = False) -> list[dict]:
    """
    Search for a regex pattern in content and return matches with context.
    
    This helper makes it easy to find security-sensitive patterns like hardcoded
    credentials or misconfigurations across the codebase.
    
    Args:
        content: Text content to search
        pattern: Regex pattern to match
        case_sensitive: Whether the search should be case-sensitive
    
    Returns:
        List of dicts with 'match', 'line', 'line_number' for each occurrence
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        for match in re.finditer(pattern, line, flags):
            matches.append({
                'match': match.group(0),
                'line': line.strip(),
                'line_number': line_num
            })
    
    return matches


def calculate_severity_base(count: int, max_count: int = 5) -> str:
    """
    Calculate a base severity based on the number of occurrences.
    
    This provides a starting point for severity that can be adjusted by AI later.
    The logic is: more occurrences = higher severity.
    
    Args:
        count: Number of occurrences found
        max_count: Threshold for considering something "many" occurrences
    
    Returns:
        Severity string: "low", "medium", "high", or "critical"
    """
    if count == 0:
        return "low"
    elif count == 1:
        return "medium"
    elif count <= max_count:
        return "high"
    else:
        return "critical"


def extract_ami_id(content: str) -> Optional[str]:
    """
    Extract AMI ID from Terraform content.
    
    Looks for common patterns like ami-xxxxx in the content.
    This is useful for rules that need to check AMI versions.
    
    Args:
        content: Terraform configuration content
    
    Returns:
        First AMI ID found, or None
    """
    pattern = r'ami-[a-f0-9]{8,17}'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(0) if match else None


def extract_security_group_ids(content: str) -> list[str]:
    """
    Extract security group IDs or references from Terraform content.
    
    Finds both literal IDs (sg-xxxxx) and resource references (aws_security_group.xxx.id).
    
    Args:
        content: Terraform configuration content
    
    Returns:
        List of security group identifiers
    """
    # Find literal security group IDs
    pattern_sg_id = r'sg-[a-f0-9]{17}'
    sgs = re.findall(pattern_sg_id, content, re.IGNORECASE)
    
    # Find security group resource references
    pattern_sg_ref = r'aws_security_group\.([a-zA-Z0-9_-]+)'
    refs = re.findall(pattern_sg_ref, content)
    sgs.extend([f"aws_security_group.{ref}" for ref in refs])
    
    return list(set(sgs))  # Remove duplicates

