# SPDX-FileCopyrightText: 2018 Coop IT Easy SC <https://coopiteasy.be>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tool function for click commands"""

import os
import signal
import time
from contextlib import contextmanager

import click

from ociedoo import lib
from ociedoo.exceptions import ConfigError


def cb_print_cmd(cmd, success, exit_code):
    """Print the command that has been run on stdout"""
    click.echo("Running: %s" % cmd.ran)


def get_filestore_path(ctx, database):
    """
    Return the filestore path of the provided database as a pathlib.Path
    object
    """
    # the filestore directory is stored in odoo's "data_dir", which is
    # configurable (--data-dir command-line option and data_dir property in
    # the configuration file) and whose default value depends on multiple
    # factors (user's home directory or platform) (see
    # odoo.tools.config._get_default_datadir()). since we don't use odoo's
    # code in here, and will not reimplement the function, we will assume the
    # most common default value, while making it overridable in the
    # configuration file.
    profile = ctx.obj["profile"]
    data_dir = profile.get("data-dir")
    return lib.get_filestore_path(database, data_dir)


def _all_proc_done(jobs):
    """Return True if all processes are done."""
    all_proc_done = True
    for job in jobs:
        if job["proc"] is None or job["proc"].poll() is None:
            all_proc_done = False
            break
    return all_proc_done


def _all_proc_success(jobs):
    """Return True if all processes are done and success."""
    all_proc_success = True
    for job in jobs:
        if (
            job["proc"] is None
            or job["proc"].poll() is None
            or job["proc"].poll()
        ):
            all_proc_success = False
            break
    return all_proc_success


def _prune_failed_proc(jobs):
    """Delete failed processes as they where not executed."""
    for job in jobs:
        if job["proc"].returncode:
            job["proc"] = None


def _count_running_proc(jobs):
    """Return the number of running processes."""
    nb_running_proc = 0
    for job in jobs:
        if job["proc"] is not None and job["proc"].poll() is None:
            nb_running_proc += 1
    return nb_running_proc


def _proc_status(jobs):
    """Return a list of string representation of proc status."""
    status = []
    for job in jobs:
        state = " "
        if job["proc"] is not None:
            if job["proc"].poll() is None:
                state = "."
            elif job["proc"].poll():
                state = "x"
            else:
                state = "v"
        status.append("[{}] {}".format(state, job["name"]))
    return status


def run_jobs(ctx, jobs, auto_retry):
    """
    Run jobs in parallel.

    jobs must be a list of dicts with name, fun and kwargs keys. name is the
    name of the job, fun is the function that with be launched with kwargs.
    fun should return a subprocess.Popen instance.

    Returns the list of failed jobs.
    """
    jobs = [{**job, "proc": None} for job in jobs]
    max_proc = os.cpu_count() if os.cpu_count() else 1
    try:
        while not _all_proc_success(jobs):
            if _count_running_proc(jobs) < max_proc:
                all_proc_done = _all_proc_done(jobs)
                if (
                    all_proc_done
                    and auto_retry
                    or click.confirm(
                        "There are failed jobs. Do you want to try again?"
                    )
                ):
                    click.echo()
                    _prune_failed_proc(jobs)
                elif all_proc_done:
                    break
                # Launch next job
                next_job = next(
                    (job for job in jobs if job["proc"] is None), None
                )
                if next_job:
                    try:
                        next_job["proc"] = next_job["fun"](
                            **next_job["kwargs"]
                        )
                    except ConfigError as ce:
                        ctx.fail("Configuration error: {0}".format(ce))
            # Show status on stdout
            click.echo("\r" + ", ".join(_proc_status(jobs)), nl=False)
            time.sleep(0.1)
        click.echo("\r" + ", ".join(_proc_status(jobs)), nl=False)
    except KeyboardInterrupt:
        click.echo()
        click.echo("CTRL-C: program will terminate properly.", err=True)
        try:
            for job in jobs:
                if job["proc"] is not None and job["proc"].poll() is None:
                    job["proc"].send_signal(signal.SIGINT)
                    job["proc"].wait()
        except KeyboardInterrupt:
            click.echo("CTRL-C: program will exit now.", err=True)
            for job in jobs:
                if job["proc"] is not None and job["proc"].poll() is None:
                    job["proc"].kill()
            ctx.exit(101)
        ctx.exit(100)
    click.echo()
    return [job for job in jobs if job["proc"].returncode]


def restart_mode_options(func):
    """
    Decorate provided function with the restart_mode options.
    """
    return click.option(
        "restart_mode",
        "--restart-before",
        "--ninja",
        flag_value="restart-before",
        help="Restart Odoo daemon before performing updates.",
    )(
        click.option(
            "restart_mode",
            "--no-restart",
            flag_value="no-restart",
            help="Do not restart Odoo daemon for performing updates.  "
            "[default]",
        )(
            click.option(
                "restart_mode",
                "--stop-before-start-after",
                flag_value="stop-odoo",
                help="Stop Odoo before performing updates and restart it "
                "after.",
            )(
                click.option(
                    "-y",
                    "--yes",
                    is_flag=True,
                    help="Answer yes to questions.",
                )(func)
            )
        )
    )


@contextmanager
def handle_restart(ctx, restart_mode, yes):
    """
    Returns a context manager that will handle the restart of the odoo daemon
    according to the provided options.
    """
    profile = ctx.obj["profile"]
    odoo_daemon_name = profile.get("daemon-name")
    if restart_mode == "restart-before":
        question = (
            "%s will be restarted. Do you want to continue?" % odoo_daemon_name
        )
        if yes or click.confirm(question):
            # Restart odoo daemon
            if lib.is_daemon_running(odoo_daemon_name) and not lib.stop_daemon(
                odoo_daemon_name
            ):
                ctx.fail(
                    "Fail to stop %s daemon. To do so try: sudo "
                    "systemctl stop %s" % (odoo_daemon_name, odoo_daemon_name)
                )
            if not lib.start_daemon(odoo_daemon_name):
                ctx.fail(
                    "Fail to start %s daemon. To do so try: sudo "
                    "systemctl start %s" % (odoo_daemon_name, odoo_daemon_name)
                )
    elif restart_mode == "stop-odoo":
        # Stop odoo daemon
        if lib.is_daemon_running(odoo_daemon_name):
            question = (
                "%s is running. Do you want to stop it?" % odoo_daemon_name
            )
            if yes or click.confirm(question):
                if not lib.stop_daemon(odoo_daemon_name):
                    ctx.fail(
                        "Fail to stop %s daemon. To do so try: sudo "
                        "systemctl stop %s"
                        % (odoo_daemon_name, odoo_daemon_name)
                    )
            else:
                click.echo(
                    "%s is running. Cannot perform updates." % odoo_daemon_name
                )
                ctx.abort()

    yield

    if restart_mode == "stop-odoo":
        # Start odoo daemon
        if not lib.is_daemon_running(odoo_daemon_name):
            question = (
                "%s is not running. Do you want to start it?"
                % odoo_daemon_name
            )
            if yes or click.confirm(question):
                if not lib.start_daemon(odoo_daemon_name):
                    ctx.fail(
                        "Fail to start %s daemon. To do so try: sudo "
                        "systemctl start %s"
                        % (odoo_daemon_name, odoo_daemon_name)
                    )


def filter_databases(db_user, databases):
    """
    Return a list of databases belonging to db_user filtered by the databases
    string.

    databases should be a comma-separated list of database names (without
    spaces) or be equal to "all" to return all databases. A warning is shown
    for any database name that does not correspond to a database belonging to
    db_user.
    """
    all_dbs = lib.get_all_db(db_user)
    if databases == "all":
        return all_dbs
    arg_dbs = set(databases.split(","))
    dbs = [db for db in all_dbs if db in arg_dbs]
    ignored_dbs = set(arg_dbs) - set(dbs)
    for db in ignored_dbs:
        click.echo(
            'Warning: Ignore database "{0}" because it does not exist or '
            "does not belong to user {1}.".format(db, db_user)
        )
    return dbs


def run_update_jobs(ctx, jobs, restart_mode, yes):
    """
    Run the provided update jobs, handling the restart of the odoo daemon and
    failing with an error message explaining which databases failed to update.
    """
    with handle_restart(ctx, restart_mode, yes):
        failed_jobs = run_jobs(ctx, jobs, auto_retry=yes)
        if failed_jobs:
            ctx.fail(
                "Error: the following databases failed to update: {0}".format(
                    ",".join(job["name"] for job in failed_jobs)
                )
            )
