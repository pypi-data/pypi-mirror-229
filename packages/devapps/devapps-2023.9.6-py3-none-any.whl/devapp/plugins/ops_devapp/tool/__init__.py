#!/usr/bin/env python
"""
# Tool Installation
"""
# TODO: set up ssh -R to tinyproxy for airight deploys in ssh mode
import devapp.gevent_patched
from .tools import run_app, do, FLG, load_spec, app, g, waitfor, spawn, time, workdir, os
from .tools import write_file, read_file, out_table, api, have_all, partial, system
from .tools import exists, dir_of, now, json, organize_bzip2, no_node
from .tools import prep_make_workdir_and_abspath_flags, tar_any_project_files
from .tools import single_node_cmds
from shutil import copyfile
from devapp.tools import abspath
import rich


class tool:
    sudo = False


class asdf(tool):
    pass


class binenv(tool):
    pass


class conda(tool):
    pass


class brew(tool):
    sudo = True


class nix(tool):
    sudo = True


class Flags:
    autoshort = ''

    class Actions:
        class status:
            d = True

        # class login:
        #     d = False
        #
        #     class count:
        #         n = 'If > 1 we will login into different tmux windows, not panes'
        #         d = 1
        #


tools = [binenv, asdf, conda, brew, nix]


class Actions:
    def status():
        return 'foo'


def run():
    if FLG.status:
        return Actions.status()

    if FLG.deploy:
        return deploy()


main = lambda: run_app(run, flags=Flags)


if __name__ == '__main__':
    main()
