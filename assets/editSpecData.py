import os
import sys

def find_datas(source_folder, base_path=''):
    datas = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, base_path)
            datas.append((relative_path, os.path.dirname(relative_path)))
    return datas

def modify_spec_file(spec_file_path, datas):
    with open(spec_file_path, 'r') as file:
        lines = file.readlines()
    
    datas_line_index = -1
    for i, line in enumerate(lines):
        if 'datas=[' in line:
            datas_line_index = i
            break
    
    if datas_line_index >= 0:
        # Remove the existing 'datas' line
        del lines[datas_line_index]
        # Insert the new 'datas' content
        datas_lines = ['        (' + repr(src) + ', ' + repr(dest) + '),\n' for src, dest in datas]
        lines.insert(datas_line_index, '    datas=[\n' + ''.join(datas_lines) + '    ],\n')
    
    with open(spec_file_path, 'w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['windows', 'linux']:
        print("It's mandatory to specify 'windows' or 'linux' as a parameter.")
        sys.exit(1)

    platform = sys.argv[1]
    spec_file_name = f'app_{platform}.spec'

    PATH = ""  # "../"
    spec_file_path = os.path.join(PATH, spec_file_name)
    base_path = os.path.abspath(PATH)
    source_folder = os.path.join(base_path, 'Bird Vocalization Samples')

    datas = find_datas(source_folder, base_path)
    modify_spec_file(spec_file_path, datas)