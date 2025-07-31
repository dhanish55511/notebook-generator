# main.py

import os
import json
import helpers.notebook_utils2 as utils

def build_custom_dsnb_notebook(url):
    html_content = utils.fetch_html(url)
    last_lines = utils.get_footer(html_content, url)
    # html_content, links_paragraph = utils.extract_and_remove_relinfo_links(html_content)
    # print(links_paragraph)

    # filtered_html_content = last_lines
    
    filtered_html_content = utils.filter_irrelevant_content(html_content, "Related Content", "Next Section Title")

    # One-pass sequential parsing
    all_paragraphs = utils.parse_html_in_order(filtered_html_content, url)

    notebook_title = utils.get_notebook_title_from_html(html_content)

    if url and all_paragraphs:
        # footer_lines = ["", f"[Source]({url})", "", "*In the business since: ({copyright_year})*"]
        if all_paragraphs[0] and all_paragraphs[0]['message']:
            all_paragraphs[0]['message'].extend(last_lines)
        else:
            all_paragraphs.insert(0, {
                "title": None,
                "hasTitle": False,
                "message": ["%md"] + last_lines
            })

    notebook_data = [{
        "name": notebook_title,
        "paragraphs": all_paragraphs
    }]

    return notebook_data

# ---- EXECUTE ----

# url = "https://abc.com"
url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"
# url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4py/2/mlpuc/regression.html"
notebook = build_custom_dsnb_notebook(url)

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)

# Write to file
with open("output/my_notebook.nbcc", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)





# # main.py
# import json
# # from helpers.notebook_utils import fetch_html, get_notebook_title_from_html, extract_h2_with_paragraphs
# import helpers.notebook_utils as utils

# # Using functions from the utils module
# def build_custom_dsnb_notebook(url):
#     html_content = utils.fetch_html(url)

#     # Step 1: Get the notebook title
#     notebook_title = utils.get_notebook_title_from_html(html_content)

#     tables = utils.extract_markdown_tables_with_headings(filtered_html_content)
#     print(tables)
#     # Step 2: Filter irrelevant content (if needed)
#     filtered_html_content = utils.filter_irrelevant_content(html_content, "Related Content", "Next Section Title")

#     # Step 3: Extract H2 paragraphs
#     h2_paragraphs = utils.extract_h2_with_paragraphs(filtered_html_content, url)

#     print(h2_paragraphs)
#     # Step 4: Extract markdown tables
#     tables = utils.extract_markdown_tables_with_headings(filtered_html_content)

#     # Step 5: Extract h3 and h4 blocks
#     h3_h4_blocks = utils.extract_h3_h4_with_paragraphs(filtered_html_content)

#     utils.li_to_custom_paragraph(filtered_html_content)

#     all_paragraphs = (
#     utils.extract_h2_with_paragraphs(filtered_html_content, url) +
#     utils.extract_h3_h4_with_paragraphs(filtered_html_content) +
#     utils.extract_markdown_tables_with_headings(filtered_html_content) +
#     utils.li_to_custom_paragraph(filtered_html_content)
# )


#     # Combine everything into the notebook structure
#     # notebook_data = [{
#     #     "name": notebook_title,
#     #     "paragraphs": h2_paragraphs + tables + h3_h4_blocks # Adding tables to the paragraphs
#     # }]

#     # Combine everything into the notebook structure
#     notebook_data = [{
#         "name": notebook_title,
#         "paragraphs": h2_paragraphs + tables + h3_h4_blocks# Adding tables to the paragraphs
#     }]


#     return notebook_data

# # Generate and save
# url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"
# notebook = build_custom_dsnb_notebook(url)

# with open("output/my_notebook.dsnb", "w", encoding="utf-8") as f:
#     json.dump(notebook, f, indent=2)


#top function is commented out.

# def build_custom_dsnb_notebook(url):
#     html_content = utils.fetch_html(url)


#     # # Step 1: Get the notebook title
#     notebook_title = utils.get_notebook_title_from_html(html_content)
#     #print(notebook_title) #Classification Use Case Scenario

#     # # Step 2: Filter content between markers
#     filtered_html_content = utils.filter_irrelevant_content(
#         html_content, "Related Content", "Next Section Title"
#     )
#     tables = utils.extract_markdown_tables_with_headings(html_content)
#     print(json.dumps(tables, indent=2))

    # print("the type is:", type(filtered_html_content))
    # # # filtered_html_content = html_content. the type is <class 'str'> which is not a beautifulsoup object and so this needs to be paresed or passed to the beautifulsoup library.
    # # with open("my_output_file.txt", "w") as outfile:
    # #     print("Starting the script...", file=outfile)
    # #     print(f"The result is: {filtered_html_content}", file=outfile)
    # #     print("Script execution complete.", file=outfile)

    # # print(html_content) #contents are comming up correctly
    # # Step 3: Extract different blocks
    # h2_paragraphs = utils.extract_h2_with_paragraphs(filtered_html_content, url)
    # # with open("my_output_file.txt", "w") as outfile:
    # #     print("Starting the script...", file=outfile)
    # #     print(f"The result is: \n{h2_paragraphs}", file=outfile)
    # #     print("\nScript execution complete.", file=outfile)

    # # h3_h4_blocks = utils.extract_h3_h4_with_paragraphs(filtered_html_content)
    # tables = utils.extract_markdown_tables_with_headings(filtered_html_content)
    # # li_blocks = utils.li_to_custom_paragraph(filtered_html_content)

    # # Step 4: Combine all blocks
    # notebook_data = [{
    #     "name": notebook_title,
    #     "paragraphs": h2_paragraphs + tables
    # }]

    # return notebook_data
