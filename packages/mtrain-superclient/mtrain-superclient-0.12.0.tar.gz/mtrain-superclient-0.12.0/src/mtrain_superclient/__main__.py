"""Command-line interface."""
import click
import logging
import json
import os
import yaml
import pathlib
from github import Github, Auth

from . import client, github_regimens, utils, autoconfig, models, utils


logger = logging.getLogger(__name__)


DEFAULT_FILE_CONFIG_PATH = pathlib.Path(
    os.environ.get(
        "FILE_CONFIG_PATH",
        r"\\allen\programs\mindscope\workgroups\dynamicrouting\chrism\mtrain-superclient-recipies\dev\dynamicrouting.yml",
    )
)


@click.group(name="mtrain-superclient")
@click.version_option()
def main() -> None:
    """Mtrain Superclient."""


@main.command("add", help="Add a regimen.")
@click.argument('regimen-yaml')
@click.option(
    '--version-update',
    default="patch",
    help='Version increment type.',
)
@click.option(
    '--dev',
    default=False,
    is_flag=True,
    help='Upload to development server.',
)
@click.option(
    '--source',
    "source_branch_name",
    default="ephys_task1a_master",
    help='If making a new branch, the source branch.',
)
def add_regimen(regimen_yaml, version_update, dev, source_branch_name):
    regimen_update_recipie = autoconfig.get(use_prod=not dev)
    
    mtrain_client = client.Client(
        regimen_update_recipie.api_base, 
        regimen_update_recipie.username,
        regimen_update_recipie.password,
    )
    auth = Auth.Token(regimen_update_recipie.access_token)
    github_client = Github(auth=auth)

    with open(regimen_yaml, "r") as f:
        regimen_dict = github_regimens.ruamel_yaml.load(f.read())
    
    # todo add some sorta of fuzzy definition map?

    script = regimen_dict.get("_script", None)
    if script is not None and script.startswith("http"):
        regimen_dict["_script_md5"] = utils.generate_script_checksum(script)
    else:
        regimen_dict["_script_md5"] = script

    # ugh...
    for stage in regimen_dict["stages"].values():
        if stage.get("script", None) is not None:
            stage["script"] = script
            stage["script_md5"] = utils.generate_script_checksum(stage["script"])

    # regimen_dict = regimen.model_dump_json()
    inferred_branch_name = regimen_dict["name"].split("_")[0]
    repo = github_client.get_repo(regimen_update_recipie.github_repo_name)
    branch_names = [branch.name for branch in repo.get_branches()]
    if inferred_branch_name not in branch_names:
        click.confirm(f"Create branch: {inferred_branch_name}?", abort=True)
        if not source_branch_name:
            if not len(branch_names) > 0:
                raise Exception("No source branches found.")
            click.echo("Available branches:")
            for branch_name in branch_names:
                click.echo(branch_name)
            source_branch_name = click.prompt("Enter a source branch name.")
            if source_branch_name not in branch_names:
                raise Exception("Invalid source branch name: %s" % source_branch_name)
        source_branch = repo.get_branch(source_branch_name)
        repo.create_git_ref(
            ref=f'refs/heads/{inferred_branch_name}',
            sha=source_branch.commit.sha,
        )
    else:
        regimen_dict["name"] = utils.generate_regimen_version(
            regimen_dict["name"], 
            utils.UpdateType(version_update),
        )

    dumped = github_regimens.ruamel_yaml.dump_to_string(
        regimen_dict
    )
    regimen = models.Regimen.from_dict(yaml.safe_load(dumped))

    response = mtrain_client.add_regimen(
        regimen_dict,
    )
    if not response.status_code in (200, ):
        response.raise_for_status()

    github_regimens.put(
        github_client,
        (regimen, regimen_dict, ),
        regimen_update_recipie.github_repo_name,
        inferred_branch_name,
    )

    click.echo("Added regimen: %s" % regimen.name)

    # hold on to your butts...TODO: do something way less sketchy...
    with open(regimen_yaml, "w") as f:
        f.write(
            github_regimens.ruamel_yaml.ruamel_yaml.dump_to_string(regimen_dict)
        )

    click.echo("Updated regimen file: %s" % regimen_yaml)


@main.command("set-state", help="Set a subject state.")
@click.argument(
    'subject_id',
)
@click.option(
    '--regimen-name',
    prompt="Enter a regimen name.",
    help='Name of the regimen to move subject to.',  # ugh
)
@click.option(
    '--stage-name',
    # prompt="Enter a stage name.",
    default=None,
    help='Name of the stage to move subject to.',  # ugh
)
# @click.option(
#     '-verbose',
#     default=True,
#     is_flag=True,
#     help='Upload to production.',
# )
def set_state(subject_id, regimen_name, stage_name):
    regimen_update_recipie = autoconfig.get(use_prod=True)

    mtrain_client = client.Client(
        regimen_update_recipie.api_base, 
        regimen_update_recipie.username,
        regimen_update_recipie.password,
    )

    current_stage = mtrain_client.get_subject_stage(subject_id)
    click.echo("Current stage: %s" % current_stage.model_dump_json(indent=4))

    if stage_name is None:
        regimen = mtrain_client.get_full_regimen(regimen_name)
        click.echo("Available stages:")
        for stage in regimen.stages:
            click.echo(stage)
        stage_name = click.prompt("Enter a stage name.")
        if stage_name not in regimen.stages:
            raise Exception("Invalid stage name. %s" % stage_name)
        click.echo("Selected stage: %s" % stage_name)
        # click.echo(
        #     "Stage definition: %s" % 
        #     regimen.stages[stage_name].model_dump_json(indent=4)
        # )
    
    mtrain_client.set_state(subject_id, regimen_name, stage_name)
    click.echo(f"Set subject state: {subject_id} {regimen_name} {stage_name}")


if __name__ == "__main__":
    # main(prog_name="mtrain-superclient")  # pragma: no cover
    main()  # pragma: no cover
