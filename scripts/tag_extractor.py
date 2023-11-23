import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import re
import yaml

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
        text = file.read()
    md = markdown.Markdown(extensions=[TagExtractorExtension()])
    front_matter, tagged_content = md.convert(text)
    return front_matter, tagged_content

# Example usage
if __name__ == "__main__":
    file_path = 'path_to_your_markdown_file.md'
    front_matter, tagged_content = parse_markdown(file_path)
    print("Front Matter:", front_matter)
    print("Tagged Content:", tagged_content)
