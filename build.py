import os
import shutil
import markdown
import yaml
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from data import site_config, bio, skills, projects

def load_posts():
    posts = []
    posts_dir = 'content/posts'
    if not os.path.exists(posts_dir):
        return posts
        
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) == 3:
                metadata = yaml.safe_load(parts[1])
                md_content = parts[2]
                html_content = markdown.markdown(md_content, extensions=['fenced_code'])
                
                post = metadata
                post['slug'] = filename.replace('.md', '')
                post['html_content'] = html_content
                posts.append(post)
    
    # Sort by date desc
    posts.sort(key=lambda x: x.get('date', ''), reverse=True)
    return posts

import json
import urllib.request

def fetch_github_activity(username):
    try:
        url = f"https://api.github.com/users/{username}/events/public"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            # Get last 5 PushEvents or CreateEvents
            events = []
            for event in data:
                if event['type'] in ['PushEvent', 'CreateEvent', 'WatchEvent']:
                    events.append(event)
                    if len(events) >= 5:
                        break
            return events
    except Exception as e:
        print(f"⚠️ Could not fetch GitHub activity: {e}")
        return []

def build():
    # 1. Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    
    # 2. Output setup
    output_dir = 'docs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3. Render Home
    # Fetch GitHub activity (using a hardcoded username for now or from config)
    # Assuming 'kumar' is the placeholder, but let's use a real one or the config one if available.
    # Since we don't have a real username in config, I'll use a placeholder or ask the user.
    # For now, I'll use 'torvalds' (Linus Torvalds) as a demo or just empty if it fails.
    # Better: Use the author name from config if it looks like a username, or add it to config.
    # I'll add 'github_username' to data.py in a moment.
    
    github_activity = fetch_github_activity(site_config.get('github_username', 'google'))

    template_home = env.get_template('index.html')
    output_home = template_home.render(
        config=site_config,
        bio=bio,
        skills=skills,
        projects=projects,
        github_activity=github_activity,
        root_path='.'
    )
    with open(os.path.join(output_dir, 'index.html'), 'w') as f:
        f.write(output_home)
    print("✅ Generated docs/index.html")

    # 4. Render Blog Index & Posts
    posts = load_posts()
    
    # Blog Index
    template_blog = env.get_template('blog.html')
    output_blog = template_blog.render(
        config=site_config,
        posts=posts,
        root_path='.'
    )
    with open(os.path.join(output_dir, 'blog.html'), 'w') as f:
        f.write(output_blog)
    print("✅ Generated docs/blog.html")

    # Individual Posts
    posts_output_dir = os.path.join(output_dir, 'posts')
    if not os.path.exists(posts_output_dir):
        os.makedirs(posts_output_dir)
        
    template_post = env.get_template('post.html')
    for post in posts:
        output_post = template_post.render(
            config=site_config,
            post=post,
            root_path='..'
        )
        with open(os.path.join(posts_output_dir, f"{post['slug']}.html"), 'w') as f:
            f.write(output_post)
    print(f"✅ Generated {len(posts)} blog posts")

    # 5. Copy static assets
    static_src = 'static'
    static_dest = os.path.join(output_dir, 'static')
    
    if os.path.exists(static_dest):
        shutil.rmtree(static_dest)
    
    shutil.copytree(static_src, static_dest)
    print("✅ Copied static assets to docs/static")

if __name__ == "__main__":
    build()
