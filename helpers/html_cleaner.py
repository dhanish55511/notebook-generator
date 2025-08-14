from bs4 import BeautifulSoup
from urllib.parse import urljoin

"""
html_clearne.py — Text & HTML Cleaning Utilities
"""


def replace_uicontrol_bold_spans(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for span in soup.find_all('span'):
        classes = span.get('class', [])
        if set(classes) == {'uicontrol', 'bold'}:
            b_tag = soup.new_tag('b')
            b_tag.string = span.get_text()
            span.replace_with(b_tag)
    return str(soup)

#Update any olinks and bs with the actual working links.
def update_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if not href.startswith(('http://', 'https://', '#')):
            tag['href'] = urljoin(base_url, href).replace('amp;', '')
        elif not href.startswith('#'):  # For full URLs, just remove amp;
            tag['href'] = href.replace('amp;', '')
    return str(soup)

# Updates any <code class="codeph"> with backticks so that the formatting is preserved.
def preserve_code_in_paragraphs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    code_tags = soup.find_all('code', class_='codeph')
    for code_tag in code_tags:
        code_text = code_tag.get_text(separator=" ").strip()
        new_text = f"`{code_text}`"
        code_tag.replace_with(new_text)
    return str(soup)

def transform_infobox_notes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    infobox_notes = soup.find_all('div', class_='infoboxnote')

    for note_div in infobox_notes:
        strong_text = ""
        first_p = note_div.find('p', class_='notep1')

        if first_p:
            strong_text = first_p.get_text(strip=True)
            first_p.decompose()

        new_b = soup.new_tag('b')
        new_b.string = strong_text + ":"

        new_p = soup.new_tag('p')
        new_p.append(new_b)
        new_p.append(" ")

        # Append all remaining child content of the note_div to the new p tag
        for child in note_div.contents:
            if child.name is not None or str(child).strip():  # Avoid empty text nodes
                new_p.append(child)

        note_div.replace_with(new_p)

    final_html = str(soup).replace("::", ":")
    return final_html



