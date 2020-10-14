# find other in-house packages in directory path
import os, sys, inspect

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# import other homegrown modules
from utils.readin import read_yaml


def allowed_files(allowed):
    file_list = allowed

    print("\nCurrently allowed file types for download:")
    for ftype in file_list:
        print(f"\t- {ftype}")


class InitializeCheck:
    def init_check(self, params, params_file):

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
                        self.key_phrase = None
                        if (params["key_phrase"].get("tag")) and\
                           (params["key_phrase"].get("search")) and\
                           (params["key_phrase"].get("nested")):
                            self.tag = params["key_phrase"].get("tag")
                            self.search = params["key_phrase"].get("search")
                            if params["key_phrase"].get("nested") == 'yes':
                                self.tag2 = True
                            else:
                                self.tag2 = False
                            self.file_ext = params["key_phrase"].get("ftype")

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
