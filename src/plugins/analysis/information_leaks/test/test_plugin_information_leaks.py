from pathlib import Path

from test.common_helper import MockFileObject
from test.unit.analysis.analysis_plugin_test_class import AnalysisPluginTest

from ..code.information_leaks import AnalysisPlugin

TEST_DATA_DIR = Path(__file__).parent / 'data'


class TestAnalysisPluginInformationLeaks(AnalysisPluginTest):
    PLUGIN_NAME = 'information_leaks'

    def setUp(self):
        super().setUp()
        config = self.init_basic_config()
        self.analysis_plugin = AnalysisPlugin(self, config=config)

    def test_find_path(self):
        fo = MockFileObject()
        fo.binary = (TEST_DATA_DIR / 'path_test_file').read_bytes()
        fo.processed_analysis[self.PLUGIN_NAME] = {}
        fo.processed_analysis['file_type'] = {'mime': 'application/x-executable'}
        fo.virtual_file_path = {}
        self.analysis_plugin.process_object(fo)

        assert 'user_paths' in fo.processed_analysis[self.PLUGIN_NAME]

        expected_user_paths = sorted([
            '/home/user/test/urandom',
            '/home/user/test/urandom_sehr_sehr_sehr-lang.txt',
            '/home/user/urandom'
        ])
        assert fo.processed_analysis[self.PLUGIN_NAME]['user_paths'] == expected_user_paths

        assert 'var_path' in fo.processed_analysis[self.PLUGIN_NAME]
        assert fo.processed_analysis[self.PLUGIN_NAME]['var_path'] == ['/var/www/tmp/me_']

        assert 'root_path' in fo.processed_analysis[self.PLUGIN_NAME]
        assert fo.processed_analysis[self.PLUGIN_NAME]['root_path'] == ['/root/user_name/this_directory']

    def test_find_git_repo(self):
        fo = MockFileObject()
        fo.binary = b'test_data'
        fo.processed_analysis[self.PLUGIN_NAME] = {}
        fo.virtual_file_path = {'firmware_uid': ['some_uid|/test/.git/config']}
        self.analysis_plugin.process_object(fo)

        assert fo.processed_analysis[self.PLUGIN_NAME]['git_repo'] == 'test_data'

    def test_find_vscode_settings(self):
        fo = MockFileObject()
        fo.files_included = {(TEST_DATA_DIR / 'path_test_file').read_bytes().decode().split('\n')}
        fo.binary = b'test_data'
        fo.processed_analysis[self.PLUGIN_NAME] = {}
        fo.virtual_file_path = {'firmware_uid': ['some_uid|/home/user/.config/Code/User/settings.json']}
        self.analysis_plugin.process_object(fo)

        assert fo.processed_analysis[self.PLUGIN_NAME]['vscode_settings'] == 'test_data'

    def test_find_artifacts(self):
        fo = MockFileObject()
        fo.processed_analysis['file_type'] = {}
        fo.processed_analysis['file_type']['mime'] = 'text/plain'
        fo.virtual_file_path = {
            1: ['|home|user|project|.git|config',
                '|home|user|some_path|.pytest_cache|some_file',
                '|root|some_directory|some_more|.config|Code|User|settings.json',
                '|some_home|some_user|urandom|42|some_file.uvprojx',
                'home', '', 'h654qf"§$%74672', 'vuwreivh54r234|', '|vr4242fdsg4%%$'
                ]
        }
        fo.processed_analysis[self.PLUGIN_NAME] = {}
        self.analysis_plugin.process_object(fo)

        assert 'summary' in fo.processed_analysis[self.PLUGIN_NAME]
        assert fo.processed_analysis[self.PLUGIN_NAME]['summary'] == ['git_repo', 'git_config_repo', 'pytest_cache_directory',
                                                                        'vscode_settings', 'keil_uvision_config']
