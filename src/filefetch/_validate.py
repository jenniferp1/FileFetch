"""Support FileFetch Class.

Verifies retrieved data is valid. Contains specialized functions added
per data source.

Classes:
    :class:`FileFetch.FileFetch` - Save data from a given url in a pd.DataFrame or csv

    :class:`_help.Helper` - Print user help information for FileFetch

    :class:`_initialize.InitializeCheck` - Validate user input to FileFetch

    :class:`_validate.ValidateCheck` - Validate data sources before save to DataFrame
"""
# find other in-house packages in directory path
import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# import other homegrown modules
import pandas as pd
from datetime import date, timedelta, datetime
import re

###################################################################
#   INSTRUCTIONS FOR UPDATING: Adding new validator methods
#
# 1. In choose_validator, add the new validator name to if clause
# 2. Add new method called the same as the new validator name
#       New method should return a DataFrame if data validate
#       OR an empty DataFrame if data not valid
# 3. Use the if clause in choose_validator to call your new method
#
###################################################################

class ValidateCheck:
    """Mixin class used by :ref:`FileFetch() <FileFetch-label>` to validate retrieved data.

    See Also
    --------
    :class:`FileFetch.FileFetch`: Class for fetching files.
    :class:`_initialize.InitializeCheck`: Mixin class to validate user input to FileFetch
    :class:`_help.Helper`: Mixin class to provide help information on FileFetch.
    """

    #############################################
    # PUBLIC METHOD TO SELECT CORRECT VALIDATOR #
    #############################################

    def choose_validator(self, data):
        """Select user supplied validator method.

        User will need to add new validator methods below if they have
        a new dataset that they need to validate before converting to DataFrame.

        Current methods:
            1. CMU CovidCast API

        Parameters
        -----------
        data : dict
            Data (json) to be validated.

        Returns
        --------
        pd.DataFrame
            DataFrame with validated data.
        """

        # whether dataset has a validation function
        # (supply name of function or leave blank)
        validator_name = self.key_phrase.get("validator")

        if validator_name == "covidcast":
            df = self.covidcast(data)
        else:
            print(f"\n\t***Error: Validator name '{validator_name}', not found.")
            print(f"\t   Empty DataFrame is returned.\n")
            df = pd.DataFrame()

        return df


    #########################
    # CMU COVIDCAST METHODS #
    #########################

    def rollback(self, key, delta, rollbacks):
        """Rollback a day.

        If no valid data is found for a given date step back a day
        and try again.

        Parameters
        ------------
        key : str
            Name of dict key for data results list.
        delta : int
            Step size (days) to go back.
        rollbacks : int
            Number of times to step back before giving up.

        Returns
        --------
        data : dict
            JSON data.
        rollbacks : int
            Number of rollback attempts left.
        """

        if rollbacks > 0:

            rollbacks -= 1

            day = re.search(r"\d{8}",self.url)

            if day:
                try:
                    day = day.group()
                    start_day = day
                    day = datetime.strptime(day,"%Y%m%d")
                    day = day - timedelta(days=delta)
                    day = day.strftime("%Y%m%d")

                    #update url with rollbacked date
                    print(f"\tReplacing {start_day} with {day}\n")
                    self.url = self.url.replace(start_day,day)

                    #retry call to API using rolled back date
                    data = self.fetch_json()

                except ValueError as e:
                    print("\n\t***Error: Date format mismatch")
                    print(f"\t{e}")
                    print("\tRolling back failed. Empty data returned.\n")
                    data = {"result":-999}
            else:
                print("\n\t***Error: Could not find a start date in url string.")
                print("\n\tRolling back failed. Empty data returned.\n")
                data = {"result":-999}

        else:
            print("\n\tRolling back failed. Empty data returned.\n")
            data = {"result":-999}

        return (data, rollbacks)


    def covidcast(self,data):
        """CMU CovidCast data validator.

        Validates data returned from CovidCast API to ensure data is
        not empty or incomplete.

        Parameters
        -----------
        data : dict
            JSON data.

        Returns
        --------
        pd.DataFrame
            DataFrame with validated JSON data.
        """

        df = pd.DataFrame()

        checkdata_key, results_key = self.key_phrase.get("keys")
        rollbacks = self.key_phrase.get("attempts")

        while rollbacks > 0:
            if data["result"] == 1:
                print("\n\tSuccess!\n")
                rollbacks = -1
                df = self.json2df(data, results_key)
            elif data["result"] == 2:
                print("\n\t*** WARNING: Too Many Results...Not all your data was returned!")
                print("\tTry using a smaller time chunk.\n")
                rollbacks = -1
                df = self.json2df(data, results_key)
            elif data["result"] == -2:
                print("\n\tNo Results Found. Stepping back a day.\n")
                data, rollbacks = self.rollback(checkdata_key,1,rollbacks)
                if data["result"] == -999:
                    rollbacks = -1
                    print("\n\t***Error: Rollback failed. No data returned.\n")
            else:
                print("\n\t***Error: Unrecognized error code.")
                print("\t   Check 'url'. Aborting call.\n")
                rollbacks = -1

        if data["result"] == -2:
            print("\n\t***Error: Rollback failed. No data returned.\n")

        return df

    ####### CMU COVIDCAST SECTION END ########
