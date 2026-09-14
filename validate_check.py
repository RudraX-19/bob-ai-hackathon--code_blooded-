import yaml, sys

with open("submission.yaml") as f:
    data = yaml.safe_load(f)

errors = []
team = data.get("team", {})
if not team.get("name") or "YOUR_TEAM" in str(team.get("name", "")):
    errors.append("team.name is empty or still a placeholder")
lead = team.get("lead", {})
if not lead.get("name") or "YOUR_NAME" in str(lead.get("name", "")):
    errors.append("team.lead.name is empty or still a placeholder")
if not lead.get("email") or "@" not in str(lead.get("email", "")):
    errors.append("team.lead.email is empty or invalid")
sub = data.get("submission", {})
if not sub.get("title"):
    errors.append("submission.title is empty")
if not sub.get("problem_statement"):
    errors.append("submission.problem_statement is empty")
if not sub.get("solution_summary"):
    errors.append("submission.solution_summary is empty")

if errors:
    for e in errors:
        print("ERROR: " + e)
    sys.exit(1)

print("submission.yaml validation passed")
