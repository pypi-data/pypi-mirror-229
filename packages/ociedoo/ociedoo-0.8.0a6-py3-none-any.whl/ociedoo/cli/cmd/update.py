# SPDX-FileCopyrightText: 2023 Coop IT Easy SC <https://coopiteasy.be>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command: update"""

import subprocess
from pathlib import Path

import click

from ociedoo import complete, lib
from ociedoo.cli import tool


def get_click_odoo_update_job(db, profile, logdir, update_all):
    """Return a dict structure for a job that can be run by
    tool.run_jobs function.
    """
    args = [
        "--database",
        db,
        "--logfile",
        lib.get_update_logfile(logdir, db),
    ]
    if update_all:
        args.append("--update-all")
    return {
        "name": db,
        "fun": lib.run_click_odoo,
        "kwargs": {
            "profile": profile,
            "command": "update",
            "args": args,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
        },
    }


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
    ),
    short_help="Update databases using click-odoo-update.",
)
@click.option(
    "databases",
    "--dbname",
    "-d",
    autocompletion=complete.databases_complete_list,
    metavar="DBNAMES",
    default="all",
    show_default=True,
    help="names of the databases to update.",
)
@click.option("--update-all", is_flag=True, help="Force a full update.")
@tool.restart_mode_options
@click.pass_context
def update(ctx, databases, update_all, restart_mode, yes):
    """
    Update databases using click-odoo-update.

    click-odoo-update ensures that only modules that have changed are updated
    (using checksums computed from the files). To force a real update of all
    modules (and still update the checksums), use the --update-all option.

    Several databases are updated simultaneously.

    DBNAMES should a comma-separated list of database names (without spaces)
    or be equal to "all" to update all databases (which is the default). "all"
    refers to all the databases that belong to the user defined in the
    "database-user" field in the configuration file. Only databases that
    belong to this user can be used, others will be ignored.
    """
    profile = ctx.obj["profile"]
    db_user = profile.get("database-user")
    logdir = Path(profile.get("odoo-log-dir")).expanduser()
    dbs = tool.filter_databases(db_user, databases)
    jobs = [
        get_click_odoo_update_job(db, profile, logdir, update_all)
        for db in dbs
    ]
    tool.run_update_jobs(ctx, jobs, restart_mode, yes)
