""" NCBI Entrez API client. This module provides a class to fetch sequences and
summaries from the NCBI database. It also provides methods to fetch taxonomy
information from the NCBI taxonomy database as well as doing esearch queries.
"""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from io import BytesIO, StringIO
from itertools import chain
from pathlib import Path
from threading import BoundedSemaphore
from time import sleep
from typing import Generator, Iterable, List, Literal, Optional, Union
from warnings import warn

import uplink as up
from Bio import Entrez, SeqIO
from loguru import logger
from more_itertools import chunked
from pydantic import validate_arguments
from requests import Response

from .models import Docsum, Taxonomy, DB
from .utils import normalize_uids

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

_NCBI_ERR_PATTERN = re.compile(r"^Invalid uid (?P<uid>\w+) at position= \d+$")


def _null_progress(it: Iterable, *args, **kwargs):
    return it


@up.retry(
    stop=up.retry.stop.after_delay(30),
    backoff=up.retry.backoff.jittered(multiplier=2),
)
class EntrezFetcher(up.Consumer):
    """NCBI Entrez API client. This class is a wrapper around the NCBI Entrez API (see
    https://www.ncbi.nlm.nih.gov/books/NBK25499/ for more information). It provides
    methods to fetch sequences and summaries from the NCBI database. It also provides
    methods to fetch taxonomy information from the NCBI taxonomy database as well as
    doing esearch queries.

    A valid email address and API key are not required to use the API, but they are
    required to make more than 3 requests per second. If you do not provide an email
    address and API key, the API will be limited to 3 requests per second. If you do
    provide an email address and API key, the API will be limited to 10 requests per
    second.

    The number of requests per second is internally limited by a semaphore. As the API
    can reject the requests even if the number of requests per second is below the
    limit,  A retry mechanism is implemented to retry the requests that are rejected by
    the API.

    The API is implemented using uplink (see https://uplink.readthedocs.io/en/latest/).

    The methods arguments are validated using pydantic.

    Parameters
    ----------
    base_url : str, optional
        Base URL of the API, by default BASE_URL
    max_batch_size : int, optional
        Maximum number of UIDs to be passed to the API in a single request, by default
        200
    email : str, optional
        Email address to be used for the API requests, by default None
    api_key : str, optional
        API key to be used for the API requests, by default None
    progress : callable, optional
        Progress bar to be used for the API requests, by default None. If None, a
        progress bar will be used if tqdm is installed, otherwise no progress bar will
        be used.
    """

    def __init__(
        self,
        base_url=BASE_URL,
        max_batch_size=200,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        progress=None,
    ):
        if max_batch_size > 200:
            warn(
                "Max batch size should not overcome 200 as the Entrez"
                " docsum parser may fail."
            )
        self.max_batch_size = max_batch_size
        if progress is None:
            try:
                from tqdm.auto import tqdm

                progress = tqdm
            except ImportError:
                progress = _null_progress
        self.progress = progress
        self.request_limit = 3 if email is None or api_key is None else 10
        self.rate_limiter = BoundedSemaphore(self.request_limit)
        super().__init__(base_url=base_url)

    @up.form_url_encoded
    @up.post("efetch")
    def _efetch(
        self,
        db: up.Query(),
        uids: up.Field("id"),
        rettype: up.Query() = None,
        retmode: up.Query() = None,
    ) -> Response:
        pass

    @up.form_url_encoded
    @up.get("esearch")
    def _esearch(
        self,
        db: up.Query(),
        term: up.Query("term"),
        retmax: up.Query() = None,
        retstart: up.Query() = None,
        rettype: up.Query() = "uilist",
    ) -> Response:
        pass

    @up.form_url_encoded
    @up.post("esummary")
    def _esummary(self, db: up.Query(), uids: up.Field("id")) -> Response:
        pass

    def _get_sequence(
        self, uids: List[str], *, db: DB, format: Literal["fna", "gb"] = "fna"
    ) -> Generator[SeqIO.SeqRecord, None, None]:
        resp: Response = self._efetch(
            db=db.value,
            uids=",".join(map(str, uids)),
            rettype={"fna": "fasta", "gb": "gbwithparts"}.get(format, format),
            retmode="text",
        )
        if resp.status_code != 200:
            raise IOError(resp)
        return SeqIO.parse(
            StringIO(resp.content.decode("UTF8")),
            format={"fna": "fasta"}.get(format, format),
        )

    def _get_summary(self, uids: List[str], *, db: DB) -> List[dict]:
        resp = self._esummary(db=db.value, uids=",".join(map(str, uids)))
        if resp.status_code != 200:
            raise IOError(resp)
        return list(Entrez.parse(BytesIO(resp.content), validate=False))

    def _get_taxonomy(self, uids: List[str]) -> List[dict]:
        resp = self._efetch(db="taxonomy", uids=",".join(map(str, uids)), retmode="xml")
        if resp.status_code != 200:
            print(resp.content)
            raise IOError(resp)
        return list(Entrez.parse(BytesIO(resp.content), validate=False))

    def _batch_routine(self, fn, uids, max_batch_size=None, desc=None):
        def to_run(uids, *args, **kwargs):
            try:
                with self.rate_limiter:
                    res = fn(uids, *args, **kwargs)
                    sleep(1.1)
            except RuntimeError as e:
                if match := _NCBI_ERR_PATTERN.match(str(e)):
                    uid = match.group("uid")
                    logger.warning(f"{uid} is not a valid NCBI UID. ({e})")
                    uids.remove(uid)
                    if not uids:
                        return []
                    return to_run(uids, *args, **kwargs)
                else:
                    raise
            return res

        if max_batch_size is None:
            max_batch_size = self.max_batch_size

        chunk_size = min(len(uids) // self.request_limit + 1, max_batch_size)
        uids_chunks = list(chunked(uids, chunk_size))

        with ThreadPoolExecutor() as e:
            fs = [e.submit(to_run, uids_to_run) for uids_to_run in uids_chunks]
            yield from self.progress(
                chain.from_iterable(f.result() for f in as_completed(fs)),
                total=len(uids),
                smoothing=0.05,
                desc=desc,
            )
            return

    @validate_arguments
    def get_sequence(
        self,
        uid: Union[str, Iterable[str]],
        *,
        db: Union[str, DB],
        format: Literal["fna", "gb"] = "fna",
        max_batch_size=None,
    ) -> Generator[SeqIO.SeqRecord, None, None]:
        """Fetch sequences from NCBI Entrez database.

        Parameters
        ----------
        uid : str or iterable of str
            The UID of the sequence to fetch.
        db : str or DB
            The database to fetch the sequence from.
        format : str, optional
            The format of the sequence to fetch. Either "fna" or "gb".
        max_batch_size : int, optional
            The maximum number of sequences to fetch in a single request.
            Default to None, which will use the default value of the class.

        Yields
        ------
        SeqIO.SeqRecord
            The sequence fetched from NCBI Entrez database.
        """

        if isinstance(db, str):
            db = DB[db]
        uids = set(normalize_uids(uid))
        fn = partial(self._get_sequence, db=db, format=format)
        yield from self._batch_routine(
            fn, uids, max_batch_size=max_batch_size, desc="Fetching sequences"
        )

    @validate_arguments
    def get_summary(
        self,
        uid: Union[str, Iterable[str]],
        *,
        db: Union[str, DB],
        max_batch_size=None,
        raw=False,
    ) -> Generator[Docsum, None, None]:
        """Fetch document summaries from NCBI Entrez database.

        Parameters
        ----------
        uid : str or iterable of str
            The UID of the document to fetch.
        db : str or DB
            The database to fetch the document from.
        max_batch_size : int, optional
            The maximum number of documents to fetch in a single request.
            Default to None, which will use the default value of the class.

        Yields
        ------
        Docsum
            The document summary fetched from NCBI Entrez database.
        """

        if isinstance(db, str):
            db = DB[db]
        uids = set(normalize_uids(uid))
        fn = partial(self._get_summary, db=db)
        if not raw:
            yield from map(
                Docsum.from_dict,
                self._batch_routine(
                    fn, uids, max_batch_size=max_batch_size, desc="Fetching docsum"
                ),
            )
        else:
            yield from self._batch_routine(
                fn, uids, max_batch_size=max_batch_size, desc="Fetching docsum"
            )

    @validate_arguments
    def get_taxonomy(
        self, uid: Union[str, Iterable[str]], max_batch_size=None
    ) -> Generator[Taxonomy, None, None]:
        """Fetch taxonomy from NCBI Entrez database.

        Parameters
        ----------
        uid : str or iterable of str
            The UID of the taxonomy to fetch.
        max_batch_size : int, optional
            The maximum number of taxonomies to fetch in a single request.
            Default to None, which will use the default value of the class.

        Yields
        ------
        Taxonomy
            The taxonomy fetched from NCBI Entrez database.
        """

        uids = set(normalize_uids(uid))
        uids.discard(0)
        if not uids:
            return
        fn = partial(self._get_taxonomy)
        yield from map(
            Taxonomy.from_dict,
            self._batch_routine(
                fn, uids, max_batch_size=max_batch_size, desc="Fetching taxonomy"
            ),
        )

    @validate_arguments
    def save_seqs_onefile(
        self,
        filename: Path,
        uid: Union[str, Iterable[str]],
        *,
        db: DB,
        format: Literal["fna", "gb"] = "fna",
        max_batch_size: Optional[int] = None,
    ) -> str:
        """Save sequences to a file.

        Parameters
        ----------
        filename : str or Path
            The filename to save the sequences to.
        uid : str or iterable of str
            The UID of the sequence to fetch.
        db : str or DB
            The database to fetch the sequence from.
        format : str, optional
            The format of the sequence to fetch. Either "fna" or "gb".
        max_batch_size : int, optional
            The maximum number of sequences to fetch in a single request.
            Default to None, which will use the default value of the class.
        """

        seqs = self.get_sequence(
            uid, db=db, format=format, max_batch_size=max_batch_size
        )
        SeqIO.write(seqs, filename, format={"fna": "fasta"}.get(format, format))
        return filename

    @validate_arguments
    def save_seqs_folder(
        self,
        folder_name: Path,
        uid: Union[str, Iterable[str]],
        *,
        db: DB,
        format: Literal["fna", "gb"] = "fna",
        max_batch_size: Optional[int] = None,
    ) -> int:
        """Save sequences to a folder.

        Parameters
        ----------
        folder_name : str or Path
            The folder name to save the sequences to.
        uid : str or iterable of str
            The UID of the sequence to fetch.
        db : str or DB
            The database to fetch the sequence from.
        format : str, optional
            The format of the sequence to fetch. Either "fna" or "gb".
        max_batch_size : int, optional
            The maximum number of sequences to fetch in a single request.
            Default to None, which will use the default value of the class.

        Returns
        -------
        int
            The number of sequences saved to the folder.
        """

        folder_name.mkdir(exist_ok=True)
        seqs = self.get_sequence(
            uid, db=db, format=format, max_batch_size=max_batch_size
        )
        for i, seq in enumerate(seqs):
            filename = folder_name / f"{seq.id}.{format}"
            SeqIO.write(seq, filename, format={"fna": "fasta"}.get(format, format))
        return locals().get("i", 0)

    @validate_arguments
    def search(self, query, db: Union[str, DB], retmax=10000):
        """Search NCBI Entrez database.

        Parameters
        ----------
        query : str
            The query to search for.
        db : str or DB
            The database to search.
        retmax : int, optional
            The maximum number of results to return in a single request.
            Default to 10000.

        Yields
        ------
        str
            The UID of the search result.
        """

        if isinstance(db, str):
            db = DB[db]

        count_search = self._esearch(term=query, rettype="count", db=db.value)
        count = int(Entrez.read(BytesIO(count_search.content))["Count"])

        def search_batch(retstart):
            with self.rate_limiter:
                search = self._esearch(
                    term=query, db=db.value, retmax=retmax, retstart=retstart
                )
                sleep(1.1)
                return Entrez.read(BytesIO(search.content))["IdList"]

        retstarts = range(0, count + 1, retmax)
        with ThreadPoolExecutor() as e:
            fs = [e.submit(search_batch, retstart) for retstart in retstarts]
            yield from self.progress(
                chain.from_iterable(f.result() for f in as_completed(fs)),
                total=count,
                desc=f"Searching {query}",
            )

    def __getstate__(self):
        return {
            key: value for key, value in self.__dict__.items() if key != "rate_limiter"
        }

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.rate_limiter = BoundedSemaphore(self.request_limit)
