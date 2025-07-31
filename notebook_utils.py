from bs4 import BeautifulSoup, Tag
import json

def extract_text_from_tag(tag):
    """Convert tag and its contents to clean markdown text."""
    return tag.get_text(strip=True, separator="\n")

def process_section(section):
    """Process one <div class="section"> into notebook paragraphs."""
    paragraphs = []
    step_items = section.find_all("li", class_="stepexpand")
    logging.info(step_items)
    if step_items:
        for li in step_items:
            text = extract_text_from_tag(li)
            print(text)
            if text:
                paragraphs.append({
                    "title": None,
                    "hasTitle": False,
                    "message": ["%md", "", text]
                })
    else:
        combined_text = extract_text_from_tag(section)
        if combined_text:
            paragraphs.append({
                "title": None,
                "hasTitle": False,
                "message": ["%md", "", combined_text]
            })
    
    return paragraphs

def parse_html_to_nbcc(html_content):
    """Main parsing logic."""
    soup = BeautifulSoup(html_content, "html.parser")
    ind = soup.find("div", class_="ind")
    if not ind:
        return []

    final_paragraphs = []

    # Process top-level <div class="section"> directly under <div class="ind">
    for child in ind.find_all(recursive=False):
        if isinstance(child, Tag) and child.name == "div":
            if "section" in child.get("class", []):
                # pass
                with open("my_output_file.txt", "w") as outfile:
                    print("===================================", file=outfile)
                    print(f"{child}", file=outfile)
                    print("===================================", file=outfile)

                # final_paragraphs.extend(process_section(child))
            elif "sect2" in child.get("class", []):
                pass
                # with open("my_output_file.txt", "a") as outfile:
                #     print("===================================", file=outfile)
                #     print(f"{child}", file=outfile)
                #     print("===================================", file=outfile)

                # for sub_child in child.find_all(recursive=False):
                #     if isinstance(sub_child, Tag):
                #         if "section" in sub_child.get("class", []):
                #             final_paragraphs.extend(process_section(sub_child))
                #         else:
                #             # orphan elements outside <div class="section">
                #             last = final_paragraphs[-1]["message"] if final_paragraphs else ["%md", ""]
                #             last_text = extract_text_from_tag(sub_child)
                #             if last_text:
                #                 if final_paragraphs:
                #                     final_paragraphs[-1]["message"].append(last_text)
                #                 else:
                #                     final_paragraphs.append({
                #                         "title": None,
                #                         "hasTitle": False,
                #                         "message": ["%md", "", last_text]
                #                     })

    return [{
        "name": "Classification Use Case Scenario",
        "paragraphs": final_paragraphs
    }]

def save_nbcc(data, output_path="output.nbcc"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
