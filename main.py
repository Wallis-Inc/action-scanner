import csv
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from github import Auth, Github, UnknownObjectException
from github.ContentFile import ContentFile
from github.Repository import Repository


@dataclass
class Contributor:
    name: str | None
    email: str | None


@dataclass
class DetectedWorkflow:
    repsitory_name: str
    workflow_name: str
    contributors: list[Contributor]


load_dotenv()
token = os.getenv("GH_TOKEN")
if token is None:
    raise Exception("No Github token found.")


def contains_actions(action_name: str, file: ContentFile) -> bool:
    if file.type == "file" and file.name.endswith(".yml"):
        content = file.decoded_content.decode("utf-8")
        if action_name in content:
            return True

    return False


def get_contributors(repo: Repository) -> list[Contributor]:
    contributors: list[Contributor] = []
    for contributor in repo.get_contributors():
        if contributor is not None:
            contributors.append(
                Contributor(name=contributor.name, email=contributor.email)
            )

    return contributors


def export_workflows(workflows: list[DetectedWorkflow]):
    csv_file_path = "detected_workflows.csv"

    fieldnames = ["repository_name", "workflow_name", "contributors"]

    with open(csv_file_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for workflow in workflows:
            contributors_str = "; ".join(
                [f"{c.name} ({c.email})" for c in workflow.contributors]
            )

            writer.writerow(
                {
                    "repository_name": workflow.repsitory_name,
                    "workflow_name": workflow.workflow_name,
                    "contributors": contributors_str,
                }
            )

    print(f"Data successfully exported to {csv_file_path}")


auth = Auth.Token(token)
client = Github(auth=auth)

if __name__ == "__main__":
    action_name = input("Input the name of the action you are scanning for: ")
    impacted_workflows: list[DetectedWorkflow] = []

    for repo in client.get_organization("Wallis-Inc").get_repos():
        try:
            workflow_dir = repo.get_contents(".github/workflows")
            if not isinstance(workflow_dir, list):
                raise Exception("Workflow directory incorrectly initialized.")

            for file in workflow_dir:
                if contains_actions(action_name, file):
                    contributors = get_contributors(repo)
                    workflow = DetectedWorkflow(
                        repsitory_name=repo.name,
                        workflow_name=file.name,
                        contributors=contributors,
                    )
                    impacted_workflows.append(workflow)

        except UnknownObjectException:
            print(f"{repo.name} has no workflows folder.")

    export_workflows(impacted_workflows)
