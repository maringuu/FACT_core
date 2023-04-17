import io

import pydantic
import typing

from analysis.plugin import addons, compat
from analysis.plugin import AnalysisPluginV0


class AnalysisPlugin(AnalysisPluginV0, compat.AnalysisBasePluginAdapterMixin):
    class Schema(pydantic.BaseModel):
        matches: typing.List[dict]

    def __init__(self):
        metadata = AnalysisPluginV0.MetaData(
            name='crypto_hints',
            description='find indicators of specific crypto algorithms',
            version='0.1.1',
            Schema=AnalysisPlugin.Schema,
        )
        super().__init__(metadata=metadata)

        self._yara = addons.Yara(plugin=self)

    def summarize(self, result):
        del result
        return []

    def analyze(self, file_handle: io.FileIO, virtual_file_path: str, analyses: dict) -> Schema:
        del virtual_file_path, analyses
        return AnalysisPlugin.Schema(
            matches=[compat.yara_match_to_dict(m) for m in self._yara.match(file_handle)],
        )
