import hashlib
from typing import Optional, Union, Iterable
import re

import autopep8 # type: ignore
import pandas as pd

__removeCommentsPattern = re.compile(r"(#.*?)(\\n|\n|$)",flags=re.MULTILINE)
def fixSource(source: str, reformat: bool) -> str:
	noComments = re.sub(__removeCommentsPattern, '\n',source, 0)
	if reformat:
		return autopep8.fix_code(noComments)
	return noComments


def hashDf(df: pd.DataFrame) -> str:
	# search for 'O'/object dtype columns
	# if found: remove them from the hashed df-subset, __unless__ they are a string
	# reasoning: object-cols with e.g. list- or set-values cannot be hashed by pd.util.hash_pandas_object
	dtypes = [(idx, val) for idx, val in enumerate(df.dtypes)]
	dtypes = list(filter(lambda tup: tup[1].kind == 'O', dtypes))
	object_cols = set(df.columns[tup[0]] for tup in dtypes)
	final_cols = set(df.columns)
	for col in object_cols:
		if not isinstance(df[col].iloc[0], str):
			final_cols.remove(col)

	return str(pd.util.hash_pandas_object(df[sorted(list(final_cols))]).sum())


def hasher(items: Iterable, exclude_kwargs: Optional[list[str]] = None, exclude_args: Optional[list[int]] = None, **kwargs) -> str:
	if exclude_kwargs is None:
		exclude_kwargs = []
	if exclude_args is None:
		exclude_args = []

	hash_str = ""
	for idx, (key, element) in enumerate(items):
		if key in exclude_kwargs or idx in exclude_args: continue
		if isinstance(element, pd.DataFrame):
			hash_str += hashDf(element)
		else:
			hash_str += str(element)
	return hashlib.sha256(hash_str.encode("utf8")).hexdigest()