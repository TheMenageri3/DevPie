import requests
import csv
import matplotlib.pyplot as plt
from typing import Dict, Set
import os
import yaml # type: ignore

# Path to the user's local GitHub CLI configuration file
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

# Create directory for output files
output_dir = f'{owner}_{repo}'
os.makedirs(output_dir, exist_ok=True)

# Keywords to check in commit messages for boilerpolate 
keywords = ["boilerplate", "scaffolding", "scaffold", "scaff", "initial", "setup"]

# Function to fetch open issues from the repository
def fetch_open_issues():
    issues_url = f'{base_url}/issues'
    response = requests.get(issues_url, headers=headers)
    issues = response.json()
    open_issues = [issue for issue in issues if issue['state'] == 'open']
    return open_issues

# Function to fetch commit data and write to CSV
def fetch_and_write_commits():
    """
    Fetches commit data from a remote repository and writes it to a CSV file.

    This function performs the following steps:
    1. Fetches a list of commits from the repository.
    2. For each commit, retrieves detailed information including author, committer, date, message, 
       lines added, lines deleted, and verification status.
    3. Calculates a points score based on the commit message, lines added, lines deleted, and verification status.
    4. Writes the commit data to a CSV file.

    Returns:
        str: The name of the generated CSV file.
    """
    commits_url = f'{base_url}/commits'
    response = requests.get(commits_url, headers=headers)
    commits = response.json()

    csv_file_name = os.path.join(output_dir, f'{owner}_{repo}_commits.csv')
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["SHA", "Author", "Author ID", "Committer", "Committer ID", "Date", "Message", "Lines Added", "Lines Deleted", "Verified", "Points"])

        for commit in commits:
            sha = commit['sha']
            author = commit['commit']['author']['name']
            author_id = commit['author']['id'] if commit['author'] else None
            committer = commit['commit']['committer']['name']
            committer_id = commit['committer']['id'] if commit['committer'] else None
            date = commit['commit']['author']['date']
            message = commit['commit']['message']

            commit_url = f'{base_url}/commits/{sha}'
            commit_response = requests.get(commit_url, headers=headers)
            commit_details = commit_response.json()

            stats = commit_details.get('stats', {})
            lines_added = stats.get('additions', 0)
            lines_deleted = stats.get('deletions', 0)

            verification = commit_details['commit'].get('verification', {})
            verified = verification.get('verified', False)

            if any(keyword in message.lower() for keyword in keywords):
                points = 5
            else:
                points = 100 + (25 * lines_added) + (50 * lines_deleted)

            if verified:
                points += 25

            if "github" in author.lower():
                author_id = None
            if "github" in committer.lower():
                committer_id = None

            if author_id:
                writer.writerow([sha, author, author_id, committer, committer_id, date, message, lines_added, lines_deleted, verified, points])

    return csv_file_name

# Function to fetch contributors and write to CSV
def fetch_and_write_contributors():
    """
    Fetches the list of contributors from a specified URL and writes their details to a CSV file.

    The function retrieves contributor data from a given URL, filters out any contributors
    of type 'Bot', and writes the remaining contributors' login, ID, and number of contributions to a CSV file.

    Returns:
        str: The name of the CSV file created.
    """
    contributors_url = f'{base_url}/contributors'
    response = requests.get(contributors_url, headers=headers)
    contributors = response.json()

    csv_file_name = os.path.join(output_dir, f'{repo}_contributors.csv')
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Login", "ID", "Contributions"])

        for contributor in contributors:
            if contributor['type'] == 'Bot':
                continue
            login = contributor['login']
            user_id = contributor['id']
            contributions = contributor['contributions']
            writer.writerow([login, user_id, contributions])

    return csv_file_name

# Function to process a single CSV file and generate a distribution plot
def process_csv(file_path: str):
    """
    Processes a CSV file to calculate contribution points for authors and committers,
    generates a pie chart of the distribution, and saves it as an image file.

    The function excludes rows where the author or committer name contains "github" or "bot".
    It aggregates points for each unique author and committer, and generates a pie chart
    showing the distribution of points.

    Additionally, the function fetches open issues from a repository and lists them
    on the pie chart image.

    Returns:
        None
    """
    points = {}
    user_id_to_names: Dict[str, Set[str]] = {}

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            author_id = row['Author ID']
            author_name = row['Author']
            committer_id = row['Committer ID']
            committer_name = row['Committer']

            # Exclude GitHub or bot authors/committers
            if "github" in author_name.lower() or "bot" in author_name.lower():
                author_id = None
            if "github" in committer_name.lower() or "bot" in committer_name.lower():
                committer_id = None

            if author_id:
                points[author_id] = points.get(author_id, 0) + int(row['Points'])
                if author_id not in user_id_to_names:
                    user_id_to_names[author_id] = set()
                user_id_to_names[author_id].add(author_name)

            if committer_id:
                points[committer_id] = points.get(committer_id, 0) + int(row['Points'])
                if committer_id not in user_id_to_names:
                    user_id_to_names[committer_id] = set()
                user_id_to_names[committer_id].add(committer_name)

    labels = [f"{', '.join(user_id_to_names[user_id])} ({user_id})" for user_id in points.keys()]
    scores = list(points.values())

    plt.figure(figsize=(10, 5))
    plt.pie(scores, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Contribution Points Distribution', loc='left')
    plt.axis('equal')

    open_issues = fetch_open_issues()
    issues_text = "\n".join([f"- {issue['title']} (#{issue['number']})" for issue in open_issues])
    plt.gcf().text(0.02, 0.02, f"Open Issues:\n{issues_text}", fontsize=8, ha='left')

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '_distribution.png')
    plt.savefig(output_file)
    plt.close()

# Function to process contributors CSV and generate a bar graph
def process_contributors_csv(file_path: str):
    """
    Processes a CSV file containing contributor data and generates a bar chart
    showing the number of contributions for each contributor.

    """
    contributors = []
    contributions = []

    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contributors.append(f"{row['Login']}")
            contributions.append(int(row['Contributions']))

    plt.figure(figsize=(10, 5))
    bars = plt.bar(contributors, contributions)
    plt.xlabel('Contributors')
    plt.ylabel('Number of Contributions')
    plt.title(f'{repo} Contributors')
    plt.xticks(rotation=0)  # Set labels to be horizontal

    # Add labels on top of the bars
    for bar, contribution in zip(bars, contributions):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(contribution), ha='center', va='bottom')


    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '_contributions.png')
    plt.savefig(output_file)
    plt.close()

# Fetch commit data and write to CSV
csv_file_name = fetch_and_write_commits()

# Process the generated CSV file
process_csv(csv_file_name)

# Fetch contributors data and write to CSV
contributors_csv_file_name = fetch_and_write_contributors()

# Process the contributors CSV file
process_contributors_csv(contributors_csv_file_name)