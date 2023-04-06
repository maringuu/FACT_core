import io

import pydantic

from helperFunctions.tag import TagColor
from plugins.mime_blacklists import MIME_BLACKLIST_COMPRESSED
from analysis.plugin.compat import AnalysisBasePluginAdapterMixin
from analysis.plugin import AnalysisPluginV0, Tag
from typing import Optional, List, Dict

from ..internal.device_tree_utils import dump_device_trees


class AnalysisPlugin(AnalysisPluginV0, AnalysisBasePluginAdapterMixin):
    class Schema(pydantic.BaseModel):
        class DeviceTree(pydantic.BaseModel):
            header: Optional[dict]
            device_tree: Optional[str]
            model: Optional[str]
            description: Optional[str]
            offset: int

        #: A list of device trees
        device_trees: List[DeviceTree]

    # pylint: disable=abstract-method
    def __init__(self):
        metadata = AnalysisPluginV0.MetaData(
            name='device_tree',
            description='get the device tree in text from the device tree blob',
            version='1.0.1',
            system_version=None,
            dependencies=[],
            mime_blacklist=[*MIME_BLACKLIST_COMPRESSED, 'audio', 'image', 'video'],
            mime_whitelist=[],
            timeout=10,
            Schema=AnalysisPlugin.Schema,
        )
        super().__init__(metadata=metadata)

    def summarize(self, result: Schema):
        models = []
        for device_tree in result.device_trees:
            model = device_tree.model
            if not model:
                continue
            models.append(model)

        if not models:
            return ['unknown-model']

        return models

    def analyze(
        self,
        file_handle: io.FileIO,
        virtual_file_path: dict,
        analyses: Dict[str, dict],
    ) -> Optional[Schema]:
        del virtual_file_path, analyses
        device_trees = dump_device_trees(file_handle.readall())
        if len(device_trees) == 0:
            return None
        return AnalysisPlugin.Schema(device_trees=device_trees)

    def get_tags(self, result, summary):
        del result, summary
        return [
            Tag(
                name=self.metadata.name,
                value='device tree',
                color=TagColor.ORANGE,
            ),
        ]
