import sys
import os

# does slash conversion and other things
def make_neat_path(path):
    neat = os.path.normpath(path)
    return neat

n = make_neat_path

def quote(s):
    if sys.platform == 'win32':
        qchar = '"'
    else:
        qchar = "'"
    return qchar + s + qchar

def make_cmd(path_to_cmd, paramlist):
    paramlist.insert(0, path_to_cmd)
    quoted_parts = [ quote(s) for s in paramlist ]
    cmd = ' '.join(quoted_parts)
    # needed in win xp sp3, dont know if it works in other OSes
    cmd = quote(cmd)
    return cmd

def main():
    # *** adjust paths to your use case ***
    # write paths unix style but aply n() to them, slash conversion will be auto
    # spaces in paths are ok.
    
    protoeditor_path = n('../protoeditor/e2_protoeditor.py')

    params = [
        # gamedef filename
        n('gamedef.py'),
        # path to resources that game provides to editor
        n('data/editor'),
        # level filename
        n('data/levels/level_00.lvl')
        ]

    cmd = make_cmd(protoeditor_path, params)
    print cmd
    os.system(cmd)

if __name__ == '__main__':
    main()
