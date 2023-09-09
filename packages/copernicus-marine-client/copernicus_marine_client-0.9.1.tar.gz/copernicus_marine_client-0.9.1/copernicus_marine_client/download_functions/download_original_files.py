import pathlib
import re
from itertools import chain
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Optional, Tuple

import boto3
import botocore
from numpy import append, arange
from tqdm import tqdm

from copernicus_marine_client.catalogue_parser.request_structure import (
    GetRequest,
)
from copernicus_marine_client.core_functions.utils import (
    flatten,
    get_unique_filename,
)
from copernicus_marine_client.download_functions.download_get import (
    download_get,
)

MARINE_DATA_LAKE_LISTING_ENDPOINT = "https://marine.copernicus.eu"
MARINE_DATA_LAKE_LISTING_ORIGINALLY_PRODUCED_FILE_BUCKET = "mdl-native-list"
MARINE_DATA_LAKE_DOWNLOAD_ORIGINALLY_PRODUCED_FILE_BUCKET = "mdl-native"
MARINE_DATA_LAKE_S3_LISTING_ORIGINAL_FILE_ROOT_URI = (
    f"{MARINE_DATA_LAKE_LISTING_ORIGINALLY_PRODUCED_FILE_BUCKET}/native"
)
MARINE_DATA_LAKE_S3_DOWNLOAD_ORIGINAL_FILE_ROOT_URI = (
    f"{MARINE_DATA_LAKE_DOWNLOAD_ORIGINALLY_PRODUCED_FILE_BUCKET}/native"
)


def download_original_files(
    username: str,
    password: str,
    get_request: GetRequest,
) -> list[pathlib.Path]:
    filenames_in, filenames_out, endpoint_url = download_get(
        username,
        password,
        get_request,
        _download_header,
        create_filenames_out,
    )
    return download_files(endpoint_url, filenames_in, filenames_out)


def download_files(
    endpoint_url: str,
    filenames_in: List[str],
    filenames_out: List[pathlib.Path],
) -> list[pathlib.Path]:
    pool = ThreadPool()
    nfiles_per_process, nfiles = 1, len(filenames_in)
    indexes = append(
        arange(0, nfiles, nfiles_per_process, dtype=int),
        nfiles,
    )
    groups_in_files = [
        filenames_in[indexes[i] : indexes[i + 1]]
        for i in range(len(indexes) - 1)
    ]
    groups_out_files = [
        filenames_out[indexes[i] : indexes[i + 1]]
        for i in range(len(indexes) - 1)
    ]

    for groups_out_file in groups_out_files:
        parent_dir = Path(groups_out_file[0]).parent
        if not parent_dir.is_dir():
            pathlib.Path.mkdir(parent_dir, parents=True)

    download_summary_list = pool.imap(
        _download_files,
        zip(
            [endpoint_url] * len(groups_in_files),
            groups_in_files,
            groups_out_files,
        ),
    )
    download_summary = list(
        tqdm(download_summary_list, total=len(groups_in_files))
    )
    return flatten(download_summary)


def _download_header(
    data_path: str, regex: Optional[str], _username: str, _password: str
) -> Tuple[str, str, list[str], float]:
    (endpoint_url, path) = parse_original_files_dataset_url(data_path)
    message = "You requested the download of the following files:\n"
    filenames, sizes, total_size = [], [], 0.0
    raw_filenames = list_files_on_marine_data_lake_s3(path)
    filename_filtered = []
    for filename, size in raw_filenames:
        if not regex or re.match(regex, filename):
            filenames += [filename]
            sizes += [float(size)]
            total_size += float(size)
            filename_filtered.append((filename, size))

    for filename, size in filename_filtered[:20]:
        message += str(filename)
        message += f" - {format_file_size(float(size))}\n"
    if len(filenames) > 20:
        message += f"Printed 20 out of {len(filenames)} files\n"
    message += (
        f"\nTotal size of the download: {format_file_size(total_size)}\n\n"
    )
    return (message, endpoint_url, filenames, total_size)


def list_files_on_marine_data_lake_s3(
    path: str,
    files_already_found: list[tuple[str, int]] = [],
) -> list[tuple[str, int]]:
    # In order to list S3 originally produced files, we are using CDN functionnalities using the following endpoint_url and path  # noqa
    path = path.replace(
        f"s3://{MARINE_DATA_LAKE_S3_DOWNLOAD_ORIGINAL_FILE_ROOT_URI}",
        f"s3://{MARINE_DATA_LAKE_S3_LISTING_ORIGINAL_FILE_ROOT_URI}",
    )

    s3_session = boto3.session.Session()
    s3_client = s3_session.client(
        "s3",
        config=botocore.config.Config(
            # Configures to use subdomain/virtual calling format.
            s3={"addressing_style": "virtual"},
            signature_version=botocore.UNSIGNED,
        ),
        endpoint_url=MARINE_DATA_LAKE_LISTING_ENDPOINT,
    )

    prefix = path.replace(
        f"s3://{MARINE_DATA_LAKE_LISTING_ORIGINALLY_PRODUCED_FILE_BUCKET}/", ""
    )

    paginator = s3_client.get_paginator("list_objects")
    page_iterator = paginator.paginate(
        Bucket=MARINE_DATA_LAKE_LISTING_ORIGINALLY_PRODUCED_FILE_BUCKET,
        Prefix=prefix,
    )

    s3_objects = chain(*map(lambda page: page["Contents"], page_iterator))

    for s3_object in s3_objects:
        files_already_found.extend(
            [
                (
                    f"s3://{MARINE_DATA_LAKE_DOWNLOAD_ORIGINALLY_PRODUCED_FILE_BUCKET}/"
                    + s3_object["Key"],
                    s3_object["Size"],
                )
            ]
        )
    return files_already_found


def _download_files(
    tuple_original_files_filename: Tuple[str, list[str], list[pathlib.Path]],
) -> list[pathlib.Path]:
    def _original_files_file_download(
        endpoint_url: str, file_in: str, file_out: pathlib.Path
    ) -> pathlib.Path:
        """
        Download ONE file and return a string of the result
        """
        s3_session = boto3.session.Session()
        s3_client = s3_session.client(
            "s3",
            config=botocore.config.Config(
                # Configures to use subdomain/virtual calling format.
                s3={"addressing_style": "virtual"},
                signature_version=botocore.UNSIGNED,
            ),
            endpoint_url=endpoint_url,
        )

        s3_client.download_file(
            MARINE_DATA_LAKE_DOWNLOAD_ORIGINALLY_PRODUCED_FILE_BUCKET,
            file_in.replace("s3://mdl-native/", ""),
            file_out,
        )

        return file_out

    endpoint_url, filenames_in, filenames_out = tuple_original_files_filename
    download_summary = []
    for file_in, file_out in zip(filenames_in, filenames_out):
        download_summary.append(
            _original_files_file_download(endpoint_url, file_in, file_out)
        )
    return download_summary


# /////////////////////////////
# --- Tools
# /////////////////////////////


def parse_original_files_dataset_url(data_path: str) -> Tuple[str, str]:
    endpoint_url, path = data_path.split("/mdl-native/", maxsplit=1)
    path = "s3://mdl-native/" + path
    return (endpoint_url, path)


def create_filenames_out(
    filenames_in: list[str],
    overwrite: bool,
    output_directory: pathlib.Path = pathlib.Path("."),
    no_directories=False,
) -> list[pathlib.Path]:
    filenames_out = []
    for filename_in in filenames_in:
        filename_out = output_directory
        if no_directories:
            filename_out = (
                pathlib.Path(filename_out) / pathlib.Path(filename_in).name
            )
        elif filename_in.startswith(
            f"s3://{MARINE_DATA_LAKE_S3_DOWNLOAD_ORIGINAL_FILE_ROOT_URI}/"
        ):
            filename_out = filename_out / pathlib.Path(
                filename_in.split(
                    f"s3://{MARINE_DATA_LAKE_S3_DOWNLOAD_ORIGINAL_FILE_ROOT_URI}/"
                )[-1]
            )
        elif filename_in.startswith(
            f"s3://{MARINE_DATA_LAKE_S3_LISTING_ORIGINAL_FILE_ROOT_URI}/"
        ):
            filename_out = filename_out / pathlib.Path(
                filename_in.split(
                    f"s3://{MARINE_DATA_LAKE_S3_LISTING_ORIGINAL_FILE_ROOT_URI}/"
                )[-1]
            )

        filename_out = get_unique_filename(
            filepath=filename_out, overwrite_option=overwrite
        )

        filenames_out.append(filename_out)
    return filenames_out


def format_file_size(
    size: float, decimals: int = 2, binary_system: bool = False
) -> str:
    if binary_system:
        units: list[str] = [
            "B",
            "KiB",
            "MiB",
            "GiB",
            "TiB",
            "PiB",
            "EiB",
            "ZiB",
        ]
        largest_unit: str = "YiB"
        step: int = 1024
    else:
        units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB"]
        largest_unit = "YB"
        step = 1000

    for unit in units:
        if size < step:
            return ("%." + str(decimals) + "f %s") % (size, unit)
        size /= step

    return ("%." + str(decimals) + "f %s") % (size, largest_unit)
