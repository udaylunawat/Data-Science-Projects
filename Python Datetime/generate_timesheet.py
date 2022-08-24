from datetime import datetime
from dateutil.parser import parse
import pandas as pd
import argparse
################### Functions #############################


def stringtodate(string):
    datetime_object = parse(string, dayfirst=True).date()
    return datetime_object


def stringtotime(time, date):
    date = stringtodate(date)
    time = datetime.strptime(time, '%H:%M').time()
    date_time = datetime.combine(date, time)
    return date_time


def days_hours_minutes(td):
    return td.total_seconds() / 60


parser = argparse.ArgumentParser(description='Generate timesheet')
parser.add_argument('-f', '--file', help='file path', required=True)
parser.add_argument('-r', '--rate', help='base rate', required=True)
parser.add_argument('-d', '--discounted_rate', help='discounted rate', required=True)
parser.add_argument('-t', '--threshold', help='discount threshold', required=True)

args = parser.parse_args()
file_name = args.file
base_rate = int(args.rate)
discounted_rate = int(args.discounted_rate)
discount_threshold = int(args.threshold)

time_zone = 5.5

hour_sign = '+'
hour_difference = 2.5





f = open(file_name, "r")
txt_data = f.read()

data = pd.DataFrame(columns=["Date", "Start Time", "End Time", "Comment"])

with open(file_name, "r") as f:
    lines = f.readlines()

    for line in lines:
        if ':' not in line:
            date = line.rstrip('\n').strip()
        elif line == '\n':
            continue
        else:
            start_time, end_time = line.split('-')
            start_time, end_time = start_time.strip(), end_time.strip()

            if '(' in end_time:
                end_time, comment = end_time.split('(')
                end_time = end_time.strip()
                comment = comment.strip('()')
            else:
                end_time, comment = end_time, None

            row = {"Date":date, "Start Time": stringtotime(start_time, date), "End Time": stringtotime(end_time, date), "Comment": comment}
            row = pd.DataFrame(row, index=[0])
            data = pd.concat([data, row], axis=0)

data['Date'] = data['Date'].apply(lambda x: parse(x, dayfirst=True).date())
data = data.sort_values(['Date'])
data['Total Time'] = data['End Time'] - data['Start Time']
data['Total Minutes'] = data['Total Time'].apply(days_hours_minutes)
data['Client Start Time'] = data['Start Time'] + pd.to_timedelta(hour_difference, unit='h')
data['Client End Time'] = data['End Time'] + pd.to_timedelta(hour_difference, unit='h')

data = data[data.Comment != 'break']

data['Start Time'] = data['Start Time'].dt.strftime('%H:%M')
data['End Time'] = data['End Time'].dt.strftime('%H:%M')
data['Client Start Time'] = data['Client Start Time'].dt.strftime('%H:%M')
data['Client End Time'] = data['Client End Time'].dt.strftime('%H:%M')

total_minutes_by_date = data.groupby(by='Date', as_index=False).sum()  # data[data['Comment']!='call

all_dates = sorted(list(set(row.Date for index, row in data.iterrows())))

total_minutes_by_date['Total Minutes'].sum()


def main():
    print("Invoicely\nTime in GMT {}{}\n".format(hour_sign, hour_difference + time_zone))

    print("{} ({} to {})".format(file_name.split('.txt')[0], all_dates[0], all_dates[-1]))

    print('Actual Total time for the week:- {} mins or {:.2f} hours'.format(int(data['Total Minutes'].sum()),
                                                                            int(data['Total Minutes'].sum()) / 60))
    # print('\n14-hour week discount calculations:- \nP.S:- It excludes solo time, 
    # as it\'s already charged at discounted rate/hr\n\n')
    if total_minutes_by_date['Total Minutes'].sum() > discount_threshold * 60:
        print("Total time greater than {} hrs, hence billing at ${}/hr.".format(discount_threshold, discounted_rate))
    else:
        print("Total time below 14 hrs, hence billing at ${}/hr".format(base_rate))
    print('#' * 50)

    for index, (date, tm) in total_minutes_by_date.iterrows():
        print('\n{}'.format(date))
        print('Actual Total time:- {} mins. or {:.2f} hours.'.format(int(tm), tm / 60))
        print('Discounted Total time:- [] mins or [] hours.\n')
        current_date = data[data['Date'] == date]
        print("Breakdown")
        for index, row in current_date.iterrows():
            if row['Comment'] is None:  # or row['Comment'].strip() == 'call'
                print('{} - {} ({} mins)'
                      .format(row['Client Start Time'],
                              row['Client End Time'],
                              int(row['Total Minutes'])))
            else:
                print('{} - {} ({} mins)'
                      .format(row['Client Start Time'],
                              row['Client End Time'],
                              int(row['Total Minutes'])),
                      end=' ({})\n'.format(row['Comment']))
    #         if row['Comment'] != None:
    #             print('({})\n'.format(row['Comment']))
        print('\n' + '#' * 50)


if __name__ == '__main__':

    main()
