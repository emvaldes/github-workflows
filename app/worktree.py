#!/usr/bin/env python

import os
import sys
import subprocess

import git

from pprint import pprint
import argparse

""" Discarding Protected Branches """
discard = [ 'HEAD', 'master', 'main' ]

def user_input() -> object:
    """
    Objective:
        Processing User-Input parameters
    Parameters:
        None
    Returns:
        args (object): User-Input parameters
    """
    parser = argparse.ArgumentParser( description='Processing User-Input parameters' )
    parser.add_argument(
        '--git-repo',
        '-r',
        dest='git_repo',
        type=str,
        default=os.getcwd(),
        help='Path to Git Repository'
    )
    parser.add_argument(
        '--create',
        '-c',
        const=True,
        default=False,
        dest='create',
        nargs='?',
        help='Create Git Worktree'
    )
    parser.add_argument(
        '--destroy',
        '-d',
        const=True,
        default=False,
        dest='destroy',
        nargs='?',
        help='Destroy Git Worktree'
    )
    # args = parser.parse_args()
    """ Displaying Help """
    if len(sys.argv) == 1:
        display_help( parser )
    else:
        return parser

def manage_worktree():
    """ Processing user-input parameters """
    parser = user_input()
    args = parser.parse_args()
    """ List of patterns to be ignored """
    ignore = [ '.', './', '.\\' ]
    """ Filtering relative-path parameter """
    if args.git_repo in ignore:
        """ Using current working directory """
        args.git_repo = os.getcwd()
        print()
        display_warning( f"Using working directory" )
        display_message( message = f"         { args.git_repo }" )
    """ Required parameters are missing (create, destroy) """
    if len(sys.argv) == 1:
        display_help( parser )
    try:
        if is_git_repo( args.git_repo ):
            """ If Git Repository exists """
            if os.path.exists( args.git_repo ):
                """ Fetching remote branches """
                print(subprocess.run(
                    ['git', 'fetch', '-v', '--', 'origin'],
                    capture_output=True, text=True).stdout
                )
                repo = git.Repo( args.git_repo )
                remote_refs = repo.remote().refs
                for refs in remote_refs:
                    """ Filtering specific reference-patterns (discard: list) """
                    branch = extract_value( refs, discard, 1 )
                    match branch:
                        case value if value != False:
                            if args.create:
                                """ Creating Worktree """
                                worktrees = os.path.join( args.git_repo, ".worktrees", branch )
                                display_section()
                                display_message( message = f"  Branch: '{ branch }'" )
                                message = str( refs.commit.message).strip()
                                """ Createing a Git Worktree (fetched branches) """
                                create_worktree( repo, message, worktrees, branch )
                                """ Changing working directory to Git Repository """
                                os.chdir( args.git_repo )
                            if args.destroy:
                                """ Destroying Worktree """
                                destroy_worktree( branch )
                        case _: pass
                display_section()
                """ Displaying Worktree List """
                print( repo.git.worktree( "list" ), end='\n' )
                print()
            return True
        return True
    except git.exc.InvalidGitRepositoryError:
        display_warning( f"Invalid Git Repository: '{ args.git_repo }'" )
        return False

def display_help( parser ):
    """
    Objective:
        Displaying Help
    Parameters:
        None
    Returns:
        True (bool)
    """
    parser.print_help()
    print()
    sys.exit()
    return True

def display_section( character = '-', length = 100 ):
    """
    Objective:
        Display sequence of character times length
    Parameters:
        string (str): Divisor character
        length (int): Length of divisor
    Returns:
        True (bool)
    """
    print(); print( character * length )
    return True

def display_message( heading = False, message = '' ):
    """
    Objective:
        Display custom (heading: message)
    Parameters:
        heading (str): Message heading (default: False)
        message (str): Message body/content
    Returns:
        True (bool)
    """
    if heading == False:
        heading = f"Message: "
    print( f"{ heading }{ message }" )
    return True

def display_warning( message ):
    """
    Objective:
        Display warning message
    Parameters:
        message (str): Message body/content
    Returns:
        True (bool)
    """
    display_message( heading = "Warning: ", message = message )
    return True

def extract_value( text, discard, index, pattern='/' ):
    """
    Objective:
        Splits key/pair set and return its value
    Parameters:
        text (str): Key/Pair set
        discard (list): List of values to be discarded
        pattern (str): Pattern to be used to split key/pair set
        index (int): Index of value to be extracted
    Returns:
        value (str): Extracted value
    """
    value = str( text ).split( pattern )[index]
    if str( value ) not in discard:
            # display_message( message = f"Extracted: {value}")
            return value
    else:   return False

def is_git_repo( path ):
    """
    Objective:
        Validates if path is a git repository
    Reference:
        https://stackoverflow.com/questions/19687394/
        python-script-to-determine-if-a-directory-is-a-git-repository
    Parameters:
        path (str): Path to Git Repository
    Returns:    
        True/False (bool)
    """
    try:
        _ = git.Repo( path ).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

def inspect_worktree( repo, path ):
    """
    Objective:
        Inspecting Worktree
    Parameters:
        repo (object): Git Repository
        path (str): Path to Git Repository
    Returns:
        True/False (bool)
    """
    if os.path.exists( path ):
        os.chdir( path )
        print( repo.git.status() )
        return True
    else:
        display_warning( f"Worktree '{ path }' does not exist!" )
        return False

def create_worktree( repo, message, path, branch ):
    """
    Objective:
        Creating Git Worktree
    Parameters:
        repo (object): Git Repository
        message (str): Commit Message
        path (str): Path to Git Repository
        branch (str): Git Branch
    Returns:
        True/False (bool)
    """
    if not os.path.exists( path ):
        display_message( message = f"Worktree: '{ path }'" )
        display_message( message = f" Message: '{ message }'\n" )
        print( subprocess.run(
            [ 'git', 'worktree', 'add', path, branch ],
            capture_output=True, text=True ).stdout
        )
    else:
        display_warning( f"Worktree: '{ path }' already exist!" )
        inspect_worktree( repo, path )
    return True

""" Destroying Worktree """
def destroy_worktree( branch ):
    """
    Objective:
        Destroying Git Worktree
    Parameters:
        branch (str): Git Branch
    Returns:
        True/False (bool)
    """
    print( subprocess.run(
        [ 'git', 'worktree', 'remove', branch ],
        capture_output=True, text=True ).stdout
    )
    return True
