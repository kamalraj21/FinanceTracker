import os
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TagExtractor(Preprocessor):
    def run(self, lines):
        content = "\n".join(lines)
        # Extract YAML front matter
        front_matter = re.search(r'^---(.+?)---', content, re.DOTALL)
        yaml_content = yaml.safe_load(front_matter.group(1)) if front_matter else {}
        
        # Extract tagged sections
        tag_pattern = re.compile(r'\[Tag: (.+?)\]')
        tagged_content = {}
        for tag in tag_pattern.findall(content):
            start = content.find(f"[Tag: {tag}]")
            end = content.find("[Tag:", start + 1)
            tagged_content[tag] = content[start:end].strip() if end != -1 else content[start:].strip()

        return yaml_content, tagged_content

class TagExtractorExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(TagExtractor(md), 'tag_extractor', 27)

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.readlines()
    md = markdown.Markdown(extensions=[TagExtractorExtension()])
    front_matter, tagged_content = md.preprocessors['tag_extractor'].run(text)
    return front_matter, tagged_content

def parse_all_markdown_files(docs_path):
    all_content = {}
    for filename in os.listdir(docs_path):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_path, filename)
            front_matter, tagged_content = parse_markdown(file_path)
            all_content[filename] = {'front_matter': front_matter, 'tagged_content': tagged_content}
            print(f"Processed {filename}")
    return all_content

def render_to_html(template_name, content, output_filename):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Load the template environment
    env = Environment(
        loader=FileSystemLoader(searchpath='../html_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    # Select the template file
    template = env.get_template(template_name)

    # Render the template with content
    html_content = template.render(content=content)

    # Write the rendered HTML to file
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"{output_filename} has been created.")

def main():
    docs_path = '../docs'
    all_extracted_content = parse_all_markdown_files(docs_path)

    # Render each Markdown file to an HTML file
    for filename, content in all_extracted_content.items():
        # Define the output HTML filename based on the Markdown filename
        output_filename = f"../html_outputs/{filename.replace('.md', '.html')}"
        # Assuming you have a generic template for all files
        render_to_html('generic_template.html', content, output_filename)

if __name__ == "__main__":
    main()
