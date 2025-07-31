#notebook_utils.py

# Step 1: Required Libraries
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from urllib.parse import urljoin

proxies = {
    "http": "http://www-proxy.us.oracle.com:80",
    "https": "http://www-proxy.us.oracle.com:80"
}

# Fetch the html content
def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

#Update any olinks and bs with the actual working links.
def update_links(soup, base_url):
    for tag in soup.find_all('a', href=True):
        href = tag['href']
        if not href.startswith(('http://', 'https://', '#')):
            tag['href'] = urljoin(base_url, href).replace('amp;', '')
        elif not href.startswith('#'):  # For full URLs, just remove amp;
            tag['href'] = href.replace('amp;', '')
    return soup

#Update any codeph blick with backticks in whole
# def preserve_code_in_paragraphs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    p_tags = soup.find_all('p')
    for p_tag in p_tags:
        code_tags = p_tag.find_all('code class="codeph"')
        for code_tag in code_tags:
            code_text = code_tag.get_text(separator=" ").strip()
            new_text = f"`{code_text}`"
            code_tag.replace_with(new_text)
    return str(soup)

def preserve_code_in_paragraphs(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    code_tags = soup.find_all('code', class_='codeph')
    for code_tag in code_tags:
        code_text = code_tag.get_text(separator=" ").strip()
        new_text = f"`{code_text}`"
        code_tag.replace_with(new_text)
    return str(soup)

# get the footer
def get_footer(html_content, url=None):
    # --- Footer ---
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # print(url)

    copyright_meta = soup.find('meta', {'name': 'dcterms.dateCopyrighted'})
    # print(copyright_meta)
    copyright_year = ""
    if copyright_meta:
        copyright_year = copyright_meta.get('content', '').replace(', ', '/')  # Handle multiple years
    # print(copyright_year)
    last_lines = ["", f"[Source]({url})", "", f"*In the business since: ({copyright_year})*"]
    return last_lines

# Extract the title
def get_notebook_title_from_html(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    h2_tag = soup.find('h2')
    if h2_tag:
        return h2_tag.get_text(strip=True)
    return "Untitled Notebook"

def get_first_paragraph_after(tag):
    next_elem = tag
    while True:
        next_elem = next_elem.find_next()
        if next_elem is None:
            return None
        if isinstance(next_elem, Tag) and next_elem.name == "p":
            return next_elem


# Coding the first paragraph: Containing the heading as h2, the paragraph as its content and a copyright at the footer.
# def extract_h2_with_paragraphs(html_content, url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    output_paragraphs = []

    for h2 in soup.find_all('h2'):
        markdown_lines = ["%md", ""]

        # Add the H2 heading as Markdown
        h2_text = h2.get_text(strip=True)
        print(h2_text)
        markdown_lines.append(f"## {h2_text}")
        markdown_lines.append("")

        # Add the next <p> if it exists
        next_p = h2.find_next_sibling()
        while next_p and not (isinstance(next_p, Tag) and next_p.name == 'p'):
            next_p = next_p.find_next_sibling()

        print(next_p)
        if next_p:
            p_text = next_p.get_text(strip=True)
            print(p_text)
            markdown_lines.append(p_text)
            markdown_lines.append("")

        # output_paragraphs.append({
        #     "title": None,
        #     "hasTitle": False,
        #     "message": markdown_lines
        # })

    # Add the final footer block if URL or attribution is needed
    if url:
        # footer_lines = ["%md", ""]
        markdown_lines = [""]
        markdown_lines.append(f"[Source]({url})")
        markdown_lines.append("")
        markdown_lines.append("*made by dhanish with help of chatgpt and internet copyright 2025*")
        
        # markdown_lines.append(footer_lines)

        output_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })



    return output_paragraphs

# def parse_html_in_order(html_content, url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body or soup
    paragraphs = []

    visited_tables = set()
    visited_lists = set()

    for tag in body.descendants:
        if isinstance(tag, Tag):
            # Handle <h2> and its next <p>
            if tag.name == 'h2':
                h2_text = tag.get_text(strip=True)
                markdown_lines = ["%md", f"## {h2_text}"]

                next_p = tag.find_next_sibling()
                while next_p and next_p.name != 'p':
                    next_p = next_p.find_next_sibling()

                if next_p and next_p.name == 'p':
                    markdown_lines.append("")
                    markdown_lines.append(next_p.get_text(strip=True))

                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": markdown_lines
                })

            # Handle <h3> and <h4> with up to 5 <p>
            elif tag.name in ['h3', 'h4']:
                header_level = "###" if tag.name == 'h3' else "####"
                markdown_lines = ["%md", f"{header_level} {tag.get_text(strip=True)}"]
                current = tag.find_next_siblings()
                count = 0

                for sibling in current:
                    if sibling.name == 'p':
                        markdown_lines.append("")
                        markdown_lines.append(sibling.get_text(strip=True))
                        count += 1
                    if count >= 5:
                        break

                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": markdown_lines
                })

            # Handle <table>
            elif tag.name == 'table' and id(tag) not in visited_tables:
                visited_tables.add(id(tag))
                table_lines = []
                headers = tag.find_all('th')
                if headers:
                    head_texts = [th.get_text(strip=True) for th in headers]
                    table_lines.append("%md")
                    table_lines.append("")
                    table_lines.append(f"| {' | '.join(head_texts)} |")
                    table_lines.append(f"| {' | '.join(['---'] * len(head_texts))} |")

                rows = tag.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        cell_texts = [td.get_text(strip=True) for td in cells]
                        table_lines.append(f"| {' | '.join(cell_texts)} |")

                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": table_lines
                })

            # Handle <li> with <span> and <pre>
            elif tag.name == 'li' and id(tag) not in visited_lists:
                visited_lists.add(id(tag))
                span = tag.find('span')
                pre = tag.find('pre')
                if span and pre:
                    if 'nocopybutton' in pre.get('class', []):
                        continue
                    code_block = pre.find('code') or pre
                    code_lines = code_block.get_text().strip().splitlines()

                    paragraphs.append({
                        "title": span.get_text(strip=True),
                        "hasTitle": True,
                        "message": ["%python", ""] + code_lines
                    })

    # Add footer at the end
    if url:
        paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": [
                "%md",
                "",
                f"[Source]({url})",
                "",
                "*made by dhanish with help of chatgpt and internet copyright 2025*"
            ]
        })

    return paragraphs

# def parse_html_in_order(html_content, url=None):
    from bs4 import BeautifulSoup, Tag, NavigableString
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body or soup

    paragraphs = []
    h2_footer_added = False
    skip_next_p = False  # Used to skip <p> immediately after <h2>

    elements = list(body.descendants)

    for idx, element in enumerate(elements):
        if isinstance(element, Tag):
            tag_name = element.name

            # --- H2 + its next <p> ---
            if tag_name == 'h2':
                # Extract h2 and its first <p>
                h2 = element
                next_p = h2.find_next_sibling()
                while next_p and not (isinstance(next_p, Tag) and next_p.name == 'p'):
                    next_p = next_p.find_next_sibling()
                
                h2_block = extract_h2_with_paragraphs(str(h2) + (str(next_p) if next_p else ""), url=None)
                paragraphs.extend(h2_block)
                skip_next_p = True  # So we don’t repeat this paragraph

            # --- h3/h4 and their next 5 paragraphs ---
            elif tag_name in ['h3', 'h4']:
                h_block = extract_h3_h4_with_paragraphs(str(element))
                paragraphs.extend(h_block)

            # --- List items with code blocks ---
            elif tag_name == 'li':
                li_block = li_to_custom_paragraph(str(element))
                paragraphs.extend(li_block)

            # --- Tables ---
            elif tag_name == 'table':
                table_block = extract_markdown_tables_with_headings(str(element))
                paragraphs.extend(table_block)

            # --- Regular <p> (not right after <h2>) ---
            elif tag_name == 'p' and not skip_next_p:
                p_text = element.get_text(strip=True)
                if p_text:
                    paragraphs.append({
                        "title": None,
                        "hasTitle": False,
                        "message": ["%md", "", p_text]
                    })
            else:
                skip_next_p = False  # reset after skipping the one after h2

    # --- Add footer once after all H2s ---
    if url:
        footer_lines = ["%md", ""]
        footer_lines.append(f"[Source]({url})")
        footer_lines.append("")
        footer_lines.append("*made by dhanish with help of chatgpt and internet copyright 2025*")

        paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": footer_lines
        })

    return paragraphs

# def parse_html_in_order(html_content, url=None):
    from bs4 import BeautifulSoup, Tag, NavigableString
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body or soup

    paragraphs = []
    h2_footer_added = False
    skip_next_p = False  # Used to skip <p> immediately after <h2>

    elements = list(body.descendants)

    for idx, element in enumerate(elements):
        if isinstance(element, Tag):
            tag_name = element.name

            # --- H2 + its next <p> ---
            if tag_name == 'h2':
                # Extract h2 and its first <p>
                h2 = element
                next_p = h2.find_next_sibling()
                while next_p and not (isinstance(next_p, Tag) and next_p.name == 'p'):
                    next_p = next_p.find_next_sibling()
                
                h2_block = extract_h2_with_paragraphs(str(h2) + (str(next_p) if next_p else ""), url=None)
                paragraphs.extend(h2_block)
                skip_next_p = True  # So we don’t repeat this paragraph

            # --- h3/h4 and their next 5 paragraphs ---
            elif tag_name in ['h3', 'h4']:
                h_block = extract_h3_h4_with_paragraphs(str(element))
                paragraphs.extend(h_block)

            # --- List items with code blocks ---
            elif tag_name == 'li':
                li_block = li_to_custom_paragraph(str(element))
                paragraphs.extend(li_block)

            # --- Tables ---
            elif tag_name == 'table':
                table_block = extract_markdown_tables_with_headings(str(element))
                paragraphs.extend(table_block)

            # --- Regular <p> (not right after <h2>) ---
            elif tag_name == 'p' and not skip_next_p:
                p_text = element.get_text(strip=True)
                if p_text:
                    paragraphs.append({
                        "title": None,
                        "hasTitle": False,
                        "message": ["%md", "", p_text]
                    })
            else:
                skip_next_p = False  # reset after skipping the one after h2

    # --- Add footer once after all H2s ---
    if url:
        footer_lines = ["%md", ""]
        footer_lines.append(f"[Source]({url})")
        footer_lines.append("")
        footer_lines.append("*made by dhanish with help of chatgpt and internet copyright 2025*")

        paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": footer_lines
        })

    return paragraphs

# def parse_html_in_order(html_content, url=None):
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body or soup

    def get_first_paragraph_after(tag):
        next_elem = tag
        while True:
            next_elem = next_elem.find_next()
            if next_elem is None:
                return None
            if isinstance(next_elem, Tag) and next_elem.name == "p":
                return next_elem

    paragraphs = []
    handled = set()

    for element in body.descendants:
        if not isinstance(element, Tag):
            continue

        if element in handled:
            continue

        # --- H2 and its paragraph ---
        if element.name == "h2":
            h2_tag = element
            p_tag = get_first_paragraph_after(h2_tag)
            h2_html = str(h2_tag)
            if p_tag:
                h2_html += str(p_tag)
                handled.add(p_tag)

            block = extract_h2_with_paragraphs(h2_html, url)
            paragraphs.extend(block)
            handled.add(h2_tag)

        # --- H3 and H4 ---
        elif element.name in ["h3", "h4"]:
            block = extract_h3_h4_with_paragraphs(str(element))
            paragraphs.extend(block)
            handled.add(element)

        # --- Tables ---
        elif element.name == "table":
            block = extract_markdown_tables_with_headings(str(element))
            paragraphs.extend(block)
            handled.add(element)

        # --- List items with code ---
        elif element.name == "li":
            block = li_to_custom_paragraph(str(element))
            paragraphs.extend(block)
            handled.add(element)

        # --- Independent <p> tags ---
        elif element.name == "p" and element not in handled:
            text = element.get_text(strip=True)
            if text:
                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": ["%md", "", text]
                })
                handled.add(element)

    # # --- Footer ---
    # if url:
    #     footer_lines = ["%md", ""]
    #     footer_lines.append(f"[Source]({url})")
    #     footer_lines.append("")
    #     footer_lines.append("*making copyright 2025*")

    #     paragraphs.append({
    #         "title": None,
    #         "hasTitle": False,
    #         "message": footer_lines
    #     })

    return paragraphs


# Coding the first paragraph: Containing the heading as h2, the paragraph as its content and a copyright at the footer.
# def extract_h2_with_paragraphs(html_content, url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    output_paragraphs = []

    for h2 in soup.find_all('h2'):
        markdown_lines = ["%md", ""]

        # Add the H2 heading as Markdown
        h2_text = h2.get_text(strip=True)
        # print(f"Found H2: {h2_text}")
        markdown_lines.append(f"## {h2_text}")
        markdown_lines.append("")

        # Find the immediately following sibling (which is likely the container div)
        next_element = h2.find_next_sibling()
        paragraph_found = False

        if next_element:
            # Search for the first <p> tag within this sibling
            paragraph = next_element.find('p')
            if paragraph:
                p_text = paragraph.get_text(strip=True)
                # print(f"  Found Paragraph (nested): {p_text}")
                markdown_lines.append(p_text)
                markdown_lines.append("")
                # print(markdown_lines)
                paragraph_found = True
            else:
                print(f"  No paragraph found within the sibling of '{h2_text}'.")
        else:
            print(f"  No sibling found after '{h2_text}'.")

        if not paragraph_found:
            print(f"  No paragraph found following '{h2_text}'.")


    # Extract copyright year from metadata
    copyright_meta = soup.find('meta', {'name': 'dcterms.dateCopyrighted'})
    copyright_year = ""
    if copyright_meta:
        copyright_year = copyright_meta.get('content', '').replace(', ', '/')  # Handle multiple years

    # Add the final footer block if URL or attribution is needed
    if url:
        markdown_lines.append(f"[Source]({url})")
        markdown_lines.append("")
        markdown_lines.append(f"*In the business since: ({copyright_year})*")
        output_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    return output_paragraphs

# def transform_infobox_notes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    infobox_notes = soup.find_all('div', class_='infoboxnote')

    for note_div in infobox_notes:
        strong_text = ""
        content_paragraphs = note_div.find_all('p')

        if content_paragraphs:
            first_p = content_paragraphs[0]
            if 'notep1' in first_p.get('class', []):
                strong_text = first_p.get_text(strip=True)
                first_p.decompose()  # Remove the "Remember:" or "Note:" paragraph

            new_content = soup.new_tag('b')
            new_content.string = strong_text + ":"

            note_div.insert(0, new_content)
            note_div.insert(1, " ") # Add a space after the bold text

            # Unwrap the div to get the desired structure
            note_div.name = 'span' # Change div to span to avoid block-level behavior if needed
            note_div.attrs = {}     # Remove the class attribute

    return str(soup)

# def transform_infobox_notes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    infobox_notes = soup.find_all('div', class_='infoboxnote')

    for note_div in infobox_notes:
        strong_text = ""
        content_paragraphs = note_div.find_all('p')

        if content_paragraphs:
            first_p = content_paragraphs[0]
            if 'notep1' in first_p.get('class', []):
                strong_text = first_p.get_text(strip=True)
                first_p.decompose()

            new_b = soup.new_tag('b')
            new_b.string = strong_text + ":"

            new_p = soup.new_tag('p')
            new_p.append(new_b)
            new_p.append(" ") # Add a space after the bold text

            # Append the remaining content paragraphs to the new p tag
            for remaining_p in note_div.find_all('p'):
                new_p.append(remaining_p)

            note_div.replace_with(new_p)

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

    return str(soup)

def preprocess_sect2_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    sect2_divs = soup.find_all('div', class_='sect2')

    for sect2_div in sect2_divs:
        h3_tag = sect2_div.find('h3', class_='sect3')
        if not h3_tag:
            continue

        transformed_children = [h3_tag]
        content_buffer = []
        subhead_found = False

        for child in sect2_div.children:
            if isinstance(child, Tag):
                if child.name == 'p' and 'subhead2' in child.get('class', []):
                    # Process the previous buffer
                    if content_buffer:
                        new_p = soup.new_tag('p')
                        new_p.extend(content_buffer)
                        transformed_children.append(new_p)
                        content_buffer = []

                    # Bold the subhead text
                    bold_tag = soup.new_tag('b')
                    bold_tag.string = child.get_text(strip=True)
                    new_p_subhead = soup.new_tag('p')
                    new_p_subhead.append(bold_tag)
                    transformed_children.append(new_p_subhead)
                    subhead_found = True
                else:
                    # Add other tags to the buffer
                    content_buffer.append(child)
            elif str(child).strip():
                # Add non-empty text nodes to the buffer
                content_buffer.append(child)

        # Process any remaining content after the last subhead
        if content_buffer:
            new_p = soup.new_tag('p')
            new_p.extend(content_buffer)
            transformed_children.append(new_p)

        # Replace the original sect2 div's content with the transformed content
        sect2_div.clear()
        sect2_div.extend(transformed_children)

    # Replace "::" with ":" in the final HTML string
    final_html = str(soup).replace("::", ":")
    return final_html
    # return str(soup)

def get_first_paragraph_in_next_sibling_descendants(tag):
        next_sibling = tag.find_next_sibling()
        # if next_sibling:
        #     return next_sibling.find('p')
        if isinstance(next_sibling, Tag):
            return next_sibling.find('p')
        return None

def extract_and_remove_relinfo_links(html_content, base_url):
    """
    Selects all distinct links within div tags with class "relinfo",
    creates a new paragraph containing these links as an unordered list
    with the original anchor tags preserved, and removes the div tags
    with class "relinfo" from the HTML content.

    Args:
        html_content (str): The input HTML content.

    Returns:
        tuple: A tuple containing:
            - str: The modified HTML content with "relinfo" divs removed.
            - dict: A paragraph dictionary containing the distinct links
                    as an unordered list. Returns None if no links are found
                    in "relinfo" divs.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    relinfo_divs = soup.find_all('div', class_='relinfo')
    distinct_links_html = set()
    # First, process and collect distinct links
    for div in relinfo_divs:
        links = div.find_all('a', href=True)
        for link in links:
            href = link['href']
            # Handle relative URLs
            cleaned_href = href.replace('amp;', '') # Remove amp; first
            if not cleaned_href.startswith(('http://', 'https://', '#')):
                link['href'] = urljoin(base_url, cleaned_href)
                # link['href'] = link['href'].replace('amp;', '')
            elif not cleaned_href.startswith('#'):  # For full URLs, just remove amp;
                link['href'] = cleaned_href.replace('amp;', '')
            distinct_links_html.add(str(link))

    for div in relinfo_divs:
        links = div.find_all('a', href=True)
        for link in links:
            distinct_links_html.add(str(link))

    # Remove the "relinfo" div tags from the soup object
    for div in relinfo_divs:
        div.decompose()

    modified_html_content = str(soup)

    if distinct_links_html:
        links_list_items = [f"* {link_html}" for link_html in sorted(list(distinct_links_html))]
        links_paragraph = {
            "title": None,
            "hasTitle": False,
            "message": ["%md", "", "Related Links:\n" + "\n".join(links_list_items)]
        }
        return modified_html_content, links_paragraph
    else:
        return modified_html_content, None

def parse_html_in_order1(html_content, url=None):
    pass
    # from bs4 import BeautifulSoup, Tag
    # base_url = "https://docs.oracle.com"
    
    # html_content0 = preserve_code_in_paragraphs(html_content) #Replace codeph with backticks
    # html_content1 = transform_infobox_notes(html_content0) # Transform note and remember so that they can be parsed.
    # html_content2 = preprocess_sect2_content(html_content1) # Parse sect2 divs.
    # modified_html_content_no_relinfo, relinfo_links_paragraph = extract_and_remove_relinfo_links(html_content2, base_url)
    # # print(relinfo_links_paragraph)
    # soup = BeautifulSoup(modified_html_content_no_relinfo, 'html.parser')

    # # Update the links within the soup object
    # base_url = "https://docs.oracle.com"
    # updated_soup = update_links(soup, base_url) #Updates all the relative links such as olinks.

    # body = updated_soup.body or updated_soup  #type is <class 'bs4.element.Tag'> which means its a parsed bs object.

    # with open("my_output_file.txt", "w") as outfile:
    #     print("Starting the script...", file=outfile)
    #     print(f"The result is: {body}", file=outfile)
    #     print("Script execution complete.", file=outfile)

    # paragraphs = []
    # handled = set()
    # first_paragraph_found = False
    # processing_content_after_header = False
    # header_markdown_lines = []
    # paragraph_count = 0

    # for element in body.descendants:
    #     if not isinstance(element, Tag):
    #         continue

    #     if element in handled:
    #         continue

    #     # --- H2 and its paragraph ---
    #     if element.name == "h2":
    #         h2_tag = element
    #         p_tag = get_first_paragraph_in_next_sibling_descendants(h2_tag)
    #         h2_html = str(h2_tag)
    #         if p_tag:
    #             h2_html += str(p_tag)
    #             handled.add(p_tag)

    #         block = extract_h2_with_paragraphs(h2_html, url)
    #         paragraphs.extend(block)
    #         handled.add(h2_tag)
    #         if block and block[0] and block[0]['message']:
    #             first_paragraph_found = True
    #         processing_content_after_header = False
    #         header_markdown_lines = []
    #         paragraph_count = 0

    #     # --- H3 and its paragraph ---
    #     if element.name == "h3":
    #         h3_tag = element
    #         p_tag = get_first_paragraph_in_next_sibling_descendants(h3_tag)
    #         h3_html = str(h3_tag)
    #         # print(h3_html)
    #         # print("p tag is, ", p_tag)
    #         if p_tag:
    #             h3_html += str(p_tag)
    #             handled.add(p_tag)

    #         block = extract_h3_with_paragraphs(h3_html, url)
    #         paragraphs.extend(block)
    #         handled.add(h3_tag)
    #         if block and block[0] and block[0]['message']:
    #             first_paragraph_found = True
    #         processing_content_after_header = False
    #         header_markdown_lines = []
    #         paragraph_count = 0


    #     elif element.name == 'p' and element.find('b') is not None and element not in handled:
    #         text_content = "".join(element.stripped_strings)
    #         if text_content:
    #             paragraphs.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", "", text_content]
    #             })
    #             handled.add(element)
    #     elif element.name == 'p' and element not in handled and not processing_content_after_header:
    #         text = element.get_text(strip=True)
    #         if text:
    #             paragraph_data = {
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", "", text]
    #             }
    #             if not first_paragraph_found:
    #                 paragraphs.append(paragraph_data)
    #                 first_paragraph_found = True
    #             else:
    #                 paragraphs.append(paragraph_data)
    #             handled.add(element)

    #     # --- Tables ---
    #     elif isinstance(element, Tag) and element.name == "table":
    #         block = extract_markdown_tables_with_headings(str(element))
    #         paragraphs.extend(block)
    #         handled.add(element)
    #         if block and block[0] and block[0]['message'] and not first_paragraph_found:
    #             first_paragraph_found = True
    #         processing_content_after_header = False
    #         header_markdown_lines = []
    #         paragraph_count = 0

    #     # --- List items with code ---
    #     elif isinstance(element, Tag) and element.name == "li":
    #         block = li_to_custom_paragraph(str(element))
    #         paragraphs.extend(block)
    #         handled.add(element)
    #         if block and block[0] and block[0]['message'] and not first_paragraph_found:
    #             first_paragraph_found = True
    #         processing_content_after_header = False
    #         header_markdown_lines = []
    #         paragraph_count = 0

    # # Handle any remaining content after the last header
    # if processing_content_after_header and header_markdown_lines:
    #     paragraphs.append({
    #         "title": None,
    #         "hasTitle": False,
    #         "message": header_markdown_lines
    #     })

    # paragraphs.append(relinfo_links_paragraph)
    # return paragraphs

# def parse_html_in_order(html_content, url=None):
    pass
    # from bs4 import BeautifulSoup, Tag
    # base_url = "https://docs.oracle.com"
    # html_content0 = preserve_code_in_paragraphs(html_content)  # Replace codeph with backticks
    # html_content1 = transform_infobox_notes(html_content0)      # Transform notes and reminders
    # html_content2 = preprocess_sect2_content(html_content1)     # Parse sect2 divs
    # modified_html_content_no_relinfo, relinfo_links_paragraph = extract_and_remove_relinfo_links(html_content2, base_url)

    # soup = BeautifulSoup(modified_html_content_no_relinfo, 'html.parser')
    # # base_url = "https://abc.com"
    # updated_soup = update_links(soup, base_url)

    # body = updated_soup.body or updated_soup

    # paragraphs = []
    # handled = set()
    # first_paragraph_found = False
    # processing_after_h3 = False

    # for element in body.descendants:
    #     if not isinstance(element, Tag):
    #         continue
    #     if element in handled:
    #         continue

    #     # --- H2 and its paragraph ---
    #     if element.name == "h2":
    #         h2_tag = element
    #         p_tag = get_first_paragraph_in_next_sibling_descendants(h2_tag)
    #         h2_html = str(h2_tag)
    #         if p_tag:
    #             h2_html += str(p_tag)
    #             handled.add(p_tag)

    #         block = extract_h2_with_paragraphs(h2_html, url)
    #         paragraphs.extend(block)
    #         handled.add(h2_tag)
    #         first_paragraph_found = True
    #         continue

    #     # --- H3 and its paragraph ---
    #     if element.name == "h3":
    #         h3_tag = element
    #         p_tag = get_first_paragraph_in_next_sibling_descendants(h3_tag)
    #         h3_html = str(h3_tag)
    #         if p_tag:
    #             h3_html += str(p_tag)
    #             handled.add(p_tag)

    #         block = extract_h3_with_paragraphs(h3_html, url)
    #         paragraphs.extend(block)
    #         handled.add(h3_tag)
    #         first_paragraph_found = True
    #         processing_after_h3 = True
    #         continue

    #     # --- Rules apply only after H3 ---
    #     if not processing_after_h3:
    #         continue

    #     # Rule 1: subhead2 → bold paragraph
    #     if element.name == "p" and "subhead2" in element.get("class", []):
    #         text = element.get_text(strip=True)
    #         if text:
    #             paragraphs.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", "", f"**{text}**"]
    #             })
    #             handled.add(element)
    #         continue

    #     # Rule 2: Normal p
    #     if element.name == "p" and element not in handled:
    #         text = element.get_text(strip=True)
    #         if text:
    #             paragraphs.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", "", text]
    #             })
    #             handled.add(element)
    #         continue

    #     # Rule 3: Tables to Markdown
    #     if element.name == "table":
    #         block = extract_markdown_tables_with_headings(str(element))
    #         paragraphs.extend(block)
    #         handled.add(element)
    #         continue

    #     # Rule 4a: stepexpand code block
    #     if element.name == "li" and "stepexpand" in element.get("class", []):
    #         span = element.find("span")
    #         code_block = element.find("pre", class_="pre codeblock")
    #         title = span.get_text(strip=True) if span else ""
    #         code = code_block.get_text(strip=True) if code_block else ""
    #         paragraphs.append({
    #             "title": title,
    #             "hasTitle": True,
    #             "message": ["%python", "", code]
    #         })
    #         handled.add(element)
    #         continue
        
    #     # Rule 4b: regular ul or ol → markdown list (with preceding intro text)
    #     # from bs4 import NavigableString

    #     # if element.name in ["ul", "ol"] and "stepexpand" not in element.get("class", []):
    #         items = element.find_all("li", recursive=False)
    #         if items:
    #             # 1) Capture any text before the list in the parent container
    #             intro = ""
    #             parent = element.parent
    #             for node in parent.contents:
    #                 if node == element:
    #                     break
    #                 if isinstance(node, NavigableString):
    #                     intro += node.strip()
    #                 elif isinstance(node, Tag) and node.name not in ["ul", "ol"]:
    #                     intro += node.get_text(strip=True)

    #             # 2) Build the markdown list lines
    #             bullet = "-" if element.name == "ul" else "1."
    #             list_lines = [f"{bullet} {li.get_text(strip=True)}" for li in items]

    #             # 3) Combine intro + list into one %md paragraph
    #             md_lines = []
    #             if intro:
    #                 md_lines.append(intro)
    #             md_lines.extend(list_lines)

    #             paragraphs.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", ""] + md_lines
    #             })
    #             handled.add(element)
    #         continue


    #             # Rule 4b: regular ul or ol → markdown list 
    #     # (pull intro text only if parent is <div class="p">)
    #     # from bs4 import NavigableString, Tag

    #     if element.name in ["ul", "ol"] and "stepexpand" not in element.get("class", []):
    #         items = element.find_all("li", recursive=False)
    #         if items:
    #             # Only grab intro text if parent is <div class="p">
    #             intro = ""
    #             parent = element.parent
    #             if isinstance(parent, Tag) and "p" in parent.get("class", []):
    #                 for node in parent.contents:
    #                     if node == element:
    #                         break
    #                     if isinstance(node, NavigableString):
    #                         intro += node.strip()
    #                     elif isinstance(node, Tag) and node.name not in ["ul", "ol"]:
    #                         intro += node.get_text(strip=True)

    #             # Build list lines
    #             bullet = "-" if element.name == "ul" else "1."
    #             list_lines = [f"{bullet} {li.get_text(strip=True)}" for li in items]

    #             # Combine into one %md paragraph
    #             md_lines = []
    #             if intro:
    #                 md_lines.append(intro)
    #             md_lines.extend(list_lines)

    #             paragraphs.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", ""] + md_lines
    #             })
    #             handled.add(element)
    #         continue

    #     # # Rule 4b: regular ul or ol → markdown list
    #     # if element.name in ["ul", "ol"] and "stepexpand" not in element.get("class", []):
    #     #     items = element.find_all("li", recursive=False)
    #     #     if items:
    #     #         bullet = "-" if element.name == "ul" else "1."
    #     #         list_lines = [f"{bullet} {li.get_text(strip=True)}" for li in items]
    #     #         paragraphs.append({
    #     #             "title": None,
    #     #             "hasTitle": False,
    #     #             "message": ["%md", ""] + list_lines
    #     #         })
    #     #         handled.add(element)
    #     #     continue

    # paragraphs.append(relinfo_links_paragraph)
    # return paragraphs

def parse_html_in_order(html_content, url=None):
    """
    Parse HTML by top-level <div class="section"> blocks.
    - If a section has no <li class="stepexpand">, emit a single markdown paragraph for the whole section.
    - Otherwise process child elements within the section in order, applying the rules for subhead2, paragraphs, tables, lists, and stepexpand.
    Returns a list of paragraph dicts.
    """
    # Preprocess as before
    html0 = preserve_code_in_paragraphs(html_content)
    html1 = transform_infobox_notes(html0)
    html2 = preprocess_sect2_content(html1)
    mod_html, relinfo = extract_and_remove_relinfo_links(html2, url)

    soup = BeautifulSoup(mod_html, 'html.parser')
    updated = update_links(soup, "https://docs.oracle.com")

    paragraphs = []
    # Process each section as a unit
    for section in updated.find_all("div", class_="section"):
        # Detect stepexpand
        with open("my_output_file.txt", "a") as outfile:
            print("==========", file=outfile)
            print("Starting the script...", file=outfile)
            print(f"The result is: {section}", file=outfile)
            print("Script execution complete.", file=outfile)

        steps = section.find_all("li", class_="stepexpand")
        if not steps:
            # Single-block mode
            md_lines = []
            # Iterate direct children in order
            for child in section.children:
                if isinstance(child, Tag):
                    # Bold subhead2
                    if child.name == "p" and "subhead2" in child.get("class", []):
                        text = child.get_text(strip=True)
                        md_lines.append(f"**{text}**")
                    # Normal paragraph
                    elif child.name == "p":
                        txt = child.get_text(strip=True)
                        if txt:
                            md_lines.append(txt)
                    # List → bullets
                    elif child.name in ["ul", "ol"]:
                        bullet = "-" if child.name == "ul" else "1."
                        for li in child.find_all("li", recursive=False):
                            md_lines.append(f"{bullet} {li.get_text(strip=True)}")
                    # Table → markdown
                    elif child.name == "table":
                        tbl_block = extract_markdown_tables_with_headings(str(child))
                        # each block is already a paragraph dict; extend messages
                        for blk in tbl_block:
                            paragraphs.append(blk)
            # Emit single markdown paragraph if lines exist
            if md_lines:
                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": ["%md", ""] + md_lines
                })
        else:
            # Step-by-step mode: process children normally
            for el in section.descendants:
                if not isinstance(el, Tag):
                    continue
                # subhead2
                if el.name == "p" and "subhead2" in el.get("class", []):
                    txt = el.get_text(strip=True)
                    paragraphs.append({"title": None, "hasTitle": False, "message": ["%md", "", f"**{txt}**"]})
                # normal p
                elif el.name == "p":
                    txt = el.get_text(strip=True)
                    if txt:
                        paragraphs.append({"title": None, "hasTitle": False, "message": ["%md", "", txt]})
                # table
                elif el.name == "table":
                    paragraphs.extend(extract_markdown_tables_with_headings(str(el)))
                # stepexpand li
                elif el.name == "li" and "stepexpand" in el.get("class", []):
                    span = el.find("span")
                    code = el.find("pre", class_="pre codeblock")
                    title = span.get_text(strip=True) if span else ""
                    src = code.get_text(strip=True) if code else ""
                    paragraphs.append({"title": title, "hasTitle": True, "message": ["%python", "", src]})
                # normal list outside stepexpand mode
                elif el.name in ["ul", "ol"]:
                    items = el.find_all("li", recursive=False)
                    if items:
                        bullet = "-" if el.name == "ul" else "1."
                        lines = [f"{bullet} {li.get_text(strip=True)}" for li in items]
                        paragraphs.append({"title": None, "hasTitle": False, "message": ["%md", ""] + lines})
    # finally append relinfo
    paragraphs.append(relinfo)
    return paragraphs

#This handles the decendent of H3 tag rather than only the sibling:
def extract_h3_with_paragraphs(html_content, url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    output_paragraphs = []
    h3_tag = soup.find('h3')
    p_tag = soup.find('p')

    h3_text = ""
    p_text = ""
    markdown_lines = ["%md", ""]
    if h3_tag:
        h3_text = h3_tag.get_text(strip=True)
        markdown_lines.append(f"### {h3_text}")
        markdown_lines.append("")
        # print(f"H3 Text: {h3_text}")

    if p_tag:
        p_text = p_tag.get_text(strip=True)
        markdown_lines.append(p_text)
        markdown_lines.append("")
        # print(markdown_lines)
        output_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    return output_paragraphs 


#This handles the decendent rather than only the sibling:
def extract_h2_with_paragraphs(html_content, url=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    output_paragraphs = []
    # print("inside the h2 function", soup)
    h2_tag = soup.find('h2')
    p_tag = soup.find('p')

    h2_text = ""
    p_text = ""
    markdown_lines = ["%md", ""]
    if h2_tag:
        h2_text = h2_tag.get_text(strip=True)
        markdown_lines.append(f"## {h2_text}")
        markdown_lines.append("")
        # print(f"H2 Text: {h2_text}")

    if p_tag:
        p_text = p_tag.get_text(strip=True)
        markdown_lines.append(p_text)
        markdown_lines.append("")
        # print(f"P Text: {p_text}")

    # for h2 in soup.find_all('h2'):
    #     markdown_lines = ["%md", ""]

    #     # Add the H2 heading as Markdown
    #     h2_text = h2.get_text(strip=True)
    #     # print(f"Found H2: {h2_text}")
    #     markdown_lines.append(f"## {h2_text}")
    #     markdown_lines.append("")

    #     # Find the first <p> tag that is a descendant of the next sibling
    #     next_element = h2.find_next_sibling()
    #     paragraph_found = False

    #     if next_element:
    #         paragraph = next_element.find('p')
    #         print(paragraph)
    #         if paragraph:
    #             p_text = paragraph.get_text(strip=True)
    #             # print(f"  Found Paragraph (nested): {p_text}")
    #             markdown_lines.append(p_text)
    #             markdown_lines.append("")
    #             # print(markdown_lines)
    #             paragraph_found = True
    #         else:
    #             # If no <p> in the immediate sibling, check its descendants
    #             first_p_descendant = next_element.find_all('p', recursive=True)
    #             if first_p_descendant:
    #                 p_text = first_p_descendant[0].get_text(strip=True)
    #                 # print(f"  Found Paragraph (descendant): {p_text}")
    #                 markdown_lines.append(p_text)
    #                 markdown_lines.append("")
    #                 paragraph_found = True
    #             else:
    #                 print(f"  No paragraph found within or as a descendant of the sibling of '{h2_text}'.")
    #     else:
    #         print(f"  No sibling found after '{h2_text}'.")

    #     if not paragraph_found:
    #         print(f"  No paragraph found following '{h2_text}'.")

        output_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    # # Extract copyright year from metadata (moved outside the loop)
    # copyright_meta = soup.find('meta', {'name': 'dcterms.dateCopyrighted'})
    # copyright_year = ""
    # if copyright_meta:
    #     copyright_year = copyright_meta.get('content', '').replace(', ', '/')  # Handle multiple years

    # # Add the final footer block if URL or attribution is needed (moved outside the loop)
    # if url and output_paragraphs:  # Only add if there were paragraphs extracted
    #     footer_lines = ["%md", ""]
    #     footer_lines.append(f"[Source]({url})")
    #     footer_lines.append("")
    #     footer_lines.append(f"*In the business since: ({copyright_year})*")
    #     output_paragraphs[-1]["message"].extend(footer_lines) # Append to the last extracted block
    # # print(output_paragraphs)
    return output_paragraphs


# Will extract any table and its link as it is in markdown format and the paragraph table b4 it as the title.
def extract_markdown_tables_with_headings(html_content):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    table_paragraphs = []

    for table in tables:
        markdown_lines = ["%md", ""]

        # Get table headers
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if headers:
            markdown_lines.append(f"| {' | '.join(headers)} |")
            markdown_lines.append(f"| {' | '.join(['---'] * len(headers))} |")

        # Iterate over rows
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if cells:
                row_data = []
                for cell in cells:
                    # Check if there's a link inside the cell
                    link = cell.find('a')
                    if link and link.get('href'):
                        text = link.get_text(strip=True)
                        href = link['href']
                        row_data.append(f"[{text}]({href})")
                    else:
                        row_data.append(cell.get_text(strip=True))

                markdown_lines.append(f"| {' | '.join(row_data)} |")

        if len(markdown_lines) > 2:  # Make sure table has actual content
            table_paragraphs.append({
                "title": None,
                "hasTitle": False,
                "message": markdown_lines
            })

    return table_paragraphs


# def extract_markdown_tables_with_headings(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table')
    table_paragraphs = []

    for table in tables:
        # Get the table's heading (if it has one)
        headings = []
        headers = table.find_all('th')
        for header in headers:
            headings.append(header.get_text(strip=True))

        if headings:
            table_paragraphs.append({
                "title": "Table: " + ", ".join(headings),
                "hasTitle": True,
                "message": ["%md", "", f"| {' | '.join(headings)} |", "| --- |" * len(headings)]
            })

        # Extract the rows of the table
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            column_data = [col.get_text(strip=True) for col in columns]

            if column_data:
                table_paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": [f"| {' | '.join(column_data)} |"]
                })

    return table_paragraphs

# Removes any unwanted things between related content and the next header (h3) - Load data

def filter_irrelevant_content(html_content, start_marker, end_marker):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the start and end markers
    start_element = soup.find(string=start_marker)
    end_element = soup.find(string=end_marker)

    if not start_element or not end_element:
        return html_content  # Return original content if markers are not found

    # Extract content between the markers
    start_tag = start_element.find_parent()
    end_tag = end_element.find_parent()

    content_before = soup.find_all(True, {'class': True}, limit=start_tag)
    content_after = soup.find_all(True, {'class': True}, limit=end_tag)

    # We can choose to remove irrelevant content (returning filtered HTML)
    # Here I’m just returning the content before and after
    filtered_content = ''.join(str(element) for element in content_before + content_after)
    
    return filtered_content


# Parses <h3> and <h4> tags and adds them as Markdown headers along with 4 or 5 paragraph.
# def extract_h3_h4_with_paragraphs(html_content, max_paragraphs=5):
    soup = BeautifulSoup(html_content, 'html.parser')
    headers = soup.find_all(['h3', 'h4'])

    notebook_paragraphs = []

    for header in headers:
        header_level = '###' if header.name == 'h3' else '####'
        markdown_lines = ["%md", "", f"{header_level} {header.get_text(strip=True)}"]

        # Collect up to N paragraphs after the header
        paragraph_count = 0
        current = header.find_next_sibling()
        while current and paragraph_count < max_paragraphs:
            if current.name == 'p':
                text = current.get_text(strip=True)
                if text:
                    markdown_lines.append("")
                    markdown_lines.append(text)
                    paragraph_count += 1
            current = current.find_next_sibling()

        notebook_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    return notebook_paragraphs


# def extract_h3_h4_with_paragraphs(html_content, max_paragraphs=5):
    soup = BeautifulSoup(html_content, 'html.parser')
    headers = soup.find_all(['h3', 'h4'])
    notebook_paragraphs = []

    for header in headers:
        header_level = '###' if header.name == 'h3' else '####'
        markdown_lines = ["%md", "", f"{header_level} {header.get_text(strip=True)}"]

        # print(markdown_lines)
        content_after_header = []
        current = header.find_next_sibling()
        while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
            content_after_header.append(current)
            current = current.find_next_sibling()

        print(current)
        paragraph_count = 0
        for element in content_after_header:
            # print('printing element in function', element)
            if element.name == 'p' and paragraph_count < max_paragraphs:
                text = element.get_text(strip=True)
                if text:
                    markdown_lines.append("")
                    markdown_lines.append(text)
                    paragraph_count += 1
            elif element.name == 'ul':
                list_items = element.find_all('li')
                if list_items:
                    markdown_lines.append("")
                    for li in list_items:
                        markdown_lines.append(f"* {li.get_text(strip=True)}")

        print("this is md b4 para:", markdown_lines)
        notebook_paragraphs.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    return notebook_paragraphs

# def extract_h3_h4_with_paragraphs(header, max_paragraphs=5):
    header_level = '###' if header.name == 'h3' else '####'
    markdown_lines = ["%md", "", f"{header_level} {header.get_text(strip=True)}"]
    paragraph_count = 0
    current = header.find_next_sibling()

    while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
        if current.name == 'p' and paragraph_count < max_paragraphs:
            text = current.get_text(strip=True)
            if text:
                markdown_lines.append("")
                markdown_lines.append(text)
                paragraph_count += 1
        elif current.name == 'ul':
            list_items = current.find_all('li')
            if list_items:
                markdown_lines.append("")
                for li in list_items:
                    markdown_lines.append(f"* {li.get_text(strip=True)}")
        current = current.find_next_sibling()

    print("this is md b4 para:", markdown_lines)
    return {
        "title": None,
        "hasTitle": False,
        "message": markdown_lines
    }

def extract_h3_h4_with_paragraphs(header, max_paragraphs=5):
    header_level = '###' if header.name == 'h3' else '####'
    markdown_lines = ["%md", "", f"{header_level} {header.get_text(strip=True)}"]
    paragraph_count = 0
    current = header.find_next_sibling()

    while current and (not isinstance(current, Tag) or current.name not in ['h1', 'h2', 'h3', 'h4']):
        if isinstance(current, Tag):
            if current.name == 'p' and paragraph_count < max_paragraphs:
                text = current.get_text(strip=True)
                if text:
                    markdown_lines.append("")
                    markdown_lines.append(text)
                    paragraph_count += 1
            elif current.name == 'ul':
                list_items = current.find_all('li')
                if list_items:
                    markdown_lines.append("")
                    for li in list_items:
                        markdown_lines.append(f"* {li.get_text(strip=True)}")
        current = current.find_next_sibling()

    # print("this is md b4 para:", markdown_lines)
    with open("my_output_file.txt", "w") as outfile:
        print("Starting the script...", file=outfile)
        print(f"The result is: {markdown_lines}", file=outfile)
        print("Script execution complete.", file=outfile)


    return {
        "title": None,
        "hasTitle": False,
        "message": markdown_lines
    }


# Extract the ul or ol as new paragraph  for each li. The span as the title and the code as the content of the paragraph.
def li_to_custom_paragraph(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    list_items = soup.find_all('li')

    notebook_paragraphs = []

    for li in list_items:
        # Get the span text as title
        span = li.find('span')
        if not span:
            continue  # skip if there's no title

        title_text = span.get_text(strip=True)
        has_title = True if title_text else False

        # Search for code blocks in <code> or <pre><code>
        code_block = li.find('pre')
        if not code_block or 'nocopybutton' in code_block.get('class', []):
            continue  # Skip if it's not a proper code block or marked as ignorable

        code_element = code_block.find('code') or code_block
        code_text = code_element.get_text()

        # Construct the paragraph
        paragraph = {
            "title": title_text,
            "hasTitle": has_title,
            "message": ["%python", ""] + code_text.strip().splitlines()
        }

        notebook_paragraphs.append(paragraph)

    return notebook_paragraphs

