"""
Terraform-specific drift detection rules.

Each function in this module represents a single drift detection rule.
Rules are designed to be:
- Independent: Can run in any order
- Stateless: No shared state between rules
- Testable: Easy to unit test individually
- Extensible: Easy to add new rules following the same pattern

To add a new rule:
1. Create a function that takes (content: str) -> list[dict]
2. Return a list of issue dictionaries with required fields
3. Import and call it in analyze_terraform()
"""

import re
from typing import List
from .utils import (
    extract_resource_name,
    find_pattern_in_content,
    calculate_severity_base,
    extract_ami_id,
    extract_security_group_ids
)


def check_unrestricted_security_group(content: str) -> List[dict]:
    """
    Rule: Detect security groups allowing ingress from 0.0.0.0/0.
    
    This is a critical security issue as it exposes resources to the entire internet.
    We look for CIDR blocks of 0.0.0.0/0 in ingress rules.
    
    Returns:
        List of issue dictionaries for each unrestricted rule found
    """
    issues = []
    
    # Pattern to match cidr_blocks containing 0.0.0.0/0
    # Handles both quoted and unquoted, with optional whitespace
    pattern = r'cidr_blocks\s*=\s*\[?\s*["\']?0\.0\.0\.0/0["\']?'
    
    matches = find_pattern_in_content(content, pattern)
    
    for match_data in matches:
        # Try to extract which security group this belongs to
        # Look backwards from the match line to find the resource block
        lines = content.split('\n')
        match_line_num = match_data['line_number']
        
        # Search backwards for the security group resource definition
        resource_name = "aws_security_group.unknown"
        for i in range(max(0, match_line_num - 20), match_line_num):
            sg_match = re.search(r'resource\s+["\']aws_security_group["\']\s+["\']([^"\']+)["\']', lines[i])
            if sg_match:
                resource_name = f"aws_security_group.{sg_match.group(1)}"
                break
        
        issues.append({
            'rule_id': 'tf-unrestricted-sg',
            'title': 'Unrestricted Security Group Rule',
            'description': f'Security group allows ingress from 0.0.0.0/0 (entire internet) at line {match_line_num}. This exposes resources to potential attacks.',
            'severity': 'high',
            'resource': resource_name,
            'raw_detected_data': {
                'line': match_data['line'],
                'line_number': match_line_num,
                'pattern': '0.0.0.0/0'
            }
        })
    
    return issues


def check_missing_tags(content: str) -> List[dict]:
    """
    Rule: Detect resources missing tags block.
    
    Tagging is a best practice for AWS resource management, cost tracking, and organization.
    We check if common AWS resources have a tags block defined.
    
    Returns:
        List of issue dictionaries for resources missing tags
    """
    issues = []
    
    # Common AWS resources that should have tags
    taggable_resources = [
        r'aws_instance',
        r'aws_security_group',
        r'aws_s3_bucket',
        r'aws_lb',
        r'aws_ecs_service'
    ]
    
    for resource_pattern in taggable_resources:
        # Find all resource blocks of this type
        pattern = rf'resource\s+["\']?{resource_pattern}["\']?\s+["\']([^"\']+)["\']'
        resource_matches = re.finditer(pattern, content)
        
        for match in resource_matches:
            resource_name = match.group(1)
            resource_id = f"{resource_pattern.replace(r'\\', '')}.{resource_name}"
            
            # Get the content of this resource block
            # Find the opening brace and look for tags block within it
            start_pos = match.end()
            brace_count = 0
            block_start = -1
            block_end = -1
            
            for i in range(start_pos, len(content)):
                if content[i] == '{':
                    if brace_count == 0:
                        block_start = i
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        block_end = i
                        break
            
            if block_start != -1 and block_end != -1:
                resource_block = content[block_start:block_end]
                
                # Check if tags block exists
                tags_pattern = r'tags\s*=\s*\{'
                if not re.search(tags_pattern, resource_block):
                    issues.append({
                        'rule_id': 'tf-missing-tags',
                        'title': 'Missing Resource Tags',
                        'description': f'Resource {resource_id} is missing a tags block. Tags are essential for resource organization, cost allocation, and compliance.',
                        'severity': 'medium',
                        'resource': resource_id,
                        'raw_detected_data': {
                            'resource_type': resource_pattern.replace(r'\\', ''),
                            'resource_name': resource_name
                        }
                    })
    
    return issues


def check_hardcoded_secrets(content: str) -> List[dict]:
    """
    Rule: Detect hardcoded secrets or credentials in configuration.
    
    Looks for common patterns like AWS access keys, secret keys, API keys, etc.
    This is a critical security issue as secrets should never be in source code.
    
    Returns:
        List of issue dictionaries for each potential secret found
    """
    issues = []
    
    # Patterns that indicate hardcoded secrets
    secret_patterns = [
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
        (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', 'AWS Secret Access Key'),
        (r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}["\']?', 'API Key'),
        (r'password\s*[:=]\s*["\'][^"\']{8,}["\']', 'Password'),
        (r'secret[_-]?key\s*[:=]\s*["\'][^"\']{10,}["\']', 'Secret Key'),
    ]
    
    for pattern, secret_type in secret_patterns:
        matches = find_pattern_in_content(content, pattern)
        
        for match_data in matches:
            # Mask the actual secret in the description
            masked_match = match_data['match'][:8] + '...' if len(match_data['match']) > 8 else '***'
            
            issues.append({
                'rule_id': 'tf-hardcoded-secret',
                'title': f'Hardcoded {secret_type} Detected',
                'description': f'Potential hardcoded {secret_type.lower()} found at line {match_data["line_number"]}. Secrets should be stored in environment variables, secrets managers, or Terraform variables, never in code.',
                'severity': 'critical',
                'resource': extract_resource_name(content, 'terraform_config'),
                'raw_detected_data': {
                    'secret_type': secret_type,
                    'line_number': match_data['line_number'],
                    'line': match_data['line'].replace(match_data['match'], masked_match),  # Masked
                    'pattern_matched': pattern
                }
            })
    
    return issues


def check_outdated_ami(content: str) -> List[dict]:
    """
    Rule: Flag AMI usage (AMI IDs suggest potentially outdated images).
    
    While we can't determine actual AMI age without AWS API calls, using
    hardcoded AMI IDs is a code smell - they should be data sources or variables.
    This rule flags AMI usage for review.
    
    Returns:
        List of issue dictionaries for AMI usage
    """
    issues = []
    
    ami_id = extract_ami_id(content)
    if ami_id:
        # Check if it's hardcoded (not from a data source)
        ami_ref_pattern = rf'["\']?{re.escape(ami_id)}["\']?'
        
        # If AMI is referenced directly (not via data.aws_ami or var), flag it
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if ami_id in line:
                # Check if it's in a data source (which is fine)
                if 'data.aws_ami' in line or 'var.' in line:
                    continue
                
                issues.append({
                    'rule_id': 'tf-outdated-ami',
                    'title': 'Hardcoded AMI ID Detected',
                    'description': f'AMI {ami_id} is hardcoded at line {line_num}. Hardcoded AMI IDs can become outdated and pose security risks. Consider using data sources or variables to fetch the latest AMI dynamically.',
                    'severity': 'medium',
                    'resource': extract_resource_name(content, 'aws_instance', 'with_ami'),
                    'raw_detected_data': {
                        'ami_id': ami_id,
                        'line_number': line_num
                    }
                })
                break  # Only flag once per AMI
    
    return issues


def check_instance_count_drift(content: str) -> List[dict]:
    """
    Rule: Detect potential scaling issues or unexpected instance counts.
    
    Looks for autoscaling configurations and instance counts that might indicate
    drift between desired and actual state.
    
    Returns:
        List of issue dictionaries for scaling/drift concerns
    """
    issues = []
    
    # Check for autoscaling groups with min/max/desired capacity
    asg_pattern = r'resource\s+["\']aws_autoscaling_group["\']\s+["\']([^"\']+)["\']'
    asg_matches = re.finditer(asg_pattern, content)
    
    for match in asg_matches:
        asg_name = match.group(1)
        resource_id = f"aws_autoscaling_group.{asg_name}"
        
        # Extract the resource block
        start_pos = match.end()
        brace_count = 0
        block_start = -1
        block_end = -1
        
        for i in range(start_pos, min(len(content), start_pos + 2000)):
            if content[i] == '{':
                if brace_count == 0:
                    block_start = i
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    block_end = i
                    break
        
        if block_start != -1 and block_end != -1:
            asg_block = content[block_start:block_end]
            
            # Extract min, max, desired values
            min_match = re.search(r'min_size\s*=\s*(\d+)', asg_block)
            max_match = re.search(r'max_size\s*=\s*(\d+)', asg_block)
            desired_match = re.search(r'desired_capacity\s*=\s*(\d+)', asg_block)
            
            if min_match and max_match and desired_match:
                min_size = int(min_match.group(1))
                max_size = int(max_match.group(1))
                desired = int(desired_match.group(1))
                
                # Flag if desired is at boundaries (might indicate drift)
                if desired == min_size or desired == max_size:
                    issues.append({
                        'rule_id': 'tf-instance-count-drift',
                        'title': 'Potential Autoscaling Drift Risk',
                        'description': f'ASG {asg_name} has desired_capacity ({desired}) at boundary (min: {min_size}, max: {max_size}). This might indicate actual instances have drifted from desired state.',
                        'severity': 'low',
                        'resource': resource_id,
                        'raw_detected_data': {
                            'min_size': min_size,
                            'max_size': max_size,
                            'desired_capacity': desired
                        }
                    })
    
    return issues


def analyze_terraform(content: str) -> List[dict]:
    """
    Main entry point for Terraform analysis.
    
    Runs all Terraform-specific rules and aggregates the results.
    This function orchestrates the rule execution - add new rules here.
    
    Args:
        content: Terraform configuration content as a string
    
    Returns:
        List of all issue dictionaries found by all rules
    """
    all_issues = []
    
    # Execute all rules
    # Order doesn't matter since rules are independent
    all_issues.extend(check_unrestricted_security_group(content))
    all_issues.extend(check_missing_tags(content))
    all_issues.extend(check_hardcoded_secrets(content))
    all_issues.extend(check_outdated_ami(content))
    all_issues.extend(check_instance_count_drift(content))
    
    return all_issues

