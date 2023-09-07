import os
import requests

from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.config.hashes import SDK_PLATFORMS
from snapctl.types.definitions import ResponseType
from snapctl.utils.echo import error, success
from sys import platform
from typing import Union

class Sdk:
  SUBCOMMANDS = ['download']

  def __init__(self, subcommand: str, base_url: str, api_key: str, cid: str, platform: str, path: Union[str, None], snaps: Union[str, None]) -> None:
    self.subcommand: str = subcommand
    self.base_url: str = base_url
    self.api_key: str = api_key
    self.cid: str = cid
    self.platform: str = platform
    self.path: Union[str, None] = path
    self.snaps: Union[str, None] = snaps

  def validate_input(self) -> ResponseType:
    response: ResponseType = {
      'error': True,
      'msg': '',
      'data': []
    }
    # Check subcommand
    if not self.subcommand in Sdk.SUBCOMMANDS:
      response['msg'] = f"Invalid command. Valid commands are {', '.join(Sdk.SUBCOMMANDS)}."
      return response
    if self.platform not in SDK_PLATFORMS.keys():
      response['msg'] = f"Invalid SDK platform. Valid platforms are {', '.join(SDK_PLATFORMS.keys())}."
      return response
    # Check file path
    if self.path and not os.path.isfile(f"{self.path}"):
      response['msg'] = f"Invalid path {self.path}. Please enter a valid path to save your SDK."
      return response
    # Send success
    response['error'] = False
    return response

  def download(self) -> bool:
    # Push the swagger.json
    with Progress(
      SpinnerColumn(),
      TextColumn("[progress.description]{task.description}"),
      transient=True,
    ) as progress:
      progress.add_task(description=f'Downloading your custom SDK...', total=None)
      try:
        url = f"{self.base_url}/v1/snapser-api/sdk?cluster_id={self.cid}&type={SDK_PLATFORMS[self.platform]['type']}&subtype={SDK_PLATFORMS[self.platform]['subtype']}"
        if self.snaps:
          url += f"&snaps={self.snaps}"
        res = requests.get(url, headers={'api-key': self.api_key})
        file_name = f"snapser-{self.cid}-{self.platform}.zip"
        file_path_symbol = '/'
        if platform == 'win32':
          file_path_symbol = '\\'
        sdk_save_path = f"{self.path}{file_path_symbol}{file_name}" if self.path is not None else f"{os.getcwd()}{file_path_symbol}{file_name}"
        if res.ok:
          with open(sdk_save_path, "wb") as file:
            file.write(res.content)
          success(f"SDK saved at {sdk_save_path}")
          return True
        error(f'Unable to download your custom SDK')
      except Exception as e:
        error("Exception: Unable to download the SDK")
      return False