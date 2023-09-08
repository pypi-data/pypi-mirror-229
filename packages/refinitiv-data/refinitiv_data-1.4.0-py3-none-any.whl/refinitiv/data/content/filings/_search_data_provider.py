from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

import pandas as pd

from ._feed_name import Feed
from ._filing_query import get_query
from ._retrieval_data_provider import DownloadAllFileResponse, DownloadFileError, ListOfFile
from .retrieval import Definition as RetrievalDefinition
from .._content_data import Data
from .._content_data_provider import ContentDataProvider
from .._content_response_factory import ContentResponseFactory
from .._error_parser import ErrorParser
from .._universe_content_validator import UniverseContentValidator
from ..._tools import ParamItem, make_enum_arg_parser
from ...delivery._data._data_provider import (
    RequestFactory,
)

if TYPE_CHECKING:
    from ...delivery._data._data_provider import ParsedData

filings_search_body_params_config = [
    ParamItem("query"),
    ParamItem("variables"),
]

feed_arg_parser = make_enum_arg_parser(Feed)


class FilingsSearchRequestFactory(RequestFactory):
    def get_body_parameters(self, *args, body_params_config=None, **kwargs) -> dict:
        body_params = {}
        if kwargs.get("query"):
            body_params["query"] = kwargs.get("query")
        if kwargs.get("variables"):
            body_params["variables"] = kwargs.get("variables")

        form_type = kwargs.get("form_type")
        feed = kwargs.get("feed")
        if feed:
            feed = feed_arg_parser.get_str(feed)
        org_id = kwargs.get("org_id")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        text = kwargs.get("text")
        sections = kwargs.get("sections")
        limit = kwargs.get("limit")
        sort_order = kwargs.get("sort_order")
        if any(
            (
                form_type,
                feed,
                org_id,
                start_date,
                end_date,
                text,
                sections,
                sort_order,
                limit,
            )
        ):
            body_params["query"] = get_query(
                form_type=form_type,
                feed=feed,
                org_id=org_id,
                start_date=start_date,
                end_date=end_date,
                text=text,
                sections=sections,
                limit=limit,
                sort_order=sort_order,
            )
        return body_params

    @property
    def body_params_config(self):
        return filings_search_body_params_config


class FilingsSearchFile:
    def __init__(
        self,
        title: str = None,
        filename: str = None,
        mimetype: str = None,
        dcn: str = None,
        doc_id: str = None,
        filing_id: int = None,
    ):
        """
        Parameters
        ----------
        title : str
            Document title of the file
        filename : str
            Name of the file
        mimetype : str
            Mime type of the file
        dcn: str
            DCN of the file
        doc_id: str
            Doc ID of the file
        filing_id: int
            Financial Filing ID
        """
        self.filename = filename
        self.title = title
        self.mimetype = mimetype
        self.dcn = dcn
        self.doc_id = doc_id
        self.filing_id = filing_id

    def _download_file(self):
        response = None
        error = False
        if pd.notna(self.filename) and self.filename:
            response = RetrievalDefinition(filename=self.filename).get_data()
        elif pd.notna(self.dcn) and self.dcn:
            response = RetrievalDefinition(dcn=self.dcn).get_data()
        elif pd.notna(self.doc_id) and self.doc_id:
            response = RetrievalDefinition(doc_id=self.doc_id).get_data()
        elif pd.notna(self.filing_id) and self.filing_id:
            response = RetrievalDefinition(filing_id=str(self.filing_id)).get_data()
        else:
            error = True
        return response, error

    def download(self, path: str = None) -> DownloadAllFileResponse:
        """

        Parameters
        ----------
        path : str
            Destination of the download file. Default is current working directory.

        Returns
        -------
        DownloadAllFileResponse
        """
        response, err = self._download_file()
        if err:
            raise DownloadFileError(
                code=None,
                message=f"Cannot download file. Missing one of Filename, DCN, DocID and Filing ID",
            )
        return response.data.files.download(path=path)

    async def download_async(self, path: str = None, callback: Callable = None) -> DownloadAllFileResponse:
        """

        Parameters
        ----------
        path : str
            Destination of the download file. Default is current working directory.
        callback: Callable
            Callback function will be called after the process is completed

        Returns
        -------
        DownloadAllFileResponse
        """
        response, err = self._download_file()
        if err:
            errors = [
                DownloadFileError(
                    code=None,
                    message=f"Cannot download file. Missing one of Filename, DCN, DocID and Filing ID",
                )
            ]
            return DownloadAllFileResponse(files=[self], errors=errors)
        return await response.data.files.download_async(path=path, callback=callback)


@dataclass
class FilingsSearchData(Data):
    _files: ListOfFile = None

    def _get_data_df(self):
        data_df = []
        for row in self.raw["data"].get("FinancialFiling"):
            filing_document = row.get("FilingDocument", {})
            identifiers = filing_document.get("Identifiers", [])
            dcn = ""
            if len(identifiers) > 0:
                dcn = identifiers[0].get("Dcn", "")
            doc_id = filing_document.get("DocId", "")
            financial_filing_id = filing_document.get("FinancialFilingId", "")
            document_title = filing_document.get("DocumentSummary", {}).get("DocumentTitle")
            filenames = []
            if filing_document.get("FilesMetaData"):
                filenames = filing_document.get("FilesMetaData", {})
            if len(filenames) == 0:
                data_df.append(
                    [
                        document_title,
                        None,
                        None,
                        dcn,
                        doc_id,
                        financial_filing_id,
                    ]
                )
            for filename in filenames:
                data_df.append(
                    [
                        document_title,
                        filename.get("FileName"),
                        filename.get("MimeType"),
                        dcn,
                        doc_id,
                        financial_filing_id,
                    ]
                )
        return data_df

    @property
    def df(self):
        if self._dataframe is None and self.raw and "errors" not in self.raw:
            # generate headers for df
            headers = [
                {"title": "DocumentTitle", "type": "string"},
                {"title": "Filename", "type": "string"},
                {"title": "MimeType", "type": "string"},
                {"title": "Dcn", "type": "string"},
                {"title": "DocId", "type": "string"},
                {"title": "FinancialFilingId", "type": "int"},
            ]
            data_df = []
            if self.raw.get("data") is not None:
                data_df = self._get_data_df()
            data_df = {"headers": headers, "data": data_df}
            self._dataframe = self._dfbuilder(data_df, **self._kwargs)
        return self._dataframe

    @property
    def files(self):
        """
        Returns
        -------
        ListOfFile[FilingsSearchFile]
        """
        if self._files is None:
            self._files = ListOfFile()
            if self.df is not None and not self.df.empty:
                self._files.extend(FilingsSearchFile(*row) for row in self.df.values)
        return self._files


class FilingsSearchValidator(UniverseContentValidator):
    @classmethod
    def content_data_has_no_errors(cls, data: "ParsedData") -> bool:
        if data.content_data.get("errors"):
            data.error_codes = None
            data.error_messages = data.content_data["errors"][0].get("message")
            return False

        return True

    def __init__(self) -> None:
        super().__init__()
        self.validators.append(self.content_data_has_no_errors)


filings_search_data_provider = ContentDataProvider(
    request=FilingsSearchRequestFactory(),
    response=ContentResponseFactory(data_class=FilingsSearchData),
    validator=FilingsSearchValidator(),
    parser=ErrorParser(),
)
