from __future__ import annotations
from geovisio_cli.sequences import external_metadata
from pathlib import Path
from typing import Optional
from geopic_tag_reader import reader


class CsvMetadataHandler(external_metadata.MetadataHandler):
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def new_from_file(file_name: Path) -> Optional[CsvMetadataHandler]:
        if file_name.suffix not in [".csv", "tsv"]:
            return None

        # TODO need to be implemented
        return CsvMetadataHandler()

    def get(self, file_name: Path) -> Optional[reader.PartialGeoPicTags]:
        # TODO need to be implemented
        pass
