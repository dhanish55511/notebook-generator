import sys
import requests
from notebook_utils import parse_html_to_nbcc, save_nbcc

def main():
    # if len(sys.argv) != 2:
    #     print("Usage: python main.py <url>")
    #     return

    # url = sys.argv[1]
    url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    html_content = response.text
    nbcc_data = parse_html_to_nbcc(html_content)
    save_nbcc(nbcc_data, "output.nbcc")
    print("Notebook written to output.nbcc")

if __name__ == "__main__":
    main()
