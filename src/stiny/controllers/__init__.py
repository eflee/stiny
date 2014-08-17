from ..templates import get_template
from ..exceptions import UnsupportedStorageTypeException
from s3 import S3Controller


def get_controller(config):
    """
    Get a pre-configured storage controller based off the application configuration

    :param config: The StinyConfiguration object used to configure the storage controller
    :type config: StinyConfiguration
    :return:
    """
    template = get_template(config.get('main', 'template'))
    storage = config.get('main', 'storage')
    if storage == 's3':
        controller = S3Controller(template=template,
                                  tiny_length=config.get('main', 'min_length'),
                                  max_retries=config.get('main', 'max_retries'),
                                  bucket_name=config.get('s3', 'bucket_name'),
                                  region=config.get('s3', 'region'),
                                  aws_access_key_id=config.get('s3', 'aws_access_key_id'),
                                  aws_secret_access_key=config.get('s3', 'aws_secret_access_key'))
    else:
        raise UnsupportedStorageTypeException("{store} is an unknown backing store type".format(store=storage))
    return controller
