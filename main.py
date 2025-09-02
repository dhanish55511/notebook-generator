# Contains the main code

import os
import json
import helpers.notebook_utils1 as utils1
import helpers.notebook_utils2 as utils2
from urllib.parse import urlparse


# ---- EXECUTE ----

# url = "https://abc.com"

#OML4SQL Classification 
# url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/classification2.html"

#OML4SQL Clustering
# Error-Notebook is not being generated
# url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/clustering1.html"

# OML$SQL Regression
url = "https://docs.oracle.com/en/database/oracle/machine-learning/oml4sql/23/mlsql/regression2.html"

# UAT Regression
# url = "https://docs-uat.us.oracle.com/en/database/oracle/machine-learning/oml4sql/21/mlsql/regression.html"


notebook = utils2.build_custom_dsnb_notebook(url)

path_parts = urlparse(url).path.strip("/").split("/")

# Look for product name (oml4sql, oml4py, etc.)
product_names = ["oml4sql", "oml4py", "oml4r"]
product = next((p for p in path_parts if p.lower() in product_names), "unknown")

# Map OML product names to magic commands or equivalents
product_map = {
    "oml4sql": "%sql",
    "oml4py": "%python",
    "oml4r": "%r"
}

product_equivalent = product_map.get(product, "%sql")

# Call utils1 function with only the interpreter
# This call is basically making sure that the notebooks are not dependednt on passing %sql or %r. Its going to decide on itself based on the url.
# utils1.process_ordered_list_items(product_equivalent=product_equivalent)
utils1.set_product_equivalent(product_equivalent)


# Extract topic name (filename without .html)
topic = os.path.splitext(path_parts[-1])[0]

# Create file name
file_name = f"{product}_{topic}.dsnb"

# Output path
output_path = os.path.join("output", file_name)

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)


# Save file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print(f"File saved as: {output_path}")

# # Write to file
# with open("output/my_notebook.dsnb", "w", encoding="utf-8") as f:
#     json.dump(notebook, f, indent=2)