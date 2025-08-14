#notebook_utils.py
import helpers.notebook_utils2 as utils2
# Step 1: Required Libraries
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
import json
from urllib.parse import urljoin
from collections import OrderedDict


# Mkaing the interpreter as a global vairable so that s it can be accesssed by any funtcion.
product_equivalent = "%sql"  # default

def set_product_equivalent(value):
    global product_equivalent
    product_equivalent = value

# get the footer
## Update this function with a new paragraph such that the title and the description is directly taken and append it the very start of the paragraph.
# eliminating any need for adding of the footer.
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

# Finds the first paragraph after a tag.
def get_first_paragraph_in_next_sibling_descendants(tag):
        next_sibling = tag.find_next_sibling()
        # if next_sibling:
        #     return next_sibling.find('p')
        if isinstance(next_sibling, Tag):
            return next_sibling.find('p')
        return None

# Handles tables where if any cell has a link, ol, ul or break in it.
def extract_markdown_tables_with_headings(table):
        from bs4 import BeautifulSoup

        # soup = BeautifulSoup(html_content, 'html.parser')
        tables = table.find_all('table')
        all_markdown_lines = []

        for table in tables:
            markdown_lines = []

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
                        cell_content = []

                        # Handle multiple paragraphs
                        for p in cell.find_all('p', recursive=False):
                            # Preserve links inside paragraphs
                            paragraph_parts = []
                            for child in p.children:
                                if child.name == 'a' and child.get('href'):
                                    link_text = child.get_text(strip=True)
                                    href = child['href']
                                    paragraph_parts.append(f"[{link_text}]({href})")
                                elif isinstance(child, str):
                                    paragraph_parts.append(child.strip())
                                else:
                                    paragraph_parts.append(child.get_text(strip=True))
                            cell_content.append(' '.join(paragraph_parts).strip())

                        # Handle unordered lists
                        ul = cell.find('ul', recursive=False)
                        if ul:
                            for li in ul.find_all('li', recursive=False):
                                cell_content.append(f"- {li.get_text(strip=True)}")

                        # Handle ordered lists
                        ol = cell.find('ol', recursive=False)
                        if ol:
                            for i, li in enumerate(ol.find_all('li', recursive=False), start=1):
                                cell_content.append(f"{i}. {li.get_text(strip=True)}")

                        # Fallback: raw text or link
                        if not cell_content:
                            link = cell.find('a')
                            if link and link.get('href'):
                                text = link.get_text(strip=True)
                                href = link['href']
                                cell_content.append(f"[{text}]({href})")
                            else:
                                cell_content.append(cell.get_text(strip=True))

                        row_data.append("<br>".join(cell_content))

                    markdown_lines.append(f"| {' | '.join(row_data)} |")

            if len(markdown_lines) > 2:
                all_markdown_lines.extend(markdown_lines)
                all_markdown_lines.append("")  # Add spacing between tables

        return "\n".join(all_markdown_lines)

def is_paragraph_like(element): #check karta h tag ki usse p tag parse karna h ki nahi
    """Returns True if element is a <p> or <div class='p'> not inside <table> or restricted <ol>."""
    if not isinstance(element, Tag):
        return False

    is_p_or_div_p = (
        element.name == 'p' or 
        (element.name == 'div' and 'p' in element.get('class', []))
    )
    
    if not is_p_or_div_p:
        return False

    if element.find_parent('table'):
        return False

    ol_parent = element.find_parent('ol')
    if ol_parent and ol_parent.find('li', class_='stepexpand'):
        return False

    return True


def handle_paragraph_like_element1(element, buffer):  # Kisi bhi paragraph tag ko buffer m adjust karta h
    paragraph_parts = []

    for child in element.children:
        if isinstance(child, NavigableString):
            paragraph_parts.append(str(child).strip())

        elif isinstance(child, Tag):
            # Skip block-level tags (leave for other functions)
            if child.name in {'ul', 'ol', 'table', 'div', 'section','b'}:
                # print(child.name)
                continue

            if child.name == 'a' and child.get('href'):
                link_text = child.get_text(strip=True)
                href = child['href']
                paragraph_parts.append(f"[{link_text}]({href})")
            elif child.name == 'strong' or child.name == 'b':
                bold_text = child.get_text(strip=True)
                paragraph_parts.append(f"**{bold_text}**")
            elif child.name == 'em':
                italic_text = child.get_text(strip=True)
                paragraph_parts.append(f"*{italic_text}*")
            else:
                paragraph_parts.append(child.get_text(strip=True))

    text = ' '.join(part for part in paragraph_parts if part).strip()
    # print("====", text)

    if 'subhead2' in element.get('class', []):
        buffer.append(f"**{text}**")
    else:
        buffer.append(text)
    # print(text)

def handle_paragraph_like_element(element, buffer):
    paragraph_parts = []

    for child in element.contents:  # Use .contents instead of .children to preserve order
        if isinstance(child, NavigableString):
            paragraph_parts.append(str(child).strip())

        elif isinstance(child, Tag):
            # Skip nested paragraph or block tags — they’ll be processed later
            if child.name in {'p', 'ul', 'ol', 'table', 'section', 'div'}:
                continue

            if child.name == 'a' and child.get('href'):
                link_text = child.get_text(strip=True)
                href = child['href']
                paragraph_parts.append(f"[{link_text}]({href})")
            elif child.name == 'strong' or 'b':
                bold_text = child.get_text(strip=True)
                paragraph_parts.append(f"**{bold_text}**")
            # elif child.name == 'b':
            #     italic_text = child.get_text(strip=True)
            #     paragraph_parts.append(f"*{bold_text}*")
            else:
                paragraph_parts.append(child.get_text(strip=True))

    text = ' '.join(part for part in paragraph_parts if part).strip()
    # print("====", text)

    if 'subhead2' in element.get('class', []):
        buffer.append(f"\n**{text}**\n")
    else:
        buffer.append(text+ "\n")

# Handles ol with li containing stepexpand. aur ekya 
def process_ordered_list_items(ol_tag, product_equivalent="%sql"):
    """Process each <li> in an <ol> into notebook paragraphs."""
    paragraphs = []

    for li in ol_tag.find_all("li", recursive=False):
        if "stepexpand" in li.get("class", []):
            title = ""
            code_content = ""
            markdown_parts = []

            span = li.find("span")
            if span:
                title = span.get_text(strip=True)

            found_code = False
            for tag in li.find_all(recursive=False):
                if tag.name == "span":
                    continue

                if not found_code:
                    code_tag = tag.find("pre", class_=lambda c: c and ("pre codeblock" in c or "oac_no_warn" in c))
                    if code_tag:
                        code_content = code_tag.get_text(strip=True)
                        found_code = True
                        continue

                if found_code:
                    if tag.find("pre", class_="nocopybutton"):
                        continue

                    # Convert paragraphs, divs, lists, tables to markdown
                    for sub in tag.find_all(['p', 'div', 'ul', 'ol', 'table'], recursive=True):
                        markdown = tag_to_markdown(sub)
                        if markdown:
                            markdown_parts.append(markdown)

            # Code paragraph
            if code_content:
                paragraphs.append({
                    "title": title,
                    "hasTitle": True,
                    "message": [product_equivalent, "", code_content],
                    "hideGutter" : True,
                    "hideVizConfig" : True,
                })

            # Markdown paragraph
            if markdown_parts:
                paragraphs.append({
                    "hasTitle": False,
                    "hideCode" : True,
                    "hideGutter" : True,
                    "hideVizConfig" : True,
                    "forms" : "[]",
                    "message": ["%md", "", "\n\n".join(markdown_parts)],
                    "selectedVisualization" : "html",
                    "relations" : [ ],
                    "dynamicFormParams" : "{}"

                })

    return paragraphs


# Chedne ka nahi: Extracted related topic function working fine
def extract_related_topic_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 1: Find all tags with class="relinfo"
    relinfo_tags = soup.find_all(class_="relinfo")

    # Step 2: Extract all <a> tags, preserving order and uniqueness
    link_dict = OrderedDict()
    for tag in relinfo_tags:
        for link in tag.find_all("a", href=True):
            href = link['href']
            if href not in link_dict:
                link_dict[href] = link.get_text(strip=True)

    # Step 3: Format as Markdown unordered list
    if link_dict:
        markdown_links = "### Related link\n" + "\n".join(
            f"- [{text}]({href})" for href, text in link_dict.items()
        )
    else:
        markdown_links = ""

    # Step 3: Format as Markdown
    # markdown_links = "\n".join(f"[{text}]({href})" for href, text in link_dict.items())
    # print(type(markdown_links))
    # with open("my_output_file1.txt", "w") as outfile:
    #     print("===================================", file=outfile)
    #     print(f"{markdown_links}", file=outfile)
    #     print("===================================", file=outfile)

    # Step 4: Remove relinfo sections from soup
    for tag in relinfo_tags:
        tag.decompose()

    return soup, markdown_links


#written so as to avoid any ul/ol inside an li with stepexpand inside an ol.
def is_nested_within_stepexpand_ol(element):
    """
    Checks if an element is nested within an <ol> that contains a <li> with class "stepexpand".
    """
    # print("yes")
    for parent in element.parents:
        if parent.name == 'ol':
            # print(parent.name)
            # Check if this parent <ol> has any direct child <li> with "stepexpand" class
            for li in parent.find_all('li', recursive=False):
                if 'stepexpand' in li.get('class', []):
                    return True
    return False



def process_section(section):
    """Processes a section, including table handling."""
    soup = section
    output = []
    buffer = []
    title = None
    hasTitle = False

    for element in soup.descendants:
        if isinstance(element, Tag):
            if element.name == 'h3':
                # If there's content in the buffer, create an object first
                if buffer:
                    # print(buffer)
                    output.append({
                        "title": title,
                        "hasTitle": False,
                        "hideCode" : True,
                        "hideGutter" : True,
                        "hideVizConfig" : True,
                        "forms" : "[]",
                        "message": ["%md", "", "\n".join(buffer)],
                        "selectedVisualization" : "html",
                        "relations" : [ ],
                        "dynamicFormParams" : "{}"

                    })
                    buffer = []  # Clear the buffer
                title = element.get_text(strip=True)
                hasTitle = True
                buffer.append(f"### **{title}**\n")
                # print(title, buffer)

            elif element.name == 'h4':
                h4_text= element.get_text(strip=True)
                buffer.append(f"#### **{h4_text}**\n")

            elif is_paragraph_like(element): #need to return buffer if you're passing buffer as a mutable list.
# In Python, lists are mutable, so any updates made to buffer inside the function will reflect outside the function too. 
                handle_paragraph_like_element(element, buffer)

            elif element.name == 'ol':
                if is_nested_within_stepexpand_ol(element):
                    continue  # Skip processing, it will be handled by process_ordered_list_items

                first_li = element.find('li', recursive=False)
                if first_li and "stepexpand" in first_li.get("class", []):
                    # Create an object with the buffer content *before* processing the stepexpand ol
                    # print(first_li.get_text(strip=True))
                    if buffer:
                        output.append({
                            "title": title,
                            "hasTitle": False,
                            "hideCode" : True,
                            "hideGutter" : True,
                            "hideVizConfig" : True,
                            "forms" : "[]",
                            "message": ["%md", "", "\n".join(buffer)],
                            "selectedVisualization" : "html",
                            "relations" : [ ],
                            "dynamicFormParams" : "{}"

                        })
                        # print(buffer)
                        buffer = []
                    #  Extend the output with the result of process_ordered_list_items
                    output.extend(process_ordered_list_items(element)) # UNDO THIS LINE FOR CODE PARAGRAPHS
                    title = None # Reset title
                    hasTitle = False
                else:
                    ol_text = []
                    for li in element.find_all('li', recursive=False):
                        ol_text.append(f"1. {li.get_text(strip=True)}")
                    buffer.append("\n".join(ol_text) + "\n")
            elif element.name == 'ul':
                if is_nested_within_stepexpand_ol(element):
                    continue  # Skip processing, it will be handled by process_ordered_list_items
                              
                # Check if the <ul> is within a <li class="stepexpand">
                parent_li = element.find_parent('li')
                if parent_li and 'stepexpand' in parent_li.get('class', []):
                    continue  # Skip processing this <ul> as it's handled elsewhere

                ul_text = []
                for li in element.find_all('li'):
                    ul_text.append(f"* {li.get_text(strip=True)}")
                buffer.append("\n".join(ul_text)+ "\n")
            elif element.name == 'table':  # Handle table tags
                mock_html = f"<html><body>{str(element)}</body></html>"
                mock_soup = BeautifulSoup(mock_html, 'html.parser')
                table_markdown = extract_markdown_tables_with_headings(mock_soup)  # Get Markdown table
                buffer.append(table_markdown+ "  \n") # Add to the buffer

            elif element.name == 'div' and 'section' in element.get('class', []):
                # Extract only direct text nodes, excluding nested tags like <p>
                text_nodes = [t for t in element.contents if isinstance(t, str) and t.strip()]
                text = ' '.join(text_nodes).strip()
                if text:
                    buffer.append(text+ "  \n")


    # Add any remaining content in the buffer as a final object
    if buffer:
        output.append({
            "title": title,
            "hasTitle": False,
            "hideCode" : True,
            "hideGutter" : True,
            "hideVizConfig" : True,
            "forms" : "[]",
            "message": ["%md", "", "\n".join(buffer)],
            "selectedVisualization" : "html",
            "relations" : [ ],
            "dynamicFormParams" : "{}"

        })


    return output
    # return None

def tag_to_markdown(tag):
    """Convert supported tags to Markdown."""
    parts = []

    def recurse(child):
        if isinstance(child, NavigableString):
            parts.append(str(child).strip())
        elif isinstance(child, Tag):
            if child.name in ['strong', 'b']:
                parts.append(f"**{child.get_text(strip=True)}**")
            elif child.name in ['em', 'i']:
                parts.append(f"*{child.get_text(strip=True)}*")
            elif child.name == 'a' and child.get('href'):
                link_text = child.get_text(strip=True)
                href = child['href']
                parts.append(f"[{link_text}]({href})")
            elif child.name in ['ul', 'ol']:
                for li in child.find_all('li', recursive=False):
                    prefix = "-" if child.name == 'ul' else "1."
                    li_text = tag_to_markdown(li)
                    parts.append(f"{prefix} {li_text.strip()}")
            elif child.name == 'table':
                # table_md = convert_table_to_markdown(child)
                table_md = extract_markdown_tables_with_headings(child)
                parts.append(table_md)
            elif child.name == 'li':
                pass  # handled above
            else:
                for sub in child.children:
                    recurse(sub)

    recurse(tag)
    return ' '.join(parts).strip()

# Called from convert to markdown
def handle_text_with_links(t):
        """Converts a tag to text with links preserved."""
        parts = []
        for content in t.descendants:
            if isinstance(content, NavigableString):
                parts.append(content.strip())
            elif isinstance(content, Tag) and content.name == "a":
                href = content.get("href", "")
                text = content.get_text(strip=True)
                parts.append(f"[{text}]({href})")
        return " ".join(filter(None, parts)).strip()

def extract_markdown_tables_with_headings_pre_sect221(soup):
    """
    Converts the first <table> in the soup to Markdown format.
    Handles <a> tags (hrefs), does NOT handle rowspan or colspan.
    """
    def get_cell_text(cell):
        for a in cell.find_all("a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            a.replace_with(f"[{text}]({href})")
        return cell.get_text(strip=True)

    table = soup.find("table")
    if not table:
        return ""

    rows = table.find_all("tr")
    if not rows:
        return ""

    markdown_rows = []

    # Header row
    header_cells = rows[0].find_all(["th", "td"])
    headers = [get_cell_text(cell) for cell in header_cells]
    markdown_rows.append("| " + " | ".join(headers) + " |")
    markdown_rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Remaining rows
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        values = [get_cell_text(cell) for cell in cells]
        markdown_rows.append("| " + " | ".join(values) + " |")

    return "\n".join(markdown_rows)

def extract_markdown_tables_with_headings_pre_sect2(table_tag):
    """
    Converts a <table> Tag to Markdown format.
    Handles <a> tags (hrefs). Ignores rowspan and colspan.
    """
    from bs4 import Tag

    def get_cell_text(cell: Tag):
        for a in cell.find_all("a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            a.replace_with(f"[{text}]({href})")
        return cell.get_text(strip=True)

    if not table_tag or table_tag.name != "table":
        return ""

    rows = table_tag.find_all("tr")
    if not rows:
        return ""

    markdown_rows = []

    # Header row
    header_cells = rows[0].find_all(["th", "td"])
    headers = [get_cell_text(cell) for cell in header_cells]
    markdown_rows.append("| " + " | ".join(headers) + " |")
    markdown_rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Remaining rows
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        values = [get_cell_text(cell) for cell in cells]
        markdown_rows.append("| " + " | ".join(values) + " |")

    return "\n".join(markdown_rows)


def convert_to_markdown(tag,h2_tag,url):
    first_para = ""
    second_para_buffer = []
    first_p_found = False

    def recurse(t):
        nonlocal first_para, first_p_found

        if isinstance(t, NavigableString):
            stripped = t.strip()
            if stripped:
                second_para_buffer.append(stripped)

        elif isinstance(t, Tag):
            # Bold text if p tag with class subhead1
            if t.name == "p" and "subhead1" in t.get("class", []):
                bold_text = "**" + handle_text_with_links(t) + "**"
                if not first_p_found:
                    first_para = bold_text
                    first_p_found = True
                else:
                    second_para_buffer.append(bold_text + '  \n')

            elif t.name == "p" and not first_p_found:
                first_para = handle_text_with_links(t)
                first_p_found = True

            elif t.name == "ul":
                for li in t.find_all("li", recursive=False):
                    line = "- " + handle_text_with_links(li)
                    second_para_buffer.append(line)

            elif t.name == "ol":
                for i, li in enumerate(t.find_all("li", recursive=False), start=1):
                    line = f"{i}. " + handle_text_with_links(li)
                    second_para_buffer.append(line)

            elif t.name == "a":
                # fallback for anchors outside p/li
                href = t.get("href", "")
                text = t.get_text(strip=True)
                second_para_buffer.append(f"[{text}]({href})")

            elif t.name == "table":  # Handle tables with markdown conversion
            #     # Use your existing helper to convert HTML table to markdown
            #     # Make sure extract_markdown_tables_with_headings returns a markdown string
            #     table_markdown = extract_markdown_tables_with_headings(t)
            #     second_para_buffer.append(table_markdown + "\n")

            # Wrap table tag string inside a minimal soup
                # mock_html = f"<html><body>{str(t)}</body></html>"
                # mock_soup = BeautifulSoup(mock_html, 'html.parser')
                table_markdown = extract_markdown_tables_with_headings_pre_sect2(t)  # Pass full soup
                second_para_buffer.append(table_markdown + "\n")

            else:
                for child in t.children:
                    recurse(child)

    recurse(tag)

    results = []

    if first_para:
        # print(type(first_para))
        updated_first_para = f"## **{h2_tag}**\n\n" + first_para
        # first_para.insert(0, f"### {h2_tag}\n\n")
        updated_first_para += " " + f"  \nRefer to the documentation, [here]({url})" + "<br>" + "  \nCopyright (c) 2025 Oracle Corporation " + "  \n###### [The Universal Permissive License (UPL), Version 1.0](https://oss.oracle.com/licenses/upl/)"
        results.append({
            "title": None,
            "hasTitle": False,
            "hideCode" : True,
            "hideGutter" : True,
            "hideVizConfig" : True,
            "forms" : "[]",
            "message": ["%md", "", updated_first_para],
            "selectedVisualization" : "html",
            "relations" : [ ],
            "dynamicFormParams" : "{}"

        })

    if second_para_buffer:
        results.append({
            "title": "Related Links",
            "hasTitle": False,
            "hideCode" : True,
            "hideGutter" : True,
            "hideVizConfig" : True,
            "forms" : "[]",
            "message": ["%md", "", "\n".join(second_para_buffer)],
            "selectedVisualization" : "html",
            "relations" : [ ],
            "dynamicFormParams" : "{}"

        })

    return results if results else None

def random_fun():
    pass
