import os
import re
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound

# Define a dictionary to store reusable content
reusable_content = {}

def clean_annotations(markdown_content):
    # Clean out the [Reusable: ...] annotations from the markdown content
    return re.sub(r'\[Reusable: .+?\]', '', markdown_content)

def extract_reusable_sections(markdown_content):
    # Extract reusable sections marked with [Reusable: SectionName]
    reusable_sections = re.findall(r'\[Reusable: (\w+)\]\n([\s\S]*?)\n\[EndReusable\]', markdown_content)
    for section_name, section_content in reusable_sections:
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
    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        print(f"Template '{template_name}' not found.")
        return
    # Pass the reusable_content directly
    html_content = template.render(front_matter=content_dict['front_matter'], content=content_dict['content'], reusable=reusable_content)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"{output_filename} has been created.")


def main():
    env = Environment(
        loader=FileSystemLoader(searchpath='../html_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    docs_path = '../docs'
    for filename in os.listdir(docs_path):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_path, filename)
            content_dict = parse_markdown(file_path)  # This creates content_dict
            template_name = filename.replace('FinanceTracker-', '').replace('.md', '_template.html').lower()
            output_file = f"../html_outputs/{filename.replace('.md', '.html')}"
            render_to_html(template_name, content_dict, output_file, env)  # content_dict is passed here

if __name__ == "__main__":
    main()
