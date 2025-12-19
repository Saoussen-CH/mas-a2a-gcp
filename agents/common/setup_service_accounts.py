#!/usr/bin/env python3
"""
Setup all service accounts for specialist agents
Creates service accounts with necessary IAM roles for Cloud Run deployment
"""

import subprocess
import sys
from typing import List
from pathlib import Path

# Import env_utils from same directory
sys.path.insert(0, str(Path(__file__).parent))
import env_utils


# Service account configuration for all 5 specialist agents
AGENTS = [
    {"name": "brand-strategist", "display_name": "Brand Strategist Agent Service Account"},
    {"name": "copywriter", "display_name": "Copywriter Agent Service Account"},
    {"name": "designer", "display_name": "Designer Agent Service Account"},
    {"name": "critic", "display_name": "Critic Agent Service Account"},
    {"name": "project-manager", "display_name": "Project Manager Agent Service Account"},
]


def run_command(cmd: List[str], check=True) -> subprocess.CompletedProcess:
    """
    Run a shell command and return the result

    Args:
        cmd: Command as list of strings
        check: Whether to raise exception on failure

    Returns:
        CompletedProcess result
    """
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        if "already exists" not in result.stderr:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)

    return result


def service_account_exists(sa_name: str, project_id: str) -> bool:
    """
    Check if a service account already exists

    Args:
        sa_name: Service account name (without @project.iam.gserviceaccount.com)
        project_id: GCP project ID

    Returns:
        True if service account exists
    """
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    result = run_command(
        ["gcloud", "iam", "service-accounts", "describe", sa_email, f"--project={project_id}"],
        check=False
    )
    return result.returncode == 0


def create_service_account_if_not_exists(name: str, display_name: str, project_id: str) -> str:
    """
    Create service account if it doesn't exist (idempotent)

    Args:
        name: Service account name
        display_name: Human-readable display name
        project_id: GCP project ID

    Returns:
        Service account email
    """
    sa_name = f"{name}-sa"
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"

    if service_account_exists(sa_name, project_id):
        print(f"✓ Service account {sa_email} already exists")
        return sa_email

    print(f"Creating service account: {sa_name}")
    run_command([
        "gcloud", "iam", "service-accounts", "create", sa_name,
        f"--display-name={display_name}",
        f"--project={project_id}"
    ])

    print(f"✓ Created service account: {sa_email}")
    return sa_email


def grant_iam_roles(service_account_email: str, project_id: str) -> None:
    """
    Grant necessary IAM roles to service account

    Args:
        service_account_email: Full service account email
        project_id: GCP project ID
    """
    roles = [
        "roles/aiplatform.user",  # Access to Vertex AI for Gemini
        "roles/run.invoker",  # Invoke Cloud Run services
    ]

    for role in roles:
        print(f"Granting role {role} to {service_account_email}")
        run_command([
            "gcloud", "projects", "add-iam-policy-binding", project_id,
            f"--member=serviceAccount:{service_account_email}",
            f"--role={role}",
            "--quiet"
        ])

    print(f"✓ Granted IAM roles to {service_account_email}")


def setup_all_service_accounts(project_id: str) -> None:
    """
    Setup service accounts for all 5 agents

    Args:
        project_id: GCP project ID
    """
    print("\n" + "=" * 70)
    print("Setting up service accounts for all specialist agents")
    print("=" * 70 + "\n")

    for agent in AGENTS:
        print(f"\n--- {agent['display_name']} ---")
        sa_email = create_service_account_if_not_exists(
            agent["name"],
            agent["display_name"],
            project_id
        )
        grant_iam_roles(sa_email, project_id)

    print("\n" + "=" * 70)
    print("✓ All service accounts setup complete!")
    print("=" * 70)


def main():
    """Main entry point"""
    print("Service Account Setup for AI Creative Studio\n")

    # Load environment configuration
    config = env_utils.load_env_file()

    try:
        env_utils.validate_required_vars(config)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set the required environment variables:")
        print("  GCP_PROJECT_ID - Your Google Cloud project ID")
        print("  GCP_REGION - Deployment region (default: us-central1)")
        sys.exit(1)

    project_id = config["PROJECT_ID"]

    # Check if gcloud is installed
    try:
        run_command(["gcloud", "version"], check=True)
    except FileNotFoundError:
        print("Error: gcloud CLI not found")
        print("Please install from: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)

    # Set project
    run_command(["gcloud", "config", "set", "project", project_id])

    # Setup all service accounts
    try:
        setup_all_service_accounts(project_id)
    except Exception as e:
        print(f"\nError during service account setup: {e}")
        sys.exit(1)

    print("\nService accounts are ready for deployment!")


if __name__ == "__main__":
    main()
