import pandas as pd
class Loader:
    def __init__(self, filepath):
        self.file_path = filepath
        self.format = self._parse_format()
        self._format_reader_dict = {
            "csv": self._read_csv,
            "parquet": self._read_parquet,
            "xlsx": self._read_xlsx
        }

    def _parse_format(self):
        assert self.file_path is not None and self.file_path.find(".") != -1, "File Path not provided can't parse the format"
        format = self.file_path.split(".")[-1]
        return format

    def _get_reader(self):
        return self._format_reader_dict[self.format]

    def _read_csv(self, **kwargs):
        return pd.read_csv(**kwargs)

    def _read_parquet(self, **kwargs):
        return pd.read_parquet(**kwargs)

    def _read_xlsx(self, **kwargs):
        return pd.read_excel(**kwargs)

    def read_file(self, **kwargs):
        reader = self._get_reader()
        return reader(**kwargs)