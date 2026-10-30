"""SDK action boundary for the SharePoint get_file action."""

import httpx
from soar_sdk.params import Params, Param
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField, PermissiveActionOutput
from soar_sdk.exceptions import ActionFailure
from ..auth import get_graph_client
from ..graph_response import GraphResponseError, get_graph_response
from ._graph import _request_graph
from ._paths import encode_path, encode_path_segment
from .drives import drive_root_endpoint
from ..asset import Asset


class GetFileSummary(ActionOutput):
    vault_id: str = OutputField(cef_types=["sha1", "vault id"])


class GetFileParams(Params):
    file_name: str = Param(description="File name to retrieve")
    file_path: str = Param(description="Folder path on site")
    drive_id: str | None = Param(
        description="The file is searched in this drive. If no drive is specified, the default drive will be used",
        cef_types=["sharepoint drive id"],
    )


class ImageOutput(PermissiveActionOutput):
    width: float | None = OutputField(example_values=[256])
    height: float | None = OutputField(example_values=[266])


class UserOutput(PermissiveActionOutput):
    displayName: str | None = OutputField(example_values=["Test User"])
    email: str | None = OutputField(
        cef_types=["email"], example_values=["test_user@tenant-name.ontest.com"]
    )
    id: str | None = OutputField(
        example_values=["eeb3645f-df19-47a1-8e8c-fcd234cb5f6f"]
    )


class CreatedByUserOutput(UserOutput):
    displayName: str | None = OutputField(
        example_values=["Test User"], column_name="Created By"
    )


class LastModifiedByUserOutput(UserOutput):
    displayName: str | None = OutputField(
        example_values=["Test User"], column_name="Last Modified By"
    )


class CreatedbyOutput(PermissiveActionOutput):
    user: CreatedByUserOutput | None = OutputField()


class HashesOutput(PermissiveActionOutput):
    quickXorHash: str | None = OutputField(
        example_values=["EIDYEgye8dEx3XhA7xc12GqSwxk="]
    )


class FileOutput(PermissiveActionOutput):
    hashes: HashesOutput | None = OutputField()
    mimeType: str | None = OutputField(example_values=["text/plain"])


class FilesysteminfoOutput(PermissiveActionOutput):
    createdDateTime: str | None = OutputField(example_values=["2022-02-10T15:25:21Z"])
    lastModifiedDateTime: str | None = OutputField(
        example_values=["2022-02-10T15:25:21Z"]
    )


class LastmodifiedbyOutput(PermissiveActionOutput):
    user: LastModifiedByUserOutput | None = OutputField()


class ParentreferenceOutput(PermissiveActionOutput):
    driveId: str | None = OutputField(
        cef_types=["sharepoint drive id"],
        example_values=[
            "b!6UNv3PpUOUqHgzFOO7vtQcRIK8S5WfFIuW7oFFtVOfpd0Y9Jee8LTIrExOon7Yvi"
        ],
        column_name="Drive ID",
    )
    driveType: str | None = OutputField(example_values=["documentLibrary"])
    id: str | None = OutputField(
        cef_types=["sharepoint drive item id"],
        example_values=["01SNFLYIRDSQLQVWP7EVDKSL3YYUNW6I4G"],
    )
    name: str | None = OutputField(example_values=["Playbook-Folder"])
    path: str | None = OutputField(example_values=["/drive/root:/test_folder_name"])
    siteId: str | None = OutputField(
        example_values=["dc6f43e9-54fa-4a39-8783-314e3bbbed41"]
    )


class SharedOutput(PermissiveActionOutput):
    scope: str | None = OutputField(example_values=["users"])


class GetFileOutput(PermissiveActionOutput):
    download_url: str | None = OutputField(
        alias="@microsoft.graph.downloadUrl",
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/_layouts/15/download.aspx?UniqueId=c743b2e0-36ec-4c8a-9ce0-190c2fd4dd97&Translate=false&tempauth=eyJ0eXAiOiJKV1QiLCJhbGciOiJub0&ApiVersion=2.0"
        ],
    )
    context: str | None = OutputField(alias="@odata.context", cef_types=["url"])
    image: ImageOutput | None = OutputField()
    cTag: str | None = OutputField(
        example_values=['"c:{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1"']
    )
    id: str | None = OutputField(
        cef_types=["sharepoint drive item id"],
        example_values=["01SNFLYIXAWJB4P2ZWTJGJZYAZBQX5JXMX"],
        column_name="Drive Item ID",
    )
    createdBy: CreatedbyOutput | None = OutputField()
    createdDateTime: str | None = OutputField(example_values=["2022-02-10T15:25:21Z"])
    eTag: str | None = OutputField(
        example_values=['"{C743B2E0-36EB-4C9A-9CE0-190C2FD4DD97},1"']
    )
    file: FileOutput | None = OutputField()
    fileSystemInfo: FilesysteminfoOutput | None = OutputField()
    lastModifiedBy: LastmodifiedbyOutput | None = OutputField()
    lastModifiedDateTime: str | None = OutputField(
        example_values=["2022-02-10T15:25:21Z"]
    )
    name: str | None = OutputField(example_values=["test_file_name.txt"])
    parentReference: ParentreferenceOutput | None = OutputField()
    shared: SharedOutput | None = OutputField()
    size: float | None = OutputField(example_values=[1422])
    webUrl: str | None = OutputField(
        cef_types=["url"],
        example_values=[
            "https://test-tenant-name.sharepoint.com/sites/TestSiteName/Shared%20Documents/test_folder_name/test_file_name.txt"
        ],
    )


def _download_file(client: httpx.Client, endpoint: str, destination: str) -> None:
    """Stream Graph file content, then follow its preauthenticated download URL."""
    try:
        with client.stream("GET", endpoint, follow_redirects=False) as response:
            if 300 <= response.status_code < 400:
                location = response.headers.get("location")
                parsed = urlsplit(location or "")
                if (
                    not location
                    or parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.username
                    or parsed.password
                ):
                    raise ActionFailure(
                        "Microsoft Graph returned an invalid download URL"
                    )
                with (
                    httpx.Client(
                        timeout=30.0, verify=True, follow_redirects=True
                    ) as download,
                    download.stream("GET", location) as file_response,
                ):
                    if not file_response.is_success:
                        file_response.read()
                        raise ActionFailure(
                            "Unable to download file content from Microsoft Graph"
                        )
                    with open(destination, "wb") as output:
                        for chunk in file_response.iter_bytes(chunk_size=1024 * 1024):
                            output.write(chunk)
                return
            if not 200 <= response.status_code < 399:
                response.read()
                try:
                    get_graph_response(response)
                except GraphResponseError as exc:
                    raise ActionFailure(str(exc)) from exc
            with open(destination, "wb") as output:
                for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                    output.write(chunk)
    except httpx.RequestError as exc:
        raise ActionFailure("Error connecting to Microsoft Graph") from exc


def _vault_exception_detail(exc: Exception) -> str:
    error_code = None
    error_message = "Unknown error occurred. Please check the asset configuration and|or action parameters"
    try:
        if len(exc.args) > 1:
            error_code, error_message = exc.args[:2]
        elif len(exc.args) == 1:
            error_message = exc.args[0]
    except Exception as exc:
        error_message = str(exc) or error_message
    return f"Error Code: {error_code}. Error Message: {error_message}"


def _file_endpoint(
    site_id: str, drive_id: str | None, file_path: str, file_name: str
) -> tuple[str, str]:
    try:
        encoded_path = encode_path(file_path, allow_empty=True)
        encoded_name = encode_path_segment(file_name)
    except ValueError as exc:
        raise ActionFailure(f"Invalid file path: {exc}") from exc
    if drive_id:
        try:
            encode_path_segment(drive_id)
        except ValueError as exc:
            raise ActionFailure(f"Invalid drive id: {exc}") from exc
    metadata_endpoint = (
        f"{drive_root_endpoint(site_id, drive_id)}/root:/{encoded_path}/{encoded_name}"
    )
    return metadata_endpoint, encoded_name


def get_file(params: GetFileParams, soar: SOARClient, asset: Asset) -> GetFileOutput:
    """Retrieve file metadata and store the file content in the SOAR vault."""
    if not asset.site_id:
        raise ActionFailure(
            "The asset configuration parameter 'Sharepoint Site ID' is required "
            "for retrieving a file from specific site"
        )

    metadata_endpoint, encoded_name = _file_endpoint(
        asset.site_id, params.drive_id, params.file_path, params.file_name
    )
    temporary_path: str | None = None
    try:
        descriptor, temporary_path = tempfile.mkstemp(
            dir=soar.vault.get_vault_tmp_dir()
        )
        os.close(descriptor)
        with get_graph_client(asset) as graph:
            metadata = _request_graph(graph, "GET", metadata_endpoint)
            _download_file(graph, f"{metadata_endpoint}:/content", temporary_path)

        try:
            vault_id = soar.vault.add_attachment(
                container_id=soar.get_executing_container_id(),
                file_location=temporary_path,
                file_name=encoded_name,
            )
        except Exception as exc:
            raise ActionFailure(
                "Unable to add file to the vault for attachment name: "
                f"{encoded_name}. Error: {_vault_exception_detail(exc)}"
            ) from exc
    finally:
        if temporary_path is not None:
            Path(temporary_path).unlink(missing_ok=True)

    output = GetFileOutput.model_validate(metadata)
    soar.set_summary(GetFileSummary(vault_id=vault_id))
    return output
