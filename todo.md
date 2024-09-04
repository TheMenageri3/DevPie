Overview
This document outlines the algorithm for assessing and awarding points to contributors based on their activities in the repository. The algorithm considers various endpoints and criteria to ensure fair and comprehensive evaluation.

Steps:

1. Assess Contributions
    - Use the /contributors endpoint to assess contributions.
    - Award points for lines added and deleted:
      - 2x points for deleted lines.
      - 1x points for added lines.
    - Remove undesired boilerplate points when querying the /commits endpoint.

2. Filter Commits
    - Query the /commits endpoint.
    - Exclude lines added or deleted in boilerplate and scaffolding code for authors and committers.
    - Exclude contributions from bots and GitHub.

3. Evaluate Commit Status
    - Check the status of commits:
      - Success: 100 points.
      - Failure: 10 points.
      - Pending: Continue processing but send an alert message and rerun once all commits are either success or failure.

4. Award Points
    - Authors: 100 points per commit.
    - Committers: 75 points per commit.
    - If the author is also the committer, they receive an additional 50 points (total 150 points).
    - Verified commits receive a bonus; unverified commits receive no bonus but are not penalized.

6. Reviewer and Commenter Points
    - Award points to reviewers:
      - 100 points for authors.
      - 75 points for committers.
    - Award points to commenters:
      - 10 points for each commenter with at least one comment on a commit or its associated PRs (maximum 10 points).

Additional Considerations:
- Use the /projects endpoint to consider the repository's projects.
- From /activity or other available endpoints, add the user's type to the CSV.
- Use /repos/{owner}/{repo}/issues to list all currently open issues, including labels.
- Display issues in the final graph/dashboard for an overview.
- Associate repository issues with the commits and PRs that address them and award points for fixing issues.
- Award 1.5x points for new features compared to bug fixes.

Endpoints Used:
- /orgs/{org}/teams 
- /repos/{owner}/{repo}/contributors
- /repos/{owner}/{repo}/commits
- /repos/{owner}/{repo}/projects
- /repos/{owner}/{repo}/activity
- /repos/{owner}/{repo}/issues

Notes:
- Points for issues are not yet awarded but may be considered in the future.
- Bugs and other labels may be considered, especially if associated with a commit/PR.
- This documentation provides a structured approach to evaluating contributions, ensuring a fair and comprehensive assessment of all activities within the repository.
