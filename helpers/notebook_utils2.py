

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

def process_section_block(section, base_url):
    def process_list(tag):
        items = []
        for li in tag.find_all("li", recursive=False):
            text = li.get_text(strip=True)
            if tag.name == "ul":
                items.append(f"- {text}")
            else:
                items.append(f"1. {text}")
        return items

    def convert_table_to_markdown(table_tag):
        headers = [th.get_text(strip=True) for th in table_tag.find_all("th")]
        rows = []
        for tr in table_tag.find_all("tr"):
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cols:
                rows.append(cols)
        if not headers and rows:
            headers = ["Column " + str(i+1) for i in range(len(rows[0]))]
        if not headers:
            return ""
        markdown = ["| " + " | ".join(headers) + " |"]
        markdown.append("|" + "|".join([" --- " for _ in headers]) + "|")
        for row in rows:
            markdown.append("| " + " | ".join(row) + " |")
        return "\n".join(markdown)

    paragraph_blocks = []
    has_stepexpand = section.find("li", class_="stepexpand") is not None

    if has_stepexpand:
        for li in section.find_all("li", class_="stepexpand"):
            title_tag = li.find("span")
            code_tag = li.find("pre", class_="codeblock")
            if title_tag and code_tag:
                title = title_tag.get_text(strip=True)
                code = code_tag.get_text()
                paragraph_blocks.append({
                    "title": title,
                    "hasTitle": True,
                    "message": ["%md", f"```\n{code}\n```"]
                })
    else:
        markdown_lines = ["%md", ""]
        for child in section.descendants:
            if not isinstance(child, Tag):
                continue

            if child.name == "p" and "subhead2" in child.get("class", []):
                markdown_lines.append(f"**{child.get_text(strip=True)}**")
            elif child.name == "p":
                markdown_lines.append(child.get_text(strip=True))
            elif child.name in ["ul", "ol"]:
                markdown_lines.extend(process_list(child))
            elif child.name == "table":
                table_md = convert_table_to_markdown(child)
                if table_md:
                    markdown_lines.append(table_md)
        paragraph_blocks.append({
            "title": None,
            "hasTitle": False,
            "message": markdown_lines
        })

    return paragraph_blocks

# def parse_html_in_order(html_content, url=None):
    pass
    # soup = BeautifulSoup(html_content, 'html.parser')
    # all_sections = []

    # # Identify the main container
    # main_container = soup.find("div", class_="ind")
    # if not main_container:
    #     return []

    # # Get all divs with class section under main_container and under any sect2
    # sections = main_container.find_all("div", class_="section")
    
    # for section in sections:
    #     if section.find("li", class_="stepexpand"):
    #         # Handle case where li.stepexpand is present — break into individual paragraphs
    #         for li in section.find_all("li", class_="stepexpand"):
    #             span = li.find("span")
    #             code = li.find("pre", class_="codeblock")
    #             title = span.get_text(strip=True) if span else ""
    #             code_text = code.get_text(strip=True) if code else ""
    #             all_sections.append({
    #                 "title": title,
    #                 "hasTitle": True,
    #                 "message": ["%md", "", f"**{title}**\n\n```python\n{code_text}\n```"]
    #             })
    #     else:
    #         # Handle standard sections as single paragraph block
    #         parts = []
    #         for el in section.descendants:
    #             if isinstance(el, Tag):
    #                 if el.name == "p":
    #                     if "subhead2" in el.get("class", []):
    #                         parts.append(f"**{el.get_text(strip=True)}**")
    #                     else:
    #                         parts.append(el.get_text(strip=True))
    #                 elif el.name in ["ul", "ol"]:
    #                     list_items = []
    #                     for li in el.find_all("li"):
    #                         bullet = "-" if el.name == "ul" else "1."
    #                         list_items.append(f"{bullet} {li.get_text(strip=True)}")
    #                     parts.append("\n".join(list_items))
    #                 elif el.name == "table":
    #                     headers = [th.get_text(strip=True) for th in el.find_all("th")]
    #                     rows = [
    #                         [td.get_text(strip=True) for td in tr.find_all("td")]
    #                         for tr in el.find_all("tr")
    #                     ]
    #                     md_table = ["| " + " | ".join(headers) + " |"] if headers else []
    #                     if headers:
    #                         md_table.append("| " + " | ".join(["---"] * len(headers)) + " |")
    #                     for row in rows:
    #                         md_table.append("| " + " | ".join(row) + " |")
    #                     parts.append("\n".join(md_table))
    #         if parts:
    #             all_sections.append({
    #                 "title": None,
    #                 "hasTitle": False,
    #                 "message": ["%md", "", "\n\n".join(parts)]
    #             })
    # return all_sections



# from bs4 import BeautifulSoup, Tag

def parse_html_in_order(html_content, url = None):
    soup = BeautifulSoup(html_content, 'html.parser')
    all_sections = []

    # Identify the main container
    main_container = soup.find("div", class_="ind")
    if not main_container:
        return []

    # Get all divs with class section under main_container and under any sect2
    sections = main_container.find_all("div", class_="sect2")
    sections = main_container.find_all("div", class_="section")
    with open("my_output_file.txt", "w") as outfile:
        # print("==========", file=outfile)
        # print("Starting the script...", file=outfile)
        print(f"The result is: {sections}", file=outfile)
        # print("Script execution complete.", file=outfile)

    
    for section in sections:
        if section.find("li", class_="stepexpand"):
            # Handle case where li.stepexpand is present — break into individual paragraphs
            for li in section.find_all("li", class_="stepexpand"):
                span = li.find("span")
                code = li.find("pre", class_="codeblock")
                title = span.get_text(strip=True) if span else ""
                code_text = code.get_text(strip=True) if code else ""
                all_sections.append({
                    "title": title,
                    "hasTitle": True,
                    "message": ["%md", "", f"**{title}**\n\n```python\n{code_text}\n```"]
                })
        else:
            # Handle standard sections as single paragraph block
            parts = []
            for el in section.descendants:
                if isinstance(el, Tag):
                    if el.name == "p":
                        if "subhead2" in el.get("class", []):
                            parts.append(f"**{el.get_text(strip=True)}**")
                        else:
                            parts.append(el.get_text(strip=True))
                    elif el.name in ["ul", "ol"]:
                        list_items = []
                        for li in el.find_all("li"):
                            bullet = "-" if el.name == "ul" else "1."
                            list_items.append(f"{bullet} {li.get_text(strip=True)}")
                        parts.append("\n".join(list_items))
                    elif el.name == "table":
                        headers = [th.get_text(strip=True) for th in el.find_all("th")]
                        rows = [
                            [td.get_text(strip=True) for td in tr.find_all("td")]
                            for tr in el.find_all("tr")
                        ]
                        md_table = ["| " + " | ".join(headers) + " |"] if headers else []
                        if headers:
                            md_table.append("| " + " | ".join(["---"] * len(headers)) + " |")
                        for row in rows:
                            md_table.append("| " + " | ".join(row) + " |")
                        parts.append("\n".join(md_table))
            if parts:
                all_sections.append({
                    "title": None,
                    "hasTitle": False,
                    "message": ["%md", "", "\n\n".join(parts)]
                })
    return all_sections



