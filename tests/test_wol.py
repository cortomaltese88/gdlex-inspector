"""Tests for Wake-on-LAN utilities."""

import unittest

from gdlex_inspector.wol import build_magic_packet, normalize_mac


class TestWol(unittest.TestCase):

    def test_normalize_mac_colons(self):
        result = normalize_mac("aa:bb:cc:dd:ee:ff")
        self.assertEqual(result, "AA:BB:CC:DD:EE:FF")

    def test_normalize_mac_hyphens(self):
        result = normalize_mac("AA-BB-CC-DD-EE-FF")
        self.assertEqual(result, "AA:BB:CC:DD:EE:FF")

    def test_normalize_mac_bare(self):
        result = normalize_mac("aabbccddeeff")
        self.assertEqual(result, "AA:BB:CC:DD:EE:FF")

    def test_normalize_mac_mixed_case(self):
        result = normalize_mac("Aa:Bb:Cc:Dd:Ee:Ff")
        self.assertEqual(result, "AA:BB:CC:DD:EE:FF")

    def test_normalize_mac_invalid_raises(self):
        with self.assertRaises(ValueError):
            normalize_mac("ZZ:ZZ:ZZ:ZZ:ZZ:ZZ")

    def test_normalize_mac_too_short_raises(self):
        with self.assertRaises(ValueError):
            normalize_mac("aa:bb:cc")

    def test_magic_packet_length(self):
        packet = build_magic_packet("AA:BB:CC:DD:EE:FF")
        self.assertEqual(len(packet), 102)  # 6 + 16*6

    def test_magic_packet_starts_with_ff(self):
        packet = build_magic_packet("AA:BB:CC:DD:EE:FF")
        self.assertEqual(packet[:6], b"\xff" * 6)

    def test_magic_packet_contains_mac_16_times(self):
        packet = build_magic_packet("AA:BB:CC:DD:EE:FF")
        mac_bytes = b"\xaa\xbb\xcc\xdd\xee\xff"
        self.assertEqual(packet[6:], mac_bytes * 16)

    def test_magic_packet_invalid_mac(self):
        with self.assertRaises(ValueError):
            build_magic_packet("not-a-mac")


if __name__ == "__main__":
    unittest.main()
