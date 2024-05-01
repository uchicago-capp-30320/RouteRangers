"""
OBJECTIVE: Import and Format Portland Ridership data
AUTHOR: Jimena Salinas
DATE: 04/30/2024

SOURCES: the data sets were obtained by a direct request to the 
TriMet Public Records department. This is the link to the form
to request data sets for Tri Met: 
https://trimet.org/publicrecords/recordsrequest.htm
The  Receipt ID for this Public Records Request is PRR 2024-254.

VARIABLES:
    - location_id: (str) combines the city "Portland" with a given stop_id
    - date: (datetime) represents a day in the format yyyy-mm-dd, only includes
    values for 2023
    - riders: (int) represents the average number of bus and light rail Tri Met
    riders. The riders value was originally provided as an average by season 
    and day type (Saturday, Sunday, and Weekday). In order to fit the data model
    for the project which is at the datetime level, the data has been mapped to dates in 2023.
"""

import pandas as pd


folder_path = ".../CloudStorage/Box-Box/Route Rangers/Transit dataset exploration/Portland Ridership Data/portland_ridership/"


file_names = {
    "spring_sat": "2023 spring_saturday.xlsx",
    "spring_weekday": "2023 spring_weekday.xlsx",
    "spring_sunday": "2023 spring_sunday.xlsx",
    "summer_sat": "2023 summer_saturday.xlsx",
    "summer_weekday": "2023 summer_weekday.xlsx",
    "summer_sunday": "2023 summer_sunday.xlsx",
    "fall_sat": "2023 fall_saturday.xlsx",
    "fall_weekday": "2023 fall_weekday.xlsx",
    "fall_sunday": "2023 fall_sunday.xlsx",
    "winter_sat": "2023 winter_saturday.xlsx",
    "winter_weekday": "2023 winter_weekday.xlsx",
    "winter_sunday": "2023 winter_sunday.xlsx",
}

# date ranges for 2023
start_date = "2023-01-01"
end_date = "2023-12-31"

# data ranges for each season in 2023
# this will be used to change the level of the data from aggreate at the
# date type level into daily level (to match our data model)
season_ranges = {
    "Spring": (pd.to_datetime("2023-03-20"), pd.to_datetime("2023-06-21")),
    "Summer": (pd.to_datetime("2023-06-21"), pd.to_datetime("2023-09-23")),
    "Fall": (pd.to_datetime("2023-09-23"), pd.to_datetime("2023-12-22")),
    "Winter": (pd.to_datetime("2023-12-22"), pd.to_datetime("2024-03-20")),
}


def load_data(file_path):
    """
    reads and individual Excel file and returns an error
    if the file path does not exist
    """
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        print("File not found:", file_path)
    except Exception as e:
        print("An error occurred while loading data:", e)


def load_ridership_datasets(file_names):
    """
    Takes a dictionary in the form key: season_day type
    and value: file name, loads the corresponding ridership
    data and creates a column with the corresponding
    season value and day type (Saturday, Weekday, or Sunday),
    and returns a dictionary with a key (season_day) and value
    (the corresponding dataframe).
    """
    data_frames = {}
    for key, value in file_names.items():
        df = load_data(folder_path + value)
        # get season from filename
        if "spring" in value:
            df["season"] = "Spring"
        elif "summer" in value:
            df["season"] = "Summer"
        elif "fall" in value:
            df["season"] = "Fall"
        elif "winter" in value:
            df["season"] = "Winter"

        # get day_type from filename
        if "sat" in value:
            df["day_type"] = "Saturday"
        elif "weekday" in value:
            df["day_type"] = "Weekday"
        elif "sunday" in value:
            df["day_type"] = "Sunday"
        data_frames[key] = df
    return data_frames


def format_data(all_rider_data):
    """
    standarize column formats and keep the relevant
    data fields needed to match our data model, or
    merge the data at the datetime level
    """
    for key, df in all_rider_data.items():
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        all_rider_data[key] = df[["location_id", "ons", "day_type", "season"]]
    return all_rider_data


def create_calendar_df(start_date, end_date, season_ranges):
    """
    Create a dataframe with datetime values as well as
    the corresponding season and day type associated with
    each datetime, return a dataframe
    """
    calendar_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    calendar_df = pd.DataFrame(calendar_dates, columns=["date"])
    calendar_df["day_type"] = calendar_df["date"].dt.day_name()
    calendar_df["day_type"] = (
        calendar_df["day_type"]
        .map({"Saturday": "Saturday", "Sunday": "Sunday"})
        .fillna("Weekday")
    )
    calendar_df["season"] = "Spring"

    # label seasons based on date ranges
    for season, (season_start, season_end) in season_ranges.items():
        calendar_df.loc[
            (calendar_df["date"] >= season_start) & (calendar_df["date"] < season_end),
            "season",
        ] = season

    return calendar_df


def merge_data(all_rider_data, calendar_df):
    """
    Combines two dataframes by day type and season value,
    returns a dataframe with the columns from both data frames
    """
    merged_data = pd.merge(
        all_rider_data, calendar_df, on=["day_type", "season"], how="left"
    )
    return merged_data.sort_values(by=["date", "day_type", "season"], ascending=True)


def preprocess_location_id(location_id):
    """
    Add a city prefix to make the location id more specific
    for our data model
    """
    return f"Portland-{location_id}"


def export_to_json(sorted_data, output_file):
    sorted_data.to_json(output_file, orient="records")


def main():
    all_rider_data = load_ridership_datasets(file_names)
    formatted_data = format_data(all_rider_data)
    all_data = pd.concat(formatted_data.values(), ignore_index=True)

    calendar_df = create_calendar_df(start_date, end_date, season_ranges)
    merged_data = merge_data(all_data, calendar_df)
    merged_data.rename(columns={"ons": "riders"}, inplace=True)
    merged_data["date"] = pd.to_datetime(merged_data["date"])
    merged_data["location_id"] = merged_data["location_id"].apply(
        preprocess_location_id
    )
    output_file = folder_path + "Portland_ridership.json"
    export_to_json(
        merged_data.reindex(columns=["location_id", "date", "riders"]), output_file
    )


if __name__ == "__main__":
    main()
