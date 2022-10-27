import math
import argparse
import pandas as pd

from typing import Tuple
from dateutil.parser import parse
from datetime import datetime

################### Functions #############################


def stringtodate(string) -> datetime:
    datetime_object = parse(string, dayfirst=True).date()
    return datetime_object


def stringtotime(time, date) -> datetime:
    date = stringtodate(date)
    time = datetime.strptime(time, "%H:%M").time()
    date_time = datetime.combine(date, time)
    return date_time


def days_hours_minutes(td) -> float:
    return td.total_seconds() / 60


def get_week(day) -> int:
    week = day / 7
    if week > 1:
        week = math.ceil(week)
    elif week < 1:
        week = 1
    return int(week)


def get_tables() -> Tuple[pd.DataFrame, pd.DataFrame]:

    data = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Comment"])

    with open(file_name, "r") as f:
        lines = f.readlines()

        for line in lines:
            if ":" not in line:
                date = line.rstrip("\n").strip()
            elif line == "\n":
                continue
            else:
                start_time, end_time = line.split("-")
                start_time, end_time = start_time.strip(), end_time.strip()

                if "(" in end_time:
                    end_time, comment = end_time.split("(")
                    end_time = end_time.strip()
                    comment = comment.strip("()")
                else:
                    end_time, comment = end_time, None

                row = {
                    "Date": date,
                    "Start Time": stringtotime(start_time, date),
                    "End Time": stringtotime(end_time, date),
                    "Comment": comment,
                }
                row = pd.DataFrame(row, index=[0])
                data = pd.concat([data, row], axis=0)

    data["Date"] = data["Date"].apply(lambda x: parse(x, dayfirst=True).date())
    data = data.sort_values(["Date"])
    data["Total Time"] = data["End Time"] - data["Start Time"]
    data["Total Minutes"] = data["Total Time"].apply(days_hours_minutes)
    data["Client Start Time"] = data["Start Time"] + pd.to_timedelta(
        hour_difference, unit="h"
    )
    data["Client End Time"] = data["End Time"] + pd.to_timedelta(
        hour_difference, unit="h"
    )

    data = data[data.Comment != "break"]

    data["Start Time"] = data["Start Time"].dt.strftime("%H:%M")
    data["End Time"] = data["End Time"].dt.strftime("%H:%M")
    data["Client Start Time"] = data["Client Start Time"].dt.strftime("%H:%M")
    data["Client End Time"] = data["Client End Time"].dt.strftime("%H:%M")

    total_minutes_by_date = data.groupby(
        by="Date", as_index=False
    ).sum()  # data[data['Comment']!='call

    all_dates = sorted(list(set(row.Date for index, row in data.iterrows())))

    total_minutes_by_date["Total Minutes"].sum()
    total_minutes_by_date["Week"] = total_minutes_by_date["Date"].apply(
        lambda x: get_week(x.day)
    )
    return data, total_minutes_by_date


def main():

    data, total_minutes_by_date = get_tables()
    week_data = total_minutes_by_date.groupby(by="Week").sum()
    month = data.iloc[1].Date.strftime("%b")
    year = file_name.split("/")[0]
    print(f"Invoice {month}-{year}\n")
    print(f"Note:- Time in GMT {hour_sign}{hour_difference + time_zone}\n")

    for index, twm in week_data.iterrows():
        print("#" * 50)
        print(f"\n\033[1m{month} Week {index}\033[0m\n")
        mins = int(twm["Total Minutes"])
        hours = int(twm["Total Minutes"]) / 60
        print(f"Actual Total time for the week:- {mins} mins or {hours:.2f} hours.")
        # print('\n14-hour week discount calculations:- \nP.S:- It excludes solo time,
        # as it\'s already charged at discounted rate/hr\n\n')
        if hours > discount_threshold:
            print(
                f"Total time greater than {discount_threshold} hrs, hence billing at ${discounted_rate}/hr.\n"
            )
        else:
            print(
                f"Total time below {discount_threshold} hrs, hence billing at ${base_rate}/hr.\n"
            )

        # if hours > discount_threshold and hours < 18:
        #     print(f"Give {hours - discount_threshold:.3f} discount for Week {index}!!!")

    total_hours = week_data["Total Minutes"].sum() / 60
    print("#" * 50)
    print(f"\nTotal time in {month} {year}:- {total_hours:.3f} hours.\n")
    print("#" * 50)
    print("\n\n\nDaily breakdown:-\n\n\n")
    for index, (date, tm, week) in total_minutes_by_date.iterrows():

        print(f"\n{date}, Week {int(week)}\n")
        print(f"Actual Total time     :- {int(tm)} mins or {tm / 60:.2f} hours.")
        print("Discounted Total time :- []  mins or []   hours.\n")
        current_date = data[data["Date"] == date]
        print("Breakdown")
        for index, row in current_date.iterrows():
            if row["Comment"] is None:  # or row['Comment'].strip() == 'call'
                print(
                    "{} - {} ({} mins)".format(
                        row["Client Start Time"],
                        row["Client End Time"],
                        int(row["Total Minutes"]),
                    )
                )
            else:
                print(
                    "{} - {} ({} mins)".format(
                        row["Client Start Time"],
                        row["Client End Time"],
                        int(row["Total Minutes"]),
                    ),
                    end=" ({})\n".format(row["Comment"]),
                )
        #         if row['Comment'] != None:
        #             print('({})\n'.format(row['Comment']))
        print("\n" + "#" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate timesheet")
    parser.add_argument("-f", "--file", help="file path", required=True)
    parser.add_argument("-r", "--rate", help="base rate", required=False, default=30)
    parser.add_argument(
        "-d", "--discounted_rate", help="discounted rate", required=False, default=25
    )
    parser.add_argument(
        "-t", "--threshold", help="discount threshold", required=False, default=14
    )
    parser.add_argument(
        "-tz", "--timezone", help="timezone", required=False, default=5.5
    )
    parser.add_argument(
        "-hrs", "--hrs_diff", help="hours difference", required=False, default=2.5
    )

    args = parser.parse_args()
    file_name = args.file
    base_rate = int(args.rate)
    discounted_rate = int(args.discounted_rate)
    discount_threshold = int(args.threshold)

    time_zone = float(args.timezone)
    hour_sign = "+"
    hour_difference = float(args.hrs_diff)

    main()
