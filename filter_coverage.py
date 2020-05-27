import sys
import os
from subprocess import Popen, PIPE
HEADER = '\033[95m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'


def filter_rows(line):
    missing_lines = []
    missed_branches = []
    cov_part = line.split("%")[1]
    cov_part = cov_part.strip()
    for t in cov_part.split(", "):
        if not t:
            continue
        if ">" in t:
            l1, l2 = t.split("->")
            l1 = int(l1)
            l2 = int(l2)

            missed_branches.append(l1)
            #print l1, l2
            #missing_lines += range(l1 + 1, l2 + 1)
        elif "-" in t:
            l1, l2 = t.split("-")
            l1 = int(l1)
            l2 = int(l2)
            missing_lines += range(l1, l2+1)
        else:
            missing_lines.append(int(t))
    return missing_lines, missed_branches


def find_tested_file(tfn):
    # Raw strings because of escape sign
    excluded_folders = [r'.\.git', r'.\docs', r'.\build',
                        r'.\installer', r'.\dist']
    exp_file = os.path.basename(tfn)[5:]
    for root, _, files in os.walk("."):
        bail = False
        for folder in excluded_folders:
            if root.startswith(folder):
                bail = True
                break
        if bail:
            continue
                    
        if exp_file in files:
            # Remove .\ in the start
            return os.path.join(root, exp_file)[2:]

    else:
        raise ValueError("Could not find expected file {fn}".format(fn=exp_file))


test_name = sys.argv[1].replace("/", "\\")
if len(sys.argv) > 2:
    file_name = sys.argv[2].replace("/", "\\")
else:
    file_name = find_tested_file(test_name)
    print file_name
if len(sys.argv) > 3:
    start_line = int(sys.argv[3])
else:
    start_line = 0
if len(sys.argv) > 4:
    stop_line = int(sys.argv[4])
else:
    stop_line = 9999999999
process = Popen("coverage run --branch %s" % test_name)
process.wait()
process = Popen("coverage report --show-missing", stdout=PIPE)

for line in process.stdout.read().split("\n"):
    if file_name in line:
        perc = line.split("%")[0][-4:]
        missing_lines, missed_branches = filter_rows(line)
        break

with open(file_name) as f:
    for row, l in enumerate(f, 1):
        if start_line <= row <= stop_line:
            colour = OKGREEN
            prefix = "C "
            if row in missing_lines:
                colour = FAIL
                prefix = "M "
            elif row in missed_branches:
                colour = WARNING
                prefix = "MB"
                
            print colour, row, prefix, l[:-1]
print RESET, BOLD, UNDERLINE, "TOTAL COVERAGE:", perc, "%"
print RESET
