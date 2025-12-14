"""
Kubernetes-specific drift detection rules.

Each function represents a single drift detection rule for Kubernetes manifests.
Rules analyze YAML content for common misconfigurations and drift indicators.

To add a new rule:
1. Create a function that takes (content: str) -> list[dict]
2. Return a list of issue dictionaries with required fields
3. Import and call it in analyze_kubernetes()
"""

import re
import yaml
from typing import List, Optional, Any
from .utils import extract_resource_name, calculate_severity_base


def safe_yaml_load(content: str) -> Optional[Any]:
    """
    Safely parse YAML content, handling errors gracefully.
    
    Returns:
        Parsed YAML object, or None if parsing fails
    """
    try:
        # Handle multi-document YAML (separated by ---)
        documents = []
        for doc in yaml.safe_load_all(content):
            if doc:
                documents.append(doc)
        return documents if len(documents) > 1 else (documents[0] if documents else None)
    except yaml.YAMLError:
        return None


def check_latest_image_tag(content: str) -> List[dict]:
    """
    Rule: Detect containers using :latest image tag.
    
    Using :latest tag makes it impossible to track which version is deployed
    and can lead to unpredictable updates and drift.
    
    Returns:
        List of issue dictionaries for each :latest image found
    """
    issues = []
    
    # Pattern to match image: something:latest
    pattern = r'image:\s*["\']?([^"\'\s:]+):latest["\']?'
    matches = re.finditer(pattern, content, re.IGNORECASE)
    
    for match in matches:
        image_name = match.group(1)
        
        # Try to determine which resource this belongs to
        lines = content.split('\n')
        match_line_num = content[:match.start()].count('\n') + 1
        
        # Look backwards for resource type and name
        resource_type = "Container"
        resource_name = image_name
        
        for i in range(max(0, match_line_num - 30), match_line_num):
            line = lines[i]
            kind_match = re.search(r'kind:\s*([A-Za-z]+)', line)
            name_match = re.search(r'name:\s*([A-Za-z0-9-]+)', line)
            if kind_match:
                resource_type = kind_match.group(1)
            if name_match:
                resource_name = name_match.group(1)
        
        issues.append({
            'rule_id': 'k8s-latest-image',
            'title': 'Container Using :latest Image Tag',
            'description': f'Container image {image_name}:latest is using the :latest tag at line {match_line_num}. This makes version tracking impossible and can lead to unexpected updates and drift.',
            'severity': 'medium',
            'resource': f"{resource_type}/{resource_name}",
            'raw_detected_data': {
                'image': f"{image_name}:latest",
                'line_number': match_line_num,
                'resource_type': resource_type
            }
        })
    
    return issues


def check_missing_resource_limits(content: str) -> List[dict]:
    """
    Rule: Detect containers missing resource requests or limits.
    
    Missing resource constraints can lead to resource contention, unpredictable
    scheduling, and difficulty detecting resource drift.
    
    Returns:
        List of issue dictionaries for containers missing resource limits
    """
    issues = []
    
    parsed = safe_yaml_load(content)
    if not parsed:
        return issues
    
    # Handle both single documents and multi-document YAML
    documents = parsed if isinstance(parsed, list) else [parsed]
    
    for doc in documents:
        if not isinstance(doc, dict):
            continue
        
        kind = doc.get('kind', '')
        metadata = doc.get('metadata', {})
        resource_name = metadata.get('name', 'unknown')
        
        # Check for Pod or Deployment/StatefulSet/DaemonSet specs
        containers = []
        if kind == 'Pod':
            containers = doc.get('spec', {}).get('containers', [])
        elif kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'ReplicaSet']:
            containers = doc.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
        
        for container in containers:
            container_name = container.get('name', 'unknown')
            resources = container.get('resources', {})
            
            has_requests = bool(resources.get('requests'))
            has_limits = bool(resources.get('limits'))
            
            if not has_requests and not has_limits:
                issues.append({
                    'rule_id': 'k8s-missing-resources',
                    'title': 'Missing Resource Requests and Limits',
                    'description': f'Container {container_name} in {kind}/{resource_name} has no resource requests or limits defined. This can cause unpredictable resource allocation and scheduling issues.',
                    'severity': 'high',
                    'resource': f"{kind}/{resource_name}",
                    'raw_detected_data': {
                        'container_name': container_name,
                        'kind': kind,
                        'resource_name': resource_name
                    }
                })
            elif not has_requests:
                issues.append({
                    'rule_id': 'k8s-missing-requests',
                    'title': 'Missing Resource Requests',
                    'description': f'Container {container_name} in {kind}/{resource_name} has limits but no requests. Requests help with proper pod scheduling and resource allocation.',
                    'severity': 'medium',
                    'resource': f"{kind}/{resource_name}",
                    'raw_detected_data': {
                        'container_name': container_name,
                        'kind': kind,
                        'resource_name': resource_name
                    }
                })
    
    return issues


def check_privileged_container(content: str) -> List[dict]:
    """
    Rule: Detect containers running in privileged mode.
    
    Privileged containers have extensive host access and pose significant
    security risks. This should only be used when absolutely necessary.
    
    Returns:
        List of issue dictionaries for privileged containers
    """
    issues = []
    
    # Pattern to match securityContext with privileged: true
    pattern = r'privileged:\s*true'
    matches = re.finditer(pattern, content, re.IGNORECASE)
    
    for match in matches:
        match_line_num = content[:match.start()].count('\n') + 1
        lines = content.split('\n')
        
        # Find the container and resource this belongs to
        container_name = "unknown"
        resource_type = "Pod"
        resource_name = "unknown"
        
        # Look backwards for context
        for i in range(max(0, match_line_num - 40), match_line_num):
            line = lines[i]
            
            name_match = re.search(r'name:\s*([A-Za-z0-9-]+)', line)
            kind_match = re.search(r'kind:\s*([A-Za-z]+)', line)
            
            if kind_match:
                resource_type = kind_match.group(1)
            if name_match:
                if 'container' in lines[max(0, i-5):i+1] and any('containers:' in l for l in lines[max(0, i-10):i]):
                    container_name = name_match.group(1)
                elif resource_name == "unknown":
                    resource_name = name_match.group(1)
        
        issues.append({
            'rule_id': 'k8s-privileged-container',
            'title': 'Privileged Container Detected',
            'description': f'Container {container_name} in {resource_type}/{resource_name} is running in privileged mode (line {match_line_num}). Privileged containers have extensive host access and pose significant security risks.',
            'severity': 'critical',
            'resource': f"{resource_type}/{resource_name}",
            'raw_detected_data': {
                'container_name': container_name,
                'line_number': match_line_num,
                'resource_type': resource_type,
                'resource_name': resource_name
            }
        })
    
    return issues


def check_hostpath_volumes(content: str) -> List[dict]:
    """
    Rule: Detect HostPath volume usage.
    
    HostPath volumes mount host filesystem into pods, which can be a security
    risk and cause issues with pod scheduling across nodes (drift).
    
    Returns:
        List of issue dictionaries for HostPath volumes
    """
    issues = []
    
    parsed = safe_yaml_load(content)
    if not parsed:
        return issues
    
    documents = parsed if isinstance(parsed, list) else [parsed]
    
    for doc in documents:
        if not isinstance(doc, dict):
            continue
        
        kind = doc.get('kind', '')
        metadata = doc.get('metadata', {})
        resource_name = metadata.get('name', 'unknown')
        
        # Get volumes from spec
        volumes = []
        if kind == 'Pod':
            volumes = doc.get('spec', {}).get('volumes', [])
        elif kind in ['Deployment', 'StatefulSet', 'DaemonSet']:
            volumes = doc.get('spec', {}).get('template', {}).get('spec', {}).get('volumes', [])
        
        for volume in volumes:
            if 'hostPath' in volume:
                volume_name = volume.get('name', 'unknown')
                host_path = volume.get('hostPath', {}).get('path', 'unknown')
                
                issues.append({
                    'rule_id': 'k8s-hostpath-volume',
                    'title': 'HostPath Volume Detected',
                    'description': f'Volume {volume_name} in {kind}/{resource_name} uses HostPath (path: {host_path}). HostPath volumes mount host filesystem and can cause security issues and pod scheduling constraints, leading to potential drift.',
                    'severity': 'high',
                    'resource': f"{kind}/{resource_name}",
                    'raw_detected_data': {
                        'volume_name': volume_name,
                        'host_path': host_path,
                        'kind': kind,
                        'resource_name': resource_name
                    }
                })
    
    return issues


def check_replica_mismatch(content: str) -> List[dict]:
    """
    Rule: Detect potential replica count drift indicators.
    
    Looks for replicas configurations that might indicate drift between
    desired and actual state (e.g., replicas set to 0, or very high values).
    
    Returns:
        List of issue dictionaries for replica concerns
    """
    issues = []
    
    # Pattern to match replicas: N
    pattern = r'replicas:\s*(\d+)'
    matches = re.finditer(pattern, content)
    
    for match in matches:
        replica_count = int(match.group(1))
        match_line_num = content[:match.start()].count('\n') + 1
        lines = content.split('\n')
        
        # Find the resource this belongs to
        resource_type = "Deployment"
        resource_name = "unknown"
        
        for i in range(max(0, match_line_num - 20), match_line_num):
            line = lines[i]
            kind_match = re.search(r'kind:\s*([A-Za-z]+)', line)
            name_match = re.search(r'name:\s*([A-Za-z0-9-]+)', line)
            
            if kind_match:
                resource_type = kind_match.group(1)
            if name_match:
                resource_name = name_match.group(1)
        
        # Flag if replicas are 0 (might indicate stopped/drifted state)
        if replica_count == 0:
            issues.append({
                'rule_id': 'k8s-replica-zero',
                'title': 'Replicas Set to Zero',
                'description': f'{resource_type}/{resource_name} has replicas set to 0. This might indicate the resource has been scaled down or drifted from desired state.',
                'severity': 'low',
                'resource': f"{resource_type}/{resource_name}",
                'raw_detected_data': {
                    'replicas': replica_count,
                    'line_number': match_line_num,
                    'resource_type': resource_type,
                    'resource_name': resource_name
                }
            })
        # Flag if replicas are very high (might indicate configuration drift)
        elif replica_count > 50:
            issues.append({
                'rule_id': 'k8s-replica-high',
                'title': 'Unusually High Replica Count',
                'description': f'{resource_type}/{resource_name} has {replica_count} replicas configured. This unusually high value might indicate configuration drift or a misconfiguration.',
                'severity': 'medium',
                'resource': f"{resource_type}/{resource_name}",
                'raw_detected_data': {
                    'replicas': replica_count,
                    'line_number': match_line_num,
                    'resource_type': resource_type,
                    'resource_name': resource_name
                }
            })
    
    return issues


def analyze_kubernetes(content: str) -> List[dict]:
    """
    Main entry point for Kubernetes analysis.
    
    Runs all Kubernetes-specific rules and aggregates the results.
    This function orchestrates the rule execution - add new rules here.
    
    Args:
        content: Kubernetes YAML manifest content as a string
    
    Returns:
        List of all issue dictionaries found by all rules
    """
    all_issues = []
    
    # Execute all rules
    # Order doesn't matter since rules are independent
    all_issues.extend(check_latest_image_tag(content))
    all_issues.extend(check_missing_resource_limits(content))
    all_issues.extend(check_privileged_container(content))
    all_issues.extend(check_hostpath_volumes(content))
    all_issues.extend(check_replica_mismatch(content))
    
    return all_issues

