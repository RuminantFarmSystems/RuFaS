This example *user* input system utilizes TOML files to specify input values. TOML files
are *much* easier to read and understand than JSON files, while still offering enormous
flexibility for input types.

In this system, there are system-level defaults ("_defaults.toml") that the program uses as
a fall-back and that an end user should never manipulate or have access to (but default 
values should be clearly documented and accessible).

User-specified values are given in a config file ("user_config.toml") and, **optionally**,
sub-config files. Sub-config files allow users to split their config into multiple files
at their convenience. The "parse_toml_example.py" contains helper functions for combining
the parsed (dict) data from multiple files. 

"parse_toml_example.py" also contains an example setup that uses user-specified values where
available and falls back to the default values otherwise. The example can be found in the 
`if __name == '__main__': ` block of the file.

Note that the `tomli_w.dump()` can be used to write TOML files from dictionaries of program
parameters.
