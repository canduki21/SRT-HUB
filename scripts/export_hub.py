import requests
import json
import os
from datetime import datetime, timezone

token = os.environ['GITHUB_TOKEN']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

QUERY = """
query($cursor: String) {
  repository(owner: "canduki21", name: "SRT-HUB") {
    discussionCategories(first: 10) {
      nodes { id name emoji slug }
    }
    discussions(first: 100, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        number
        title
        body
        author { login avatarUrl }
        category { name emoji slug }
        labels(first: 10) { nodes { name color } }
        comments(first: 50) {
          totalCount
          nodes {
            id
            body
            author { login avatarUrl }
            createdAt
          }
        }
        createdAt
        url
      }
    }
  }
}
"""

all_discussions = []
categories = []
cursor = None

while True:
    resp = requests.post(
        'https://api.github.com/graphql',
        headers=headers,
        json={'query': QUERY, 'variables': {'cursor': cursor}}
    )
    data = resp.json()
    if 'errors' in data:
        print('GraphQL error:', data['errors'])
        break

    repo = data['data']['repository']
    categories = repo['discussionCategories']['nodes']
    page = repo['discussions']
    all_discussions.extend(page['nodes'])

    if not page['pageInfo']['hasNextPage']:
        break
    cursor = page['pageInfo']['endCursor']

output = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'repo_id': 'R_kgDOTXasIg',
    'categories': categories,
    'discussions': all_discussions,
}

with open('hub-data.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Exported {len(all_discussions)} discussions, {len(categories)} categories")
