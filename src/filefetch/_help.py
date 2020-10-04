"""Support FileFetch Class.

Provides command line help and information to user.

Classes:
    :class:`FileFetch.FileFetch` - Save data from a given url in a pd.DataFrame or csv

    :class:`_help.Helper` - Print user help information for FileFetch

    :class:`_initialize.InitializeCheck` - Validate user input to FileFetch
"""

class Helper:
    """Mixin class used by :ref:`FileFetch() <FileFetch-label>` for command-line help.

    See Also
    --------
    :class:`FileFetch.FileFetch`: Class for fetching files.
    :class:`_initialize.InitializeCheck`: Mixin class to verify input to FileFecth.
    """

    def file_info(self):
        """Print information on file_list options.

        Parameters
        -------------
        None

        Returns
        ---------
        None
            Prints message to screen.

        Examples
        ----------
        To access the output, type the following at the command line:

        .. code-block:: python

            > python FileFetch.py file_list

        """

        print("\n*** Most types in list are different ways to retrieve a csv file.\n\
        Using 'findlink(s)' allows downloading a CSV, XLSX, or PDF. (9/24/2020)\n")
        for i, type in enumerate(self.file_list):
            desc = self.file_desc[type]
            print(f"\t{i+1}. {type}: {desc}")
        return

    def help_opts(self):
        """Print options for getting more help.

        Parameters
        -------------
        None

        Returns
        ---------
        None
            Prints message to screen.

        Examples
        ----------
        To access the output, type the following at the command line:

        .. code-block:: python

            > python FileFetch.py

        """

        print("\n\t>>> python FileFetch.py file_list \n")
        print("\t>>> python FileFetch.py doc \n")
        print("\t>>> python FileFetch.py help \n")
