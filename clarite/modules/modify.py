"""
Modify
========

Functions used to filter and/or change some data

  **DataFrame Accessor**: ``clarite_modify``

  **CLI Command**: ``modify``

  .. autosummary::
     :toctree: modules/modify

     colfilter_percent_zero
     colfilter_min_n
     colfilter_min_cat_n
     rowfilter_incomplete_observations
     recode_values
     remove_outliers
     make_binary
     make_categorical
     make_continuous
     merge_variables

"""

from typing import Optional, List

import numpy as np
import pandas as pd

from ..internal.utilities import _validate_skip_only


def colfilter_percent_zero(data: pd.DataFrame, proportion: float = 0.9,
                           skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
    """
    Remove columns which have <proportion> or more values of zero (excluding NA)

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    proportion: float, default 0.9
        If the proportion of rows in the data with a value of zero is greater than or equal to this value, the variable is filtered out.
    skip: list or None, default None
        List of variables that the filter should *not* be applied to
    only: list or None, default None
        List of variables that the filter should *only* be applied to

    Returns
    -------
    data: pd.DataFrame
        The filtered DataFrame

    Examples
    --------
    >>> import clarite
    >>> nhanes_discovery_cont = clarite.modify.colfilter_percent_zero(nhanes_discovery_cont)
    Removed 30 of 369 variables (8.13%) which were equal to zero in at least 90.00% of non-NA observations.
    """
    columns = _validate_skip_only(list(data), skip, only)
    num_before = len(data.columns)

    percent_value = data.apply(lambda col: sum(col == 0) / col.count())
    kept = (percent_value < proportion) | ~data.columns.isin(columns)
    num_removed = num_before - sum(kept)

    print(f"Removed {num_removed:,} of {num_before:,} variables ({num_removed/num_before:.2%}) "
          f"which were equal to zero in at least {proportion:.2%} of non-NA observations.")
    return data.loc[:, kept]


def colfilter_min_n(data: pd.DataFrame, n: int = 200,
                    skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
    """
    Remove columns which have less than <n> unique values (excluding NA)

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    n: int, default 200
        The minimum number of unique values required in order for a variable not to be filtered
    skip: list or None, default None
        List of variables that the filter should *not* be applied to
    only: list or None, default None
        List of variables that the filter should *only* be applied to

    Returns
    -------
    data: pd.DataFrame
        The filtered DataFrame

    Examples
    --------
    >>> import clarite
    >>> nhanes_discovery_bin = clarite.modify.colfilter_min_n(nhanes_discovery_bin)
    Removed 129 of 361 variables (35.73%) which had less than 200 values
    """
    columns = _validate_skip_only(list(data), skip, only)
    num_before = len(data.columns)

    counts = data.count()  # by default axis=0 (rows) so counts number of non-NA rows in each column
    kept = (counts >= n) | ~data.columns.isin(columns)
    num_removed = num_before - sum(kept)

    print(f"Removed {num_removed:,} of {num_before:,} variables ({num_removed/num_before:.2%}) which had less than {n} values")
    return data.loc[:, kept]


def colfilter_min_cat_n(data, n: int = 200, skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
    """
    Remove columns which have less than <n> occurences of each unique value

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    n: int, default 200
        The minimum number of occurences of each unique value required in order for a variable not to be filtered
    skip: list or None, default None
        List of variables that the filter should *not* be applied to
    only: list or None, default None
        List of variables that the filter should *only* be applied to

    Returns
    -------
    data: pd.DataFrame
        The filtered DataFrame

    Examples
    --------
    >>> import clarite
    >>> nhanes_discovery_bin = clarite.modify.colfilter_min_cat_n(nhanes_discovery_bin)
    Removed 159 of 232 variables (68.53%) which had a category with less than 200 values
    """
    columns = _validate_skip_only(list(data), skip, only)
    num_before = len(data.columns)

    min_category_counts = data.apply(lambda col: col.value_counts().min())
    kept = (min_category_counts >= n) | ~data.columns.isin(columns)
    num_removed = num_before - sum(kept)

    print(f"Removed {num_removed:,} of {num_before:,} variables ({num_removed/num_before:.2%}) which had a category with less than {n} values")
    return data.loc[:, kept]


def rowfilter_incomplete_observations(data, skip, only):
    """
    Remove rows containing null values

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    skip: list or None, default None
        List of columns that are not checked for null values
    only: list or None, default None
        List of columns that are the only ones to be checked for null values

    Returns
    -------
    data: pd.DataFrame
        The filtered DataFrame

    Examples
    --------
    >>> import clarite
    >>> nhanes = clarite.modify.rowfilter_incomplete_observations(only=[phenotype] + covariates)
    Removed 3,687 of 22,624 rows (16.30%) due to NA values in the specified columns
    """
    columns = _validate_skip_only(list(data), skip, only)

    keep_IDs = data[columns].isnull().sum(axis=1) == 0  # Number of NA in each row is 0
    n_removed = len(data) - sum(keep_IDs)

    print(f"Removed {n_removed:,} of {len(data):,} rows ({n_removed/len(data):.2%}) due to NA values in the specified columns")
    return data[keep_IDs]


def recode_values(data, replacement_dict,
                  skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
    """
    Convert values in a dataframe.  By default, replacement occurs in all columns but this may be modified with 'skip' or 'only'.
    Pandas has more powerful 'replace' methods for more complicated scenarios.

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    replacement_dict: dictionary
        A dictionary mapping the value being replaced to the value being inserted
    skip: list or None, default None
        List of variables that the replacement should *not* be applied to
    only: list or None, default None
        List of variables that the replacement should *only* be applied to

    Examples
    --------
    >>> import clarite
    >>> clarite.recode_values(df, {7: np.nan, 9: np.nan}, only=['SMQ077', 'DBD100'])
    Replaced 17 values from 22,624 rows in 2 columns
    >>> clarite.recode_values(df, {10: 12}, only=['SMQ077', 'DBD100'])
    No occurences of replaceable values were found, so nothing was replaced.
    """
    # Limit columns if needed
    if skip is not None or only is not None:
        columns = _validate_skip_only(list(data), skip, only)
        replacement_dict = {c: replacement_dict for c in columns}

    # Replace
    result = data.replace(to_replace=replacement_dict, value=None, inplace=False)

    # Log
    diff = result.eq(data)
    diff[pd.isnull(result) == pd.isnull(data)] = True  # NAs are not equal by default
    diff = ~diff  # not True where a value was replaced
    cols_with_changes = (diff.sum() > 0).sum()
    cells_with_changes = diff.sum().sum()
    if cells_with_changes > 0:
        print(f"\tReplaced {cells_with_changes:,} values from {len(data):,} rows in {cols_with_changes:,} columns")
    else:
        print(f"\tNo occurences of replaceable values were found, so nothing was replaced.")

    # Return
    return result


def remove_outliers(data, method: str = 'gaussian', cutoff=3,
                    skip: Optional[List[str]] = None, only: Optional[List[str]] = None):
    """
    Remove outliers from the dataframe by replacing them with np.nan

    Parameters
    ----------
    data: pd.DataFrame
        The DataFrame to be processed and returned
    method: string, 'gaussian' (default) or 'iqr'
        Define outliers using a gaussian approach (standard deviations from the mean) or inter-quartile range
    cutoff: positive numeric, default of 3
        Either the number of standard deviations from the mean (method='gaussian') or the multiple of the IQR (method='iqr')
        Any values equal to or more extreme will be replaced with np.nan
    skip: list or None, default None
        List of variables that the replacement should *not* be applied to
    only: list or None, default None
        List of variables that the replacement should *only* be applied to

    Examples
    --------
    >>> import clarite
    >>> nhanes_rm_outliers = clarite.remove_outliers(nhanes, method='iqr', cutoff=1.5, only=['DR1TVB1', 'URXP07', 'SMQ077'])
    Removing outliers with values < 1st Quartile - (1.5 * IQR) or > 3rd quartile + (1.5 * IQR) in 3 columns
        430 of 22,624 rows of URXP07 were outliers
        730 of 22,624 rows of DR1TVB1 were outliers
        Skipped filtering 'SMQ077' because it is a categorical variable
    >>> nhanes_rm_outliers = clarite.remove_outliers(only=['DR1TVB1', 'URXP07'])
    Removing outliers with values more than 3 standard deviations from the mean in 2 columns
        42 of 22,624 rows of URXP07 were outliers
        301 of 22,624 rows of DR1TVB1 were outliers
    """
    # Copy to avoid replacing in-place
    data = data.copy(deep=True)

    # Which columns
    columns = _validate_skip_only(list(data), skip, only)

    # Check cutoff and method, printing what is being done
    if cutoff <= 0:
        raise ValueError("'cutoff' must be >= 0")
    if method == 'iqr':
        print(f"Removing outliers with values < 1st Quartile - ({cutoff} * IQR) or > 3rd quartile + ({cutoff} * IQR) in {len(columns):,} columns")
    elif method == 'gaussian':
        print(f"Removing outliers with values more than {cutoff} standard deviations from the mean in {len(columns):,} columns")
    else:
        raise ValueError(f"'{method}' is not a supported method for outlier removal - only 'gaussian' and 'iqr'.")

    # Process each column
    for c in columns:
        if str(data.dtypes[c]) == 'category':
            print(f"\tSkipped filtering '{c}' because it is a categorical variable")
            continue
        # Calculate outliers
        if method == 'iqr':
            q1 = data[c].quantile(0.25)
            q3 = data[c].quantile(0.75)
            iqr = abs(q3 - q1)
            bottom = q1 - (iqr * cutoff)
            top = q3 + (iqr * cutoff)
            outliers = (data[c] < bottom) | (data[c] > top)
        elif method == 'gaussian':
            outliers = (data[c]-data[c].mean()).abs() > cutoff*data[c].std()
        # If there are any, log a message and replace them with np.nan
        if sum(outliers) > 0:
            print(f"\t{sum(outliers):,} of {len(data):,} rows of {c} were outliers")
            data.loc[outliers, c] = np.nan

    return data


def make_binary(df: pd.DataFrame):
    """
    Validate and type a dataframe of binary variables

    Checks that each variable has at most 2 values and converts the type to pd.Categorical

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to be processed

    Returns
    -------
    df: pd.DataFrame
        DataFrame with the same data but validated and converted to categorical types

    Examples
    --------
    >>> import clarite
    >>> df = clarite.modify.make_binary(df)
    Processed 32 binary variables with 4,321 observations
    """
    # Validate index
    if isinstance(df.index, pd.core.index.MultiIndex):
        raise ValueError("bin_df: DataFrames passed to the ewas function must not have a multiindex")
    df.index.name = "ID"
    # Check the number of unique values
    unique_values = df.nunique()
    non_binary = unique_values[unique_values != 2]
    if len(non_binary) > 0:
        raise ValueError(f"{len(non_binary)} of {len(unique_values)} variables did not have 2 unique values and couldn't be processed as a binary type")
    # TODO: possibly add further validation to make sure values are 1 and 0
    df = df.astype('category')
    print(f"Processed {len(df.columns):,} binary variables with {len(df):,} observations")
    return df


def make_categorical(df: pd.DataFrame):
    """
    Validate and type a dataframe of categorical variables

    Converts the type to pd.Categorical

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to be processed

    Returns
    -------
    df: pd.DataFrame
        DataFrame with the same data but validated and converted to categorical types

    Examples
    --------
    >>> import clarite
    >>> df = clarite.modify.make_categorical(df)
    Processed 12 categorical variables with 4,321 observations
    """
    # Validate index
    if isinstance(df.index, pd.core.index.MultiIndex):
        raise ValueError("cat_df: DataFrames passed to the ewas function must not have a multiindex")
    df.index.name = "ID"
    # TODO: add further validation
    df = df.astype('category')
    print(f"Processed {len(df.columns):,} categorical variables with {len(df):,} observations")
    return df


def make_continuous(df: pd.DataFrame):
    """
    Validate and type a dataframe of continuous variables

    Converts the type to numeric

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to be processed

    Returns
    -------
    df: pd.DataFrame
        DataFrame with the same data but validated and converted to numeric types

    Examples
    --------
    >>> import clarite
    >>> df = clarite.modify.make_continuous(df)
    Processed 128 continuous variables with 4,321 observations
    """
    # Validate index
    if isinstance(df.index, pd.core.index.MultiIndex):
        raise ValueError("cont_df: DataFrames passed to the ewas function must not have a multiindex")
    df.index.name = "ID"
    # TODO: add further validation
    df = df.apply(pd.to_numeric)
    print(f"Processed {len(df.columns):,} continuous variables with {len(df):,} observations")
    return df


def merge_variables(data: pd.DataFrame, other: pd.DataFrame, how: str = 'outer'):
    """
    Merge a list of dataframes with different variables side-by-side.  Keep all observations ('outer' merge) by default.

    Parameters
    ----------
    data: pd.Dataframe
        "left" DataFrame
    other: pd.DataFrame
        "right" DataFrame which uses the same index
    how: merge method, one of {'left', 'right', 'inner', 'outer'}
        Keep only rows present in the left data, the right data, both datasets, or either dataset.

    Examples
    --------
    >>> import clarite
    >>> df = clarite.modify.merge_variables(df_bin, df_cat, how='outer')
    """
    return data.merge(other, left_index=True, right_index=True, how=how)