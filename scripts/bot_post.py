import os
import sys
import random
import requests
from datetime import datetime, timezone

SUPABASE_URL = 'https://mtdpaiadnldbvaqmyteg.supabase.co'
SERVICE_KEY = os.environ['SUPABASE_SERVICE_KEY']

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

BOT_ID = '00000000-0000-0000-0000-000000000001'
BOT_EMAIL = 'SRT'

CAT_RESEARCH = 'f0689df7-1e03-4889-b746-38e44cf7278a'
CAT_QA = 'DIC_kwDOTXasIs4DBIEE'
CAT_IDEAS = 'DIC_kwDOTXasIs4DBIEF'
CAT_ACADEMIA = '98e92f54-2a8d-4fff-bf6a-cd0b02173cbf'


def sb_get(path):
    resp = requests.get(f'{SUPABASE_URL}/rest/v1/{path}', headers=headers)
    resp.raise_for_status()
    return resp.json()


def sb_post(path, data):
    resp = requests.post(f'{SUPABASE_URL}/rest/v1/{path}', headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()


def build_applications_body(title, authors, year, simulant, applications, url):
    if applications:
        bullets = '\n'.join(f'- {a}' for a in applications[:5])
    else:
        bullets = (
            f'- Further characterization of **{simulant}** properties\n'
            '- Benchmarking against other lunar simulants\n'
            '- Input data for lunar/planetary engineering models'
        )
    return (
        f'Based on *{title}* *{authors}, {year}*, here are some potential applications worth exploring:\n\n'
        f'{bullets}\n\n'
        f'What else could this research enable? Share your ideas below.\n\n'
        f'`{simulant}`\n\n'
        f'[→ Read the paper]({url})'
    )


def build_scientific_context_body(title, simulant, keywords, url):
    keyword_str = ', '.join(keywords[:4]) if keywords else 'regolith simulation'
    return (
        f'This paper contributes to the field of **lunar regolith simulation** by investigating '
        f'**{keyword_str}** using simulant {simulant}.\n\n'
        f'Understanding these properties is essential for mission planning, hardware testing, '
        f'and in-situ resource utilization (ISRU) research.\n\n'
        f'[→ Full paper]({url})'
    )


# Get already-posted paper IDs
posted = sb_get('bot_post_log?select=paper_id')
posted_ids = {row['paper_id'] for row in posted}

# Get unposted papers that have simulants
all_papers = sb_get('papers?select=id,title,authors,year,url,simulants,applications,keywords&simulants=not.is.null')
candidates = [p for p in all_papers if p['id'] not in posted_ids and p.get('simulants')]

if not candidates:
    print('No unposted papers available.')
    sys.exit(0)

paper = random.choice(candidates)
paper_id = paper['id']
title = paper['title']
authors = paper['authors'] or 'Unknown authors'
year = paper['year'] or ''
url = paper['url'] or ''
simulant = paper['simulants'][0]
applications = paper.get('applications') or []
keywords = paper.get('keywords') or []

posts = [
    {
        'title': f'📄 {title}',
        'body': f'*{authors}, {year}*\n\n`{simulant}`\n\n[→ Read the full paper]({url})',
        'category_id': CAT_RESEARCH,
        'simulant': simulant,
        'post_type': 'paper',
    },
    {
        'title': f'💬 Community question: {simulant}',
        'body': (
            f'> Inspired by: *{title}*\n\n'
            'If you were designing a follow-up study to this paper, what would you test next '
            '— and which simulant would you use? Drop your thoughts below 👇\n\n'
            f'[→ Read the paper]({url})'
        ),
        'category_id': CAT_QA,
        'simulant': simulant,
        'post_type': 'community_question',
    },
    {
        'title': f'💡 Applications: {simulant}',
        'body': build_applications_body(title, authors, year, simulant, applications, url),
        'category_id': CAT_IDEAS,
        'simulant': simulant,
        'post_type': 'applications',
    },
    {
        'title': f'🎓 Scientific context: {title}',
        'body': build_scientific_context_body(title, simulant, keywords, url),
        'category_id': CAT_ACADEMIA,
        'simulant': simulant,
        'post_type': 'scientific_context',
    },
]

now = datetime.now(timezone.utc).isoformat()

for p in posts:
    post_type = p.pop('post_type')
    p['author_id'] = BOT_ID
    p['author_email'] = BOT_EMAIL
    sb_post('hub_posts', p)
    sb_post('bot_post_log', {
        'paper_id': paper_id,
        'posted_at': now,
        'post_type': post_type,
    })
    print(f'  Posted [{post_type}]: {p["title"][:60]}')

print(f'Done — posted 4 entries for paper: {title[:80]}')
