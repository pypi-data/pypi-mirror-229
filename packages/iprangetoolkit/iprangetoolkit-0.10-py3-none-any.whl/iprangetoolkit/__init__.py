import re
from functools import cache
from typing import Dict, Union, Text, Optional

import numexpr
import numpy as np
import regex
import pandas as pd
import ipaddress

flags = regex.I  # | regex.ASCII | regex.MULTILINE
addcheck = regex.compile(b"[^a-f0-9]", flags=flags)
addchecku = re.compile("[^a-f0-9]", flags=flags)
int_array = np.frompyfunc(int, 2, 1)
# regex based on https://nokia.github.io/pattern-clustering/_modules/pattern_clustering/regexp.html
IPV4ADDR = rb'\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b"'
IPV6SEG = rb"(?:(?:[0-9a-fA-F]){1,4})"
IPV6GROUPS = (
    rb"(?:" + IPV6SEG + rb":){7,7}" + IPV6SEG,  # 1:2:3:4:5:6:7:8
    rb"(?:"
    + IPV6SEG
    + rb":){1,7}:",  # 1::                                 1:2:3:4:5:6:7::
    rb"(?:"
    + IPV6SEG
    + rb":){1,6}:"
    + IPV6SEG,  # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
    rb"(?:"
    + IPV6SEG
    + rb":){1,5}(?::"
    + IPV6SEG
    + rb"){1,2}",  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
    rb"(?:"
    + IPV6SEG
    + rb":){1,4}(?::"
    + IPV6SEG
    + rb"){1,3}",  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
    rb"(?:"
    + IPV6SEG
    + rb":){1,3}(?::"
    + IPV6SEG
    + rb"){1,4}",  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
    rb"(?:"
    + IPV6SEG
    + rb":){1,2}(?::"
    + IPV6SEG
    + rb"){1,5}",  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
    IPV6SEG
    + rb":(?:(?::"
    + IPV6SEG
    + rb"){1,6})",  # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
    rb":(?:(?::"
    + IPV6SEG
    + rb"){1,7}|:)",  # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
    rb"fe80:(?::"
    + IPV6SEG
    + rb"){0,4}%[0-9a-zA-Z]{1,}",  # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
    rb"::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]"
    + IPV4ADDR,  # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    rb"(?:"
    + IPV6SEG
    + rb":){1,4}:[^\s:]"
    + IPV4ADDR,  # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)
IPV6ADDRu = re.compile(
    "|".join(["(?:" + g.decode("utf-8") + ")" for g in IPV6GROUPS[::-1]]), flags=flags
)
data_type = Dict[Text, Union[int, Dict]]


def to_int(x):
    if isinstance(x, int):
        return x
    try:
        return int(x)
    except Exception:
        pass
    try:
        return int(
            "%02x%02x%02x%02x" % tuple([int(y) for y in x.strip().split(".")]), 16
        )
    except Exception:
        return None


@cache
def encode_tmp(bu):
    try:
        return bu.encode("utf-8")
    except Exception:
        if isinstance(bu, int):
            return chr(bu).encode("utf-8")
    return bu


class Trie:
    """Create a Trie for a sequence of strings.

    The Trie can be exported to a Regex pattern, which should match much faster than a
    simple Regex union.

    """

    __slots__ = "data"

    def __init__(self):
        self.data = {}  # type: data_type

    def add(self, word):
        """Add a word to the current Trie."""
        ref = self.data
        for char in word:
            if not char:
                continue
            char = encode_tmp(char)
            ref[char] = ref.get(char, {})
            ref = ref[char]
        ref[b""] = 1

    def dump(self):  # type: (...) -> data_type
        """Dump the current trie as dictionary."""
        return self.data

    def pattern(self):  # type: (...) -> Text
        """Dump the current trie as regex string."""
        return rb"\b" + self._pattern(self.dump()) + rb"\b" or b""

    @classmethod
    def _pattern(cls, data):  # type: (...) -> Optional[Text]
        """Build regex string from Trie."""
        if not data or len(data) == 1 and b"" in data:
            return None

        deeper = []
        current = []
        leaf_reached = False
        for char in sorted(data):
            if data[char] == 1:
                leaf_reached = True
                continue

            recurse = cls._pattern(data[char])
            if recurse is None:
                current.append(re.escape(char))
            else:
                deeper.append(re.escape(char) + recurse)

        final = list(deeper)

        if current:
            if len(current) == 1:
                final.append(current[0])
            else:
                final.append(b"[" + b"".join(current) + b"]")

        if len(final) == 1:
            result = final[0]
        else:
            final.sort()
            result = b"(?:" + b"|".join(final) + b")"

        if leaf_reached:
            if not deeper:
                result += b"?"
            else:
                result = b"(?:" + result + b")?"

        return result


def _getpattern(tt, asbytes=True, compileregex=False):
    pattern = tt.pattern().replace(b"[0123456789]", rb"[\d]")
    pattern = pattern.replace(b"[\\.0123456789]", rb"[\.\d]")
    if not asbytes:
        pattern = pattern.decode("utf-8")
    if compileregex:
        pattern = regex.compile(pattern)
    return pattern


def generate_regex_from_ipv4_range(
    startip,
    endip,
    asbytes=False,
    compileregex=False,
):
    r"""
    Generate a regular expression pattern that matches IPv4 addresses within a specified range.

    Args:
        startip (str): The starting IPv4 address.
        endip (str): The ending IPv4 address.
        asbytes (bool, optional): If True, return the regex pattern as bytes. Default is False.
        compileregex (bool, optional): If True, compile the regex pattern. Default is False.

    Returns:
        Union[str, bytes, regex.Regex]: The generated regex pattern.

    Example:
        >>> generate_regex_from_ipv4_range("192.168.0.0", "192.168.255.255")
        b'\\b192\\.168\\.(?:0\\.[\\d]|1(?:0[\\.\\d]|1[\\.\\d]|2[\\.\\d]|3[\\.\\d]|....'
    """
    tt = Trie()
    for ip in generate_ipv4_range_from_2_ips(startip, endip):
        tt.add(ip)
    return _getpattern(tt, asbytes, compileregex)


def convert_ipv4_ints2string(ip_integers):
    a = np.dstack(
        [
            (
                numexpr.evaluate(
                    "(ip_integers >> 24)",
                    local_dict={"ip_integers": ip_integers},
                    global_dict={},
                ).astype(np.uint32)
                & 0xFF
            ),
            (
                numexpr.evaluate(
                    "(ip_integers >> 16)",
                    local_dict={"ip_integers": ip_integers},
                    global_dict={},
                ).astype(np.uint32)
                & 0xFF
            ),
            (
                numexpr.evaluate(
                    "(ip_integers >> 8)",
                    local_dict={"ip_integers": ip_integers},
                    global_dict={},
                ).astype(np.uint32)
                & 0xFF
            ),
            (
                numexpr.evaluate(
                    "(ip_integers)",
                    local_dict={"ip_integers": ip_integers},
                    global_dict={},
                ).astype(np.uint32)
                & 0xFF
            ),
        ]
    ).astype("S3")
    a2 = np.empty(shape=a[..., 0].shape, dtype="S1")
    a2[:] = b"."
    return np.apply_along_axis(
        lambda r: b"".join(r),
        1,
        np.squeeze(np.dstack([a[..., 0], a2, a[..., 1], a2, a[..., 2], a2, a[..., 3]])),
    ).astype("U15")


def generate_ipv4_range_from_2_ips(start, end):
    r"""
    Generate a range of IPv4 addresses inclusively between two IPv4 addresses.

    Args:
        start (str): The starting IPv4 address.
        end (str): The ending IPv4 address.

    Returns:
        numpy.ndarray: An array containing the generated IPv4 addresses as strings.

    Example:
        >>> generate_ipv4_range_from_2_ips("1.2.4.5", "1.3.5.1")
        array(['1.2.4.5', '1.2.4.6', '1.2.4.7', ..., '1.3.4.2', '1.3.5.0', '1.3.5.1'], dtype='<U15')
    """
    ip_integers = np.arange(to_int(start), (to_int(end)) + 1, dtype=np.int64)
    return convert_ipv4_ints2string(ip_integers)


def get_last_address_of_subnet_mask_ipv6(_ipaddress, strict=False):
    subnet = ipaddress.IPv6Network(_ipaddress, strict=strict)
    last_address = subnet.network_address + subnet.num_addresses - 1
    return str(last_address)


def get_last_address_of_subnet_mask_ipv4(_ipaddress, strict=False):
    subnet = ipaddress.IPv4Network(_ipaddress, strict=strict)
    last_address = subnet.network_address + subnet.num_addresses - 1
    return str(last_address)


def generate_ipv6_range_from_1_ip_with_subnetmask(ipaddress_with_subnetmask):
    r"""
    Generate a range of IPv6 addresses based on a given IPv6 address with a subnet mask.

    Args:
        ipaddress_with_subnetmask (str): The IPv6 address with a subnet mask (e.g., "2001:0db8:1234:5678:9abc:def0:1234:5678/106").

    Returns:
        numpy.ndarray: An array containing the generated IPv6 addresses as strings.

    Example:
        >>> generate_ipv6_range_from_1_ip_with_subnetmask("2001:0db8:1234:5678:9abc:def0:1234:5678/106")
        array(['2001:0db8:1234:5678:9abc:def0:1234:5678',
               '2001:0db8:1234:5678:9abc:def0:1234:5679',
               '2001:0db8:1234:5678:9abc:def0:1234:567a', ...,
               '2001:0db8:1234:5678:9abc:def0:123f:fffc',
               '2001:0db8:1234:5678:9abc:def0:123f:fffd',
               '2001:0db8:1234:5678:9abc:def0:123f:fffe'], dtype='<U39')
    """
    final = get_last_address_of_subnet_mask_ipv6(ipaddress_with_subnetmask)
    return generate_ipv6_range_from_2_ips(
        ipaddress_with_subnetmask.split("/")[0].strip(), final
    )


def generate_ipv4_range_from_1_ip_with_subnetmask(ipaddress_with_subnetmask):
    r"""
    Generate a range of IPv4 addresses based on a given IPv4 address with a subnet mask.

    Args:
        ipaddress_with_subnetmask (str): The IPv4 address with a subnet mask (e.g., "192.168.0.1/24").

    Returns:
        numpy.ndarray: An array containing the generated IPv4 addresses as strings.

    Example:
        >>> generate_ipv4_range_from_1_ip_with_subnetmask("69.30.212.168/29")
        array(['69.30.212.168', '69.30.212.169', '69.30.212.170', '69.30.212.171',
               '69.30.212.172', '69.30.212.173', '69.30.212.174', '69.30.212.175'], dtype='<U15')
    """
    final = get_last_address_of_subnet_mask_ipv4(ipaddress_with_subnetmask)

    return generate_ipv4_range_from_2_ips(
        ipaddress_with_subnetmask.split("/")[0].strip(), final
    )


def generate_ipv6_range_from_2_ips(beginning, final):
    r"""
    Generate a range of IPv6 addresses inclusively between two IPv6 addresses.

    Args:
        beginning (str): The starting IPv6 address.
        final (str): The ending IPv6 address.

    Returns:
        numpy.ndarray: An array containing the generated IPv6 addresses as strings.

    Example:
        >>> generate_ipv6_range_from_2_ips(
        ...     beginning="2001:0db8:0001:0000:0000:0ab9:C0A8:0002",
        ...     final="2001:0db8:0001:0000:0000:0ab9:C0A8:f202",
        ... )
        array(['2001:0db8:0001:0000:0000:0ab9:c0a8:0002',
               '2001:0db8:0001:0000:0000:0ab9:c0a8:0003',
               '2001:0db8:0001:0000:0000:0ab9:c0a8:0004', ...,
               '2001:0db8:0001:0000:0000:0ab9:c0a8:f1ff',
               '2001:0db8:0001:0000:0000:0ab9:c0a8:f200',
               '2001:0db8:0001:0000:0000:0ab9:c0a8:f201'], dtype='<U39')
    """
    df2 = pd.DataFrame([[beginning, final]], columns=["aa_startip", "aa_endip"])
    start, end = "aa_startip", "aa_endip"
    if isinstance(df2, list):
        if not isinstance(df2[0], (list, tuple, np.ndarray)):
            df2 = [df2]
        df2 = pd.DataFrame(df2)
        df2.columns = [start, end]
    df = (
        df2.loc[df2[start].str.match(IPV6ADDRu) & df2[end].str.match(IPV6ADDRu)]
        .rename(columns={start: "aa_startip", end: "aa_endip"})
        .reset_index(drop=True)
        .copy()
    )
    df["aa_startip_cpy"] = df["aa_startip"]
    df["aa_endip_cpy"] = df["aa_endip"]
    for ipaddi in ["aa_startip_cpy", "aa_endip_cpy"]:
        df["missingcol"] = 8 - df[ipaddi].str.count(":")
        df[ipaddi] = df.apply(lambda x: x[ipaddi] + ":" * x["missingcol"], axis=1)
        dfax = df[ipaddi].str.split(":", expand=True, regex=False)
        dfax = dfax.replace("", "0").apply(lambda q: int_array(q, 16))
        arb = dfax.__array__()
        df[f"{ipaddi[:-4]}_int"] = (
            (arb[..., 0] << 112)
            + (arb[..., 1] << 96)
            + (arb[..., 2] << 80)
            + (arb[..., 3] << 64)
            + (arb[..., 4] << 48)
            + (arb[..., 5] << 32)
            + (arb[..., 6] << 16)
            + arb[..., 7]
        )

    ips2 = df.drop(columns=["missingcol", "aa_startip_cpy", "aa_endip_cpy"])
    return (
        pd.Series(range(ips2.aa_startip_int.iloc[0], ips2.aa_endip_int.iloc[0]))
        .apply(
            lambda integer_value: ":".join(
                format((integer_value >> i) & 0xFFFF, "04x")
                for i in range(112, -16, -16)
            )
        )
        .__array__()
        .astype("U39")
    )


def generate_regex_from_individual_ipsv4(iplist, asbytes=False, compileregex=False):
    r"""
    Generate a regular expression pattern that matches a list of individual IPv4 addresses.

    Args:
        iplist (List[str]): A list of IPv4 addresses.
        asbytes (bool, optional): If True, return the regex pattern as bytes. Default is False.
        compileregex (bool, optional): If True, compile the regex pattern. Default is False.

    Returns:
        Union[str, bytes, regex.Regex]: The generated regex pattern.

    Example:
        >>> generate_regex_from_individual_ipsv4(
        ...     iplist=["1.2.3.4", "3.5.3.1", "1.10.12.1",
    """
    ip_integers = np.fromiter((to_int(x) for x in iplist), dtype=np.uint32)

    tt = Trie()
    for ip in convert_ipv4_ints2string(ip_integers):
        tt.add(ip)
    return _getpattern(tt, asbytes, compileregex)


