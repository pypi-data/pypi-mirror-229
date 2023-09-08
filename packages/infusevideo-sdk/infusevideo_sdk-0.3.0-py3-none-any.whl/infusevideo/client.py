import json
import logging
import os.path
import requests
from typing import Union, Optional, Any, BinaryIO, Iterator

from .auth import Auth
from .config import Profile
from .errors import AuthorizationError, UnrequestedScopeError, RequestedScopeError
from . import errors
from .loghelpers import ml, debugml

class Client:
	class Response:
		def __init__(self, response: requests.Response, machineJSON: bool = True) -> None:
			self._response = response
			self._machineJSON = machineJSON
			self._code: int = response.status_code
			self._ok: bool = response.ok
			self._data: Union[list[Any], dict[str, Any]] = {}
			if self._code == 204:
				if response.text:
					raise errors.ApiError(f"Received non-empty 204: {response.text}")
			else:
				try:
					self._data = response.json()
				except requests.JSONDecodeError:
					raise errors.ApiResponseDecodeError(response.text)
			if not self.ok:
				raise errors.ApiError(self)

		@property
		def data(self) -> Union[list[Any], dict[str, Any]]:
			return self._data

		@property
		def code(self) -> int:
			return self._code

		@property
		def ok(self) -> bool:
			return self._ok

		def __str__(self) -> str:
			if self._code == 204:
				return ""
			return json.dumps(self.data, indent=4, ensure_ascii=self._machineJSON)

		def __getitem__(self, key) -> Any:
			return self.data[key]

		def __len__(self, key) -> int:
			return len(self.data)

		def __iter__(self) -> Union[Iterator[list[Any]], Iterator[dict[str, Any]]]:
			return iter(self.data)

		def __contains__(self, key) -> bool:
			return key in self.data

	def __init__(self, profile: Profile, machineJSON: bool = True) -> None:
		self._machineJSON = machineJSON
		self._baseUrl = f"https://{profile.server}"
		self._profile = profile
		self._auth = Auth(profile)
		debugml(
			"Initiated client",
			("profile: %s", self._profile),
			("baseUrl='%s'", self._baseUrl),
		)

	@property
	def auth(self) -> Auth:
		return self._auth

	@property
	def profile(self) -> Profile:
		return self._profile

	def request(
			self,
			method: str,
			route: str,
			*,
			params: Optional[list[tuple[str, str]]] = None,
			data: Optional[Union[str, list[Any], dict[str, Any]]] = None,
			content_type: str = "application/json",
			fileName: Optional[str] = None,
			fileField: str = "file",
	) -> Response:
		"""Do the actual request

		Args:
			...

		Returns:
			...
		"""
		logging.debug(ml(
			f"Starting request {method=} {route=}",
			f"{content_type=}",
			f"{fileField=} {fileName=}",
			f"{params=}",
			f"{data=}",
		))
		jsondata: Optional[Union[list[Any], dict[str, Any]]] = None
		databytes: Optional[bytes] = None
		if data is not None:
			if not isinstance(data, str):
				jsondata = data
				data = None
			else:
				databytes = data.encode()

		for tries in range(2):
			files: Optional[dict[str, tuple[str, str]]] = None
			fileObj: Optional[BinaryIO] = None

			headers: dict[str, str] = {
				"Content-Type": content_type,
				"Authorization": f"Bearer {self._auth.token}",
			}

			try:
				if fileName is not None:
					del headers["Content-Type"] # Automatically supplied by requests in this case
					fileObj = open(fileName, "rb")
					files = {
						fileField: (
							os.path.basename(fileName),
							fileObj,
						),
					}

				# Request with auth
				url = f"{self._baseUrl}{route}"
				logging.debug(ml(
					f"Executing request {method=} {url=}",
					f"{params=}",
					f"{databytes=}",
					f"{jsondata=}",
					f"{headers=}",
					f"{files=}",
				))
				response = requests.request(
					method,
					url,
					params=params,
					data=databytes,
					json=jsondata,
					headers=headers,
					files=files,
					allow_redirects=False,
				)
			finally:
				if fileObj is not None:
					fileObj.close()

			# if 401 auth
			if response.status_code == 401:
				try:
					error = response.json()
					if error["type"] == "InvalidSignature":
						# We should be able to automatically recover from this
						self._auth.refresh()
						continue
					if error["type"] == "MissingScope":
						# We can also recover from this, if that scope is in the profile but hasn't
						# been requested yet.
						required = error["required"]
						if self._auth.profileScope and required not in self._auth.profileScope:
							# Cannot happen, config change required
							raise UnrequestedScopeError(required, self._profile)
						elif required in self._auth.requestedScope:
							# Requested but apparently not granted, not going to happen either
							raise RequestedScopeError(required, self._profile)
						else:
							# It is in the profile, not in requested, just refresh the token
							self._auth.refresh()
							continue
					raise AuthorizationError(json.dumps(error, indent=4))
				except (requests.JSONDecodeError, KeyError):
					raise AuthorizationError(response.text)

			return self.Response(response, self._machineJSON)
