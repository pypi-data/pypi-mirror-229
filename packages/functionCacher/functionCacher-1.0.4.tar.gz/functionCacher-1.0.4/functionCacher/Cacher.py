import datetime
import functools
import getpass
import hashlib
import hmac
import inspect
import itertools
import logging
import lzma
import os
import pathlib
import pickle
import tempfile
from typing import Union, Callable, Optional, Any, IO

import deprecated
import pyzstd

from .CacheEntry import CacheEntry
from .CompressionType import CompressionType, compression_suffix_map
from .helpers import hasher, fixSource


class Cacher:
    def __init__(self, 
                 cachePath: Optional[Union[pathlib.Path, str]] = None,
                 cacheFolder: str = "caches",
                 shouldCache: bool = True,
                 compressionType: CompressionType = CompressionType.DEFAULT,
                 maxCacheAge: datetime.timedelta = datetime.timedelta(days=1),
                 createCacheFolder: bool = True,
                 deleteOutdatedCacheFile: bool = True,
                 deleteThrowingCacheFile: bool = True, 
                 reformatSourceOnGenerateHash: bool = True,
                 num_workers: int = 1,
                 name: Optional[str] = None,
                 hmac_cache: bool = True,
                 hmac_key: bytes = b"fancy-hmac-key",
                 **kwargs):
        """

        Notes `reformatSourceOnGenerateHash`: Used if `Cacher.get` is invoked with parameter `generate_cache_id` set (default: True). 
        If set, then the Cacher will automatically generate a fitting cache ID. If `hash_source_code` is also set (default: True), then 
        the source code of the cached function is also included in the cache ID; If the source code of the cached function changes between cache attempts,
        then the cache will automatically fail. If `reformatSourceOnGenerateHash` is set (default: True), then the source code is reformatted using autopep8.
        This protects against false cache misses if e.g. a newline was added or removed to the cached source code.

        :param cachePath: Path to cache folder (default: `tempfile.gettempdir() / $USER / cacheFolder`)
        :param cacheFolder: Folder for caches (default: caches)
        :param shouldCache: Whether to activate the cache (default: True)
        :param compressionType: Compression Type (default: DEFAULT == ZSTD)
        :param maxCacheAge: Age threshold (default: 24h)
        :param createCacheFolder: Whether to create cache folder if not exists (default: True)
        :param deleteOutdatedCacheFile: Whether to delete outdated cache file (age(cache) > maxCacheAge) (default: True)
        :param deleteThrowingCacheFile: Whether to delete cache file causing an Exception during read (default: True)
        :param reformatSourceOnGenerateHash: Whether to reformat source code of cached function during cache ID generation (see notes) (default: True)
        :param num_workers: Number of workers for compression library (only respected for CompressionType.ZSTD) (default: 1)
        :param name: Optional cacher name, currently used for logger name (default: None)
        :param hmac_cache: Whether to HMAC the cache file (default: True)
        :param hmac_key: HMAC key (default: b"fancy-hmac-key")
        :param kwargs: key-word arguments, currently used for backwards-compatibility
        """

        self.log = logging.getLogger(name if isinstance(name, str) else __name__)

        if isinstance(cachePath, (pathlib.Path, str)):
            self.cachePath = pathlib.Path(cachePath)
        else:
            # first differentiate by user, then by the cache folder
            self.cachePath = pathlib.Path(tempfile.gettempdir()) / getpass.getuser() / cacheFolder
            self.log.debug(f"No cache path given, will use {self.cachePath}")

        if createCacheFolder and not os.path.isdir(self.cachePath):
            self.log.debug(f"The cache folder at {self.cachePath} does not exist! Will create..")
            self.cachePath.mkdir(parents=True)

        self.log.debug(f"Cache Path set to: {self.cachePath}")

        self.shouldCache = shouldCache
        self.compressionType = compressionType
        self.num_workers = num_workers  # TODO: find something like os.sched_getaffinity that's cross platform (includes windows)
        self.deleteOutdatedCacheFile = deleteOutdatedCacheFile
        self.deleteThrowingCacheFile = deleteThrowingCacheFile
        self.maxCacheAge = maxCacheAge
        self.reformatSourceOnGenerateHash = reformatSourceOnGenerateHash

        self.hmac_cache = hmac_cache
        self.hmac_key = hmac_key
        self._initCaches()

    def _initCaches(self):
        self.caches: dict[str, CacheEntry] = {}
        now = datetime.datetime.now()
        for entry in self.cachePath.iterdir():
            if not entry.is_file():
                self.log.debug(f"Entry {entry} is not a file! Will skip.")
                continue

            file_name = entry.name

            # use st_ctime as timestamp for cache entry
            file_timestamp = datetime.datetime.fromtimestamp(int(entry.stat().st_ctime))
            entry_suffix = entry.suffixes[-1]  # handle multi-suffix file (e.g. .pkl.xz)
            file_cache_id = entry.name[:-len(''.join(entry.suffixes))]

            if entry_suffix not in compression_suffix_map:
                self.log.debug(f"Unknown file ending on {entry.name}! Will skip.")
                continue

            compression_type = compression_suffix_map[entry_suffix]

            if file_cache_id not in self.caches or self.caches[file_cache_id].timestamp < file_timestamp:
                if self.hmac_cache:
                    with open(self.cachePath / file_name, "rb") as infile:
                        digest = hmac.new(self.hmac_key, infile.read(), hashlib.blake2b).digest()
                else:
                    digest = None
                self._updateCache(cacheId=file_cache_id, file_name=file_name, timestamp=file_timestamp,
                                  compression_type=compression_type, hmac=digest)

            if (now - file_timestamp).total_seconds() > self.maxCacheAge.total_seconds() and self.deleteOutdatedCacheFile:
                self.log.debug(f"Found outdated cache {entry}, will delete!")
                if os.path.exists(entry):
                    os.remove(entry)
                del self.caches[file_cache_id]

    def _updateCache(self, cacheId: str, file_name: Union[str, pathlib.Path], timestamp: datetime.datetime,
                     compression_type: CompressionType, hmac):
        self.caches[cacheId] = CacheEntry(file_path=self.cachePath / file_name, timestamp=timestamp,
                                          compression_type=compression_type, hmac=hmac)

    def _getCache(self, cacheId: str) -> Union[CacheEntry, None]:
        if entry := self.caches.get(cacheId):
            current_datetime = datetime.datetime.now()
            cache_timestamp = entry.timestamp
            cacheAge = current_datetime - cache_timestamp
            if cacheAge.total_seconds() <= self.maxCacheAge.total_seconds() or self.maxCacheAge.total_seconds() == 0:  # maxCacheAge == 0 -> disable cache age
                self.log.debug(f"Found cache for cacheId {cacheId}: {self.caches[cacheId]}")
                return entry
            else:
                if self.maxCacheAge.total_seconds() > 0:
                    self.log.debug(f"Found outdated cache ({cache_timestamp})")
                    if self.deleteOutdatedCacheFile:
                        self.log.info(f"Will delete outdated cache ({cache_timestamp})")
                        if os.path.exists(entry.file_path):
                            os.remove(entry.file_path)
                        del self.caches[cacheId]
        return None

    def _generate_hash(self, 
                       args: tuple, 
                       kwargs: dict, 
                       callback, 
                       hash_code: bool = True,
                       exclude_kwargs: Optional[list[str]] = None, 
                       exclude_args: Optional[list[int]] = None,
                       additional_cache_id_data: Optional[str] = None,
                       **ckwargs) -> str:
        """
        Generate hash for given callback(*args, **kwargs)

        Use exclude_{args, kwargs} to remove args from automatic caching which may be unstable,
        such as database connections.

        :param args: args to callback
        :param kwargs: kwargs to callback
        :param callback: callback function, used for generating hash of source code
        :param exclude_kwargs: a list of kwargs to callback to exclude while caching
        :param exclude_args: a list of indices into args to exclude.
        :param additional_cache_id_data: additional data appended to the automatically generated cacheId
        :return: string of cache
        """

        # convert callback name into a hashable string
        callback_name: Union[tuple, list, str] = list(
            filter(lambda x: x[0] == "__name__", inspect.getmembers(callback)))
        if len(callback_name) > 0:  # callback could be a lambda
            callback_name = callback_name[0][1]
        else:  # callback could be a lambda
            callback_name = list(filter(lambda x: x[0] == "__func__", inspect.getmembers(callback)))
            if len(callback_name) == 0:
                callback_name = 'private_callback'
                self.log.warning(f"Could not get name for callback! Will set to cacheId prefix to '{callback_name}'")
            else:
                callback_name = callback_name[0][1].__name__
        if hash_code:
            code = fixSource(inspect.getsource(callback), self.reformatSourceOnGenerateHash)
            code_hashed = hashlib.sha256(code.encode('utf8')).hexdigest()
        else:
            code_hashed = ""
        # hash the function code and both args and kwargs separately & use them as cacheId
        # note: hasher expects a list of 2-tuples (key, value), so pad the args-list with None-"keys"
        hash_args = hasher(list(itertools.product([None], list(args))), exclude_kwargs=exclude_kwargs,
                           exclude_args=exclude_args)
        hash_kwargs = hasher(kwargs.items(), exclude_kwargs=exclude_kwargs, exclude_args=exclude_args)
        hash_additional = hashlib.sha256(
            additional_cache_id_data.encode("utf8")).hexdigest() if additional_cache_id_data else ""
        hash_both = hashlib.sha256((hash_args + hash_kwargs + hash_additional).encode('utf8')).hexdigest()
        cacheId = f"{callback_name}" \
                  f"-{code_hashed}" \
                  f"-{hash_both}"
        return cacheId

    def _writeCache(self, cacheId: str, data):
        """
        Write data directly using the given cacheId
        :param cacheId: cache id for saving cache files (needs to be unique for each cache)
        :param data: data to write to cache file
        :return:
        """
        outfile: Union[IO, pyzstd.ZstdFile] # noqa
        if self.compressionType is CompressionType.ZSTD:
            import pyzstd
            file_name = f"{cacheId}.pkl.zst"
            outfile = pyzstd.open(self.cachePath / file_name, "w",
                                  level_or_option={pyzstd.CParameter.nbWorkers: self.num_workers,  # noqa
                                                   pyzstd.CParameter.compressionLevel: 15,
                                                   pyzstd.CParameter.enableLongDistanceMatching: True})
        elif self.compressionType is CompressionType.LZMA:
            file_name = f"{cacheId}.pkl.xz"
            outfile = lzma.open(self.cachePath / file_name, "w")
        elif self.compressionType is CompressionType.NONE:
            file_name = f"{cacheId}.pkl"
            outfile = open(self.cachePath / file_name, "wb")
        else:
            self.log.error(f"Unhandled compression type {self.compressionType}! Did you forget to handle it?")
            raise NotImplementedError(f"Unhandled compression type {self.compressionType}")

        pickle.dump(data, outfile)
        outfile.close()

        if self.hmac_cache:
            with open(self.cachePath / file_name, "rb") as infile: # explicitly read data _after_ encryption
              digest = hmac.new(self.hmac_key, infile.read(), hashlib.blake2b).digest()
        else:
            digest = None
        self.log.debug(f"Written data with id {cacheId} to location {file_name}")
        self._updateCache(cacheId=cacheId, file_name=file_name, timestamp=datetime.datetime.now(),
                          compression_type=self.compressionType, hmac=digest)

    def _readCache(self, cacheId: str) -> Optional[Any]:
        """
        Attempt to read a cache using cacheId, returns None if attempt fails
        :param cacheId: cache id for reading cache file
        :return: cached data if successful, else None
        """

        cache_entry = self._getCache(cacheId)
        if not cache_entry:
            self.log.debug(f"Did not find cache for {cacheId}")
            return None

        cacheInfile: Union[IO, pyzstd.ZstdFile]
        if cache_entry.compression_type is CompressionType.LZMA:
            cacheInfile = lzma.open(cache_entry.file_path, "r")
        elif cache_entry.compression_type is CompressionType.ZSTD:
            cacheInfile = pyzstd.open(cache_entry.file_path, "r")
        elif cache_entry.compression_type is CompressionType.NONE:
            cacheInfile = open(cache_entry.file_path, "rb")
        else:
            self.log.error(f"Unsupported CacheType: {cache_entry.compression_type}")
            return None

        self.log.debug(f"Reading file with compression type {cache_entry.compression_type.name}")
        try:
            with open(cache_entry.file_path, "rb") as infile: # explicitly read data _before_ possible compression
                file_bytes = infile.read()

            if self.hmac_cache:
                if not isinstance(cache_entry.hmac, bytes):
                    self.log.error(f"HMAC metadata entry for cache {cacheId} is invalid! Will delete")
                    os.remove(cache_entry.file_path)
                    return None

                if not hmac.compare_digest(cache_entry.hmac, hmac.new(self.hmac_key, file_bytes, hashlib.blake2b).digest()):
                    self.log.error(f"HMAC for cache entry at {cache_entry.file_path} did not match! Will delete.")
                    os.remove(cache_entry.file_path)
                    return None

            cache = pickle.load(cacheInfile)  # type: ignore
            
        except (EOFError, lzma.LZMAError, pyzstd.ZstdError, ValueError) as e:
            self.log.error(f"Error while unpickling file {cache_entry.file_path}: {e}")
            if self.deleteThrowingCacheFile:
                self.log.warning(f"Will delete throwing cache")
                if os.path.exists(cache_entry.file_path):
                    os.remove(cache_entry.file_path)
            return None
        finally:
            cacheInfile.close()
        return cache


    def get(self, 
            callback, 
            args: Optional[tuple] = None, 
            kwargs: Optional[dict] = None,
            cacheId: Optional[str] = None,
            generate_cache_id: bool = True,
            cache_response_callback: Optional[Callable] = None,
            exclude_kwargs: Optional[list[str]] = None,
            exclude_args: Optional[list[int]] = None,
            additional_cache_id_data: Optional[str] = None,
            slow_cache_path: bool = False,
            hash_source_code: bool = True,
            **ckwargs):
        """
        Try to get a cached function call result. If successful, return the cache file.
        Otherwise, invoke `callback(*args, **kwargs)`, cache the result, and return the data.

        Either provide a unique `cacheId` used for lookup, or set `generate_cache_id`, which will automatically derive a
        `cacheId` based on the callback and args/kwargs. Use `exclude_{args, kwargs}` to remove unstable arguments from
        automatic caching, such as database connection metadata.

        Note *slow_cache_path*: In some scenarios, the caching (i.e. pickling) process might change the underlying data in subtle ways.
        This is caused by some data structure serialisers/deserialisers acting funnily. In case you encounter this issue,
        set slow_cache_path, which - on cache miss - will execute the `callback(*args, **kwargs)`, cache (i.e. pickle) the result,
        then _load_ that result back from disk, and return this value. This approach, as opposed to the intuitive optimisation of returning
        the callback result immediately, will always return the same type of data, despite any serialisers acting funny.

        :param cacheId: Cache ID for saving cache files (needs to be unique for each cache)
        :param callback: Function to call if cache file does not exist
        :param args: Tuple with non-keyworded arguments to callback
        :param kwargs: Dictionary containing all necessary callback function parameters
        :param generate_cache_id: Whether to generate hash based on function name, arguments, and source code if hash_source_code is set
        :param cache_response_callback: Callback with signature callback(bool), called with True on cache hit, False on cache miss
        :param exclude_kwargs: List of kwargs of `callback` to exclude while caching
        :param exclude_args: List of indices into args of `callback` to exclude
        :param additional_cache_id_data: Additional data considered while generating the automatic cache ID. This could be data not present
        :param slow_cache_path: If set and on cache miss: execute callback, cache results, read cached results, return cached results (see notes)
        :param hash_source_code: Whether to include hash of cached function's source code in cache ID (default: True)
        :param ckwargs: Key-worded args for internal cacher-functionality, currently unused
        :return: Result from callback or cache file
        """

        if not isinstance(ckwargs, dict):
            ckwargs = {}

        if not isinstance(kwargs, dict):
            kwargs = {}

        if not isinstance(args, tuple):
            args = tuple()

        if not self.shouldCache:
            self.log.debug(f"shouldCache is set to false, will call callback directly")
            if callable(cache_response_callback):
                cache_response_callback(False)
            return callback(*args, **kwargs)

        if generate_cache_id:
            if isinstance(cacheId, str):
                self.log.warning(
                    f"generate_cache_id set to true AND cacheId is given! cacheId will be overwritten with generated hash.")
            cacheId = self._generate_hash(args=args, callback=callback, kwargs=kwargs,
                                          exclude_args=exclude_args, exclude_kwargs=exclude_kwargs,
                                          additional_cache_id_data=additional_cache_id_data, hash_code=hash_source_code, **ckwargs)

        if not isinstance(cacheId, str):
            raise TypeError(f"Must provide cacheId or set generate_hash_id")

        cache_entry = self._readCache(cacheId=cacheId)

        if cache_entry is not None:
            if callable(cache_response_callback):
                cache_response_callback(True)
            return cache_entry

        self.log.debug(f"Did not find valid cache for cacheId {cacheId}, using callback..")
        try:
            data = callback(*args, **kwargs)
        except TypeError as te:
            self.log.error(f"Error while calling callback {callback} with arguments {kwargs}: {te}")
            raise

        self._writeCache(cacheId, data)
        if slow_cache_path:
            data = self._readCache(cacheId)

        if callable(cache_response_callback):
            cache_response_callback(False)
        return data

    def cache(self, func=None, **ckwargs):
        """
        Use as decorator for function with `@self.cache`. See `.get` for ckwargs.

        :param func: function to be cached - this is automatically handled by the decorator mechanism. 
        """
        @functools.wraps(func, ckwargs)  # type: ignore
        def wrapper(*args, **kwargs):
            return self.get(callback=func, args=args, kwargs=kwargs, generate_cache_id=True, **ckwargs)

        if func is None:
            return functools.partial(self.cache, **ckwargs)
        return wrapper

    def cacheExists(self, cacheId: str) -> bool:
        """
        Check whether a cache file for `cacheId` exists.

        :param cacheId: ID of cache to check
        :returns: True if exists
        """

        return not isinstance(self._getCache(cacheId=cacheId), type(None))

    def invalidate(self, cacheId: str):
        """
        Invalidate / remove cache for given cacheId
        
        :param cacheId: cache ID to invalidate / remove
        """

        if entry := self.caches.get(cacheId):
            os.remove(entry.file_path)
            del self.caches[cacheId]
