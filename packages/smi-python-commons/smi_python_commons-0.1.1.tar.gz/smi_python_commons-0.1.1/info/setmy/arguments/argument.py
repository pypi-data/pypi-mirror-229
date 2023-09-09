from info.setmy.string.operations import split_and_trim


class Argument:

    def __init__(self, name: str, short_flag: str, argument_type, argument_help: str, required: bool = False):
        self.name = name
        self.short_flag = short_flag
        self.argument_type = argument_type
        self.argument_help = argument_help
        self.required = required


smi_profiles_argument = Argument('smi-profiles', 'p', split_and_trim, 'Comma separated profiles string.', False)
smi_config_paths = Argument('smi-config-paths', 'c', split_and_trim, 'Comma separated config paths.', False)
