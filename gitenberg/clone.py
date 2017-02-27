""" Implements functionality for cloning a gitenberg repo book from GITenberg """
import logging
import os

import sh

from .library import GitbergLibraryManager
from .parameters import GITHUB_ORG
from .util.catalog import get_repo_name

clone_url_ssh_template = u"git@github.com:{org_name}/{repo_name}.git"

def clone(book_repo_name, library_path=None):
    book_repo_name = get_repo_name(book_repo_name)
    logging.info("running clone for{}".format(book_repo_name))
    vat = CloneVat(book_repo_name)

    success, message = vat.clone()
    logging.info(message)


class CloneVat(object):
    """ An object for cloning GITenberg repos
    :takes: `book_repo_name` --  eg. `'Frankenstein_84`

    """
    def __init__(self, book_repo_name):
        self.book_repo_name = book_repo_name

        # create a local instance of the library manager with the provided
        # config if available
        self.l_manager = GitbergLibraryManager()

    def library_book_dir(self):
        return os.path.join(self.l_manager.library_base_path, self.book_repo_name)

    def path_exists(self):
        if os.path.exists(self.library_book_dir()):
            return True
        else:
            return False
    
    def get_clone_url_ssh(self):
        return clone_url_ssh_template.format(org_name=GITHUB_ORG, repo_name=self.book_repo_name)

    def clone(self):
        """ clones a book from GITenberg's repo into the library
        assumes you are authenticated to git clone from repo?
        returns True/False, message
        """
        # FIXME: check if this works from a server install
        logging.debug("Attempting to clone {0}".format(self.book_repo_name))

        if self.path_exists():
            return False, "Error: Local clone of {0} already exists".format(self.book_repo_name)

        try:
            sh.git('clone', self.get_clone_url_ssh(), self.library_book_dir())
            return True, "Success! Cloned {0}".format(self.book_repo_name)
        except sh.ErrorReturnCode_1 as e:
            print e
            logging.debug("clone ran into an issue, likely bad library path")
            logging.debug(e.stderr)
            return False, "Error sh.py returned with a fail code"
        except sh.ErrorReturnCode_128:
            logging.debug("clone ran into an issue, likely this already exists")
            return False, "Error sh.py returned with a fail code"
