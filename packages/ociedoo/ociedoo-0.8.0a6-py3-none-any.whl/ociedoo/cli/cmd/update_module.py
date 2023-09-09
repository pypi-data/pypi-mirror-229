# SPDX-FileCopyrightText: 2018 Coop IT Easy SC <https://coopiteasy.be>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command: update-module"""

import subprocess
from pathlib import Path

import click

from ociedoo import complete, lib
from ociedoo.cli import tool


def get_odoo_job(db, profile, logdir, update_options, odoo_args):
    """Return a dict structure of a job that can be run by tool.run_jobs"""
    return {
        "name": db,
        "fun": lib.run_odoo,
        "kwargs": {
            "profile": profile,
            "database": db,
            "logfile": lib.get_update_logfile(logdir, db),
            "other_args": update_options + list(odoo_args),
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        },
    }


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    short_help="Update odoo modules on databases.",
)
@click.argument("modules", autocompletion=complete.modules_complete_list)
@click.argument("odoo_args", nargs=-1, type=click.UNPROCESSED)
@click.option(
    "databases",
    "--dbname",
    "-d",
    autocompletion=complete.databases_complete_list,
    metavar="DBNAMES",
    default=False,
    show_default=(
        "databases where MODULES are installed, or all databases if MODULES "
        'is "all"'
    ),
    help="names of the databases to update.",
)
@tool.restart_mode_options
@click.pass_context
def update_module(ctx, modules, odoo_args, databases, restart_mode, yes):
    """
    Update MODULES on each database where at least one of MODULES are
    installed.

    Odoo is run with some default options in order to update MODULES.

    Several databases are updated simultaneously.

    When running Odoo, the default options are:

        - write log in a new file (one for each database)

        - stop after init

        - multithread mode (workers = 0)

        - No cron threads (max-cron-threads = 0)

    More options can be given to Odoo via ODOO_ARGS.

    MODULES should be a comma-separated list of module names (without spaces)
    or be equal to "all" to update all modules.

    DBNAMES should a comma-separated list of database names (without spaces)
    or be equal to "all" to update all databases. The default is to only
    update the databases where MODULES are installed. "all" refers to all the
    databases that belong to the user defined in the "database-user" field in
    the configuration file. Only databases that belong to this user can be
    used, others will be ignored.

    ODOO_ARGS are standard options that the Odoo binary accepts. For example
    it is useful to supply debug option when something goes wrong.
    """
    profile = ctx.obj["profile"]
    db_user = profile.get("database-user")
    logdir = Path(profile.get("odoo-log-dir")).expanduser()
    update_options = ["-u", modules, "--stop-after-init"]

    version = lib.get_bin_odoo_version(profile)
    if version > 10:
        update_options.append("--no-http")
    else:
        update_options.append("--no-xmlrpc")

    if databases:
        dbs = tool.filter_databases(db_user, databases)
    else:
        alldbs = lib.get_all_db(db_user)
        if modules == "all":
            dbs = alldbs
        else:
            args_modules = {mod.strip() for mod in modules.split(",")}
            dbs = []
            for db in alldbs:
                installed_modules = set(lib.get_installed_modules(db))
                if args_modules & installed_modules:
                    dbs.append(db)
            click.echo(
                "Info: The following databases will be updated: %s"
                % ",".join(dbs)
            )

    jobs = [
        get_odoo_job(db, profile, logdir, update_options, odoo_args)
        for db in dbs
    ]
    tool.run_update_jobs(ctx, jobs, restart_mode, yes)
