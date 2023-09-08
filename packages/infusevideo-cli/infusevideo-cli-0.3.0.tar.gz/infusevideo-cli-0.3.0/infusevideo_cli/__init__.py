#!/usr/bin/env python3

from docopt import docopt
import json
import logging
import os
from pydantic import BaseSettings, Field, ValidationError, validator
import sys
from typing import Optional, Literal, Any, Union
import urllib.parse
import warnings

import infusevideo
from infusevideo.loghelpers import setupLogging, ml


doc = """
Usage: ivc METHOD ROUTEPART ...
           [--json=JSON] [--query=QUERY ...]
           [--file=PATH] [--file-field=FIELD]
           [--profile=NAME]
           [--script]
       ivc --generate-config
       ivc --clear-token [--profile=NAME]
       ivc --list-profiles [--full]
       ivc --help

Arguments:
  METHOD      the method to use (GET, POST, PUT, PATCH or DELETE)
  ROUTEPART   the desired route, full or partial. Can be specified as:
                actual route "/media/abcdef/url"
                route parts "media" "abcdef" "url"

Options:
  --json=JSON          the JSON string to send in the request body
  --query=QUERY        data to pass on in the query string, as "name=value"
  --file=PATH          path to the file to upload. This will be sent as
                       multipart/form-data
  --file-field=FIELD   name of the field used for file upload. Default "file"
  --profile=NAME       name of the configuration profile to use
  --script             run in script mode. This does the following:
                         * skip human authentication methods
                         * ensure output json is machine-readable as
                           opposed to human-readable, e.g. for special glyphs
                       Alternatively, invoking the program "ivs" does the
                       same as running "ivc --script".

First use:
  --generate-config   generates a sample configuration file

Other:
  --clear-token     Clears the cached authentication token for the selected
                    profile. Only necessary when permissions were changed.
  --list-profiles   Lists the available profiles and some basic information
  --full            Instead of basic information, show all information

Help:
  -h --help   show this help
"""

warnings.filterwarnings(
	"ignore",
	"aliases are no longer used by BaseSettings to define which environment variables to read",
	FutureWarning,
)


class CommandlineOptions(BaseSettings):
	generateConfig: bool = Field(alias="--generate-config")
	listProfiles: bool = Field(alias="--list-profiles")
	listFullProfiles: bool = Field(alias="--full")
	clearToken: bool = Field(alias="--clear-token")
	profile: Optional[str] = Field(alias="--profile")
	help: bool = Field(alias="--help")
	script: bool = Field(alias="--script")
	fileField: str = Field(alias="--file-field", default="file")
	file: Optional[str] = Field(alias="--file")
	jsonData: Optional[str] = Field(alias="--json")
	queryData: list[str] = Field(alias="--query")
	method: Optional[str] = Field(alias="METHOD")
	routeparts: list[str] = Field(alias="ROUTEPART")

	@validator("method")
	def method_uppercase(cls, value: str) -> str:
		"""Validate the method is valid and convert it to uppercase"""
		if value is None:
			return value
		methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
		method = value.upper()
		if method not in methods:
			raise ValueError(f"Invalid value {value!r}, permitted: {', '.join(methods)}")
		return method

	@validator("jsonData")
	def is_valid_json(cls, value: Optional[str]) -> str:
		"""Validate the JSON is correct"""
		if value is None:
			return value
		try:
			json.loads(value)
		except json.decoder.JSONDecodeError as e:
			raise ValueError(f"Invalid JSON: {e}")
		return value

	@validator("queryData")
	def is_valid_querydata(cls, values: list[str]) -> list[str]:
		"""Validate the query data is in the correct format"""
		for value in values:
			if "=" not in value:
				raise ValueError(f"Missing '=' in {value!r}")
		return values

	@property
	def route(self) -> str:
		"""The route to query"""
		return "/" + "/".join([part.strip("/") for part in self.routeparts])

	@property
	def queryParams(self) -> list[tuple[str, str]]:
		"""The query parameters, split into a list of tuples"""
		return [tuple(query.split("=", maxsplit=1)) for query in self.queryData]

def generateConfig() -> int:
	try:
		path = infusevideo.Config.generate_sample_config()
		print(f"Sample configuration created at {path}.")
	except infusevideo.errors.ConfigAlreadyExists as e:
		logging.error(e)
		return 1
	return 0

def listProfiles(full: bool = False) -> int:
	config = infusevideo.Config()
	print("D Profile             Basic settings")
	print("- ------------------- -------------------------------")
	for entry in sorted(config._config):
		if not entry.startswith("profile-"):
			continue
		_, name = entry.split("-", 1)
		default = "*" if name == config.defaultProfile else " "
		profile = infusevideo.config.Profile(name=name, **config._config[entry])
		print(f"{default} {name:19s} ", end="")
		if full:
			print("------------------------------------------")
			for k, v in profile:
				if k == "name":
					continue
				print(f"{default:21s} {k}={v}")
			print("")
		else:
			print(f"{profile.server}, auth={profile.auth}, scope_type={profile.scope_type}, account={profile.account}")
	return 0

def cli() -> None:
	"""The actual CLI program"""
	setupLogging()

	# Process commandline options
	try:
		options = CommandlineOptions(**{k: v for k, v in docopt(doc).items() if v is not None})
	except ValidationError as e:
		logging.error(e)
		sys.exit(1)

	# Determine how this was invoked
	basename = os.path.basename(sys.argv[0])
	if basename.startswith("ivs"):
		options.script = True
	if (basename.startswith("ivd") or
		os.environ.get("DEBUG", "0").lower() not in ["0", "false"]):
		setupLogging(logging.DEBUG, "%(asctime)s,%(msecs)03d %(levelname)s: %(message)s")

	# If requested, generate config and exit
	if options.generateConfig:
		sys.exit(generateConfig())

	# If requested, list profiles
	if options.listProfiles:
		sys.exit(listProfiles(options.listFullProfiles))

	# Instantiate InfuseVideo
	try:
		api = infusevideo.InfuseVideo(
			options.profile,
			disableHumanAuth=options.script,
			machineJSON=options.script,
		)
	except infusevideo.errors.ConfigNotFound as e:
		logging.error(ml(
			e,
			"A sample configuration file can be created by running:",
			f"  {sys.argv[0]} --generate-config",
		))
		sys.exit(1)
	except infusevideo.Error as e:
		logging.error(e)
		sys.exit(1)

	# If requested, clear the token cache and exit
	if options.clearToken:
		api.client.auth.clear_cache()
		print(f"Token cache cleared for profile {api.client.profile.name}")
		sys.exit(0)

	# Execute according to options
	try:
		response = api.client.request(
			options.method,
			options.route,
			params=options.queryParams,
			data=options.jsonData,
			fileName=options.file,
			fileField=options.fileField,
		)
		print(response)
	except infusevideo.errors.ApiError as e:
		logging.error(f"Request returned error code {e.response.code}")
		print(e)
		sys.exit(1)
	except infusevideo.errors.RequestedScopeError as e:
		logging.error(ml(
			f"Authorization error: {e}",
			f"You can refresh your token by executing:",
			f"    {sys.argv[0]} --clear-token --profile {e.profile.name}",
			f"and then trying again.",
		))
		sys.exit(1)
	except infusevideo.errors.AuthorizationError as e:
		logging.error(ml(
			"An authorization error occurred:",
			e,
		))
		sys.exit(1)
	except infusevideo.errors.AuthenticationError as e:
		logging.error(ml(
			"An authentication error occurred:",
			e,
		))
		sys.exit(1)
	except infusevideo.Error as e:
		logging.error(e)
		sys.exit(1)
