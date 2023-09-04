import datetime
import pathlib
from typing import Optional
from functionCacher.CompressionType import CompressionType


class CacheEntry:
	def __init__(self, file_path: pathlib.Path, timestamp: datetime.datetime,
				 compression_type: CompressionType, hmac: Optional[bytes]):
		"""
		CacheEntry stores metadata for cache entry.

		:param file_path: Stores location of cache on FS
		:param timestamp: Stores last modification time of cache entry
		:param compression_type: Stores compression type
		:param hmac: Optionally stores hmac, if enabled in Cacher
		"""

		self.file_path = file_path
		self.timestamp = timestamp
		self.compression_type = compression_type
		self.hmac = hmac
