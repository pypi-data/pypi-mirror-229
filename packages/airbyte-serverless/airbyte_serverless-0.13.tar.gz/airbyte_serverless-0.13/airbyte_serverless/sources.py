import tempfile
import subprocess
import json
import yaml

from . import airbyte_utils


class AirbyteSourceException(Exception):
    pass


class AirbyteSource:

    def __init__(self, exec, config=None, configured_catalog=None):
        self.exec = exec
        self.config = config
        self.configured_catalog = configured_catalog
        self.temp_dir_obj = tempfile.TemporaryDirectory()  # Used to dump config as files used by airbyte connector
        self.temp_dir = self.temp_dir_obj.name
        self.temp_dir_for_executable = self.temp_dir  # May be different if executable is a docker image where temp dir is mounted elsewhere

    def _run(self, action, state=None):
        command = f'{self.exec} {action}'

        def add_argument(name, value):
            file = open(f'{self.temp_dir}/{name}.json', 'w', encoding='utf-8')
            json.dump(value, file)
            return f' --{name} {self.temp_dir_for_executable}/{name}.json'

        needs_config = (action != 'spec')
        if needs_config:
            assert self.config, 'config attribute is not defined'
            config = yaml.safe_load(self.config)
            command += add_argument('config', config)

        needs_configured_catalog = (action == 'read')
        if needs_configured_catalog:
            command += add_argument('catalog', self.configured_catalog)

        if state:
            command += add_argument('state', self.state)

        print('COMMAND', command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in iter(process.stdout.readline, b""):
            content = line.decode().strip()
            try:
                message = json.loads(content)
            except:
                print('NOT JSON:', content)
                continue
            if message.get('trace', {}).get('error'):
                raise AirbyteSourceException(json.dumps(message['trace']['error']))
            yield message

    def _run_and_return_first_message(self, action):
        messages = self._run(action)
        message = next(
            (message for message in messages if message['type'] not in ['LOG', 'TRACE']),
            None
        )
        assert message is not None, f'No message returned by AirbyteSource with action `{action}`'
        return message

    @property
    def spec(self):
        message = self._run_and_return_first_message('spec')
        return message['spec']

    @property
    def config_spec(self):
        spec = self.spec
        return spec['connectionSpecification']

    @property
    def documentation_url(self):
        spec = self.spec
        return spec['documentationUrl']

    @property
    def config(self):
        if self._config is None:
            spec = self.spec
            self._config = airbyte_utils.generate_connection_yaml_config_sample(spec)
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    @property
    def catalog(self):
        message = self._run_and_return_first_message('discover')
        return message['catalog']

    @property
    def configured_catalog(self):
        if self._configured_catalog is None:
            self._configured_catalog = self.catalog
            self._configured_catalog['streams'] = [
                {
                    "stream": stream,
                    "sync_mode": "incremental" if 'incremental' in stream['supported_sync_modes'] else 'full_refresh',
                    "destination_sync_mode": "append",
                    "cursor_field": stream.get('default_cursor_field', [])
                }
                for stream in self._configured_catalog['streams']
            ]
        return self._configured_catalog

    @configured_catalog.setter
    def configured_catalog(self, configured_catalog):
        self._configured_catalog = configured_catalog

    @property
    def streams(self):
        return [stream['name'] for stream in self.catalog['streams']]

    @property
    def connection_status(self):
        message = self._run_and_return_first_message('check')
        return message['connectionStatus']

    @property
    def first_record(self):
        message = self._run_and_return_first_message('read')
        return message['record']

    def extract(self, state=None):
        return self._run('read', state=state)


class DockerAirbyteSource(AirbyteSource):

    def __init__(self, docker_image, *args, **kwargs):
        super().__init__('', *args, **kwargs)
        self.temp_dir_for_executable = '/mnt/temp'
        self.exec = f'docker run --rm -i --volume {self.temp_dir}:{self.temp_dir_for_executable} {docker_image}'
