import requests
from datetime import datetime
import os

GITHUB_USER = "Lux-Jason"
README_FILE = "README.md"
TOKEN = os.getenv('GITHUB_TOKEN')

def get_repo_stats():
    headers = {'Authorization': f'token {TOKEN}'} if TOKEN else {}
    url = f"https://api.github.com/users/{GITHUB_USER}/repos"
    repos = requests.get(url, headers=headers).json()
    
    stats = {
        'total_repos': len(repos),
        'total_stars': sum(repo['stargazers_count'] for repo in repos),
        'languages': {},
        'recent_activity': []
    }

    for repo in repos:
        # Get language stats
        lang_url = repo['languages_url']
        langs = requests.get(lang_url, headers=headers).json()
        for lang, bytes in langs.items():
            stats['languages'][lang] = stats['languages'].get(lang, 0) + bytes

        # Get recent activity
        commits_url = f"{repo['url']}/commits"
        commits = requests.get(commits_url, headers=headers).json()
        if commits:
            latest_commit = commits[0]['commit']['committer']['date']
            stats['recent_activity'].append({
                'name': repo['name'],
                'last_commit': latest_commit
            })

    return stats

def update_readme(stats):
    with open(README_FILE, 'r') as f:
        content = f.read()

    # Update stats section
    stats_section = f"""## 📊 Real-time Stats

Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

- Total Repositories: {stats['total_repos']}
- Total Stars: {stats['total_stars']}
- Most Used Languages: {', '.join(sorted(stats['languages'].keys()))}

<div align="center">
![Language Stats](https://github-readme-stats.vercel.app/api/top-langs/?username={GITHUB_USER}&layout=compact&theme=radical)
![Project Activity](https://activity-graph.herokuapp.com/graph?username={GITHUB_USER}&theme=github)
</div>
"""

    # Find and replace stats section
    start_marker = "## 📊 Real-time Stats"
    end_marker = "## 💻 Tech Stack"
    new_content = content.split(start_marker)[0] + stats_section + content.split(end_marker)[1]

    with open(README_FILE, 'w') as f:
        f.write(new_content)

if __name__ == "__main__":
    stats = get_repo_stats()
    update_readme(stats)
