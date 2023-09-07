# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['broad_babel']

package_data = \
{'': ['*'], 'broad_babel': ['data/*']}

setup_kwargs = {
    'name': 'broad-babel',
    'version': '0.1.1',
    'description': 'A translator of Broad and JUMP ids to more conventional names.',
    'long_description': '# Proposal for broad-babel Module\n\nIt aims to translate identifiers from the Broad Institute or JUMP consortium into more standardised versions. In the case of genes NCBI gene names and in the case of chemical compounds InChiKey. From there the user can get more biological context and explore different translations.\n\nMaking this a python modules facilitates its integration into existing workflows and facilitates updating the (small) database. The python code contains exclusively the querying logic, and the csv files have been trimmed as much as possible to focus on the important data.\n\n## Input and output design\n### Inputs\n- One or multiple (str) identifiers of a type (either the JUMP or Broad ID).\n- A (str) specifying the type of identifier to query.\n\n### Outputs\n- A dictionary where key-value pairs are input_id -> output id.\n\n## Data sources\n- JUMP perturbation lists: https://github.com/jump-cellpainting/jump-perturbation-lists/tree/main\n- JUMP CP Metadata: https://github.com/jump-cellpainting/datasets/tree/main/metadata\n- JUMP-target metadata: https://github.com/jump-cellpainting/JUMP-Target/blob/master/JUMP-Target-1_compound_metadata.tsv\n\n## Considerations\n### Advantages\n- Broad-babel would make plotting data with "well-known" gene names seamless. Just translate your broad ids and plot away. It also provides access to the CSV compendium with all the name-based metadata of the JUMP data collective.\n- It would also make it easier for other biologists or data scientists to approach the JUMP dataset, as Broad/JUMP ids mean nothing to them. \n\n### Limitations\n- Data and metadata may be currently incomplete, but it would be useful to find the holes in JUMP metadata. This would make it easier to be aware of what is missing, as current data\n- Querying in python is probably inefficient, but as long as the size of the dataset is small this should not be prohibitive.\n',
    'author': 'Alan Munoz',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
