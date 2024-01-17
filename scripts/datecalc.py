import argparse

#############################################################

### usage: datecalc.py
###
### Optional arguments:
### 
###   start_date (s)    Date in the format of YEAR.MONTH.DAY (eg. 1936.2.20) that script starts calculating from. If not used its assumed to be 1936.1.1 
###   end_date (e)      Date in the format of YEAR.MONTH.DAY (eg. 1936.2.20) trhat script calculates until.
###   convert_days (c)  If used instead of start_date or end_date, will convert the amount of days given (eg 300) to the format YEAR.MONTH.DAY
###
### The script is meant as a way to calculate the amount of dates that is needed to do x action, for example events. 
### If you want an event to fire at 30th May 1938, you have to calculate the amount of dates manually, as to fire an event:
### country_event = { id = event.num days = x }
### is the syntax, which as you see doesn't get a date to fire and instead needs days.

#############################################################

def parse_date(date_str):
    try:
        year, month, day = map(int, date_str.split('.'))
        if not (1 <= month <= 12) or not (1 <= day <= 30):
            raise ValueError("Invalid month or day")
        return year, month, day
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid date format. Use YEAR.MONTH.DAY (e.g., 1936.2.20). {e}")

def date_to_days(year, month, day):
    return (year - 1) * 360 + (month - 1) * 30 + day

def calculate_days(start_date, end_date):
    start_days = date_to_days(*start_date)
    end_days = date_to_days(*end_date)

    return end_days - start_days

def days_to_date(days):
    years = days // 360
    remaining_days = days % 360
    month = 1 + remaining_days // 30
    day = 1 + remaining_days % 30
    if month == 13:
        years += 1
        month = 1
    return years, month, day

def main():
    parser = argparse.ArgumentParser(description="Date Calculator")
    parser.add_argument("-s", "--start_date", type=parse_date, default=(1936, 1, 1), help="The start date in the format YEAR.MONTH.DAY (e.g., 1936.1.1)")
    parser.add_argument("-e", "--end_date", type=parse_date, help="The end date in the format YEAR.MONTH.DAY (e.g., 1939.2.20)")
    parser.add_argument("-c", "--convert_days", type=int, help="Convert the given number of days to the format YEAR.MONTH.DAY")

    args = parser.parse_args()

    if args.convert_days is not None:
        result_date = days_to_date(args.convert_days)
        print(f"{result_date[0]}.{result_date[1]}.{result_date[2]}")
    else:
        start_date = args.start_date
        end_date = args.end_date if args.end_date else (1936, 1, 1)

        if end_date < start_date:
            raise ValueError("End date cannot be less than start date")

        days_difference = calculate_days(start_date, end_date)
        print(f"Number of days between {start_date[0]}.{start_date[1]}.{start_date[2]} and {end_date[0]}.{end_date[1]}.{end_date[2]}: {days_difference}")

if __name__ == "__main__":
    main()
