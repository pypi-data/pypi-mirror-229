import enum


class CompressionType(enum.Enum):
	"""
	CompressionType stores the currently used cache file compression algorithm.
	"""

	NONE = 1
	LZMA = 2
	ZSTD = 3
	DEFAULT = 3 # default: ZSTD


compression_suffix_map = {
	".xz": CompressionType.LZMA,
	".zst": CompressionType.ZSTD,
	".pkl": CompressionType.NONE
}
