"""Support FileFetch Class.

Verifies input to FileFetch is valid. Provides help and error messages to user
if any input is missing or invalid.

Classes:
    :class:`FileFetch.FileFetch` - Save data from a given url in a pd.DataFrame or csv

    :class:`_help.Helper` - Print user help information for FileFetch

    :class:`_initialize.InitializeCheck` - Validate user input to FileFetch

    :class:`_validate.ValidateCheck` - Validate data sources before save to DataFrame
"""


# import other homegrown modules
from utilsx.readin import read_yaml


def allowed_files(allowed):
    """Print a list of allowed file types.

    If user does not provide valid input, prints a message to
    the screen letting user know what options are available.

    Parameters
    ------------
    allowed : list
        Available file retrieval options.

    Returns
    --------
    None
        Prints message to screen

    See Also
    ---------
    :ref:`file_list <ff-attribute-label>`
    """
    file_list = allowed

    print("\nCurrently allowed file types for download:")
    for ftype in file_list:
        print(f"\t- {ftype}")


class InitializeCheck:
    """Mixin class used by :ref:`FileFetch() <FileFetch-label>` to validate user input.

    See Also
    --------
    :class:`FileFetch.FileFetch`: Class for fetching files.
    :class:`_help.Helper`: Mixin class to provide help information on FileFetch.
    :class:`_validate.ValidateCheck`: Mixin class to validate data sources before save to DataFrame.
    """

    def init_check(self, params, params_file):
        """Validate input and initialize FileFetch instance.

        Verifies user input is valid. If anything is missing or invalid, provides
        warning message and directions to user. If all is good, a new instance
        is initialized.

        Parameters
        -----------
        params : dict, optional
            Gives url, file_type, and optional key_phrase.
        params_file : list, optional
            Provides location of input yaml and a keyword header in the yaml.
            The yaml contains same information as the params dict.


        .. warning:: Use either `params` or `parms_file`. Using both throws an error.

        .. tip:: Option using `params_file` is preferred.


        Returns
        --------
        None
            Created a new instance.

        Examples
        ---------
        Define either params or params_file (see sample :ref:`params_file yaml <ff-note-label1>` format):

        .. code-block:: text

            my_params = {
                 "url": "http//www.my.website.com",
                 "file_type": "html-stream",
                 "key_phrase": data:application/octet-stream;charset=utf-8,
                 }

            yaml_file = ["./my_params.yml", "keyword_header"]

        Then initialize using:

        .. code-block:: python

            > file = FileFetch(params=my_params)
            > file = FileFetch(params_file=yaml_file)
        """

        if params == None and params_file == None:
            print("\nError: You did not supply any inputs.")
            print(
                """\nOptions: Supply a dictionary with inputs
            OR
        a list provding a path to your yaml file and data source header"""
            )
            print(
                "\t- dictionary format: {'url':'your url', 'file_type':'download file type', 'key_phrase':'html-stream key word'}"
            )
            print(
                "\t\t set key_phrase to None unless your file_type = html-stream"
            )
            print(
                """\t- yaml format: if using yaml file input instead of the dictionary option,
                \tsee sample yaml for structure. data source header should match header line in your yaml."""
            )
            allowed_files(
                self.file_list
            )  # print a list of allowed file types for user
            print("Exiting...")
            exit()
        elif params and params_file:
            print(
                "\nError: You supplied input parameters AND an input file"
            )
            print("\tOnly one should be supplied")
            print("Exiting....")
            exit()
        elif params:
            try:
                self.url = params["url"]
                self.file_type = params["file_type"]
                self.desc = None
                self.webref = None
                if params["key_phrase"]:
                    if isinstance(params["key_phrase"], dict):
                        if (params["key_phrase"].get("tag")) and\
                           (params["key_phrase"].get("search")) and\
                           (params["key_phrase"].get("nested")):
                            self.key_phrase = None
                            self.tag = params["key_phrase"].get("tag")
                            self.search = params["key_phrase"].get("search")
                            if params["key_phrase"].get("nested") == 'yes':
                                self.tag2 = True
                            else:
                                self.tag2 = False
                            self.file_ext = params["key_phrase"].get("ftype")
                        else:
                            self.key_phrase = data["key_phrase"]

                    if isinstance(params["key_phrase"], str):
                        self.key_phrase = params["key_phrase"]
                else:
                    self.key_phrase = None
                    self.tag = None
                    self.search = None
                    self.tag2 = None
                    self.file_ext = None
            except Exception as error:
                print(f"\nError in initializing FileFetch: {error}")
                print("Exiting....")
                exit()
        elif params_file:
            data = read_yaml(params_file)
            try:
                self.url = data["file_url"]
                self.file_type = data["file_type"]
                self.desc = data["description"]
                self.webref = data["website"]
                if data["key_phrase"]:
                    if isinstance(data["key_phrase"], dict):
                        if (data["key_phrase"].get("tag")) and\
                           (data["key_phrase"].get("search")) and\
                           (data["key_phrase"].get("nested")):
                            self.key_phrase = None
                            self.tag = data["key_phrase"].get("tag")
                            self.search = data["key_phrase"].get("search")
                            if data["key_phrase"].get("nested") == 'yes':
                                self.tag2 = True
                            else:
                                self.tag2 = False
                            self.file_ext = data["key_phrase"].get("ftype")
                        else:
                            self.key_phrase = data["key_phrase"]

                    if isinstance(data["key_phrase"], str):
                        self.key_phrase = data["key_phrase"]
                else:
                    self.key_phrase = None
                    self.tag = None
                    self.search = None
                    self.tag2 = None
                    self.file_ext = None
            except Exception as error:
                print(f"\nError in initializing FileFetch: {error}")
                print(
                    "Suggest checking your yaml file is properly formatted."
                )
                print("Exiting....")
                exit()

        return
