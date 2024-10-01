import requests # type: ignore
import csv
import yaml # type: ignore
import os

# Path to the GitHub CLI configuration file
config_path = os.path.expanduser('~/.config/gh/hosts.yml')

# Read the GitHub API token from the configuration file
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
    token = config['github.com']['oauth_token']

# GitHub repository details
owner = 'Web3-Builders-Alliance'
repo = 'soda'
base_url = f'https://api.github.com/repos/{owner}/{repo}'

headers = {
    'Authorization': f'token {token}'
}

# Keywords to check in commit messages
keywords = ["boilerplate", "scaffolding", "scaffold", "scaff", "initial", "setup"]

# Fetch commit data
commits_url = f'{base_url}/commits'
commits_response = requests.get(commits_url, headers=headers)
commits = commits_response.json()

# Fetch contributor data
contributors_url = f'{base_url}/contributors'
contributors_response = requests.get(contributors_url, headers=headers)
contributors = contributors_response.json()

# Fetch issues data
issues_url = f'{base_url}/issues'
issues_response = requests.get(issues_url, headers=headers)
issues = issues_response.json()

# Format the CSV file name with the owner and repo values
csv_file_name = f'{owner}_{repo}_commits.csv'

# Open a CSV file to write the data
with open(csv_file_name, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(["SHA", "Author", "Author ID", "Committer", "Committer ID", "Date", "Message", "Lines Added", "Lines Deleted", "Verified", "Points"])

    # Write commit data
    for commit in commits:
        sha = commit['sha']
        author = commit['commit']['author']['name']
        author_id = commit['author']['id'] if commit['author'] else None
        committer = commit['commit']['committer']['name']
        committer_id = commit['committer']['id'] if commit['committer'] else None
        date = commit['commit']['author']['date']
        message = commit['commit']['message']

        # Fetch detailed commit information
        commit_url = f'{base_url}/commits/{sha}'
        commit_response = requests.get(commit_url, headers=headers)
        commit_details = commit_response.json()

        # Extract lines added and deleted
        stats = commit_details.get('stats', {})
        lines_added = stats.get('additions', 0)
        lines_deleted = stats.get('deletions', 0)

        # Extract verification details
        verification = commit_details['commit'].get('verification', {})
        verified = verification.get('verified', False)

        # Skip empty lines
        if not sha.strip() or not author.strip() or not committer.strip() or not date.strip() or not message.strip():
            continue

        # Evaluate points
        if any(keyword in message.lower() for keyword in keywords):
            points = 5
        else:
            points = 100 + (25 * lines_added) + (50 * lines_deleted)

        writer.writerow([sha, author, author_id, committer, committer_id, date, message, lines_added, lines_deleted, verified, points])

print(f"Commit data has been written to {csv_file_name}")