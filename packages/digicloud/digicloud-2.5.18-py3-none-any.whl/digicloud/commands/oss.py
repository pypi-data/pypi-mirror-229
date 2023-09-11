"""
    DigiCloud OSS
"""
from marshmallow.exceptions import ValidationError

from .base import Lister, ShowOne, Command
from ..error_handlers import CLIError
from .. import schemas


class ListLocation(Lister):
    """List oss locations"""
    schema = schemas.OSSLocationDetails(many=True)

    def get_data(self, parsed_args):
        locations = self.app.session.get('/oss/locations')
        return locations


class ListBucket(Lister):
    """List oss buckets"""
    schema = schemas.OSSBucketList(many=True)

    def get_data(self, parsed_args):
        buckets = self.app.session.get('/oss/buckets')
        return buckets


class CreateBucket(ShowOne):
    """Create Bucket"""
    schema = schemas.OSSBucketDetails()

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='bucket name'
        )
        parser.add_argument(
            '--location',
            metavar='<location>',
            help='Bucket location',
            type=str.lower,
            required=True,
        )
        parser.add_argument(
            '--storage-class',
            metavar='<storage_class>',
            help='Bucket storage class',
            choices=("standard",),
            type=str.lower,
            default="standard",
        )
        parser.add_argument(
            '--access-type',
            metavar='<access-type>',
            help='Bucket access type',
            choices=("private", "read_only", "public"),
            type=str.lower,
            required=True,
        )
        return parser

    def get_data(self, parsed_args):
        payload = {
            'name': parsed_args.name,
            'location': parsed_args.location,
            'access_type': parsed_args.access_type,
            'storage_class': parsed_args.storage_class,
        }
        bucket = self.app.session.post('/oss/buckets', payload)
        return bucket


class DeleteBucket(Command):
    """Delete bucket."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bucket',
            metavar='<bucket>',
            help='Bucket name or ID',
        )
        return parser

    def take_action(self, parsed_args):
        uri = '/oss/buckets/{}'.format(parsed_args.bucket)
        self.app.session.delete(uri)


class UpdateBucket(ShowOne):
    """Update bucket."""
    schema = schemas.OSSBucketDetails()

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bucket',
            metavar='<bucket>',
            help='Bucket name or ID',
        )
        parser.add_argument(
            '--access-type',
            metavar='<access-type>',
            help='Bucket access type',
            choices=("private", "read_only", "public"),
            type=str.lower,
            required=False,
        )
        parser.add_argument(
            '--referrers',
            metavar='<referrers>',
            help='List of valid FQDNs, to be used for accepting HTTP referers',
            nargs='+',
            required=False,
            default=[],
        )
        parser.add_argument(
            '--cors-sources',
            metavar='<cors_sources>',
            help='List of HTTP origins to be used in '
                 'Access-Control-Allow-Origin HTTP response header.',
            nargs='+',
            required=False,
            default=[],
        )
        parser.add_argument(
            '--cors-allowed-methods',
            metavar='<cors_allowed_methods>',
            help='List of allowed HTTP methods for CORS. valid methods to include are:'
                 'get post put head option delete',
            nargs='+',
            required=False,
            default=[],
        )
        parser.add_argument(
            '--cors-allowed-headers',
            metavar='<cors_allowed_headers>',
            help='List of HTTP headers to be used for '
                 'Access-Control-Allow-Headers preflight response.',
            nargs='+',
            required=False,
            default=[],
        )
        parser.add_argument(
            '--cors-exposed-headers',
            metavar='<cors_exposed_headers>',
            help='List of HTTP headers to be used for '
                 'Access-Control-Expose-Headers response header.',
            nargs='+',
            required=False,
            default=[],
        )
        parser.add_argument(
            '--is-referrers-enabled',
            metavar='<is_referrers_enabled>',
            help='Enable or disable referrer options, true or false respectively',
            type=t_or_f_or_n,
            required=False,
        )
        parser.add_argument(
            '--is-blank-referrer',
            metavar='<is_blank_referrer>',
            help='Indicates that any referrer is allowed for the specified bucket,'
                 ' true or false respectively.',
            type=t_or_f_or_n,
            required=False,
        )
        parser.add_argument(
            '--cors-cache-timeout',
            metavar='<cors_cache_timeout>',
            help='CORS cache timeout.',
            type=int,
            required=False,
        )
        parser.add_argument(
            '--is-cors-enabled',
            metavar='<is_cors_enabled>',
            help='Enable or disable cors options, true or false respectively',
            type=t_or_f_or_n,
            required=False,
        )

        return parser

    def get_data(self, parsed_args):
        uri = '/oss/buckets/{}'.format(parsed_args.bucket)
        payload = {}
        if parsed_args.access_type:
            payload['access_type'] = parsed_args.access_type
        if parsed_args.is_referrers_enabled is not None:
            payload['is_referrers_enabled'] = parsed_args.is_referrers_enabled
        if parsed_args.is_blank_referrer is not None:
            payload['is_blank_referrer'] = parsed_args.is_blank_referrer
        if parsed_args.cors_cache_timeout:
            payload['cors_cache_timeout'] = parsed_args.cors_cache_timeout
        if parsed_args.referrers:
            payload['referrers'] = '\n'.join(parsed_args.referrers)
        if parsed_args.cors_sources:
            payload['cors_sources'] = '\n'.join(parsed_args.cors_sources)
        if parsed_args.cors_allowed_methods:
            payload['cors_allowed_methods'] = parsed_args.cors_allowed_methods
        if parsed_args.cors_allowed_headers:
            payload['cors_allowed_headers'] = '\n'.join(parsed_args.cors_allowed_headers)
        if parsed_args.cors_allowed_headers:
            payload['cors_exposed_headers'] = '\n'.join(parsed_args.cors_exposed_headers)
        if parsed_args.is_cors_enabled is not None:
            payload['is_cors_enabled'] = parsed_args.is_cors_enabled

        if not payload:
            raise CLIError([{'msg': 'At least one attribute should be specified for update'}])

        bucket = self.app.session.patch(uri, payload)
        return bucket


class ShowBucket(ShowOne):
    """Show bucket details."""
    schema = schemas.OSSBucketDetails()

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bucket',
            metavar='<bucket>',
            help='Bucket name or ID',
        )
        return parser

    def get_data(self, parsed_args):
        uri = '/oss/buckets/{}'.format(parsed_args.bucket)
        bucket = self.app.session.get(uri)
        return bucket


class ListAccessKey(Lister):
    """List oss bucket access key"""
    schema = schemas.AccessKeyDetails(many=True)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bucket',
            metavar='<bucket>',
            help='Bucket name or ID',
        )
        return parser

    def get_data(self, parsed_args):
        url = '/oss/buckets/{}/access-keys'.format(parsed_args.bucket)
        access_keys = self.app.session.get(url)
        if access_keys:
            return access_keys[:1]
        else:
            return []


class CreateAccessKey(ShowOne):
    """Create AccessKey"""
    schema = schemas.AccessKeyDetails()

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'bucket',
            metavar='<bucket>',
            help='bucket name or id'
        )
        return parser

    def get_data(self, parsed_args):
        payload = {}
        url = '/oss/buckets/{}/access-keys'.format(parsed_args.bucket)
        access_key = self.app.session.post(url, payload)
        self.app.console.print(
            "[green bold] Attention: \n Please Save Secret Key somewhere safe.[green bold]"
        )
        return access_key


def t_or_f_or_n(arg):
    upper_arg = str(arg).upper()
    if 'TRUE'.startswith(upper_arg):
        return True
    elif 'FALSE'.startswith(upper_arg):
        return False
    else:
        return None
