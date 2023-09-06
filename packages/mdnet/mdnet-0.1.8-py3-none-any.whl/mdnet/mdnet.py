import argparse
import frontmatter
import markdown
import yaml
import shutil
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
from datetime import date
from rss_generator import generate_xml

def convert_md_to_html(md):
    return markdown.markdown(md)

def get_template(template_path):
    try:
        template_dir = template_path.parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        return env.get_template(template_path.name)
    except TemplateNotFound:
        print(f"Error: Template not found at {template_path}")
        exit(1)

def render_template(template_path, **kwargs):
    template = get_template(template_path)
    return template.render(**kwargs)
    
def clear_output_directories(output_dir):
    """
    Clear the specified directories and files in the given output directory.
    
    Args:
    - output_dir (str/Path): The base directory where the output files and directories reside.
    """
    output_dir = Path(output_dir)
    
    # List of directories to clear
    directories_to_clear = ['posts', 'tags']
    
    # Clear each directory
    for directory in directories_to_clear:
        dir_path = output_dir / directory
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
    
    # Clear the index.html file
    index_file = output_dir / 'index.html'
    if index_file.exists() and index_file.is_file():
        index_file.unlink()

def generate_site(config):
    input_dir = Path(config['input_dir'])
    output_dir = Path(config['output_dir'])
    
    clear_output_directories(output_dir)
    
    post_template_path = Path(config['post_template_path'])
    index_template_path = Path(config['index_template_path'])

    posts_dir = output_dir / 'posts'
    posts_dir.mkdir(parents=True, exist_ok=True)

    posts = []
    tags_dict = {}
    
    site_title = config['site_title']

    for md_file in input_dir.iterdir():
        if md_file.suffix == ".md":
            post = frontmatter.load(md_file)
            
            # Default values for missing metadata
            title = post.metadata.get('title', md_file.stem)
            date_str_or_obj = post.metadata.get('date', None)

            if isinstance(date_str_or_obj, str):
                date_obj = date.fromisoformat(date_str_or_obj)
            elif isinstance(date_str_or_obj, date):
                date_obj = date_str_or_obj
            else:
                date_obj = date.today()
            
            tldr = post.metadata.get('tldr', "")
            post_tags = post.metadata.get('tags', [])

            html_file = posts_dir / (title + ".html")
            html_content = render_template(post_template_path, site_title=site_title, title=title, date=date_obj, content=convert_md_to_html(post.content))
            html_file.write_text(html_content)
            
            post_data = {'title': title, 'date': date_obj, 'tldr': tldr, 'file': html_file.name}
            posts.append(post_data)

            for tag in post_tags:
                if tag not in tags_dict:
                    tags_dict[tag] = []
                tags_dict[tag].append(post_data)

    posts.sort(key=lambda post: post['date'], reverse=True)

    if 'tag_template_path' in config:
        generate_tag_pages(output_dir, site_title, tags_dict, Path(config['tag_template_path']))

    if 'all_tags_template_path' in config:
        generate_all_tags_page(output_dir, site_title, tags_dict, Path(config['all_tags_template_path']))

    index_content = render_template(index_template_path, site_title=site_title, posts=posts[:config.get('num_posts', 8)], tags_dict=tags_dict)
    (output_dir / 'index.html').write_text(index_content)

    if 'all_posts_template_path' in config:
        all_posts_content = render_template(Path(config['all_posts_template_path']), site_title=site_title, posts=posts)
        (posts_dir / 'index.html').write_text(all_posts_content)

    if config.get('rss'):
        generate_xml(config, posts)

def generate_tag_pages(output_dir, site_title, tags_dict, tag_template_path):
    tags_dir = output_dir / 'tags'
    tags_dir.mkdir(parents=True, exist_ok=True)

    for tag, tag_posts in tags_dict.items():
        tag_content = render_template(tag_template_path, site_title=site_title, posts=tag_posts, tag=tag)
        (tags_dir / f'{tag}.html').write_text(tag_content)

def generate_all_tags_page(output_dir, site_title, tags_dict, all_tags_template_path):
    all_tags_content = render_template(all_tags_template_path, site_title=site_title, tags_dict=tags_dict)
    (output_dir / 'tags' / 'index.html').write_text(all_tags_content)

def load_config(config_path="config.yaml"):
    try:
        with open(config_path, 'r') as stream:
            return yaml.safe_load(stream)
    except Exception as exc:
        print(f"Error reading {config_path}: {exc}")
        exit(1)

def main():
    config = load_config()

    parser = argparse.ArgumentParser(description="Generate a static website from Markdown files using specified templates.")
    
    parser.add_argument("input_dir", nargs='?', default=config.get('input_dir'), help="Directory containing the Markdown source files.")
    parser.add_argument("output_dir", nargs='?', default=config.get('output_dir'), help="Destination directory for the generated HTML files.")
    parser.add_argument("post_template_path", nargs='?', default=config.get('post_template_path'), help="Path to the HTML template for individual posts.")
    parser.add_argument("index_template_path", nargs='?', default=config.get('index_template_path'), help="Path to the HTML template for the main index page.")
    parser.add_argument("-t", "--tag_template_path", nargs='?', default=config.get('tag_template_path'), help="Optional: Path to the HTML template for individual tag pages. If provided, tag pages will be generated.")
    parser.add_argument("-a", "--all_tags_template_path", nargs='?', default=config.get('all_tags_template_path'), help="Optional: Path to the HTML template for the page listing all tags.")
    parser.add_argument("-n", "--num_posts", type=int, default=config.get('num_posts', 8), help="Number of latest posts to display on the main index page. Defaults to 8.")
    parser.add_argument("-p", "--all_posts_template_path", nargs='?', default=config.get('all_posts_template_path'), help="Optional: Path to the HTML template for the page listing all posts.")
    parser.add_argument("-r", "--rss", nargs='?', default=config.get('rss'), help="Optional: Generate an RSS Feed XML Document.")
    
    args = parser.parse_args()

    # Override config values with command-line arguments if provided
    for arg in ['input_dir', 'output_dir', 'post_template_path', 'index_template_path', 'tag_template_path', 'all_tags_template_path', 'all_posts_template_path', 'num_posts', 'rss']:
        if getattr(args, arg) is not None:
            config[arg] = getattr(args, arg)

    missing_args = [arg for arg in ['input_dir', 'output_dir', 'post_template_path', 'index_template_path'] if not config.get(arg)]
    if missing_args:
        print(f"Error: Missing required argument(s): {', '.join(missing_args)}")
        return

    generate_site(config)

if __name__ == "__main__":
    main()
