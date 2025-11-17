import requests
from bs4 import BeautifulSoup
import json
import time

# List of all HTML elements
elements = [
    "a", "abbr", "acronym", "address", "area", "article", "aside", "audio",
    "b", "base", "bdi", "bdo", "big", "blockquote", "body", "br", "button",
    "canvas", "caption", "center", "cite", "code", "col", "colgroup",
    "data", "datalist", "dd", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt",
    "em", "embed",
    "fencedframe", "fieldset", "figcaption", "figure", "font", "footer", "form", "frame", "frameset",
    "h1", "head", "header", "hgroup", "hr", "html",
    "i", "iframe", "img", "input", "ins",
    "kbd",
    "label", "legend", "li", "link",
    "main", "map", "mark", "marquee", "menu", "meta", "meter",
    "nav", "nobr", "noembed", "noframes", "noscript",
    "object", "ol", "optgroup", "option", "output",
    "p", "param", "picture", "plaintext", "pre", "progress",
    "q",
    "rb", "rp", "rt", "rtc", "ruby",
    "s", "samp", "script", "search", "section", "select", "selectedcontent", "slot", "small", "source", "span", "strike", "strong", "style", "sub", "summary", "sup",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "tt",
    "u", "ul",
    "var", "video",
    "wbr",
    "xmp"
]

base_url = "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/"
result = {}

print(f"Starting to scrape {len(elements)} elements...")

for index, element in enumerate(elements, 1):
    url = base_url + element
    print(f"[{index}/{len(elements)}] Scraping: {element}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract description from content-section paragraphs
        description_parts = []
        content_section = soup.find(class_='section-content')
        if content_section:
            paragraphs = content_section.find_all('p', recursive=False)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Skip very short paragraphs
                    description_parts.append(text)
        
        # Create a clean, well-formatted description
        if description_parts:
            description = " ".join(description_parts)
        else:
            description = f"The <{element}> HTML element."
        
        # Extract example from code-example class (preserve HTML formatting)
        example = ""
        demo = soup.find(class_='code-example')
        if demo:
            code_block = demo.find('code')
            if code_block:
                # Get the text content with preserved formatting
                example = code_block.get_text()
        
        if not example:
            example = f"<{element}></{element}>"
        
        # Extract attribute names only from dl > dt > a > code
        attributes = []
        dl_elements = soup.find_all('dl')
        for dl in dl_elements:
            dt_elements = dl.find_all('dt')
            for dt in dt_elements:
                a_tag = dt.find('a')
                if a_tag:
                    code_tag = a_tag.find('code')
                    if code_tag:
                        attr_name = code_tag.get_text(strip=True)
                        if attr_name and attr_name not in attributes:
                            attributes.append(attr_name)
        
        # If no specific attributes found, note that it uses global attributes
        if not attributes:
            attributes = ["This element includes the global attributes."]
        
        # Store in result
        result[element] = {
            "name": element,
            "description": description,
            "example": example,
            "attributes": attributes
        }
        
        print(f"   ✓ Successfully scraped {element}")
        
        # Be polite to the server
        time.sleep(0.5)
        
    except requests.RequestException as e:
        print(f"   ✗ Error scraping {element}: {e}")
        result[element] = {
            "name": element,
            "description": f"The <{element}> HTML element.",
            "example": f"<{element}></{element}>",
            "attributes": ["This element includes the global attributes."]
        }
    except Exception as e:
        print(f"   ✗ Unexpected error for {element}: {e}")
        result[element] = {
            "name": element,
            "description": f"The <{element}> HTML element.",
            "example": f"<{element}></{element}>",
            "attributes": ["This element includes the global attributes."]
        }

# Write to JSON file
output_file = "elements/elements-data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n✓ Done! Data saved to {output_file}")
print(f"Total elements scraped: {len(result)}")
