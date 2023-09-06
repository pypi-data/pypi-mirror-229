from collections.abc import Mapping
from textwrap import dedent
from urllib.parse import urlparse

from typing_extensions import override

from .mime_type import LINK_MIME_TYPE, MARKDOWN_MIME_TYPE, TEXT_MIME_TYPE


class Link:
    def __init__(
        self,
        *,
        path: str,
        session_local_url: str,
        session_location: Mapping[str, object],
    ):
        self._path = path.lstrip("/")
        self._session_local_url = session_local_url
        self._session_location = session_location

    @override
    def __repr__(self) -> str:
        text = self._repr_mimebundle_({}, {})[TEXT_MIME_TYPE]
        assert isinstance(text, str)
        return text

    def _repr_mimebundle_(
        self,
        include: object,  # noqa: ARG002
        exclude: object,  # noqa: ARG002
    ) -> dict[str, object]:
        url = self._session_local_url

        if self._path:
            url += f"/{self._path}"

        bundle: dict[str, object] = {
            LINK_MIME_TYPE: {
                "path": self._path,
                "sessionLocation": self._session_location,
            }
        }

        is_local = urlparse(url).hostname == "localhost"

        if is_local:
            note = "This is the session's local URL: it may not be reachable if Atoti is running on another machine."

            bundle[MARKDOWN_MIME_TYPE] = dedent(
                f"""\
                {url}

                _Note_: {note}
                """
            ).strip()
            bundle[TEXT_MIME_TYPE] = f"{url} ({note})"
        else:
            bundle[TEXT_MIME_TYPE] = url

        return bundle
