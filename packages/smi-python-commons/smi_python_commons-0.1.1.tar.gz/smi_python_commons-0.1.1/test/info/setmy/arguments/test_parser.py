import unittest

from info.setmy.arguments.argument import Argument, smi_profiles_argument
from info.setmy.arguments.config import Config
from info.setmy.arguments.parser import parse_arguments


class TestFoo(unittest.TestCase):

    def test_parse_arguments(self):
        argv = ["example_application_name.py", '-i', 'input.txt', '-o', 'output.txt', '--smi-profiles',
                'profile1,profile2']
        argv_config = Config(
            'Example parser',
            [
                Argument('input', 'i', str, 'Input file', True),
                Argument('output', 'o', str, 'Output file', True),
                smi_profiles_argument
            ])

        parsed = parse_arguments(argv, argv_config)

        self.assertEqual(parsed.input, 'input.txt')
        self.assertEqual(parsed.output, 'output.txt')
        self.assertEqual(parsed.smi_profiles, ['profile1', 'profile2'])


if __name__ == '__main__':
    unittest.main()
