import json
import os

# Read the notebook
with open('main.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Function to update a cell's source
def update_cell_source(cell):
    if cell['cell_type'] != 'code':
        return cell
    
    new_source = []
    for line in cell['source']:
        # Replace the pip installation line
        if line.strip() == '!pip -q install openai json-repair':
            new_source.append('from platform_utils import install_packages\n')
            new_source.append("install_packages(['openai', 'json-repair'])\n")
        # Replace the project_path setting
        elif line.strip().startswith('project_path = ') and ("'/content/aimetodolog'" in line or "'/home/avm/prog/AIMetodolog'" in line):
            new_source.append('from platform_utils import get_project_root\n')
            new_source.append('project_path = get_project_root()\n')
        # Keep other lines unchanged
        else:
            new_source.append(line)
    
    cell['source'] = new_source
    return cell

# Update all cells
nb['cells'] = [update_cell_source(cell) for cell in nb['cells']]

# Write back the notebook
with open('main.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("Notebook updated successfully!")
