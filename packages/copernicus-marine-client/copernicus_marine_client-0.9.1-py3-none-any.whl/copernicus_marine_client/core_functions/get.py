import fnmatch
import logging
import logging.config
import pathlib
from typing import List, Optional

from copernicus_marine_client.catalogue_parser.catalogue_parser import (
    CopernicusMarineDatasetServiceType,
    parse_catalogue,
)
from copernicus_marine_client.catalogue_parser.request_structure import (
    GetRequest,
    get_request_from_file,
)
from copernicus_marine_client.core_functions.credentials_utils import (
    get_and_check_username_password,
)
from copernicus_marine_client.core_functions.services_utils import (
    CommandType,
    get_dataset_service,
)
from copernicus_marine_client.download_functions.download_ftp import (
    download_ftp,
)
from copernicus_marine_client.download_functions.download_original_files import (
    download_original_files,
)


def get_function(
    dataset_url: Optional[str],
    dataset_id: Optional[str],
    username: Optional[str],
    password: Optional[str],
    no_directories: bool,
    show_outputnames: bool,
    output_directory: Optional[pathlib.Path],
    credentials_file: Optional[pathlib.Path],
    force_download: bool,
    overwrite_output_data: bool,
    request_file: Optional[pathlib.Path],
    force_service: Optional[str],
    overwrite_metadata_cache: bool,
    no_metadata_cache: bool,
    filter: Optional[str],
    regex: Optional[str],
) -> List[pathlib.Path]:
    get_request = GetRequest()
    if request_file:
        get_request = get_request_from_file(request_file)
    request_update_dict = {
        "dataset_url": dataset_url,
        "dataset_id": dataset_id,
        "output_directory": output_directory,
        "force_service": force_service,
    }
    get_request.update(request_update_dict)

    # Specific treatment for default values:
    # In order to not overload arguments with default values
    if no_directories:
        get_request.no_directories = no_directories
    if show_outputnames:
        get_request.show_outputnames = show_outputnames
    if force_download:
        get_request.force_download = force_download
    if overwrite_output_data:
        get_request.overwrite_output_data = overwrite_output_data
    if force_service:
        get_request.force_service = force_service
    if filter:
        get_request.regex = fnmatch.translate(filter)
    if regex:
        get_request.regex = (
            regex
            if not filter
            else "(" + regex + "|" + fnmatch.translate(filter) + ")"
        )

    return _run_get_request(
        username,
        password,
        get_request,
        credentials_file,
        overwrite_metadata_cache,
        no_metadata_cache,
    )


def _run_get_request(
    username: Optional[str],
    password: Optional[str],
    get_request: GetRequest,
    credentials_file: Optional[pathlib.Path],
    overwrite_metadata_cache: bool,
    no_metadata_cache: bool,
) -> List[pathlib.Path]:
    username, password = get_and_check_username_password(
        username,
        password,
        credentials_file,
    )
    catalogue = parse_catalogue(overwrite_metadata_cache, no_metadata_cache)
    dataset_service = get_dataset_service(
        catalogue,
        get_request.dataset_id,
        get_request.dataset_url,
        get_request.force_service,
        CommandType.GET,
    )
    get_request.dataset_url = dataset_service.uri
    logging.info(
        "Downloading using service "
        f"{dataset_service.service_type.service_name.value}..."
    )
    if dataset_service.service_type == CopernicusMarineDatasetServiceType.FTP:
        downloaded_files = download_ftp(
            username,
            password,
            get_request,
        )
        logging.info(downloaded_files)
    elif (
        dataset_service.service_type
        == CopernicusMarineDatasetServiceType.FILES
    ):
        downloaded_files = download_original_files(
            username,
            password,
            get_request,
        )
        logging.info(downloaded_files)
    return downloaded_files
