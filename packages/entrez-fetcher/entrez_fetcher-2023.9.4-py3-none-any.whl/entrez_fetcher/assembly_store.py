""" Assembly reference genome downloader.

Download reference genomes from NCBI using assembly accessions. Assembly consists of
a set of sequences (chromosomes, plasmids, organelles, scaffolds, contigs, or
whole-genome shotgun sequences) assembled from a set of reads.

This module aim to downlad the latest version of reference genomes from NCBI. It
uses the assembly summary file available at the NCBI ftp/http mirror to get the proper
url, and download the reference genome that correspond to the
{path_name}/{path_name}_genomic.gbff.gz. The file is then decompressed and stored in
the folder specified by the user.

This module is based on the pooch package, which is a data downloader for Python.

:::{warning}
As all this package, it uses the NCBI servers, which performance are heavily dependent
on the load of the servers. It can be slow, and sometimes, the connection can be
interrupted. Retrying is done automatically, but it is always enough. Relevant error
are raised if the connection is interrupted.

Especially in this module, a large summary file is downloaded, which can take a long
time, depending on the NCBI server load. Try to do this operation at a time where the
servers are not too busy.
:::

Examples
--------

>>> refseq_adl = AssemblyDownloader("/tmp/assembly_genomes", db="refseq")
>>> refseq_adl.download("GCF_001735525.1")
'/tmp/assembly_genomes/GCF_001735525.1.gb'
>>> uids = [
...     "GCF_001735525",
...     "GCF_025402875",
...     "GCF_007197645",
...     "GCF_900111765",
...     "GCF_900109545",
...     "GCF_001027285",
...     "GCF_001189295",
...     "GCF_002343915",
...     "GCF_022870945",
...     "GCF_002222655",
... ]
>>> gb_adl.download_many(uids)
['/tmp/assembly_genomes/GCF_001735525.gb',
 '/tmp/assembly_genomes/GCF_025402875.gb',
 '/tmp/assembly_genomes/GCF_007197645.gb',
 '/tmp/assembly_genomes/GCF_900111765.gb',
 '/tmp/assembly_genomes/GCF_900109545.gb',
 '/tmp/assembly_genomes/GCF_001027285.gb',
 '/tmp/assembly_genomes/GCF_001189295.gb',
 '/tmp/assembly_genomes/GCF_002343915.gb',
 '/tmp/assembly_genomes/GCF_022870945.gb',
 '/tmp/assembly_genomes/GCF_002222655.gb']

An AutoAssemblyDownloader is also available, which will automatically download the
reference genome from the proper database (refseq or genbank) according to the assembly
accession prefix (GCF or GCA). It can also recast the accession to the other database
if the genome is not available in the proper database.
"""

from dataclasses import asdict, dataclass
from functools import cached_property
import os
from pathlib import Path
from typing import Dict, List, Literal, Optional, Protocol, Sequence, Union
from functools import partial
from Bio import SeqIO
from filelock import FileLock
import polars as pl
from polars.exceptions import ColumnNotFoundError
import pooch
from tqdm.contrib.concurrent import thread_map

from entrez_fetcher.entrez_eutils import EntrezFetcher
from entrez_fetcher.models import Taxonomy
from entrez_fetcher.utils import FakeLock, grouper

pooch_logger = pooch.get_logger()
pooch_logger.setLevel("ERROR")


class AssemblyDownloaderProtocol(Protocol):
    @property
    def assembly_summary_url(self):
        ...

    @property
    def assembly_summary_filename(self):
        ...

    @property
    def assembly_summary(self):
        ...

    @property
    def download_paths(self):
        ...

    def download(self, accession: str, progressbar=True):
        ...

    def download_many(self, accessions, max_workers=None):
        ...


@dataclass
class AssemblyDownloader:
    """Download reference genomes from NCBI using assembly accessions.

    Parameters
    ----------
    folder : str
        Folder to store downloaded files.
    db : {"refseq", "genbank"}, default="refseq"
        Database to download from.
    subdir : str, default="bacteria"
        Subdirectory to download from.
    ncbi_ftp_url : str, default="https://ftp.ncbi.nlm.nih.gov"
        NCBI FTP base url.

    Attributes
    ----------
    assembly_summary_url : str
        URL to assembly summary file.
    assembly_summary_filename : str
        Path to assembly summary file.
    assembly_summary : polars.DataFrame
        Assembly summary file as a polars.DataFrame.
    download_paths : polars.DataFrame
        Download paths for reference genomes as a polars.DataFrame.
    """

    folder: str
    db: Literal["refseq", "genbank"] = "refseq"
    subdir: str = "bacteria"
    ncbi_ftp_url: str = "https://ftp.ncbi.nlm.nih.gov"
    sequence_format: Literal["gb", "fasta"] = "gb"

    @property
    def assembly_summary_url(self):
        return (
            f"{self.ncbi_ftp_url}/genomes/{self.db}/{self.subdir}/assembly_summary.txt"
        )

    @property
    def assembly_summary_filename(self):
        return pooch.retrieve(
            url=self.assembly_summary_url,
            path=pooch.os_cache("entrez_fetcher"),
            known_hash=None,
            progressbar=True,
        )

    @cached_property
    def assembly_summary(self):
        unstructed_acc = pl.col("#assembly_accession").str.split(".")
        return pl.read_csv(
            self.assembly_summary_filename,
            separator="\t",
            skip_rows=1,
            null_values=["na"],
            infer_schema_length=None,
        ).with_columns(
            accession=unstructed_acc.list.get(0),
            version=unstructed_acc.list.get(1).cast(int),
        )

    @property
    def download_paths(self):
        basename = pl.col("ftp_path").str.split("/").list.get(-1)
        ext = {"gb": "gbff", "fna": "fna"}[self.sequence_format]
        return (
            self.assembly_summary.filter(
                (pl.col("version_status") == "latest")
                & (
                    pl.col("refseq_category").is_in(
                        ["reference genome", "representative genome"]
                    )
                )
            )
            .select(
                "accession",
                "version",
                basename=basename,
                ftp_path="ftp_path",
            )
            .with_columns(
                url=pl.col("ftp_path") + "/" + basename + f"_genomic.{ext}.gz"
            )
        ).select("accession", "version", "basename", "ftp_path", "url")

    def download(self, accession: str, progressbar=True):
        """Download a reference genome from NCBI.

        Parameters
        ----------
        accession : str
            Assembly accession.
        progressbar : bool, default=True
            Show progress bar.
        """
        row = self.download_paths.filter(pl.col("accession") == accession).to_dicts()[0]
        url = row["url"]
        return pooch.retrieve(
            url=url,
            known_hash=None,
            progressbar=progressbar,
            path=self.folder,
            fname=row["accession"] + f".{self.sequence_format}.gz",
            processor=pooch.Decompress(
                name=row["accession"] + f".{self.sequence_format}"
            ),
        )

    def download_many(self, accessions, max_workers=None):
        """Download multiple reference genomes from NCBI.

        Parameters
        ----------
        accessions : list
            List of assembly accessions.
        max_workers : int, default=None
            Number of threads to use.
        """
        return thread_map(
            partial(self.download, progressbar=False),
            accessions,
            max_workers=max_workers,
            desc="Downloading reference genomes",
        )


@dataclass
class AutoAssemblyDownloader:
    folder: str
    subdir: str = "bacteria"
    ncbi_ftp_url: str = "https://ftp.ncbi.nlm.nih.gov"
    allow_recast_db: bool = False
    sequence_format: Literal["gb", "fasta"] = "gb"

    def __post_init__(self):
        self.refseq_adl = AssemblyDownloader(
            self.folder,
            db="refseq",
            subdir=self.subdir,
            ncbi_ftp_url=self.ncbi_ftp_url,
            sequence_format=self.sequence_format,
        )
        self.gb_adl = AssemblyDownloader(
            self.folder,
            db="genbank",
            subdir=self.subdir,
            ncbi_ftp_url=self.ncbi_ftp_url,
            sequence_format=self.sequence_format,
        )

    def get_origin_db(self, accession: str) -> Literal["refseq", "genbank"]:
        """Get the origin database of an assembly accession.

        Parameters
        ----------
        accession : str
            Assembly accession.

        Returns
        -------
        {"refseq", "genbank"}
            Origin database.
        """
        db_marker, assembly_id = accession.split("_")
        if db_marker == "GCA":
            return "genbank"
        elif db_marker == "GCF":
            return "refseq"
        else:
            raise ValueError(f"Invalid accession {accession}")

    def is_available_in(self, accession: str, db: Literal["refseq", "genbank"]):
        """Check if an assembly is available in a database.

        Parameters
        ----------
        accession : str
            Assembly accession.
        db : {"refseq", "genbank"}
            Database to check.

        Returns
        -------
        bool
            True if available, False otherwise.
        """
        _, assembly_id = accession.split("_")
        if db == "refseq":
            dler = self.refseq_adl
            acc = f"GCF_{assembly_id}"
        elif db == "genbank":
            dler = self.gb_adl
            acc = f"GCA_{assembly_id}"
        else:
            raise ValueError("db must be either 'refseq' or 'genbank'")
        return acc in dler.assembly_summary["accession"].to_list()

    def availability(self, accession: str):
        return {
            "refseq": self.is_available_in(accession, "refseq"),
            "genbank": self.is_available_in(accession, "genbank"),
        }

    def recast_accession(
        self, accession: str, db: Literal["refseq", "genbank"], check=False
    ) -> str:
        """Recast an assembly accession to another database.

        Parameters
        ----------
        accession : str
            Assembly accession.
        db : {"refseq", "genbank"}
            Database to recast to.

        Returns
        -------
        str
            Recasted accession.
        """

        db_marker, assembly_id = accession.split("_")
        if db == "refseq":
            dler = self.refseq_adl
            acc = f"GCF_{assembly_id}"
        elif db == "genbank":
            dler = self.gb_adl
            acc = f"GCA_{assembly_id}"
        else:
            raise ValueError("db must be either 'refseq' or 'genbank'")
        if not check:
            return acc
        if acc in dler.assembly_summary["accession"].to_list():
            return acc
        else:
            raise ValueError(f"Assembly {accession} not available in {db}")

    def recast_if_needed(self, accession: str):
        """Recast an assembly accession to another database if not available in the
        prefered database.

        Parameters
        ----------
        accession : str
            Assembly accession.
        db : {"refseq", "genbank"}
            Database to recast to.

        Returns
        -------
        str
            Recasted accession.
        """
        origin_db = self.get_origin_db(accession)
        fallback_db = "refseq" if origin_db == "genbank" else "genbank"
        if self.is_available_in(accession, self.get_origin_db(accession)):
            return accession
        try:
            return self.recast_accession(accession, fallback_db, check=True)
        except ValueError:
            raise ValueError(
                f"Assembly {accession} not available in {origin_db} or {fallback_db}"
            )

    def download(
        self,
        accession: str,
        progressbar=True,
        recast_in: Optional[Literal["refseq", "genbank"]] = None,
    ):
        """Download a reference genome from NCBI.

        Parameters
        ----------
        accession : str
            Assembly accession.
        progressbar : bool, default=True
            Show progress bar.
        """
        if recast_in is not None:
            accession = self.recast_accession(accession, recast_in, check=False)
        if self.allow_recast_db:
            accession = self.recast_if_needed(accession)
        db_marker = accession.split("_")[0]
        if db_marker == "GCA":
            dler = self.gb_adl
        elif db_marker == "GCF":
            dler = self.refseq_adl

        return dler.download(accession, progressbar=progressbar)

    def download_many(
        self,
        accessions,
        max_workers=None,
        recast_in: Optional[Literal["refseq", "genbank"]] = None,
    ):
        """Download multiple reference genomes from NCBI.

        Parameters
        ----------
        accessions : list
            List of assembly accessions.
        max_workers : int, default=None
            Number of threads to use.
        """
        return thread_map(
            partial(self.download, progressbar=False, recast_in=recast_in),
            accessions,
            max_workers=max_workers,
            desc="Downloading reference genomes",
        )

    @property
    def assembly_summary(self):
        return self.refseq_adl.assembly_summary.vstack(self.gb_adl.assembly_summary)


@dataclass
class AssemblyStore:
    folder: str
    subdir: str = "bacteria"
    ncbi_ftp_url: str = "https://ftp.ncbi.nlm.nih.gov"
    email: Optional[str] = None
    api_key: Optional[str] = None
    allow_recast_db: bool = True
    buffer_size: Optional[int] = None
    sequence_format: Literal["gb", "fasta"] = "gb"
    read_only: bool = False

    def __post_init__(self):
        self.adl = AutoAssemblyDownloader(
            self.folder,
            subdir=self.subdir,
            ncbi_ftp_url=self.ncbi_ftp_url,
            allow_recast_db=self.allow_recast_db,
            sequence_format=self.sequence_format,
        )
        self.fetcher = EntrezFetcher(
            email=self.email,
            api_key=self.api_key,
        )
        self.buffer_size = self.buffer_size or self.fetcher.max_batch_size
        self.folder = Path(self.folder)
        self.folder.mkdir(parents=True, exist_ok=True)
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
        return self.adl.assembly_summary["accession"].to_list()

    @property
    def available_taxonomies(self) -> Sequence[int]:
        try:
            return self.taxonomies["tax_id"].to_list()
        except ColumnNotFoundError:
            return []

    @property
    def docsums(self) -> pl.DataFrame:
        return self.adl.assembly_summary

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
        if self.read_only:
            return
        if isinstance(accession, str):
            accession = [accession]
        accession = [acc.split(".")[0] for acc in accession]
        to_get = set(accession).difference(self.available_sequences.keys())
        with self._lock:
            self.adl.download_many(to_get, max_workers=max_batch_size)

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
        tax_ids = self.get_docsum(accession)["taxid"].to_list()
        to_fetch = set(tax_ids).difference(self.available_taxonomies)
        if self.read_only and to_fetch:
            raise ValueError(
                f"Cannot load taxonomy for {to_fetch} as the store is read-only"
            )
        if to_fetch:
            entry_gen = self.fetcher.get_taxonomy(
                uid=to_fetch, max_batch_size=max_batch_size
            )
            for entries in grouper(self.buffer_size, map(asdict, entry_gen)):
                self.taxonomies = pl.concat([self.taxonomies, pl.DataFrame(entries)])
            for uid in set(to_fetch).difference(self.available_taxonomies):
                self.taxonomies = pl.concat(
                    [self.taxonomies, pl.DataFrame([asdict(Taxonomy(tax_id=uid))])]
                )
        return tax_ids

    def load_docsum(self):
        """Load the docsum for all available genomes.

        :::note
        This method does not allow to specify a list of accession numbers to load as
        all the available genomes are loaded from the assembly summary files.
        :::

        Returns
        -------
        List[str]
            The accession numbers of the loaded genomes.
        """
        df = self.adl.assembly_summary
        return df["accession"].to_list()

    def get_docsum(self, accession: str) -> Union[pl.Series, pl.DataFrame]:
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
        return self.docsums.filter(pl.col("accession").is_in(accession))

    def get_taxonomy(self, accession: str):
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
            print(self.adl.download(accession))
            return self.get_genome_filename(accession, fetch=False)
        else:
            raise KeyError(accession)

    def get_genome_record(self, accession: str, as_iterator=False):
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
        gen = SeqIO.parse(
            self.get_genome_filename(accession),
            format={"fna": "fasta"}.get(self.sequence_format, self.sequence_format),
        )
        if as_iterator:
            return gen
        return list(gen)
