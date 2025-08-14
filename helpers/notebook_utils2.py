#This is the execution file. Don't add any function here.

#Import the function file
import helpers.notebook_utils1 as utils1
import helpers.html_cleaner as cleaner
import helpers.network_utils as network



def build_custom_dsnb_notebook(url):
    html_content = network.fetch_html(url)
    # One-pass sequential parsing
    all_paragraphs = parse_html_in_order(html_content, url)

    notebook_data = [{
        "name": "notebook_title",
        "description" : None,
        "tags" : None,
        "version" : "7",
        "layout" : "zeppelin",
        "type" : "low",
        "snapshot" : False,
        "isEditable" : True,
        "isRunnable" : True,
        "template" : "dsrgmn3y",
        "templateConfig" : "{\"visualization\":{\"filters\":[{\"_id\":1583324064459,\"type\":\"styling\",\"enabled\":true,\"conditions\":{\"operator\":\"and\",\"conditions\":[{\"property\":\"hiddenConnection\",\"operator\":\"*\",\"value\":\"\"}]},\"component\":\"edge\",\"target\":\"edge\",\"properties\":{\"colors\":[\"rgba(0, 0, 0, 0.1)\"],\"style\":[\"dashed\"],\"legendTitle\":[\"Hidden Connection\"]}},{\"_id\":1590499315755,\"type\":\"aggregation\",\"enabled\":true,\"conditions\":{\"operator\":\"and\",\"conditions\":[]},\"component\":\"vertex\",\"target\":\"vertex\",\"properties\":{},\"aggregation\":[{\"source\":\"\",\"type\":\"average\"}]}],\"version\":4}}",
        "paragraphs": all_paragraphs
    }]

    return notebook_data


def parse_html_in_order(html_content, url=None):
    # pass
    from bs4 import BeautifulSoup, Tag
    base_url = "https://docs.oracle.com"

    code_spans_backticked  = cleaner.preserve_code_in_paragraphs(html_content) #Replace codeph with backticks
    uicontrol_bolded = cleaner.replace_uicontrol_bold_spans(code_spans_backticked)
    final_html = cleaner.transform_infobox_notes(uicontrol_bolded) # Transform note and remember so that they can be parsed.

    # with open("my_output_file.txt", "w", encoding="utf-8") as outfile:
    #     print("===================================", file=outfile)
    #     print(f"{final_html}", file=outfile)
    #     print("===================================", file=outfile)



    base_url = "https://docs.oracle.com" #To be appended to the start of the relative links.
    soup1 = cleaner.update_links(final_html, base_url) #Updates all the relative links such as olinks.

    updated_soup, markdown_links = utils1.extract_related_topic_links(soup1) #markdown_links contains all the distinct links with order and href maintained.

    body = updated_soup.body or updated_soup  #type is <class 'bs4.element.Tag'> which means its a parsed bs object.

    h2_element = body.find('h2')
    if h2_element:
        h2_tag = h2_element.text
        # print(h2_tag)
    else:
        print("No <h2> tag found in the body.")
    # h2_tag = body.find('h2')
    # print(h2_tag.text)
    # print(markdown_links)
    # with open("my_output_file.txt", "w") as outfile:
    #     print("===================================", file=outfile)
    #     print(f"{body}", file=outfile)
    #     print("===================================", file=outfile)

    # return []
    # Find the div with class "ind"
    ind_div = body.find('div', class_='ind')

    if ind_div:
        # Create containers
        paragraph_list = []
        remaining_content_div = BeautifulSoup("<div></div>", 'html.parser').div
        pre_sect2_div = BeautifulSoup("<div></div>", 'html.parser').div

        # Split ind_div content into pre-sect2 and sect2 parts
        sect2_found = False
        for child in ind_div.children:
            if isinstance(child, Tag):
                if 'sect2' in child.get('class', []):
                    sect2_found = True
                if not sect2_found:
                    pre_sect2_div.append(child)
                else:
                    remaining_content_div.append(child)
        
        # Process karega pre-sect2 content
        #=====================================
        for child in pre_sect2_div.children:
            if isinstance(child, Tag):
                md = utils1.convert_to_markdown(child,h2_tag, url)
                if md:
                    paragraph_list.extend(md)

        # Process karega sect2 divs
        sect2_divs = remaining_content_div.find_all('div', class_='sect2')
        for sect2_div in sect2_divs:
            paragraphs = utils1.process_section(sect2_div)
            paragraph_list.extend(paragraphs)
        # =======================================================

    else:
        print("Error: Could not find the 'ind' div.")


    # Adding the last paragraph to the notebook.
    # print(markdown_links)
    paragraph_list.append({
            "title": "For more information...",
            "hasTitle": True,
            "hideCode" : True,
            "hideGutter" : True,
            "hideVizConfig" : True,
            "message": ["%md", "", (markdown_links)],
            "selectedVisualization" : "html"
        })

    return paragraph_list
