import re
import subprocess
import argparse

RE_COMMIT_HEADER_COMMIT_INFO = re.compile(
    r"""^Commit:\s*(?P<sha>[0-9A-Fa-f]+)\n\s*Date:\s*(?P<date>.*)\n\s*Tree:\s*(?P<tree>[0-9A-Fa-f]+)\n\s*Parents:\t(?P<parents>.*)?(?:\n\n|$)?(?P<file_stats>(?:^:.+\n)+)?(?P<file_numstats>(?:.+\t.*\t.*\n)+)?(?:\n|\n\n|$)?(?P<patch>(?:diff[ ]--git(?:.+\n)+)+)?(?:\n\n|$)?""",
    re.VERBOSE | re.MULTILINE)
RE_COMMIT_HEADER_COMMIT_INFO_MIN = re.compile(
    r"""^Commit:\s*(?P<sha>[0-9A-Fa-f]+)\n\s*Date:\s*(?P<date>.*)\n\s*Tree:\s*(?P<tree>[0-9A-Fa-f]+)\n?""",
    re.VERBOSE | re.MULTILINE)
COMMAND_COMMIT_COMMIT_INFO = "git show --reverse --first-parent --raw --numstat --abbrev=40 --full-index -p -M --pretty=format:'Commit:\t%H%nDate:\t%ai%nTree:\t%T%nParents:\t%P%n' {}"
COMMAND_COMMIT_COMMIT_INFO_MIN = "git show --reverse --first-parent --abbrev=40 --full-index -s -M --pretty=format:'Commit:\t%H%nDate:\t%ai%nTree:\t%T%nParents:\t%P%n' {}"



def execute(commandLine):
    try:
        process = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out = process.stdout.read().strip().decode("UTF-8", errors='ignore')
        error = process.stderr.read().strip().decode("UTF-8", errors='ignore')

        if error:
            process.kill()
            print("Execution '{}'".format(repr(commandLine)))
            print("with error '{}'".format(error))
            raise Exception(error)
    except Exception as ex:
        print("execute",ex)
        sys.exit(1)
    return out

is_windows = True

sha_parent = "cba203bb67d8f9efd2856caf1f4d31060c9332a3"
#sha_parent = "370560f142481eb3e6250fa2c3024179b4efc670"

commit_cmd = COMMAND_COMMIT_COMMIT_INFO_MIN.format(sha_parent)
if is_windows:
    commit_cmd = commit_cmd.replace('\'', '\"')
    commit_cmd = commit_cmd.replace('\t', '%x09')

print('Commit cmd for commit info : {}'.format(commit_cmd))
output = execute(commit_cmd)
print('Output commit info {}'.format(output))
print("!!!!!!")
try:
    commit_info = RE_COMMIT_HEADER_COMMIT_INFO.findall(output)[0]
    print('Output info regex {}'.format(commit_info))
    commit_numstats = {"additions": 0, "deletions": 0, "changes": 0,
                        "total": 0, "files": 0}
    sha, \
    date, \
    tree, \
    parents, \
    file_stats, \
    file_numstats, \
    patch = commit_info
except:
    commit_info = RE_COMMIT_HEADER_COMMIT_INFO_MIN.findall(output)[0]
    print('Output info regex {}'.format(commit_info))
    commit_numstats = {"additions": 0, "deletions": 0, "changes": 0,
                        "total": 0, "files": 0}
    sha, \
    date, \
    tree = commit_info

print('parents {}'.format(commit_info))





print("#################################################################################")

parser = argparse.ArgumentParser(description='Sync a number of commits before a specific commit')
parser.add_argument('--minimize', dest='minimize', action='store_true')
parser.set_defaults(minimize=False)

args = parser.parse_args()
minimize = args.minimize

print(minimize)



COMMAND_COMMIT = "git show --reverse --first-parent --raw --numstat --abbrev=40 --full-index -p -M --pretty=format:'Commit:\t%H%nDate:\t%ai%nTree:\t%T%nParents:\t%P%nAuthor:\t%an\t%ae\t%ai%nCommitter:\t%cn\t%ce\t%ci%nMessage:\t%s%n' {}"

RE_COMMIT_HEADER = re.compile(
    r"""^Commit:\t(?P<sha>[0-9A-Fa-f]+)\nDate:\t(?P<date>.*)\nTree:\t(?P<tree>[0-9A-Fa-f]+)\nParents:\t(?P<parents>.*)\nAuthor:\t(?P<author>.*)\nCommitter:\t(?P<committer>.*)\nMessage:\t(?P<message>.*)?(?:\n\n|$)?(?P<file_stats>(?:^:.+\n)+)?(?P<file_numstats>(?:.+\t.*\t.*\n)+)?(?:\n|\n\n|$)?(?P<patch>(?:diff[ ]--git(?:.+\n)+)+)?(?:\n\n|$)?""",
    re.VERBOSE | re.MULTILINE)
output = "Commit:    39893b96f2266881f28c51e33b64009774fafb2d\n Date:    2023-04-10 16:51:21 +0000\n Tree:    e42ea2ed893e8142c6dde955fcc582f082a6c014\n Parents:    a3dec2a341252993040578cd6f47c038164772ce 66ced5e022152a8a88518a95a0841313028cd5e2\n Author:    Evan Knox    eknox@kinaxis.com    2023-04-10 16:51:21 +0000\n Committer:    Evan Knox    eknox@kinaxis.com    truenMessage:    Pull request #48514: Part 1 - Refactor the EditRangeDialog\n :100644 100644 8ceb931d8c05b8a516b45db008a36e34563c19f8 5f84113ec9bbac11c92fcf1f2d0da773deb9adaa M    RapidResponse/Web\n Server/Web/app/packages/worksheet-react/src/ag-grid/components/EditRangeDialog.tsx\n :000000 100644 0000000000000000000000000000000000000000 f3a2fbd2460f6a30982ebbf8b8026ea3439f49df A    RapidResponse/Web\n Server/Web/app/packages/worksheet-react/src/ag-grid/components/test/EditRangeDialog.jest.tsx\n" 



def execute(commandLine):
    try:
        process = subprocess.Popen(commandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out = process.stdout.read().strip().decode("UTF-8", errors='ignore')
        error = process.stderr.read().strip().decode("UTF-8", errors='ignore')

        if error:
            process.kill()
            raise Exception(error)
    except Exception as ex:
        print(ex)
    return out


sha = "72c4da75d7c71115d4770a6552098456ca20263b"
commit_cmd = COMMAND_COMMIT.format(sha)
commit_cmd = commit_cmd.replace('\'', '\"')
commit_cmd = commit_cmd.replace('\t', '%x09')
print('Commit command {}'.format(commit_cmd))
#output = execute(commit_cmd)


commit_header = RE_COMMIT_HEADER.findall(output)[0]
print(commit_header)
print("#####################################")
print("#####################################")
#print(output)