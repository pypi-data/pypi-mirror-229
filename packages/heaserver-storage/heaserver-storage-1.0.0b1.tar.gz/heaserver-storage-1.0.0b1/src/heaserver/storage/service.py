"""
The HEA Server storage Microservice provides ...
"""

from heaserver.service import response
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import aws, awsservicelib
from heaserver.service.wstl import builder_factory, action
from heaserver.service.appproperty import HEA_DB
from heaobject.bucket import AWSBucket
from heaobject.storage import AWSStorage
from botocore.exceptions import ClientError
from collections import defaultdict
from datetime import datetime
import logging
import asyncio

MONGODB_STORAGE_COLLECTION = 'storage'


@routes.get('/volumes/{volume_id}/storage')
@routes.get('/volumes/{volume_id}/storage/')
@action(name='heaserver-storage-storage-get-properties', rel='hea-properties')
async def get_all_storage(request: web.Request) -> web.Response:
    """
    Gets all the storage of the volume id that associate with the AWS account.
    :param request: the HTTP request.
    :return: A list of the account's storage or an empty array if there's no any objects data under the AWS account.
    ---
    summary: get all storage for a hea-volume associate with account.
    tags:
        - heaserver-storage-storage-get-account-storage
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
    """
    return await _get_all_storages(request)


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok(None)


def main() -> None:
    config = init_cmd_line(description='a service for managing storage and their data within the cloud',
                           default_port=8080)
    start(package_name='heaserver-storage', db=aws.S3Manager, wstl_builder_factory=builder_factory(__package__), config=config)


async def _get_all_storages(request: web.Request) -> web.Response:
    """
    List available storage classes by name

    :param request: the aiohttp Request (required).
    :return: (list) list of available storage classes
    """

    logger = logging.getLogger(__name__)
    volume_id = request.match_info.get("volume_id", None)
    bucket_id = request.match_info.get('id', None)
    bucket_name = request.match_info.get('bucket_name', None)
    if not volume_id:
        return web.HTTPBadRequest(body="volume_id is required")
    s3_client = await request.app[HEA_DB].get_client(request, 's3', volume_id)
    s3_resource = await request.app[HEA_DB].get_resource(request, 's3', volume_id)

    try:
        resp = []
        if bucket_id or bucket_name:
            bucket_result = await awsservicelib.get_bucket(volume_id=volume_id, s3_resource=s3_resource, s3_client=s3_client,
                                             bucket_name=bucket_name, bucket_id=bucket_id)
            if bucket_result is not None and type(bucket_result) is AWSBucket:
                resp.append({'Name': bucket_result.name})
        else:
            resp = s3_client.list_buckets()['Buckets']

        groups = defaultdict(list)
        for bucket in resp:
            s3_bucket = s3_resource.Bucket(bucket['Name'])
            if s3_bucket is not None:
                for obj in s3_bucket.objects.all():
                    if obj.storage_class is not None:
                        groups[obj.storage_class].append(obj)

        async_storage_class_list = []
        for item in groups.items():
            item_key = item.__getitem__(0)
            item_values = item.__getitem__(1)
            storage_class = _get_storage_class(volume_id=volume_id, item_key=item_key, item_values=item_values)
            if storage_class is not None:
                async_storage_class_list.append(storage_class)

        storage_class_list = await asyncio.gather(*async_storage_class_list)

    except ClientError as e:
        logging.error(e)
        return response.status_bad_request()

    storage_class_dict_list = [storage.to_dict() for storage in storage_class_list if storage is not None]
    return await response.get_all(request, storage_class_dict_list)


async def _get_storage_class(volume_id: str, item_key: str, item_values: list | None = None) -> AWSStorage | None:
    """
    :param item_key: the item_key
    :param item_values:  item_values
    :return: Returns either the AWSStorage or None for Not Found
    """
    logger = logging.getLogger(__name__)

    if not volume_id:
        return None
    if not item_key:
        return None

    total_size = 0
    object_count = 0
    init_mod = None
    last_mod = None

    for val in item_values or []:
        total_size += val.size
        object_count += 1
        init_mod = val.last_modified if init_mod is None or val.last_modified < init_mod else init_mod
        last_mod = val.last_modified if last_mod is None or val.last_modified > last_mod else last_mod

    s = AWSStorage()
    s.name = item_key
    s.id = item_key
    s.display_name = item_key
    s.object_init_modified = init_mod
    s.object_last_modified = last_mod
    s.storage_bytes = total_size
    s.object_count = object_count
    s.created = datetime.now()
    s.modified = datetime.now()
    s.volume_id = volume_id
    s.set_storage_class_from_str(item_key)
    return s
