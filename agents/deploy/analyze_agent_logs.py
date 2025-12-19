#!/usr/bin/env python3
"""
Agent Log Analyzer
Analyzes logs from the Creative Director orchestrator to provide insights into agent interactions.
"""

import re
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple

def parse_logs(log_file: str) -> Dict:
    """Parse agent logs and extract key metrics"""

    metrics = {
        'agent_calls': [],
        'agent_responses': [],
        'errors': [],
        'total_calls': 0,
        'total_responses': 0,
        'agents_used': Counter(),
        'response_times': defaultdict(list),
        'response_sizes': defaultdict(list),
    }

    current_call = None

    with open(log_file, 'r') as f:
        for line in f:
            # Parse agent call
            if '🔧 AGENT CALL:' in line:
                match = re.search(r'AGENT CALL: (\w+)', line)
                if match:
                    agent_name = match.group(1)
                    current_call = {
                        'agent': agent_name,
                        'timestamp': None,
                        'query_length': 0,
                    }
                    metrics['total_calls'] += 1
                    metrics['agents_used'][agent_name] += 1

            # Parse timestamp for call
            elif 'Timestamp:' in line and current_call:
                match = re.search(r'Timestamp: ([\d\-T:\.]+)', line)
                if match:
                    current_call['timestamp'] = match.group(1)

            # Parse query length
            elif 'Query length:' in line and current_call:
                match = re.search(r'Query length: (\d+)', line)
                if match:
                    current_call['query_length'] = int(match.group(1))
                    metrics['agent_calls'].append(current_call)
                    current_call = None

            # Parse agent response
            elif '📥 AGENT RESPONSE:' in line:
                match = re.search(r'AGENT RESPONSE: (\w+) - (.*)', line)
                if match:
                    agent_name = match.group(1)
                    status = match.group(2).strip()

                    response_entry = {
                        'agent': agent_name,
                        'status': status,
                        'timestamp': None,
                        'response_length': 0,
                    }
                    metrics['total_responses'] += 1

                    # Track errors
                    if 'ERROR' in status:
                        metrics['errors'].append(response_entry)

            # Parse response length
            elif 'Response length:' in line:
                match = re.search(r'Response length: (\d+)', line)
                if match:
                    length = int(match.group(1))
                    if 'response_entry' in locals():
                        response_entry['response_length'] = length
                        metrics['response_sizes'][response_entry['agent']].append(length)
                        metrics['agent_responses'].append(response_entry)

    return metrics


def print_summary(metrics: Dict):
    """Print summary of agent interactions"""

    print("\n" + "=" * 70)
    print("AGENT LOG ANALYSIS SUMMARY")
    print("=" * 70)

    # Overall statistics
    print(f"\n📊 Overall Statistics:")
    print(f"  Total agent calls: {metrics['total_calls']}")
    print(f"  Total responses: {metrics['total_responses']}")
    print(f"  Errors: {len(metrics['errors'])}")

    # Agent usage breakdown
    print(f"\n🔧 Agent Usage:")
    for agent, count in metrics['agents_used'].most_common():
        print(f"  {agent}: {count} calls")

    # Response size analysis
    print(f"\n📏 Average Response Sizes:")
    for agent, sizes in metrics['response_sizes'].items():
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            print(f"  {agent}: {avg_size:.0f} chars (min: {min(sizes)}, max: {max(sizes)})")

    # Error details
    if metrics['errors']:
        print(f"\n❌ Errors Detected:")
        for error in metrics['errors']:
            print(f"  {error['agent']}: {error['status']}")
    else:
        print(f"\n✅ No errors detected!")

    # Workflow sequence
    print(f"\n📋 Workflow Sequence:")
    for i, call in enumerate(metrics['agent_calls'], 1):
        print(f"  {i}. {call['agent']} (query: {call['query_length']} chars)")

    print("\n" + "=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_agent_logs.py <log_file>")
        print("\nTo get logs from Cloud Run:")
        print("  gcloud logging read 'resource.type=\"aiplatform.googleapis.com/ReasoningEngine\"' \\")
        print("    --project=devfestahlen --limit=500 --format=json > orchestrator_logs.json")
        sys.exit(1)

    log_file = sys.argv[1]

    try:
        metrics = parse_logs(log_file)
        print_summary(metrics)
    except FileNotFoundError:
        print(f"Error: Log file '{log_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing logs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
