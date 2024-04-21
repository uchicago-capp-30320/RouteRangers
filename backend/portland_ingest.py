"""
OBJECTIVE: Import and Format Portland Ridership data
AUTHOR: Jimena Salinas
DATE: 04/20/2024

SOURCES: the data sets were obtained by a direct request to the 
TriMet Public Records department. This is the link to the form
to request data sets for Tri Met: 
https://trimet.org/publicrecords/recordsrequest.htm
The  Receipt ID for this Public Records Request is PRR 2024-254.

VARIABLES:
    - location_id: (str) combines the city abbreviation "PDX" with a given stop_id
    - date: (datetime) represents a day in the format yyyy-mm-dd, only includes
    values for 2023
    - riders: (int) represents the average number of bus and light rail Tri Met
    riders. The riders value was originally provided as an average by season 
    and day type (Saturday, Sunday, and Weekday). In order to fit the data model
    for the project which is at the datetime level, the data has been mapped to dates in 2023.
"""

import pandas as pd

folder_path = ".../CloudStorage/Box-Box/Route Rangers/Transit dataset exploration/Portland Ridership Data/portland_ridership/"

spring_sat = "2023 spring_saturday.xlsx"
spring_weekday = "2023 spring_weekday.xlsx"
spring_sunday = "2023 spring_sunday.xlsx"

summer_sat = "2023 summer_saturday.xlsx"
summer_weekday = "2023 summer_weekday.xlsx"
summer_sunday = "2023 summer_sunday.xlsx"


# load data sets
def load_ridership_dasets():
    """
    import raw files with, and create standarized flags to
    combine all individual sets into a single file
    """
    try:
        # load data sets
        spring_data_sat = pd.read_excel(folder_path + spring_sat)
        spring_data_week = pd.read_excel(folder_path + spring_weekday)
        spring_data_sun = pd.read_excel(folder_path + spring_sunday)

        summer_data_sat = pd.read_excel(folder_path + summer_sat)
        summer_data_week = pd.read_excel(folder_path + summer_weekday)
        summer_data_sun = pd.read_excel(folder_path + summer_sunday)

        # add flags to specify season and day of week, this will be helpful
        # when converting the dataset from average by season to day level
        spring_data_sat["day_type"] = "Saturday"
        spring_data_week["day_type"] = "Weekday"
        spring_data_sun["day_type"] = "Sunday"

        summer_data_sat["day_type"] = "Saturday"
        summer_data_week["day_type"] = "Weekday"
        summer_data_sun["day_type"] = "Sunday"

        spring_data_sat["season"] = "Spring"
        spring_data_week["season"] = "Spring"
        spring_data_sun["season"] = "Spring"

        summer_data_sat["season"] = "Summer"
        summer_data_week["season"] = "Summer"
        summer_data_sun["season"] = "Summer"

        # append into one data set
        all_rider_data = pd.concat(
            [
                spring_data_sat,
                spring_data_week,
                spring_data_sun,
                summer_data_sat,
                summer_data_week,
                summer_data_sun,
            ],
            ignore_index=True,
        )

        print("Data loaded and appended successfully.")

    except FileNotFoundError:
        print("Files not found. Check the file path and filename.")
    except Exception as e:
        print("An error occurred:", e)


# load data sets
all_rider_data = load_ridership_dasets()

# format data sets
all_rider_data.columns = all_rider_data.columns.str.lower().str.replace(" ", "_")

all_rider_data = all_rider_data[["location_id", "ons", "day_type", "season"]]

# Since the data is at the day type + season level,
# create a df with all calendar days of 2023
start_date = "2023-01-01"
end_date = "2023-12-31"
calendar_dates = pd.date_range(start=start_date, end=end_date, freq="D")

# flag days of 2023 to match day_type field
calendar_df = pd.DataFrame(calendar_dates, columns=["date"])

calendar_df["day_type"] = calendar_df["date"].dt.day_name()

day_type_mapping = {"Saturday": "Saturday", "Sunday": "Sunday"}

calendar_df["day_type"] = (
    calendar_df["day_type"].map(day_type_mapping).fillna("Weekday")
)

# flag seasons, all days are flagged to Spring, except for summer months,
# to differenciate for routes that only run during the summer months
calendar_df["season"] = "Spring"

# Summer 2023 date range
summer_start = pd.to_datetime("2023-06-21")
summer_end = pd.to_datetime("2023-09-22")

calendar_df.loc[
    (calendar_df["date"] >= summer_start) & (calendar_df["date"] <= summer_end),
    "season",
] = "Summer"

# combine Tri Met data with calendar dates in order to convert the data set
# from day_type (sat, sun, or weekday) + season level into date level

merged_data = pd.merge(
    all_rider_data, calendar_df, on=["day_type", "season"], how="left"
)

sorted_data = merged_data.sort_values(by=["date", "day_type", "season"], ascending=True)

sorted_data = sorted_data.reindex(columns=["location_id", "date", "ons"])

sorted_data.rename(columns={"ons": "riders"}, inplace=True)

sorted_data["date"] = pd.to_datetime(sorted_data["date"])

# modify location_id to include city code
sorted_data["location_id"] = sorted_data["location_id"].apply(lambda x: f"PDX-{x}")

# export final data set in JSON format
output_file = folder_path + "PDX_ridership.json"
sorted_data.to_json(
    output_file,
    orient="records",
)
