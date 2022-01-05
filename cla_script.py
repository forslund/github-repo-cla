# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from github import Github
import requests
import os
import sys
import re
import argparse
from datetime import date

CLA_TEXT = """
Hello, @{}, thank you for helping with the Mycroft project! We welcome everyone
into the community and greatly appreciate your help as we work to build an AI
for Everyone.

To protect yourself, the project, and users of Mycroft technologies we require
a Contributor Licensing Agreement (CLA) before accepting any code
contribution. This agreement makes it crystal clear that along with your
code you are offering a license to use it within the confines of this project.
You retain ownership of the code, this is just a license.

Please visit https://mycroft.ai/cla to initiate this one-time signing. Thank
you!
"""


def get_contributors():
    """ Finds contributors in the contributors repository's README.md. """
    contributors = requests.get('https://raw.githubusercontent.com/'
                                'MycroftAI/contributors/master/'
                                'README.md').text
    # Everything after the --- break line
    contributors = contributors.split('---\n')[1]
    contributors = contributors.split('\n')
    return [re.sub(r'(^.*\(|\))', '', c.strip()) for c in contributors]


def main(repo, branch, dry_run=False):
    if dry_run:
        print("Doing a dry-run...\nNo changes will be applied to the repo")

    extra_contributors = ['JarbasAl']

    contributors = get_contributors() + extra_contributors
    gh = Github(os.environ['GITHUB_ACCESS_TOKEN'])
    repo = gh.get_repo(repo)

    cla_yes = [label for label in repo.get_labels()
               if label.name == 'CLA: Yes'][0]
    cla_needed = [label for label in repo.get_labels()
                  if label.name == 'CLA: Needed'][0]

    for pr in repo.get_pulls(base=branch):
        if pr.created_at.date() < date(2019, 6, 6):
            continue
        print(u'\n\nChecking {} by {}:'.format(pr.title, pr.user.login))
        if pr.user.login in contributors:
            print(u'\t{} has signed the CLA'.format(pr.user.login))

            labels = list(pr.get_labels())
            if cla_yes not in labels and cla_needed not in labels:
                print('\t"CLA Yes" needs to be added')
                if not dry_run:
                    labels.append(cla_yes)
                    pr.set_labels(*labels)
            elif cla_yes not in labels and cla_needed in labels:
                print('"\tCLA Needed" must be removed')
                if not dry_run:
                    labels.remove(cla_needed)
                    labels.append(cla_yes)
                    pr.set_labels(*labels)

        else:  # No CLA Signed
            print(u'\t{} has not signed the CLA'.format(pr.user.login))

            labels = list(pr.get_labels())
            if cla_needed not in labels:
                print('\tAdding "CLA Needed" Label')
                if not dry_run:
                    labels.append(cla_needed)
                    pr.set_labels(*labels)

                print('\tAdding Comment with CLA Instructions')
                if not dry_run:
                    issue = repo.get_issue(pr.number)
                    issue.create_comment(CLA_TEXT.format(pr.user.login))
            else:
                print('\tAll is well nothing needs to be done.')

    print('\n\nAll PR\'s have been reviewed\n\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Only analyze, don\'t modify the PR\'s')
    parser.add_argument('-b', '--branch', default='master',
                        help='Only analyze, don\'t modify the PR\'s')
    parser.add_argument('repo', help='Github Repo, Example: '
                                     'MycroftAI/mycroft-core')
    args = parser.parse_args(sys.argv[1:])
    main(args.repo, branch=args.branch, dry_run=args.dry_run)
