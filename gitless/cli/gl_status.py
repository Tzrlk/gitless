# Gitless - a version control system built on top of Git.
# Licensed under GNU GPL v2.

"""gl status - Show the status of files in the repo."""


from clint.textui import colored

from gitless.core import core
from gitless.core import file as file_lib

from . import pprint


def parser(subparsers):
  """Adds the status parser to the given subparsers object."""
  status_parser = subparsers.add_parser(
      'status', help='show status of the repo')
  status_parser.add_argument(
      'paths', nargs='*', help='the specific path(s) to status')
  status_parser.set_defaults(func=main)


def main(args):
  repo = core.Repository()
  curr_b = repo.current_branch
  pprint.msg('On branch {0}, repo-directory {1}'.format(
    colored.green(curr_b.branch_name), colored.green('//' + repo.cwd)))

  if curr_b.merge_in_progress:
    pprint.blank()
    _print_conflict_exp('merge')
  elif curr_b.rebase_in_progress:
    pprint.blank()
    _print_conflict_exp('rebase')

  tracked_mod_list = []
  untracked_list = []
  for f in file_lib.status_all(only_paths=args.paths):
    if f.type == file_lib.TRACKED and f.modified:
      tracked_mod_list.append(f)
    elif f.type == file_lib.UNTRACKED:
      untracked_list.append(f)
  pprint.blank()
  tracked_mod_list.sort(key=lambda f: f.fp)
  _print_tracked_mod_files(tracked_mod_list)
  pprint.blank()
  pprint.blank()
  untracked_list.sort(key=lambda f: f.fp)
  _print_untracked_files(untracked_list)
  return True


def _print_tracked_mod_files(tracked_mod_list):
  pprint.msg('Tracked files with modifications:')
  pprint.exp('these will be automatically considered for commit')
  pprint.exp(
      'use gl untrack <f> if you don\'t want to track changes to file f')
  pprint.exp(
      'if file f was committed before, use gl checkout <f> to discard '
      'local changes')
  pprint.blank()
  if not tracked_mod_list:
    pprint.item('There are no tracked files with modifications to list')
  else:
    for f in tracked_mod_list:
      exp = ''
      color = colored.yellow
      # TODO(sperezde): sometimes files don't appear here if they were resolved.
      if not f.exists_in_lr:
        exp = ' (new file)'
        color = colored.green
      elif not f.exists_in_wd:
        exp = ' (deleted)'
        color = colored.red
      elif f.in_conflict:
        exp = ' (with conflicts)'
        color = colored.cyan
      elif f.resolved:
        exp = ' (conflicts resolved)'
      pprint.item(color(f.fp), opt_text=exp)


def _print_untracked_files(untracked_list):
  pprint.msg('Untracked files:')
  pprint.exp('these won\'t be considered for commit')
  pprint.exp('use gl track <f> if you want to track changes to file f')
  pprint.blank()
  if not untracked_list:
    pprint.item('There are no untracked files to list')
  else:
    for f in untracked_list:
      s = ''
      color = colored.blue
      if f.exists_in_lr:
        color = colored.magenta
        if f.exists_in_wd:
          s = ' (exists in local repo)'
        else:
          s = ' (exists in local repo but not in working directory)'
      pprint.item(color(f.fp), opt_text=s)


def _print_conflict_exp(op):
  pprint.msg(
      'You are in the middle of a {0}; all conflicts must be resolved before '
      'commiting'.format(op))
  pprint.exp(
      'use gl {0} --abort to go back to the state before the {0}'.format(op))
  pprint.exp('use gl resolve <f> to mark file f as resolved')
  pprint.exp('once you solved all conflicts do gl commit to continue')
  pprint.blank()
