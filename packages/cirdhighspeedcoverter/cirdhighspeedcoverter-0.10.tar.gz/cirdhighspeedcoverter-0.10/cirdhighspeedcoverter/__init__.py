import numexpr
import numpy as np
import pandas as pd


def cidr_to_ip_and_subnet_mask(df_series_list, column="network"):

    r"""
    Convert CIDR notation IP addresses to start and end IP addresses along with subnet masks.

    This function takes a list or pandas DataFrame/Series containing CIDR notation IP addresses
    and returns a DataFrame with the following columns:

    - 'aa_startip': The starting IP address in string format.
    - "aa_subnet": The subnet mask in integer format (uint8).
    - 'aa_endip': The ending IP address in string format.
    - 'aa_startip_int': The starting IP address in integer format (uint32).
    - 'aa_endip_int': The ending IP address in integer format (uint32).
    - 'aa_subnetmask': The subnet mask in string format.

    Parameters:
    -----------
    df_series_list : list, pandas.Series, or pandas.DataFrame
        The input data containing CIDR notation IP addresses.
    column : str, optional (default="network")
        The name of the column containing the CIDR notation IP addresses if df_series_list is a DataFrame.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame with the converted IP addresses and subnet masks.

    Examples:
    ---------
    >>> df2 = pd.read_csv("GeoLite2-City-Blocks-IPv4.csv")
    >>> df = cidr_to_ip_and_subnet_mask(df2.network.to_list())

    >>> df = cidr_to_ip_and_subnet_mask(df2.network)

    >>> df = cidr_to_ip_and_subnet_mask(df2, column="network")
    """


    if not isinstance(df_series_list, (pd.DataFrame, pd.Series)):
        df_series_list = pd.Series(df_series_list)
    if isinstance(df_series_list, pd.Series):
        df_series_list = df_series_list.to_frame()
        df_series_list.columns = [column]
    df = df_series_list[column].str.split("/", expand=True)
    df[1] = df[1].astype(np.uint8)
    df.rename(columns={0: "aa_startip", 1: "aa_subnet"}, inplace=True)
    dfs = df["aa_startip"].str.split(".", expand=True).astype(np.uint8)
    dfs["aa_subnet"] = df["aa_subnet"].copy()
    df_series_list = df.copy()
    df = dfs.copy()
    a = np.zeros(dfs.shape, dtype=np.uint8)
    asbits = np.unpackbits(a).reshape((-1, a.shape[1] * 8))
    for i in df.aa_subnet.unique():
        npw = np.where(
            numexpr.evaluate(
                "aa_subnet==i",
                global_dict={},
                local_dict={"i": i, "aa_subnet": df.aa_subnet.__array__()},
            )
        )[0]
        asbits[npw, :i] = 1
    subnetmask = np.packbits(asbits).reshape(a.shape)
    maxip = pd.concat(
        [np.bitwise_or(df[x], ~subnetmask[..., x]) & 0xFF for x in range(4)], axis=1
    )

    return (
        pd.concat(
            [
                df_series_list,
                pd.Series(
                    numexpr.evaluate(
                        "(maxip0 << 24) + (maxip1 << 16) + (maxip2 << 8) + (maxip3)",
                        global_dict={},
                        local_dict={
                            "maxip0": df[0].__array__().astype(np.int64),
                            "maxip1": df[1].__array__().astype(np.int64),
                            "maxip2": df[2].__array__().astype(np.int64),
                            "maxip3": df[3].__array__().astype(np.int64),
                        },
                    )
                ),
                (
                    maxip[0].astype("string")
                    + "."
                    + maxip[1].astype("string")
                    + "."
                    + maxip[2].astype("string")
                    + "."
                    + maxip[3].astype("string")
                ),
                pd.Series(
                    numexpr.evaluate(
                        "(maxip0 << 24) + (maxip1 << 16) + (maxip2 << 8) + (maxip3)",
                        global_dict={},
                        local_dict={
                            "maxip0": maxip[0].__array__().astype(np.int64),
                            "maxip1": maxip[1].__array__().astype(np.int64),
                            "maxip2": maxip[2].__array__().astype(np.int64),
                            "maxip3": maxip[3].__array__().astype(np.int64),
                        },
                    )
                ),
                (
                    pd.Series(subnetmask[..., 0]).astype("string")
                    + "."
                    + pd.Series(subnetmask[..., 1]).astype("string")
                    + "."
                    + pd.Series(subnetmask[..., 2]).astype("string")
                    + "."
                    + pd.Series(subnetmask[..., 3]).astype("string")
                ),
            ],
            axis=1,
            copy=False,
        )
        .rename(
            columns={
                0: "aa_startip_int",
                1: "aa_endip",
                2: "aa_endip_int",
                3: "aa_subnetmask",
            }
        )
        .astype(
            {
                "aa_startip": "string",
                "aa_startip_int": np.uint32,
                "aa_endip_int": np.uint32,
            }
        )
    )


