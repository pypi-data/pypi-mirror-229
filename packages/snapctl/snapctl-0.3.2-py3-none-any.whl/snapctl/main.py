import configparser
import os
import requests
import typer

from snapctl.commands.byosnap import ByoSnap
from snapctl.commands.byogs import ByoGs
from snapctl.commands.sdk import Sdk
from snapctl.config.constants import API_KEY, CONFIG_FILE_MAC, CONFIG_FILE_WIN, DEFAULT_PROFILE, VERSION, HTTP_NOT_FOUND, HTTP_FORBIDDEN, HTTP_UNAUTHORIZED
from snapctl.config.endpoints import ENDPOINTS
from snapctl.config.hashes import SDK_PLATFORMS
from snapctl.types.definitions import ResponseType
from snapctl.utils.echo import error, success, info
from sys import platform
from typing import Union

app = typer.Typer()

######### HELPER METHODS #########
def extract_api_key(profile: str | None = None) -> str:
  '''
    Extracts the API Key from the
  '''
  # Parse the config
  config = configparser.ConfigParser()
  if platform == 'win32':
    config.read(os.path.expandvars(CONFIG_FILE_WIN), encoding="utf-8-sig")
  else:
    config.read(os.path.expanduser(CONFIG_FILE_MAC))
  config_profile: str = DEFAULT_PROFILE
  if profile is not None and profile != '' and profile != DEFAULT_PROFILE:
    config_profile = f'profile {profile}'
    info(f"Using Profile from input {profile}")
  else:
    env_api_key = os.getenv(API_KEY)
    if env_api_key is not None:
      config_profile = f'profile {env_api_key}'
      info(f"Using Profile environment variable {profile}")
  return config.get(config_profile, API_KEY, fallback=None, raw=True)

def get_base_url(api_key: str) -> str:
  if api_key.startswith('dev_'):
    return ENDPOINTS['DEV']
  elif api_key.startswith('playtest_'):
    return ENDPOINTS['PLAYTEST']
  return ENDPOINTS['PROD']

def get_composite_token(base_url:str, api_key: str, action: str, params: object) -> str:
  # Exhange the api_key for a token
  payload: object = {
    'action': action,
    'params': params
  }
  res = requests.post(f"{base_url}/v1/snapser-api/composite-token", headers={'api-key': api_key}, json=payload)
  if not res.ok:
    if res.status_code == HTTP_NOT_FOUND:
      error('Service ID is invalid.')
    elif res.status_code == HTTP_UNAUTHORIZED:
      error('API Key verification failed. Your API Key may have expired. Please generate a new one from the Snapser dashboard.')
    elif res.status_code == HTTP_FORBIDDEN:
      error('Permission denied. Your role has been revoked. Please contact your administrator.')
    else:
      error(f'Failed to validate API Key. Error: {res.text}')
    raise typer.Exit()
  success('API Key validated')
  return res.json()['token']

######### CALLBACKS #########
def set_context_callback(ctx: typer.Context, profile: str | None = None):
  '''
    Sets the context for the command
    This method will always set the context for the default profile
    Then if the command has a --profile override it will apply it
  '''
  # Ensure ctx object is instantiated
  ctx.ensure_object(dict)

  # If the user has not overriden the profile you can early exit
  # this is because when you come here from `def common` the context
  # setup happens considering the default profile
  # So only if the user has overriden the profile is when we want to run this
  # method again
  if 'profile' in ctx.obj and ctx.obj['profile'] == profile:
    return

  # Extract the api_key
  api_key = extract_api_key(profile)
  if api_key is None:
    if profile is not None and profile != '':
      conf_file = ''
      if platform == 'win32':
        conf_file = os.path.expandvars(CONFIG_FILE_WIN)
      else:
        conf_file = os.path.expanduser(CONFIG_FILE_MAC)
      error(f'Invalid profile. Please check your snap config file at {conf_file} and try again.')
    else:
      error('API Key not found. Please generate a new one from the Snapser dashboard.')
    raise typer.Exit()
  # Set the context
  ctx.obj['version'] = VERSION
  ctx.obj['api_key'] = api_key
  ctx.obj['profile'] = profile if profile else DEFAULT_PROFILE
  ctx.obj['base_url'] = get_base_url(api_key)


# Presently in typer this is the only way we can expose the `--version`
def version_callback(value: bool = True):
  if value:
    typer.echo(f"Snapctl version: {VERSION}")
    raise typer.Exit()

@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
      None, "--version",
      help="Get the Snapctl version.",
      callback=version_callback
    )
):
    """
    Snapser CLI Tool
    """
    # Verify if the user has a config
    # Note this executes only when the user runs a command and not for --help or --version
    if platform == 'win32':
      config_file_path = os.path.expandvars(CONFIG_FILE_WIN)
    else:
      config_file_path = os.path.expanduser(CONFIG_FILE_MAC)
    if not os.path.isfile(config_file_path):
      error(f'Snapser configuration file not found at {config_file_path} ')
      raise typer.Exit()
    # Set the main context this always sets the default context
    set_context_callback(ctx)

######### TYPER COMMANDS #########
@app.command()
def validate(
  profile: str = typer.Option(None, "--profile", help="Profile to use.", callback=set_context_callback),
):
  """
  Validate your Snapctl setup
  """
  success("Setup is valid 👊")

@app.command()
def byosnap(
  ctx: typer.Context,
  # Required fields
  subcommand: str = typer.Argument(..., help="BYOSnap Subcommands: " + ", ".join(ByoSnap.SUBCOMMANDS) + "."),
  sid: str = typer.Argument(..., help="Snap Id"),
  tag: str = typer.Argument(..., help="Tag for your snap"),
  # publish-image
  path: Union[str, None] = typer.Option(None, "--path", help="(req: publish-image) Path to your snap code"),
  docker_file: str = typer.Option("Dockerfile", help="Dockerfile name to use"),
  # publish-version
  prefix: str = typer.Option('/v1', "--prefix", help="(req: publish-version) URL Prefix for your snap"),
  version: Union[str, None] = typer.Option(None, "--version", help="(req: publish-version) Snap version"),
  http_port: Union[str, None] = typer.Option(None, "--http-port", help="(req: publish-version) Ingress HTTP port version"),
  # profile override
  profile: Union[str, None] = typer.Option(None, "--profile", help="Profile to use.", callback=set_context_callback),
) -> None:
  """
    Bring your own Snap
  """
  token = get_composite_token(ctx.obj['base_url'], ctx.obj['api_key'], ctx.command.name, {'service_id': sid})
  byosnap: ByoSnap = ByoSnap(subcommand, token, ctx.obj['base_url'], ctx.obj['api_key'], sid, tag, path, docker_file, prefix, version, http_port)
  validate_input_response: ResponseType = byosnap.validate_input()
  if validate_input_response['error']:
    return error(validate_input_response['msg'])
  command_method = subcommand.replace('-', '_')
  method: function = getattr(byosnap, command_method)
  if not method():
    return error(f"BYOSnap {subcommand} failed :face_with_head-bandage:")
  success(f"BYOSnap {subcommand} complete :oncoming_fist:")

@app.command()
def byogs(
  ctx: typer.Context,
  # Required fields
  subcommand: str = typer.Argument(..., help="BYOGs Subcommands: " + ", ".join(ByoGs.SUBCOMMANDS) + "."),
  sid: str = typer.Argument(..., help="Snap Id"),
  tag: str = typer.Argument(..., help="Tag for your snap"),
  # publish-image
  path: Union[str, None] = typer.Option(None, "--path", help="(req: publish-image, upload-docs) Path to your snap code"),
  docker_file: str = typer.Option("Dockerfile", help="Dockerfile name to use"),
  # publish-version
  version: Union[str, None] = typer.Option(None, "--version", help="(req: publish-version) Snap version"),
  http_port: Union[str, None] = typer.Option(None, "--http-port", help="(req: publish-version) Ingress HTTP port version"),
  # profile override
  profile: Union[str, None] = typer.Option(None, "--profile", help="Profile to use.", callback=set_context_callback),
) -> None:
  """
    Bring your own Game server
  """
  token = get_composite_token(ctx.obj['base_url'], ctx.obj['api_key'], ctx.command.name, {'service_id': sid})
  byogs: ByoGs = ByoGs(subcommand, token, ctx.obj['base_url'], ctx.obj['api_key'], sid, tag, path, docker_file, version, http_port)
  validate_input_response: ResponseType = byogs.validate_input()
  if validate_input_response['error']:
    return error(validate_input_response['msg'])
  command_method = subcommand.replace('-', '_')
  method: function = getattr(byogs, command_method)
  if not method():
    return error(f"BYOGs {subcommand} failed :face_with_head-bandage:")
  success(f"BYOGs {subcommand} complete :oncoming_fist:")

@app.command()
def sdk(
  ctx: typer.Context,
  # Required fields
  subcommand: str = typer.Argument(..., help="SDK Subcommands: " + ", ".join(Sdk.SUBCOMMANDS) + "."),
  cid: str = typer.Argument(..., help="Cluster Id"),
  platform: str = typer.Argument(..., help="SDK Platforms: " + ", ".join(SDK_PLATFORMS.keys()) + "."),
  path: Union[str, None] = typer.Option(None, "--path", help="Path to save the SDK"),
  snaps: Union[str, None] = typer.Option(None, "--snaps", help="Comma separated list of snap ids to include in the SDK"),
  profile: Union[str, None] = typer.Option(None, "--profile", help="Profile to use.", callback=set_context_callback),
) -> None:
  """
    Download the Snapser SDK
  """
  sdk: Sdk = Sdk(subcommand, ctx.obj['base_url'], ctx.obj['api_key'], cid, platform, path, snaps)
  validate_input_response: ResponseType = sdk.validate_input()
  if validate_input_response['error']:
    return error(validate_input_response['msg'])
  command_method = subcommand.replace('-', '_')
  method: function = getattr(sdk, command_method)
  if not method():
    return error(f"Sdk {subcommand} failed :face_with_head-bandage:")
  success(f"SDK {subcommand} complete :oncoming_fist:")
