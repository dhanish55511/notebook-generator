from bs4 import BeautifulSoup
import requests
import os

def extract_sect2_content_from_url_with_ind_context(url, output_dir="output"):
    """
    Fetches HTML content from a URL, parses it, and saves content from
    <div> tags that are descendants of a <div class="ind"> tag AND
    are associated with an <h2> tag having class "sect2".

    The association is assumed to be that the <h2> tag with class "sect2"
    precedes the target <div> tag within the <div class="ind">.

    Args:
        url (str): The URL of the HTML page to fetch and parse.
        output_dir (str, optional): The directory to save the output files. Defaults to "output".
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Find the main <div class="ind">
        ind_div = soup.find('div', class_='ind')
        if ind_div:
            sect2_h2_elements = ind_div.find_all('h2', class_='sect2')
            for i, h2_tag in enumerate(sect2_h2_elements):
                # Find the next sibling that is a <div>
                next_div = h2_tag.find_next_sibling('div')
                if next_div:
                    filename = f"sect2_from_ind_content_{i+1}.html"
                    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
                        f.write(str(next_div))
                    print(f"Found and saved a <div> descendant of <div class='ind'> following <h2 class='sect2'> tag {i+1} to '{os.path.join(output_dir, filename)}' from '{url}'")
                else:
                    print(f"No immediately following <div> found after <h2 class='sect2'> tag {i+1} within <div class='ind'> from '{url}'.")
        else:
            print(f"No <div class='ind'> tag found in the HTML content from '{url}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL '{url}': {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Example usage: Replace with a valid URL
    # target_url = "https://example.com"  # Replace with a URL containing the target structure
    target_url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"
    extract_sect2_content_from_url_with_ind_context(target_url, output_dir="extracted_sect2_in_ind")
    print("\nFiles saved in the 'extracted_sect2_in_ind' directory.")

# from bs4 import BeautifulSoup
# import requests
# import os

# def extract_sect2_content_from_url(url, output_dir="output"):
#     """
#     Fetches HTML content from a URL, parses it, and saves content from
#     elements with class "sect2" (found within either <h2> or <div> tags)
#     into separate files.

#     Args:
#         url (str): The URL of the HTML page to fetch and parse.
#         output_dir (str, optional): The directory to save the output files. Defaults to "output".
#     """
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for bad status codes
#         html_content = response.text
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Create the output directory if it doesn't exist
#         os.makedirs(output_dir, exist_ok=True)

#         # Find all elements with class "sect2" inside <h2> tags
#         sect2_h2_elements = soup.find_all('h2', class_='sect2')
#         for i, element in enumerate(sect2_h2_elements):
#             filename = f"sect2_h2_content_{i+1}.html"
#             with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
#                 f.write(str(element))
#             print(f"Found and saved <h2 class='sect2'> tag {i+1} to '{os.path.join(output_dir, filename)}' from '{url}'")

#         # Find all elements with class "sect2" inside <div> tags
#         sect2_div_elements = soup.find_all('div', class_='sect2')
#         for i, element in enumerate(sect2_div_elements):
#             filename = f"sect2_div_content_{i+1}.html"
#             with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
#                 f.write(str(element))
#             print(f"Found and saved <div class='sect2'> tag {i+1} to '{os.path.join(output_dir, filename)}' from '{url}'")

#         if not sect2_h2_elements and not sect2_div_elements:
#             print(f"No elements with class 'sect2' found inside either <h2> or <div> tags in the HTML content from '{url}'.")

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching URL '{url}': {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == '__main__':
#     # Example usage: Replace with a valid URL
#     # target_url = "https://example.com"  # Replace with a URL containing the target tags
#     target_url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"
#     extract_sect2_content_from_url(target_url, output_dir="extracted_sect2_content")
#     print("\nFiles saved in the 'extracted_sect2_content' directory.")




# from bs4 import BeautifulSoup
# import requests
# import os

# def parse_and_split_html_from_url(url, output_dir="output"):
#     """
#     Fetches HTML content from a URL, parses it, and saves specific div tags
#     to separate files.

#     Args:
#         url (str): The URL of the HTML page to fetch and parse.
#         output_dir (str, optional): The directory to save the output files. Defaults to "output".
#     """
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for bad status codes

#         html_content = response.text
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Create the output directory if it doesn't exist
#         os.makedirs(output_dir, exist_ok=True)

#         # Find the single div with class "ind"
#         ind_div = soup.find('div', class_='ind')
#         if ind_div:
#             with open(os.path.join(output_dir, "ind_content.html"), "w", encoding="utf-8") as f:
#                 f.write(str(ind_div))
#             print(f"Found and saved the <div class='ind'> tag to '{os.path.join(output_dir, 'ind_content.html')}' from '{url}'")
#         else:
#             print(f"No <div class='ind'> tag found in the HTML content from '{url}'.")

#         # Find all divs with class "sect2"
#         sect2_divs = soup.find_all('div', class_='sect2')
#         if sect2_divs:
#             for i, div in enumerate(sect2_divs):
#                 filename = f"sect2_content_{i+1}.html"
#                 with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
#                     f.write(str(div))
#                 print(f"Found and saved <div class='sect2'> tag {i+1} to '{os.path.join(output_dir, filename)}' from '{url}'")
#         else:
#             print(f"No <div class='sect2'> tags found in the HTML content from '{url}'.")

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching URL '{url}': {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# if __name__ == '__main__':
#     # Example usage: Replace with a valid URL
#     # target_url = "https://example.com"  # Replace with a URL containing the target div tags
#     target_url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"
#     parse_and_split_html_from_url(target_url, output_dir="extracted_from_url")
#     print("\nFiles saved in the 'extracted_from_url' directory.")