import os
import markdown
import yaml
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape

reusable_content = {}

def clean_annotations(markdown_content):
    return re.sub(r'\[Reusable: .+?\]', '', markdown_content)

def extract_reusable_sections(markdown_content):
    pattern = re.compile(r'\[Reusable: (\w+)\]\n([\s\S]*?)(?=\n## |\Z)', re.DOTALL)
    sections = pattern.findall(markdown_content)
    for section_name, section_content in sections:
        reusable_content[section_name] = markdown.markdown(section_content.strip())

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    parts = text.split('---', 2)
    yaml_content = yaml.safe_load(parts[1]) if len(parts) > 2 else {}
    markdown_content = parts[2] if len(parts) > 2 else text
    extract_reusable_sections(markdown_content)
    cleaned_markdown_content = clean_annotations(markdown_content)
    html_content = markdown.markdown(cleaned_markdown_content)
    return {'front_matter': yaml_content, 'content': html_content}

def render_to_html(template_name, content_dict, output_filename, env):
    template = env.get_template(template_name)
    content_dict['reusable'] = reusable_content
    html_content = template.render(content_dict)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

def main():
    env = Environment(
        loader=FileSystemLoader(searchpath='../html_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    docs_path = '../docs'
    for filename in os.listdir(docs_path):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_path, filename)
            content_dict = parse_markdown(file_path)
            template_name = 'generic_template.html'
            output_file = f"../html_outputs/{filename.replace('.md', '.html')}"
            render_to_html(template_name, content_dict, output_file, env)
            print(f"Generated HTML for {filename}")

if __name__ == "__main__":
    main()
