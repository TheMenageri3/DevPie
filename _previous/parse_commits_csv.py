import csv
import matplotlib.pyplot as plt # type: ignore
from typing import Dict, Set
import glob
import os

# Function to process a single CSV file and generate a distribution plot
def process_csv(file_path: str):
    # Initialize dictionaries to store points and user ID to name mapping
    points = {}
    user_id_to_names: Dict[str, Set[str]] = {}

    # Keywords to check in commit messages
    keywords = ["boilerplate", "scaffolding", "scaffold", "scaff", "initial", "setup"]

    # Read the CSV file
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            author_id = row['Author ID']
            author_name = row['Author']
            committer_id = row['Committer ID']
            committer_name = row['Committer']
            lines_added = int(row['Lines Added'])
            lines_deleted = int(row['Lines Deleted'])
            commit_message = row['Message']

            # Check if the commit message contains any of the keywords
            if any(keyword in commit_message.lower() for keyword in keywords):
                author_points = 5
                committer_points = 5
            else:
                author_points = 100 + (25 * lines_added) + (50 * lines_deleted)
                committer_points = 100 + (25 * lines_added) + (50 * lines_deleted)

            # Update the user ID to names mapping
            if author_id not in user_id_to_names:
                user_id_to_names[author_id] = set()
            user_id_to_names[author_id].add(author_name)

            if committer_id not in user_id_to_names:
                user_id_to_names[committer_id] = set()
            user_id_to_names[committer_id].add(committer_name)

            # Exclude GitHub commits from calculations
            if "GitHub" in author_name:
                continue

            # Calculate points for the author
            if author_id not in points:
                points[author_id] = 0
            points[author_id] += author_points

            # Exclude GitHub commits from calculations
            if "GitHub" in committer_name:
                continue

            # Calculate points for the committer, excluding GitHub
            if committer_id not in points:
                points[committer_id] = 0
            points[committer_id] += committer_points

    # Generate the distribution pie chart
    labels = [f"{', '.join(user_id_to_names[user_id])} ({user_id})" for user_id in points.keys()]
    scores = list(points.values())

    plt.figure(figsize=(10, 5))
    plt.pie(scores, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Contribution Points Distribution', loc='left')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the plot as a PNG file
    output_file = os.path.splitext(file_path)[0] + '_distribution.png'
    plt.savefig(output_file)
    plt.close()

# Find all *_commits.csv files
csv_files = glob.glob('*_commits.csv')

# Process each CSV file
for csv_file in csv_files:
    process_csv(csv_file)