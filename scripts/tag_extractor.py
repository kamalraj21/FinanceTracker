import os
import re
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateNotFound

# Define a dictionary to store reusable content
reusable_content = {}

def clean_annotations(markdown_content):
    # Clean out the [Reusable: ...] and [EndReusable] annotations from the markdown content
    markdown_content = re.sub(r'\[Reusable: .+?\]', '', markdown_content)
    markdown_content = re.sub(r'\[EndReusable\]', '', markdown_content)
    return markdown_content

def extract_reusable_sections(markdown_content):
    # Extract reusable sections marked with [Reusable: SectionName]
    reusable_sections = re.findall(r'\[Reusable: (\w+)\]\n([\s\S]*?)\n\[EndReusable\]', markdown_content)
    for section_name, section_content in reusable_sections:
        reusable_content[section_name] = markdown.markdown(section_content.strip())

def include_sections(markdown_content):
    # Replace [Include: SectionName] annotations with the corresponding reusable HTML content
    def replace_include(match):
        section_name = match.group(1)
        return reusable_content.get(section_name, f"<!-- Section {section_name} not found -->")
    
    return re.sub(r'\[Include: (\w+)\]', replace_include, markdown_content)

def parse_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"Markdown file {file_path} not found.")
        return None

    try:
        parts = text.split('---', 2)
        yaml_content = yaml.safe_load(parts[1]) if len(parts) > 2 else {}
        markdown_content = parts[2] if len(parts) > 2 else text
        extract_reusable_sections(markdown_content)
        markdown_content = include_sections(markdown_content)
        cleaned_markdown_content = clean_annotations(markdown_content)
        html_content = markdown.markdown(cleaned_markdown_content)
        return {'front_matter': yaml_content, 'content': html_content}
    except Exception as e:
        print(f"Error parsing markdown file {file_path}: {e}")
        return None

def render_to_html(template_name, content_dict, output_filename, env):
    if not content_dict:
        return
    
    try:
        template = env.get_template(template_name)
        html_content = template.render(front_matter=content_dict['front_matter'], content=content_dict['content'], reusable=reusable_content)
        output_dir = os.path.dirname(output_filename)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"{output_filename} has been created.")
    except TemplateNotFound:
        print(f"Template '{template_name}' not found.")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")

def main():
    base_dir = os.path.dirname(__file__)
    html_template_dir = os.path.abspath(os.path.join(base_dir, '..', 'html_templates'))
    docs_dir = os.path.abspath(os.path.join(base_dir, '..', 'docs'))
    output_dir = os.path.abspath(os.path.join(base_dir, '..', 'html_outputs'))

    env = Environment(
        loader=FileSystemLoader(searchpath=html_template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )

    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_dir, filename)
            content_dict = parse_markdown(file_path)
            if content_dict:
                template_name = filename.replace('FinanceTracker-', '').replace('.md', '_template.html').lower()
                output_file = f"{output_dir}/{filename.replace('.md', '.html')}"
                render_to_html(template_name, content_dict, output_file, env)

if __name__ == "__main__":
    main()
