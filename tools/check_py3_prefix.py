from __future__ import division, print_function, unicode_literals

import os

#base = r"C:\cocos_pristine\cocos_trunk_clean\test"
base = "../test"
must_have = "from __future__ import division, print_function, unicode_literals"
non_compliant = []
for shortname in os.listdir(base):
    fname = os.path.join(base, shortname)
    if fname.endswith('.py'):
        with open(fname, "r") as f:
            text = f.read()
            if must_have not in text:
                non_compliant.append(fname)

if non_compliant:
    print("Files which don't have the stock py3 compat line:\n")
    for name in non_compliant:
        print(name)
    print()
else:
    print("All files have the stock py3 compat line.")
