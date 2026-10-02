import unittest
from configparser import RawConfigParser

from benedict.serializers import INISerializer


class ini_serializer_test_case(unittest.TestCase):
    def test_decode_default_section(self) -> None:
        for section in ("DEFAULT", "general", "Common Settings"):
            with self.subTest(section=section):
                source = (
                    f"[{section}]\nAttempts = 3\nEnabled = yes\nLabel = café\n"
                    "[service]\nAttempts = 5\nPort = 8080\n"
                )
                self.assertEqual(
                    INISerializer().decode(source, default_section=section),
                    {
                        "Attempts": 3,
                        "Enabled": True,
                        "Label": "café",
                        "service": {
                            "Attempts": 5,
                            "Enabled": True,
                            "Label": "café",
                            "Port": 8080,
                        },
                    },
                )

    def test_encode_default_section(self) -> None:
        data = {"Attempts": 3, "Enabled": True, "service": {"Attempts": 5}}
        for section in ("DEFAULT", "general", "Common Settings"):
            with self.subTest(section=section):
                encoded = INISerializer().encode(data, default_section=section)
                parser = RawConfigParser(default_section=section)
                parser.optionxform = str
                parser.read_string(encoded)
                self.assertEqual(
                    parser.defaults(), {"Attempts": "3", "Enabled": "True"}
                )
                self.assertEqual(parser.sections(), ["service"])
                self.assertEqual(parser.getint("service", "Attempts"), 5)
                self.assertTrue(parser.getboolean("service", "Enabled"))

    def test_custom_default_section_keeps_default_as_regular_section(self) -> None:
        data = {"DEFAULT": {"Attempts": 5}, "Attempts": 3}
        serializer = INISerializer()
        source = "[general]\nAttempts = 3\n[DEFAULT]\nAttempts = 5\n"
        self.assertEqual(serializer.decode(source, default_section="general"), data)
        encoded = serializer.encode(data, default_section="general")
        self.assertEqual(serializer.decode(encoded, default_section="general"), data)
