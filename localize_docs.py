import os
import re

def localize_content(content):
    # -ize to -ise (handles prefixes like primary_specialization)
    content = re.sub(r'([a-zA-Z]{3,})ize\b', r'\1ise', content)
    content = re.sub(r'([a-zA-Z]{3,})izes\b', r'\1ises', content)
    content = re.sub(r'([a-zA-Z]{3,})ized\b', r'\1ised', content)
    content = re.sub(r'([a-zA-Z]{3,})izing\b', r'\1ising', content)
    content = re.sub(r'([a-zA-Z]{3,})ization\b', r'\1isation', content)
    content = re.sub(r'([a-zA-Z]{3,})izations\b', r'\1isations', content)
    
    # -yze to -yse
    content = re.sub(r'([a-zA-Z]{3,})yze\b', r'\1yse', content)
    content = re.sub(r'([a-zA-Z]{3,})yzes\b', r'\1yses', content)
    content = re.sub(r'([a-zA-Z]{3,})yzed\b', r'\1ysed', content)
    content = re.sub(r'([a-zA-Z]{3,})yzing\b', r'\1ysing', content)
    
    # other common ones
    replacements = {
        r'\bbehavior\b': 'behaviour',
        r'\bbehaviors\b': 'behaviours',
        r'\bbehavioral\b': 'behavioural',
        r'\bbehaviorally\b': 'behaviourally',
        r'\bBehavior\b': 'Behaviour',
        r'\bBehaviors\b': 'Behaviours',
        r'\bBehavioral\b': 'Behavioural',
        r'\bcolor\b': 'colour',
        r'\bcolors\b': 'colours',
        r'\bmodeling\b': 'modelling',
        r'\bmodeled\b': 'modelled',
        r'\bmodeler\b': 'modeller',
        r'\bcenter\b': 'centre',
        r'\bcentered\b': 'centred',
        r'\bcenters\b': 'centres',
        r'\bdefense\b': 'defence',
        r'\boffense\b': 'offence',
        r'\blicense\b': 'licence',
        r'\bcatalog\b': 'catalogue',
        r'\banalog\b': 'analogue',
        r'\bDefense\b': 'Defence',
        r'\bCenter\b': 'Centre',
        r'\bprogrammatic\b': 'programmatic', # Keep as is
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    return content

def localize_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    new_content = localize_content(content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Localised: {file_path}")

def walk_and_localize(root_dir):
    for root, dirs, files in os.walk(root_dir):
        # We WANT to include .pi and other hidden dirs if they contain documentation?
        # Actually, let's just stick to the main folders.
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith('.md') or file.endswith('.raw'):
                localize_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_localize('.')
