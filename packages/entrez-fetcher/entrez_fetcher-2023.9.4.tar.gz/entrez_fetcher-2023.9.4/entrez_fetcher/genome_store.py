""" A class to store and retrieve genome sequences, summaries and taxonomies from
NCBI given accession numbers. Uses the Entrez API (see
https://www.ncbi.nlm.nih.gov/books/NBK25499/).

The class is thread-safe and process-safe, and uses a file lock to prevent
concurrent access to the same folder.

It uses the nuccore (nucleotide) database, as well as the Assembly downloader (also
available as a standalone class) to download bot nucleotide sequences and assembly
reference genomes.
"""

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from shutil import rmtree
from typing import Callable, Dict, List, Literal, Optional, Sequence, Union

import polars as pl
from appdirs import user_data_dir
from Bio import SeqIO
from filelock import FileLock
from polars.exceptions import ColumnNotFoundError
from pydantic import DirectoryPath

from entrez_fetcher.models import Docsum, Taxonomy
from entrez_fetcher.utils import FakeLock, grouper

from .entrez_eutils import EntrezFetcher

DEFAULT_GENOME_FOLDER = Path(user_data_dir("entrez_fetcher")) / "genomes"
DEFAULT_DB = "nuccore"


def is_assembly(accession):
    return accession.startswith("GCA_") or accession.startswith("GCF_")


@dataclass
class GenomeStore:
    folder: DirectoryPath = DEFAULT_GENOME_FOLDER
    email: Optional[str] = None
    api_key: Optional[str] = None
    progress: Optional[Callable] = None
    buffer_size: Optional[int] = None
    read_only: bool = False
    sequence_format: Literal["fna", "gb"] = "fna"

    """A class to store and retrieve genome sequences, summaries and taxonomies from
    NCBI given accession numbers. Uses the Entrez API (see
    https://www.ncbi.nlm.nih.gov/books/NBK25499/).

    The class is thread-safe and process-safe, and uses a file lock to prevent
    concurrent access to the same folder.

    Parameters
    ----------
    folder : DirectoryPath, optional
        The folder to store the genomes, by default $appdir/entrez_fetcher/genomes
    email : Optional[str], optional
        The email to use for the NCBI API, by default None
    api_key : Optional[str], optional
        The API key to use for the NCBI API, by default None
    progress : Optional[Callable], optional
        A function to use for progress bars. If None, will use tqdm. by default None
    db : DB, optional
        The database to use for the NCBI API, by default "nuccore"
    buffer_size : Optional[int], optional
        The number of sequences to fetch at once. If None, will use the maximum allowed
        by the NCBI API (change if you provide email and api key), by default None
    read_only : bool, optional
        If True, will not write to the folder, by default False. If True, will not
        use the file lock, which will allow concurrent access to the same folder.

    Attributes
    ----------
    available_sequences : Dict[str, Path]
        A dictionary of accession numbers to the path of the corresponding fasta file.
    available_docsums : List[str]
        A list of the accession numbers for which docsums are available.
    available_taxonomies : List[int]
        A list of the taxonomy ids for which taxonomies are available.
    docsums : pl.DataFrame
        A dataframe of the docsums for the available sequences : data lives in a parquet
        file and modifying the dataframe will overwrite the file.
    taxonomies : pl.DataFrame
        A dataframe of the taxonomies for the available sequences : data lives in a
        parquet file and modifying the dataframe will overwrite the file.

    Examples
    --------
    >>> from entrez_fetcher import GenomeStore
    >>> store = GenomeStore()
    >>> store.get_genome_record("NC_000913")
    SeqRecord(seq=Seq('AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAG...TTC'), id='NC_000913.3', name='NC_000913.3', description='...', dbxrefs=[])
    """  # noqa: E501

    def __post_init__(self):
        self.fetcher = EntrezFetcher(
            email=self.email, api_key=self.api_key, progress=self.progress
        )
        self.buffer_size = self.buffer_size or self.fetcher.max_batch_size

        self.folder = Path(self.folder)
        self.folder.mkdir(parents=True, exist_ok=True)

        self.docsum_folder = self.folder / "docsums.pq"
        self.taxonomy_folder = self.folder / "taxonomy.pq"

    @property
    def _lock(self):
        if self.read_only:
            return FakeLock()
        return FileLock(self.folder / ".lock")

    @property
    def available_sequences(self) -> Dict[str, Path]:
        with self._lock:
            fasta_files = self.folder.glob(f"*.{self.sequence_format}")
            return {
                os.path.splitext(fa_file.stem)[0]: fa_file for fa_file in fasta_files
            }

    @property
    def available_docsums(self) -> Sequence[str]:
        try:
            return self.docsums["caption"].to_list()
        except ColumnNotFoundError:
            return []

    @property
    def available_taxonomies(self) -> Sequence[int]:
        try:
            return self.taxonomies["tax_id"].to_list()
        except ColumnNotFoundError:
            return []

    @property
    def docsums(self) -> pl.DataFrame:
        try:
            with self._lock:
                return pl.read_parquet(self.docsum_folder)
        except FileNotFoundError:
            return pl.DataFrame()

    @docsums.setter
    def docsums(self, docsums):
        if self.read_only:
            return
        with self._lock:
            docsums.write_parquet(self.docsum_folder)

    @property
    def taxonomies(self) -> pl.DataFrame:
        try:
            with self._lock:
                return pl.read_parquet(self.taxonomy_folder)
        except FileNotFoundError:
            return pl.DataFrame()

    @taxonomies.setter
    def taxonomies(self, taxonomies):
        if self.read_only:
            return
        with self._lock:
            taxonomies.write_parquet(self.taxonomy_folder)

    def load_sequences(
        self, accession: Union[str, Sequence[str]], max_batch_size=None
    ) -> None:
        """Load the sequences for the given accession numbers.

        Parameters
        ----------
        accessions : Union[str, Sequence[str]]
            The accession numbers to load. Can be a single accession number or a list
            of accession numbers.
        max_batch_size : Optional[int], optional
            The maximum number of sequences to fetch at once. If None, will use the
            maximum allowed by the NCBI API (change if you provide email and api key),
            by default None

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.load_sequences("NC_000913")
        >>> store.load_sequences(["NC_000913", "NC_000964"])
        >>> store.available_sequences.keys()
        dict_keys(['NC_000913', 'NC_000964'])

        """
        if self.read_only:
            return
        if isinstance(accession, str):
            accession = [accession]
        accession = [acc.split(".")[0] for acc in accession]
        to_get = set(accession).difference(self.available_sequences.keys())
        with self._lock:
            self.fetcher.save_seqs_folder(
                self.folder,
                uid=to_get,
                db=DEFAULT_DB,
                max_batch_size=max_batch_size,
                format=self.sequence_format,
            )

    def load_docsums(
        self, accession: Union[str, Sequence[str]], max_batch_size=None
    ) -> List[str]:
        """Load the docsums for the given accession numbers.

        Parameters
        ----------
        accessions : Union[str, Sequence[str]]
            The accession numbers to load. Can be a single accession number or a list
            of accession numbers.
        max_batch_size : Optional[int], optional
            The maximum number of sequences to fetch at once. If None, will use the
            maximum allowed by the NCBI API (change if you provide email and api key),
            by default None

        Returns
        -------
        List[str]
            The accession numbers for which docsums were loaded.

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.load_docsums("NC_000913")
        >>> store.load_docsums(["NC_000913", "NC_000964"])
        >>> store.available_docsums
        ['NC_000913', 'NC_000964']

        """

        if isinstance(accession, str):
            accession = [accession]
        accession = [acc.split(".")[0] for acc in accession]
        to_fetch = set(accession).difference(self.available_docsums)
        if self.read_only and to_fetch:
            raise ValueError(
                f"Cannot load docsums for {to_fetch} as the store is read-only"
            )
        if to_fetch:
            entry_gen = self.fetcher.get_summary(
                uid=to_fetch, db=DEFAULT_DB, max_batch_size=max_batch_size
            )
            for entries in grouper(self.buffer_size, map(asdict, entry_gen)):
                self.docsums = pl.concat([self.docsums, pl.DataFrame(entries)])
            for uid in set(to_fetch).difference(self.available_docsums):
                print(self.docsums)
                print(pl.DataFrame([asdict(Docsum(caption=uid))]))
                self.docsums = pl.concat(
                    [self.docsums, pl.DataFrame([asdict(Docsum(caption=uid))])]
                )
        return accession

    def load_taxonomy(
        self, accession: Union[str, Sequence[str]], max_batch_size=None
    ) -> List[int]:
        """Load the taxonomy for the given accession numbers.

        Parameters
        ----------
        accessions : Union[str, Sequence[str]]
            The accession numbers to load. Can be a single accession number or a list
            of accession numbers.
        max_batch_size : Optional[int], optional
            The maximum number of sequences to fetch at once. If None, will use the
            maximum allowed by the NCBI API (change if you provide email and api key),
            by default None

        Returns
        -------
        List[int]

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.load_taxonomy("NC_000913")
        >>> store.load_taxonomy(["NC_000913", "NC_000964"])
        >>> store.available_taxonomies
        [511145, 224308]

        """
        if isinstance(accession, str):
            accession = [accession]
        accession = [acc.split(".")[0] for acc in accession]
        tax_ids = self.get_docsum(accession, squeeze=False).tax_id
        to_fetch = set(tax_ids).difference(self.available_taxonomies)
        if self.read_only and to_fetch:
            raise ValueError(
                f"Cannot load taxonomy for {to_fetch} as the store is read-only"
            )
        if to_fetch:
            entry_gen = self.fetcher.get_taxonomy(
                uid=to_fetch, max_batch_size=max_batch_size
            )
            for entries in _grouper(self.buffer_size, map(asdict, entry_gen)):
                self.taxonomies = pl.concat([self.taxonomies, pl.DataFrame(entries)])
            for uid in set(to_fetch).difference(self.available_taxonomies):
                self.taxonomies = pl.concat(
                    [self.taxonomies, pl.DataFrame([asdict(Taxonomy(tax_id=uid))])]
                )
        return tax_ids.to_list()

    def get_genome_filename(self, accession: str, fetch: bool = True) -> Path:
        """Get the filename for the genome with the given accession number.

        Parameters
        ----------
        accession : str
            The accession number of the genome to get the filename for.
        fetch : bool, optional
            Whether to fetch the genome if it is not already available, by default True

        Returns
        -------
        Path
            The filename of the genome with the given accession number.

        Raises
        ------
        KeyError
            If the genome is not available and fetch is False.

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.get_genome_filename("NC_000913")
        PosixPath('$HOME/.local/share/entrez_fetcher/genomes/NC_000913.3.fasta')

        """
        if file := self.available_sequences.get(accession, False):
            return file
        if fetch and not self.read_only:
            self.fetcher.save_seqs_folder(
                self.folder, accession, db=DEFAULT_DB, format=self.sequence_format
            )
            return self.get_genome_filename(accession, fetch=False)
        else:
            raise KeyError(accession)

    def get_genome_record(self, accession: str):
        """Get the genome record for the given accession number.

        Parameters
        ----------
        accession : str
            The accession number of the genome to get the filename for.
        fetch : bool, optional
            Whether to fetch the genome if it is not already available, by default True

        Returns
        -------
        SeqRecord
            The genome record for the given accession number.

        Raises
        ------
        KeyError
            If the genome is not available and fetch is False.

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.get_genome_record("NC_000913")
        SeqRecord(seq=Seq('AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAG...TTC'), id='NC_000913.3', name='NC_000913.3', description='...', dbxrefs=[])
        """  # noqa: E501
        return SeqIO.read(
            self.get_genome_filename(accession),
            format={"fna": "fasta"}.get(self.sequence_format, self.sequence_format),
        )

    def get_docsum(
        self, accession: str, squeeze: bool = True
    ) -> Union[pl.Series, pl.DataFrame]:
        """Get the docsum for the given accession number.

        Parameters
        ----------
        accession : str
            The accession number of the genome to get the filename for.
        squeeze : bool, optional
            Whether to squeeze the result to a single row, by default True

        Returns
        -------
        Union[pl.Series, pl.DataFrame]
            The docsum for the given accession number. If squeeze is True and there is
            only one accession number, will return a Series. Otherwise, will return a
            DataFrame.

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.get_docsum("NC_000913")
        ...
        """
        if isinstance(accession, str):
            accession = [accession]
        self.load_docsums(accession)
        return self.docsums.filter(pl.col("caption").is_in(accession))

    def get_taxonomy(self, accession: str, squeeze: bool = True):
        """Get the taxonomy for the given accession number.

        Parameters
        ----------
        accession : str
            The accession number of the genome to get the filename for.
        squeeze : bool, optional
            Whether to squeeze the result to a single row, by default True

        Returns
        -------
        Union[pl.Series, pl.DataFrame]
            The taxonomy for the given accession number. If squeeze is True and there
            is only one accession number, will return a Series. Otherwise, will return
            a DataFrame.

        Examples
        --------
        >>> from entrez_fetcher import GenomeStore
        >>> store = GenomeStore()
        >>> store.get_taxonomy("NC_000913")
        ...
        """
        if isinstance(accession, str):
            accession = [accession]
        tax_ids = self.load_taxonomy(accession)  # noqa: F841
        return self.taxonomies.filter(pl.col("tax_id").is_in(tax_ids))

    def clear(self):
        if self.read_only:
            return
        """Clear the cache."""
        with self._lock:
            rmtree(self.folder)
            self.folder.mkdir(parents=True, exist_ok=True)
            self.docsum_folder.unlink(missing_ok=True)
            self.taxonomy_folder.unlink(missing_ok=True)

    def __getstate__(self):
        state = {**self.__dict__}
        del state["fetcher"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.fetcher = EntrezFetcher(
            email=self.email, api_key=self.api_key, progress=self.progress
        )
