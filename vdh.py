import glob
import os, re
import pandas as pd
from datetime import datetime, date

# TODO: Add function to verify save folder path exists (file_county)

def clean_vdh(filedir):

    district2county = "~/Documents/datasets/va_healthdistrict_county.csv"
    file_district = max(glob.iglob(filedir),key=os.path.getmtime)
    filedir = filedir.replace("*.csv","")
    file_county = f"{filedir}county/VirginiaCountyTestData"

    day = re.findall(r"(\d{4}-\d{2}-\d{2})", file_district)[0]

    file_county = f"{file_county}_{day}.csv"

    df = pd.read_csv(file_district)

    check_date_format = df[df['lab_report_date'] != "Not Reported"]["lab_report_date"]
    if "-" in check_date_format.any():
        df['lab_report_date'] = df['lab_report_date'].str.replace('-','/')

    if df[df['lab_report_date'] != "Not Reported"]["lab_report_date"].str.contains(r"\d{4}\/\d{1,2}\/\d{1,2}").all():
        df.loc[df.lab_report_date == "Not Reported", "lab_report_date"] = "1900/1/1"
        df["lab_report_date"] = pd.to_datetime(df["lab_report_date"], format="%Y/%m/%d")
    elif df[df['lab_report_date'] != "Not Reported"]["lab_report_date"].str.contains(r"\d{1,2}\/\d{1,2}\/\d{4}").all():
        df.loc[df.lab_report_date == "Not Reported", "lab_report_date"] = "1/1/1900"
        df["lab_report_date"] = pd.to_datetime(df["lab_report_date"], format="%m/%d/%Y")
    else:
        print("Error in code to convert VA health districts to counties")
        print("Check datetime format in downloaded file from vdh")
        print("Exiting....")
        exit()

    df = df[df["lab_report_date"].dt.year != 1900]
    df["Positivity_pcr_tests"] = (df["number_of_positive_pcr_testing"]/df["number_of_pcr_testing"]).apply(lambda x: round(x, 5))
    df["Positivity_tot_tests"] = (df["total_number_of_positive"]/df["total_number_of_testing"]).apply(lambda x: round(x, 5))

    df = df[(df.health_district != "Out of State") & (df.health_district != "Unknown")]
    df.sort_values(by=["lab_report_date"], inplace=True)

    df["Positivity_pcr_7day"] = df.groupby(by="health_district")["Positivity_pcr_tests"].transform(lambda x: x.rolling(7, 1).mean())
    df["Positivity_pcr_7day"] = df["Positivity_pcr_7day"].apply(lambda x: round(x, 5))

    hd = pd.read_csv(district2county)

    df = pd.merge(df,
                 hd[["CityCounty","CountyFIPS","HealthDistrict"]],
                 left_on="health_district",
                 right_on="HealthDistrict",
                 how="left" )
    df.drop(columns=["HealthDistrict"], inplace=True)

    df.to_csv(file_county, index=False)

    print(f"\nDataFrame saved to {file_county}\n")

    return

if __name__ == "__main__":

    clean_vdh("./virginia/*.csv")
