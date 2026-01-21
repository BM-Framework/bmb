import os

directory = r"C:\Users\hp\OneDrive\Desktop\BM\bmb\bmb"

for filename in os.listdir(directory):
    filepath = os.path.join(directory, filename)
    if not os.path.isfile(filepath):
        continue
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = content.replace('é','e').replace('è','e').replace('ê','e')
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Modified: {filename}")
    except:
        pass