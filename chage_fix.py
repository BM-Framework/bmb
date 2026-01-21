import os

parent_dir = r"C:\Users\hp\OneDrive\Desktop\BM\bmb"
sub_dir    = r"C:\Users\hp\OneDrive\Desktop\BM\bmb\bmb"
oldV = "1.0.2"
newV = "1.0.3"
skip_file = "chage_fix.py"

# Parent folder: version only, skip chage_e.py
for filename in os.listdir(parent_dir):
    if filename == skip_file:
        continue
    filepath = os.path.join(parent_dir, filename)
    if not os.path.isfile(filepath):
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content.replace(oldV, newV)
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Version updated: {filename}")
    except:
        pass

# Sub folder: accents + version
for filename in os.listdir(sub_dir):
    filepath = os.path.join(sub_dir, filename)
    if not os.path.isfile(filepath):
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = (
            content
            .replace('é','e').replace('è','e').replace('ê','e').replace('à','a')
        )
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filename}")
    except:
        pass