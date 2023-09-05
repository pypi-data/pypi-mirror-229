"""This module is used to generate and export descriptive statistics. 

Supported statistic units:
- Author
- Journal
- Keyword
- Institution
- Publication year
- Document type
"""
import os
from typing import Literal, Optional

import pandas as pd


class ComputeMetrics:
    """Compute descriptive statistics of docs.

    Attributes:
        merged_docs_df: DataFrame of docs merged with citation relationship.
        source_type: Source type of docs, `wos`, `cssci` or `scopus`.

    """

    def __init__(
        self,
        docs_df: pd.DataFrame,
        citation_relationship: pd.DataFrame,
        source_type: Literal["wos", "cssci", "scopus"],
    ):
        """
        Args:
            docs_df: DataFrame of docs.
            citation_relationship: DataFrame of citation relationship.
            source_type: Source type of docs, `wos`, `cssci` or `scopus`.
        """
        self.merged_docs_df: pd.DataFrame = docs_df.merge(
            citation_relationship[["doc_index", "LCR", "LCS"]], on="doc_index"
        )
        self.source_type: Literal["wos", "cssci", "scopus"] = source_type

    @staticmethod
    def generate_df_factory(
        merged_docs_df: pd.DataFrame,
        use_cols: list[str],
        col: str,
        split_char: Optional[str] = None,
        str_lower: bool = False,
        sort_by_col: Literal["Recs", "TLCS", "TGCS"] = "Recs",
    ) -> pd.DataFrame:
        """A factory method to generate DataFrame of specific field.
        You can analyze any field besides the provided functions through this method.

        Args:
            merged_docs_df: DataFrame of docs merged with citation relationship.
            use_cols: Columns to use, e.g. `["AU", "LCS", "TC"]`.
            col: Column to analyze, e.g. `AU`.
            split_char: Whether to split string, e.g. `; `. Defaults to `None`.
            str_lower: Whether to convert string to lowercase. Defaults to `False`.
            sort_by_col: Sort DataFrame by column, `Recs`, `TLCS` or `TGCS`. Defaults to `Recs`.

        Returns:
            DataFrame of specific field.
        """
        assert col in use_cols, "Argument <col> must be in use_cols"
        if sort_by_col == "TLCS":
            assert "LCS" in use_cols, "LCS must be in <use_cols> when sorting by TLCS"
        elif sort_by_col == "TGCS":
            assert "TC" in use_cols, "TC must be in <use_cols> when sorting by TGCS"

        df = merged_docs_df[use_cols]
        if split_char:
            df = df.dropna(subset=[col])
            df = df.astype({col: "str"})
            if str_lower:
                df[col] = df[col].str.lower()
            df[col] = df[col].str.split(split_char)
            df = df.explode(col)
            df = df.reset_index(drop=True)

        if "LCS" in use_cols:
            if "TC" in use_cols:
                grouped_df = df.groupby(col).agg(
                    {col: "count", "LCS": "sum", "TC": "sum"}
                )
            else:
                grouped_df = df.groupby(col).agg({col: "count", "LCS": "sum"})
        else:
            grouped_df = df.groupby(col).agg({col: "count"})

        grouped_df.rename(
            columns={col: "Recs", "LCS": "TLCS", "TC": "TGCS"}, inplace=True
        )
        # e.g. Andersson, Gerhard (7202645907)
        if col == "Author full names":
            grouped_df.index = grouped_df.index.str.replace(r" \(\d+\)", "", regex=True)

        if not sort_by_col:
            sort_by_col = "Recs"
        return grouped_df.sort_values(sort_by_col, ascending=False)

    def generate_records_df(self) -> pd.DataFrame:
        """Return records DataFrame. Similar to `merged_docs_df`."""
        if self.source_type in ["wos", "scopus"]:
            use_cols = [
                "AU",
                "TI",
                "SO",
                "PY",
                "TI",
                "LCS",
                "TC",
                "LCR",
                "NR",
                "source file",
            ]
        elif self.source_type == "cssci":
            use_cols = ["AU", "TI", "SO", "PY", "LCS", "LCR", "NR", "source file"]
        else:
            raise ValueError("Invalid source type")
        records_df = self.merged_docs_df[use_cols]
        if "TC" in use_cols:
            records_df = records_df.rename(columns={"TC": "GCS"})
        if "NR" in use_cols:
            records_df = records_df.rename(columns={"NR": "GCR"})
        return records_df

    def generate_author_df(self) -> pd.DataFrame:
        """Return author DataFrame."""
        if self.source_type == "wos":
            use_cols = ["AU", "LCS", "TC"]
        elif self.source_type == "cssci":
            use_cols = ["AU", "LCS"]
        elif self.source_type == "scopus":
            use_cols = ["Author full names", "LCS", "TC"]
        else:
            raise ValueError("Invalid source type")
        return self.generate_df_factory(
            self.merged_docs_df, use_cols, use_cols[0], "; "
        )

    def generate_keyword_df(self) -> pd.DataFrame:
        """Return keyword DataFrame."""
        if self.source_type in ["wos", "scopus"]:
            use_cols = ["DE", "LCS", "TC"]
        elif self.source_type == "cssci":
            use_cols = ["DE", "LCS"]
        else:
            raise ValueError("Invalid source type")
        return self.generate_df_factory(self.merged_docs_df, use_cols, "DE", "; ", True)

    def generate_institution_df(self) -> pd.DataFrame:
        """Return institution DataFrame. Not support Scopus."""
        assert (
            self.source_type != "scopus"
        ), "Scopus is not supported to analyze <institution> field yet."
        if self.source_type == "wos":
            use_cols = ["C3", "LCS", "TC"]
        elif self.source_type == "cssci":
            use_cols = ["C3", "LCS"]
        else:
            raise ValueError("Invalid source type")
        return self.generate_df_factory(self.merged_docs_df, use_cols, "C3", "; ")

    def generate_journal_df(self) -> pd.DataFrame:
        """Return journal DataFrame."""
        if self.source_type in ["wos", "scopus"]:
            use_cols = ["SO", "LCS", "TC"]
        elif self.source_type == "cssci":
            use_cols = ["SO", "LCS"]
        else:
            raise ValueError("Invalid source type")
        return self.generate_df_factory(self.merged_docs_df, use_cols, "SO")

    def generate_year_df(self) -> pd.DataFrame:
        """Return publication year DataFrame. Sort by `PY` ascending."""
        use_cols = ["PY"]
        return self.generate_df_factory(
            self.merged_docs_df, use_cols, "PY"
        ).sort_values(by="PY")

    def generate_document_type_df(self) -> pd.DataFrame:
        """Return document type DataFrame. Not support CSSCI."""
        assert self.source_type != "cssci", "CSSCI doesn't have <document type> info"
        use_cols = ["DT"]
        return self.generate_df_factory(self.merged_docs_df, use_cols, "DT")

    # def generate_reference_df(self):
    #     """Generate reference DataFrame. The `local` field means whether the reference is in the downloaded docs."""
    #     assert self.refs_df is not None, "Argument <refs_df> can't be None"
    #     if self.source_type == "wos":
    #         keys = ["FAU", "PY", "J9", "VL", "BP", "DI", "local"]
    #     elif self.source_type == "cssci":
    #         keys = ["FAU", "TI", "SO", "PY", "VL", "local"]
    #     elif self.source_type == "scopus":
    #         keys = ["FAU", "TI", "SO", "VL", "BP", "EP", "PY", "local"]
    #     else:
    #         raise ValueError("Invalid source type")
    #     refs_df = (
    #         self.refs_df.groupby(by=keys, dropna=False).size().reset_index(name="Recs")
    #     )
    #     refs_df.insert(len(refs_df.columns) - 1, "local", refs_df.pop("local"))
    #     return refs_df.sort_values(by="Recs", ascending=False)

    def write2excel(self, save_path: str):
        """Write all dataframes to an excel file. Each dataframe is a sheet.

        Args:
            save_path: The path to save the excel file.

        Returns:
            An excel file with multiple sheets.
        """
        save_folder_path = os.path.dirname(save_path)
        os.makedirs(save_folder_path, exist_ok=True)
        with pd.ExcelWriter(save_path) as writer:
            self.generate_records_df().to_excel(
                writer, sheet_name="Records", index=False
            )
            self.generate_author_df().to_excel(writer, sheet_name="Authors")
            self.generate_journal_df().to_excel(writer, sheet_name="Journals")
            self.generate_keyword_df().to_excel(writer, sheet_name="Keywords")
            self.generate_year_df().to_excel(writer, sheet_name="Years")

            if self.source_type in ["wos", "cssci"]:
                self.generate_institution_df().to_excel(
                    writer, sheet_name="Institutions"
                )
            if self.source_type in ["wos", "scopus"]:
                self.generate_document_type_df().to_excel(
                    writer, sheet_name="Document Type"
                )
