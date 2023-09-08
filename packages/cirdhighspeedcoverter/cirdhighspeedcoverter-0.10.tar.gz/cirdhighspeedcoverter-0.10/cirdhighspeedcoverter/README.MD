# High speed conversion of IP addresses represented in CIDR notation into their corresponding start and end IPs, along with their respective subnet masks.

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install cirdhighspeedcoverter


The cidr_to_ip_and_subnet_mask function serves as a versatile tool for converting 
IP addresses represented in CIDR (Classless Inter-Domain Routing) notation into 
their corresponding start and end IPs, along with their respective subnet masks. 
This process is crucial in network management and data analysis tasks. 
By automating this conversion, the function significantly accelerates the handling of 
large datasets containing CIDR notation IP addresses. It accepts various input formats, 
including lists, pandas Series, and DataFrames, enhancing its adaptability. 
Leveraging optimized array operations through NumPy and numexpr, 
the function ensures efficient processing, particularly with extensive datasets. 
This functionality is valuable to network administrators, data scientists, security 
professionals, and developers alike, providing a streamlined approach for tasks 
involving IP address manipulation and analysis. Ultimately, it simplifies the management 
of network configurations and enhances the efficiency of data processing pipelines 
that involve IP address transformations.

## Advantages:

### Automation and Efficiency: 
It automates the process of converting CIDR notation IP addresses to start and 
end IP addresses along with subnet masks. This can save a significant 
amount of time and effort compared to manual conversion.

### Scalability: 
It can handle a large number of CIDR notation IP addresses 
efficiently, making it suitable for processing datasets 
with a large number of IP addresses.

### Flexibility: 
The function can accept input in various formats, including lists, pandas Series, and DataFrames. 
This makes it versatile and adaptable to different data structures.

### Optimized Computation: 
The function leverages NumPy and numexpr for efficient array operations, 
which can lead to improved performance, especially with large datasets.

### Readability and Reusability: 
The function is well-organized and includes meaningful variable names, 
making it easy for others (and the original developer) to understand and reuse the code.



```python

from cirdhighspeedcoverter import cidr_to_ip_and_subnet_mask
df2 = pd.read_csv(
    r"C:\Users\hansc\Downloads\GeoLite2-City-CSV_20230908\GeoLite2-City-CSV_20230908\GeoLite2-City-Blocks-IPv4.csv"
)
print(df2[:10].to_string())
df = cidr_to_ip_and_subnet_mask(df2[:1000].network.to_list())
df = cidr_to_ip_and_subnet_mask(df2[:1000].network)
df = cidr_to_ip_and_subnet_mask(df2[:1000], column="network")
print(df[:10].to_string())


       network  geoname_id  registered_country_geoname_id  represented_country_geoname_id  is_anonymous_proxy  is_satellite_provider postal_code  latitude  longitude  accuracy_radius
0   1.0.0.0/24   2077456.0                      2077456.0                             NaN                   0                      0         NaN  -33.4940   143.2104           1000.0
1   1.0.1.0/24   1814991.0                      1814991.0                             NaN                   0                      0         NaN   34.7732   113.7220           1000.0
2   1.0.2.0/23   1814991.0                      1814991.0                             NaN                   0                      0         NaN   34.7732   113.7220           1000.0
3   1.0.4.0/22   2147714.0                      2077456.0                             NaN                   0                      0        2000  -33.8715   151.2006           1000.0
4   1.0.8.0/21   1814991.0                      1814991.0                             NaN                   0                      0         NaN   34.7732   113.7220           1000.0
5  1.0.16.0/20   1861060.0                      1861060.0                             NaN                   0                      0         NaN   35.6897   139.6895            500.0
6  1.0.32.0/19   1814991.0                      1814991.0                             NaN                   0                      0         NaN   34.7732   113.7220           1000.0
7  1.0.64.0/22   1862415.0                      1861060.0                             NaN                   0                      0    730-0851   34.3927   132.4501              5.0
8  1.0.68.0/23  11818936.0                      1861060.0                             NaN                   0                      0    739-0424   34.2976   132.2898             20.0
9  1.0.70.0/25   1856520.0                      1861060.0                             NaN                   0                      0    730-0011   34.3978   132.4525             10.0
  aa_startip  aa_subnet  aa_startip_int    aa_endip  aa_endip_int    aa_subnetmask
0    1.0.0.0         24        16777216   1.0.0.255      16777471    255.255.255.0
1    1.0.1.0         24        16777472   1.0.1.255      16777727    255.255.255.0
2    1.0.2.0         23        16777728   1.0.3.255      16778239    255.255.254.0
3    1.0.4.0         22        16778240   1.0.7.255      16779263    255.255.252.0
4    1.0.8.0         21        16779264  1.0.15.255      16781311    255.255.248.0
5   1.0.16.0         20        16781312  1.0.31.255      16785407    255.255.240.0
6   1.0.32.0         19        16785408  1.0.63.255      16793599    255.255.224.0
7   1.0.64.0         22        16793600  1.0.67.255      16794623    255.255.252.0
8   1.0.68.0         23        16794624  1.0.69.255      16795135    255.255.254.0
9   1.0.70.0         25        16795136  1.0.70.127      16795263  255.255.255.128


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
```