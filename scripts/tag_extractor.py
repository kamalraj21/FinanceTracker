import os
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TagExtractor(Extension):
    def extendMarkdown(self, md):
        md.registerExtension(self)
        md.preprocessors.register(TagPreprocessor(md), 'tag_extractor', 27)

class TagPreprocessor(Preprocessor):
    def run(self, lines):
        content = "\n".join(lines)
        yaml_content = {}
        front_matter = re.search(r'^---(.+?)---', content, re.DOTALL)
        if front_matter:
            yaml_content = yaml.safe_load(front_matter.group(1))
            content = content[front_matter.end():]  # Adjust content to exclude front matter
        content_without_tags = re.sub(r'\[Tag: .+?\]', '', content).strip()
        return [content_without_tags], yaml_content

def parse_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    md = markdown.Markdown(extensions=[TagExtractor()])
    content, yaml_content = md.convert(text)
    return yaml_content, content

def parse_all_markdown_files(docs_path):
    all_content = {}
    for filename in os.listdir(docs_path):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_path, filename)
            yaml_content, content = parse_markdown(file_path)
            all_content[filename] = {'front_matter': yaml_content, 'content': content}
            print(f"Processed {filename}")
    return all_content

def render_to_html(template_name, content, output_filename):
    env = Environment(
        loader=FileSystemLoader(searchpath='../html_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_name)
    html_content = template.render(content=content)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    print(f"{output_filename} has been created.")

def main():
    docs_path = '../docs'
    all_extracted_content = parse_all_markdown_files(docs_path)
    for filename, content in all_extracted_content.items():
        output_filename = f"../html_outputs/{filename.replace('.md', '.html')}"
        render_to_html('generic_template.html', content, output_filename)

if __name__ == "__main__":
    main()
