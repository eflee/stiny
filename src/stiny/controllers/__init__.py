from ..templates import get_template
from ..exceptions import UnsupportedStorageTypeException
from ..analytics import Analytics
from s3 import S3Controller


def get_controller(config):
    """
    Get a pre-configured storage controller based off the application configuration

    :param config: The StinyConfiguration object used to configure the storage controller
    :type config: StinyConfiguration
    :return:
    """
    template = get_template(config.get('main', 'template'))
    analytics = Analytics(config.get('main', 'analytics_id')) if config.has('main', 'analytics_id') else None

    storage = config.get('main', 'storage')
    if storage == 's3':
        compress = config.get('s3', 'compress') == 1 if config.has('s3', 'compress') else False
        controller = S3Controller(template=template,
                                  tiny_length=config.get('main', 'min_length'),
                                  max_retries=config.get('main', 'max_retries'),
                                  bucket_name=config.get('s3', 'bucket_name'),
                                  region=config.get('s3', 'region'),
                                  aws_access_key_id=config.get('s3', 'aws_access_key_id'),
                                  aws_secret_access_key=config.get('s3', 'aws_secret_access_key'),
                                  analytics=analytics,
                                  compress=compress)

    else:
        raise UnsupportedStorageTypeException("{store} is an unknown backing store type".format(store=storage))
    return controller
