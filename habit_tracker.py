# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 15:03:54 2025

@author: Brandyn Ewanek
"""

import datetime
# from datetime import date
from datetime import datetime as dt
import json
import pandas as pd
import google.generativeai as genai
import os
# import warnings
# warnings.simplefilter('ignore')


def display_menu():
    """Displays the main menu of the habit tracking app."""

    print("\nHabit Tracker Main Menu")
    print("-----------------------")
    print("1. Create User")
    print("2. Log In")  
    print("3. Add New Current Habit")
    print("4. Remove Current Habit")
    print("5. Track Habit")
    print("6. Track Historical Habit")
    print("7. Correct Tracked Habit")
    print("8. Analyze Number of Current Habits")
    print("9. Analyze Habits (Specific, All, or Current)")    
    print("10. Analyze Longest Streak")
    print("11. Analyze if Habit is Broken")
    print('12. Today Report') 
    print("13. Suggest a Habit") 
    print("14. Exit")
    print("-----------------------")


    # Get user's choice
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 1 <= choice <= 14:
                return choice
            else:
                print("Invalid choice. Please enter a number between 1 and 13.")
        except ValueError:
            print("Invalid input. Please enter a number.")




# Habit Class
class Habit:
    """
    A class to represent a habit tracker.
    
    Attributes:
        username (str): The username of the person tracking the habit.
        today (str): The current date in YYYY-MM-DD format. Defaults to '2025-01-14' for testing.
        api_key (str): The API key for Google Generative AI.
    
    Methods:
        load_tracking_data(): Loads tracking data from a CSV file.
        save_tracking_data(df_tracking): Saves tracking data to a CSV file.
        load_user_data(): Loads user data from a CSV file.
        save_user_data(df_user): Saves user data to a CSV file.
        get_tracked_completed_today(): Returns a list of habits completed today.
        get_unit_of_measurement(): Returns a dictionary of units of measurement for each habit.
        get_current_habits(): Returns a list of current habits.
        get_habit_history(habit): Returns the history of a habit as a list of dates and a list of values.
        get_periodicity(habit): Returns the periodicity of a habit ('daily' or 'weekly').
        track_habit(habit_name, tracked_value): Tracks a habit for the current date.
        correct_tracked_habit(date, habit, new_value, entry=1): Corrects a previously tracked habit.
        track_historical_habit(habit_name, tracked_value, date): Tracks a habit for a past date.
        today_report(): Prints a report of habits completed and not completed today.
        calculate_streak(habit, inside=False): Calculates the current streak for a habit.
        longest_streak(): Prints the longest current streak for any habit.
        is_broken(habit, period): Checks if a habit with a given streak is broken.
        analyze_all_habits(task, current=False): Analyzes all habits (or only current habits) for a given task ('average', 'total', or 'count').
    """
    
    
    
    def __init__(self, username, today='2025-01-14'): # today is static for testingdatetime.date.today().strftime("%Y-%m-%d")
        """
        Initializes a new Habit object.
    
        Parameters:
            username (str): The username of the person tracking the habit.
            today (str): The current date in YYYY-MM-DD format. Defaults to '2025-01-14' for testing.
        """
        self.__username = username
        self.__today = today

        

    ### data management #############################################
    def load_tracking_data(self):
      """Loads tracking data from a CSV file."""
      return pd.read_csv(f'data\/tracking_{self.__username}.csv')

    def save_tracking_data(self, df_tracking):
      """Saves tracking data to a CSV file."""
      df_tracking.to_csv(f'data\/tracking_{self.__username}.csv', index=False)

    def load_user_data(self):
      """Loads user data from a CSV file."""
      return pd.read_csv(f'data\/user_data_{self.__username}.csv') 

    def save_user_data(self, df_user):
      """Saves user data to a CSV file."""
      df_user.to_csv(f'data\/user_data_{self.__username}.csv', index=False)

    ### Getters ######################################################
    # get habits completed today
    def get_tracked_completed_today(self):
        """Returns a list of habits completed today."""
        df_tracking = self.load_tracking_data()
        habits = df_tracking.loc[df_tracking['date'] == self.__today, 'habit'].tolist()
        return habits


    # get habit unit of measurment
    def get_unit_of_measurement(self):
        """Returns a dictionary of units of measurement for each habit."""
        df_user = self.load_user_data()
        # get dictionary unit of measurement
        habits_data = df_user.loc[0, 'measured_in']
        habits_dict = json.loads(habits_data)
        # return unit of measurement
        return habits_dict


    def get_current_habits(self):
        """Returns a list of current habits."""
        df_user = self.load_user_data()
        habits_string = df_user.loc[0, 'current_habits']
        habits_list = habits_string.split(",")
        return habits_list

    def get_habit_history(self, habit):
        """
        Returns the history of a habit as a list of dates and a list of values.

        Parameters:
            habit (str): The name of the habit.

        Returns:
            tuple: A tuple containing two lists: the dates and the corresponding values.
        """
        
        habit = habit.lower() #ensure habit_name continuity
        
        df_tracking = self.load_tracking_data()
        df_tracking = df_tracking.sort_values(by='date')
        
        df_tracking['habit'] = df_tracking['habit'].str.lower()
        df_tracking = df_tracking[df_tracking['habit'] == habit]
        habit_history_date = df_tracking['date'].tolist()
        habit_history_value = df_tracking['value'].tolist()
        return habit_history_date, habit_history_value

    def get_periodicity(self, habit):
        """
        Returns the periodicity of a habit ('daily' or 'weekly').

        Parameters:
            habit (str): The name of the habit.

        Returns:
            str: The periodicity of the habit.
        """
        df_user = self.load_user_data()
        habit = habit.lower()
        
        # get dictionary unit of measurement
        habits_data = df_user.loc[0, 'period']
        habits_dict = json.loads(habits_data)
        habits_dict = {k.lower(): v for k, v in habits_dict.items()}
        return habits_dict[habit]


    ### interactions ################################################
    # track habit
    def track_habit(self, habit_name, tracked_value):
        """
        Tracks a habit for the current date.
        
        Parameters:
            habit_name (str): The name of the habit.
            tracked_value (float): The value to track for the habit.
        """
        df_tracking = self.load_tracking_data()
        
        habit_name = habit_name.lower() # lowercase habit name for continuity 

        # Create a new DataFrame for the new entry
        new_entry = pd.DataFrame({'date': [self.__today], 'habit': [habit_name], 'value': [tracked_value]})

        # Append the new entry to the existing DataFrame
        df_tracking = pd.concat([df_tracking, new_entry], ignore_index=True)

        self.save_tracking_data(df_tracking)

    # correct previously tracked habit
    def correct_tracked_habit(self, date, habit, new_value, entry=1):
        """
        Corrects a previously tracked habit.

        Parameters:
            date (str): The date of the entry to correct (YYYY-MM-DD).
            habit (str): The name of the habit to correct.
            new_value (float): The new value for the habit.
            entry (int): The entry number to correct (1 for the first entry, 2 for the second, etc.). Defaults to 1.
        """ 
        df_tracking = self.load_tracking_data()
        # Calculate the actual index of the entry to be corrected

        try:
            entry_index = df_tracking[(df_tracking['date'] == date) & (df_tracking['habit'].str.lower() == habit)].index[entry-1]
            print('ENTRY INDEX', entry_index)
            df_tracking.loc[entry_index, 'value'] = new_value
        except IndexError:
            print(f"Error: Entry no. {entry} for habit '{habit}' on date '{date}' not found and not corrected.")
            return


        self.save_tracking_data(df_tracking)
        print('Habit Corrected!!')

    # track habit that happened in the past
    def track_historical_habit(self, habit_name, tracked_value, date):
        """
        Tracks a habit for a past date.

        Parameters:
            habit_name (str): The name of the habit.
            tracked_value (float): The value to track for the habit.
            date (str): The date to track the habit for (YYYY-MM-DD).
        """
        df_tracking = self.load_tracking_data()
        
        # lowercase habit name for continuity 
        habit_name = habit_name.lower()

        # Create a new DataFrame for the new entry
        new_entry = pd.DataFrame({'date': [date], 'habit': [habit_name], 'value': [tracked_value]})

        # Append the new entry to the existing DataFrame
        df_tracking = pd.concat([df_tracking, new_entry], ignore_index=True)

        self.save_tracking_data(df_tracking)


    ### analysis ####################################################
    # habits still to be completed today
    def today_report(self):
        """Prints a report of habits completed and not completed today."""
        
        df_tracking = self.load_tracking_data()# load user data
        current_habits = self.get_current_habits() # get list of current habits
        current_habits = [h.lower() for h in current_habits] # ensure habits are all lowercase
        daily_habits = []
        weekly_habits = []
        for habit in current_habits:   # sort weekly and daily habits into two lists
            if self.get_periodicity(habit) == 'daily':
                daily_habits.append(habit)
            else:
                weekly_habits.append(habit)
        
        print('daily_habits', ', '.join(daily_habits)) # show current habits
        print('weekly_habits', ', '.join(weekly_habits))
              
        # get habits completed today
        today_tracked_habits = df_tracking[df_tracking['date'] == self.__today]['habit'].unique().tolist()
        today_tracked_habits = [h.lower() for h in today_tracked_habits]
        
        # daily habits get habits not completed today
        habits_to_track = [habit for habit in daily_habits if habit not in today_tracked_habits]
        
        if not habits_to_track: # print habits tracked today if
          print('Congratulations!! You\'ve finished all of your daily habits' )
          print('Habits Tracked today:  ', ', '.join(today_tracked_habits))
        else:
          print('Habits Tracked today: ', ', '.join(today_tracked_habits))
          print(f'Habits that have not been compelete today {self.__today}: ',', '.join(habits_to_track))

        today = dt.strptime(self.__today, "%Y-%m-%d") #covert string to datetime object
        start_of_week = today - datetime.timedelta(days=today.weekday()) # get monday of week
        weekly_tracked_habits = []
        weekly_to_track = []
        if not weekly_habits:
          for habit in weekly_habits: # checks if habit has been tracked since this last Monday
              df_tmp = df_tracking[df_tracking['habit']==habit]
              df_tmp = df_tmp.sort_values('date', ascending=False)
              last_track_date = dt.strptime(df_tmp.iloc[0,0], "%Y-%m-%d")
              if start_of_week <= last_track_date:
                  weekly_tracked_habits.append(habit)
              else:
                  weekly_to_track.append(habit)
        
        if not weekly_to_track: # display message based of if weekly habits still to track
          print('Congratulations!! You\'ve finished all of your weekly habits' )
          print('Habits Tracked this week:  ', ', '.join(weekly_tracked_habits))
        else:
          print('Habits Tracked today: ', ', '.join(weekly_tracked_habits))
          print(f'Habits that have not been compelete today {self.__today}: ',', '.join(weekly_to_track))

              





    # calculate streak
    def calculate_streak(self, habit, inside=False):
        """
        Calculates the current streak for a habit.

        Parameters:
            habit (str): The name of the habit.
            inside (bool): Whether the function is being called internally (True) or externally (False). 
                           If True, no messages are printed to the user. Defaults to False.

        Returns:
            int: The current streak for the habit.
            date(str): Date Streak was broken
        """

        habit_periodicity = self.get_periodicity(habit)
        if habit_periodicity not in ['daily', 'weekly']:
            print('Incorrect Habit Periodicity, Please change to daily or weekly') # error message if habit was created with incorrect periodcity
            return
        habit_history, habit_past_values = self.get_habit_history(habit)
        last_date_tracked = ''
        if habit_periodicity == "daily": # daily habits
            streak = 0
            today = self.__today
            # Iterate through completion dates in reverse (from most recent to oldest)
            for completion_date_str in reversed(habit_history):          
                if completion_date_str == today:
                    streak += 1
                    today = dt.strptime(today, "%Y-%m-%d") # convert string to datetime 
                    today -= datetime.timedelta(days=1)  # Move to the previous day
                    today = today.strftime("%Y-%m-%d") # convert datetime to string
                    last_date_tracked = completion_date_str
                else:
                    break  # Break the loop if there's a gap in completion dates


        elif habit_periodicity == "weekly": # weekly habits
            streak = 0
            today = dt.strptime(self.__today, "%Y-%m-%d")
            
            # create boundaries of week
            start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday of the current week
            end_of_week = start_of_week + datetime.timedelta(days=6) # Sunday of the current week
            
            for completion_date_str in reversed(habit_history):# Iterate through completion dates in reverse
                completion_date = dt.strptime(completion_date_str, "%Y-%m-%d") # convert string from database into datatime object

                if start_of_week <= completion_date <= end_of_week: # Check if completion is within the current week or previous weeks
                    streak += 1
                    start_of_week -= datetime.timedelta(days=7)  # Move to the previous week's start back 7 days
                    end_of_week -= datetime.timedelta(days=7)  # Move end of the week back 7 days
                    last_date_tracked = completion_date_str
                else:
                    break

        if inside: # if used as an inside function to quiet messages, or externally messages print
          # message to user
          if streak == 0:
              print(f'''You have no streak for the habit {habit}. Keep tracking your habits.''')
          else:
              print(f'''Your streak for the habit {habit} was {streak}.  Congratulation!!!''')

        return streak, last_date_tracked

    def longest_streak(self): 
        """Prints the longest current streak for any habit."""
        # get current habits
        current_habits = self.get_current_habits()
        
        # get current streak for each current have
        streaks_daily = []
        dates_daily = []
        daily_habits = []
        streaks_weekly = []
        dates_weekly = []
        weekly_habits = []
        for habit in current_habits:  # get streak length for each habit
            streak_length, date_completed = self.calculate_streak(habit) 
                       
            if self.get_periodicity(habit) == 'daily':
                streaks_daily.append(streak_length)
                dates_daily.append(date_completed)
                daily_habits.append(habit)
            else:
                streaks_weekly.append(streak_length)
                dates_weekly.append(date_completed)
                weekly_habits.append(habit)
               
        longest_streak_habit_daily = daily_habits[streaks_daily.index(max(streaks_daily))]
        longest_streak_date_daily = dates_daily[streaks_daily.index(max(streaks_daily))]        
        print(f'''Your current longest daily streak is {max(streaks_daily)} for {longest_streak_habit_daily} since {longest_streak_date_daily}''')

        # show longest streak for daily habits
        if streaks_weekly:
            longest_streak_habit_weekly = weekly_habits[streaks_weekly.index(max(streaks_weekly))]
            longest_streak_date_weekly = dates_weekly[streaks_weekly.index(max(streaks_weekly))]      
            print(f'''Your current longest weekly streak is {max(streaks_weekly)} for {longest_streak_habit_weekly} since {longest_streak_date_weekly}''')

        if not streaks_weekly:
            print(f'The habit your have been tracking for the longest time is {longest_streak_habit_daily} since {longest_streak_date_daily}')
        
        else:
            # print('hi')
            if dt.strptime(longest_streak_date_daily, "%Y-%m-%d") < dt.strptime(longest_streak_date_weekly, "%Y-%m-%d"):
                print(f'The habit your have been tracking for the longest time is {longest_streak_habit_daily} since {longest_streak_date_daily}')
            else:
                print(f'The habit your have been tracking for the longest time is {longest_streak_habit_weekly} since {longest_streak_date_weekly}')


    def is_broken(self, habit,  period):
        """
        Checks if a habit with a given streak is broken.

        Parameters:
            habit (str): The name of the habit.
            period (int): The period to check for a broken streak (in days or weeks, depending on habit periodicity).
        """
        # load periodicity and habit history
        habit_periodicity = self.get_periodicity(habit)
        habit_history, habit_past_values = self.get_habit_history(habit)


        if habit_periodicity == "daily":  # for daily habits
            streak = 0
            today = dt.strptime(self.__today, "%Y-%m-%d")

            # Iterate through completion dates in reverse (from most recent to oldest)
            for completion_date_str in reversed(habit_history):
                completion_date = dt.strptime(completion_date_str, "%Y-%m-%d")#.date()

                # Check if the completion date is consecutive
                if completion_date == today:
                    streak += 1
                    today -= datetime.timedelta(days=1)  # Move to the previous day
                    if streak == period:
                        print(f'You had a streak for {habit} for the last {period} days')
                        return
                else:
                    break  # Break the loop if there's a gap in completion dates
            print(f'You had a streak of {streak} but it was broken on {today.strftime("%Y-%m-%d")}')


        elif habit_periodicity == "weekly":  # for weekly habits
            streak = 0
            today = dt.strptime(self.__today, "%Y-%m-%d")
            
            # create boundaries of week
            start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday of the current week
            end_of_week = start_of_week + datetime.timedelta(days=6)   # Sunday of current week
            
            # Iterate through completion dates in reverse
            for completion_date_str in reversed(habit_history):
                completion_date = dt.strptime(completion_date_str, "%Y-%m-%d")
                if start_of_week <= completion_date <= end_of_week:
                    streak += 1
                    start_of_week -= datetime.timedelta(days=7)  # Move beg of week back 7 days
                    end_of_week -= datetime.timedelta(days=7)  # Move end of week back 7 days
                    if streak == period:
                        print(f'You had a streak of {streak} but it was broken on the week of {start_of_week.strftime("%Y-%m-%d")}')
                        return
                else:
                    break
            print(f'You had a streak of {streak} but it was broken on the week of {start_of_week.strftime("%Y-%m-%d")}')


    def analyze_all_habits(self, task, current=False):
        """
        Analyzes all habits (or only current habits) for a given task ('average', 'total', or 'count').
        
        Parameters:
            task (str): The type of analysis to perform ('average', 'total', or 'count').
            current (bool): Whether to analyze only current habits (True) or all habits (False). Defaults to False.
        """

        # get tracking data, current habits, unit of measurement
        df_tracking = self.load_tracking_data()
        current_habits = self.get_current_habits()
        units = self.get_unit_of_measurement()
        
        # ensure lowercase habit_name
        df_tracking['habit'] = df_tracking['habit'].str.lower()
        current_habits = [h.lower() for h in current_habits]
        units = {k.lower(): v for k, v in units.items()}
        
        
        if current: # reduce historical records to only current habits
          df_tracking = df_tracking[df_tracking['habit'].isin(current_habits)]
        
        # display different summarize statistics for all or current habits
        if task == 'average':  
            df_tmp = df_tracking.groupby('habit').mean(numeric_only=True)
            for h, avg in df_tmp.iterrows():
                print(f'For Habit: {h}, you AVERAGED {round(avg.value,2)} {units[h]}')

        elif task == 'total':
          df_tmp = df_tracking.groupby('habit').sum(numeric_only=True)
          for h, tot in df_tmp.iterrows():
              print(f'For Habit: {h}, you TOTALLED {round(tot.value,2)} {units[h]}')

        elif task == 'count':
          df_tmp = df_tracking.groupby('habit').count()
          for h, cnt in df_tmp.iterrows():
              print(f'For Habit: {h}, you TRACKED {round(cnt.value,0)} times')


class User:
    """
    A class to represent a user.

    Attributes:
        username (str): The username of the user.
        today (str): The current date in YYYY-MM-DD format.
        api_key (str): The API key for Google Generative AI.

    Methods:
        load_user_data(): Loads user data from a CSV file.
        save_user_data(df_user): Saves user data to a CSV file.
        get_current_habits(): Returns a list of current habits.
        set_habit_meta(df_user, habit, value, meta): Sets the value of a habit's meta information (measured_in or period).
        create_user(user_name, DOB, city): Creates a new user.
        add_current_habit(habit_name, measured_in, period): Adds a new habit to the user's list of current habits.
        remove_current_habit(habit_name): Removes a habit from the user's list of current habits.
        get_suggestions(): Gets suggestions for new habits based on the user's current habits and other information.
    """
    
    def __init__(self, username):
        """
        Initializes a new User object.

        Parameters:
            username (str): The username of the user.
        """
        self.__username = username
        
    ### data management ############################################
    def load_tracking_data(self):
      """Loads tracking data from a CSV file."""
      return pd.read_csv(f'data\/tracking_{self.__username}.csv')
  
    # load user data
    def load_user_data(self):
      """Loads user data from a CSV file."""
      return pd.read_csv( f'data\/user_data_{self.__username}.csv')

    # save user data
    def save_user_data(self, df_user):
      """Saves user data to a CSV file."""
      df_user.to_csv( f'data\/user_data_{self.__username}.csv', index=False)

    ### Getters
    # list of current habits
    def get_current_habits(self):
      """Returns a list of current habits.
        or empty list if no current habits for initialization"""
      try:
        df_user = self.load_user_data()
        habits_string = df_user.loc[0, 'current_habits']
        habits_list = habits_string.split(",")
        return habits_list
      except:
        return []

    ### Setters ################################################
    # set_habit_meta
    def set_habit_meta(self, df_user, habit, value, meta='measured_in'):
      """
          Sets the value of a habit's meta information (measured_in or period).
        
          Parameters:
          df_user (pd.DataFrame): The DataFrame containing the user data.
          habit (str): The name of the habit.
          value (str): The new value for the meta information.
          meta (str): The type of meta information to set ('measured_in' or 'period').
      """

      if meta=='measured_in':
        df_user = self.load_user_data()
        # set dictionary unit of measurement
        habits_data = df_user.loc[0, 'measured_in']
        habits_dict = json.loads(habits_data)   #load json from user data
        habits_dict[habit] = value     # Update the value for the specified habit
        habits_data = json.dumps(habits_dict)   # Convert back to JSON
        df_user.loc[0, 'measured_in'] = habits_data    # Save the updated data
        
      elif meta=='period':
        value = value.lower()    # periodicity ensure not captialized
        if value not in ['daily', 'weekly']:   # ensure periodcity is correct format
            print('Incorrect Habit Periodicity, Please change to daily or weekly')  # error message if habit was created with incorrect periodcity
            return
        habits_data = df_user.loc[0, 'period']
        habits_dict = json.loads(habits_data)   #load json from user data
        habits_dict[habit] = value     # Update the value for the specified habit
        habits_data = json.dumps(habits_dict)    # Convert back to JSON
        df_user.loc[0, 'period'] = habits_data    # Save the updated data

      return df_user


    # create user
    def create_user(self, user_name, DOB, city):
      """
          Creates a new user.
        
          Parameters:
              user_name (str): The username of the user.
              DOB (str): The date of birth of the user.
              city (str): The city of the user.
      """
      user_dict = {
          'username': user_name,
          'DOB': DOB,
          'city': city,
          'current_habits': '',
          'measured_in':'{}',
          'period':'{}'}
      df_user_tmp = pd.DataFrame(user_dict, index=[0])
      df_tracking_tmp = pd.DataFrame(columns=['date', 'habit', 'value']) 
      df_user_tmp.to_csv(os.path.join('data', f'user_data_{user_name}.csv'), index=False)
      df_tracking_tmp.to_csv(os.path.join('data', f'tracking_{user_name}.csv'), index=False)


    # add new current habit
    def add_current_habit(self, habit_name, measured_in, period):
        """
        Adds a new habit to the user's list of current habits.
        
        Parameters:
            habit_name (str): The name of the habit.
            measured_in (str): The unit of measurement for the habit.
            period (str): The periodicity of the habit ('daily' or 'weekly').
        """
        # load user data add
        df_user = self.load_user_data()
        
        # lower habit name for continuaity
        habit_name = habit_name.lower()
        
        # check if current habit already exists
        habits_list = self.get_current_habits()
        if habit_name in habits_list:
          print('Habit already exists, Please choose another name.')
          return

        # add measured_in to json
        df_user = self.set_habit_meta(df_user, habit_name, measured_in, meta='measured_in')

        # add habit period to json
        df_user = self.set_habit_meta(df_user, habit_name, period, meta='period')


        # Ensure habit_name is treated as a single item in a list
        if isinstance(habit_name, str):    # Check if habit_name is a string
            habit_name = [habit_name]    # Convert it to a list


        try:
          # extend habit to list
          habits_list = self.get_current_habits()
          habits_list.extend(habit_name)
          habits_string = ",".join(habits_list)
          df_user.loc[0, 'current_habits'] = habits_string    # save updated hait

        except:
          habits_string = ",".join(habit_name)
          df_user.loc[0, 'current_habits'] = habits_string    # save first habit

        # save user data
        self.save_user_data(df_user)


    # remove current habit
    def remove_current_habit(self, habit_name):
        """
        Removes a habit from the user's list of current habits.

        Parameters:
            habit_name (str): The name of the habit to remove.
        """
        # load user data
        df_user = self.load_user_data()
        
        # lowercase habit name for continuity 
        habit_name = habit_name.lower()

        try:
          # remove habit from list
          habits_list = self.get_current_habits()
          habits_list.remove(habit_name)
          habits_string = ",".join(habits_list)
          df_user.loc[0, 'current_habits'] = habits_string

        except:
          print(f'There was no {habit_name} to remove.')
          return
          # habits_string = ",".join(habit_name)
          # df_user.loc[0, 'current_habits'] = habits_string

        # save user data
        self.save_user_data(df_user)

    # call gemini (LLM) for suggestions
    def get_suggestions(self):
        """
        Gets suggestions for new habits based on the user's current habits and other information.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = '''
        You will recieve a persons name, date of birth, city and current habits.
        I need you to reccomend 3 likely habits this person might be interested in.
        I would also like that you give a very short sentences as to why they would be interested for a maximum 20 words.
        And a 4th habit that is a very creative fun suggestion of a potential habit they.
        could potentially be interested in and explain why.
        
        You will return the response in the following format only.
        
        Template:
            Here are some potential habits you might be interested in.
            Habit 1.  You might be interested in Habit 1 because ......
            Habit 2.  You might be interested in Habit 2 because ......
            Habit 3.  You might be interested in Habit 3 because ......
            Habit 4.  You might be interested in Habit 4 because ......
            
            
        The person your will recommend a habit for is:
            Name: {}
            DOB: {}
            City: {}
            Current habits: {}

        '''
        df_user = self.load_user_data()
        current_habits = self.get_current_habits()
        prompt = prompt.format(df_user['username'], df_user['DOB'], df_user['city'], current_habits)
        result = model.generate_content(prompt)
        
        print(result.text)
        
    # call gemini to give warm intro message
    def llm_hello(self):
        """
        Gets suggestions for new habits based on the user's current habits and other information.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = '''
        You will recieve a persons name, date of birth, city and current habits.
        I need you to give a warm motivating message to the user of my habit tracking app.
        Make the greeting appropriate for users location, age.
        Yoo will also receive the users tracking history.  Please give on motivational comment
        to the user to inspire them to be consistent with their habits.  It should be appropriate 
        for age and location and interests of user. It should also be fun.
        
        You will return the response in the following format only.
        
        Template:
            Hello, NAME it is great to see you again.  Great job with your tracking of .....
            This is an important habit because ...SOMETHING FUN.  
            
            
        The person your will recommend a habit for is:
            Name: {}
            DOB: {}
            City: {}
            Habits History: {}

        '''
        df_user = self.load_user_data()
        df_tracking = self.load_tracking_data()
        prompt = prompt.format(df_user['username'], df_user['DOB'], df_user['city'], df_tracking)
        result = model.generate_content(prompt)
        
        print('\n')
        print(result.text)


# load api key
def load_api_key(filepath="api_keys.json"):
    """Loads the API key from a JSON file."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("Gemini_API_KEY")
    except FileNotFoundError:
        print(f"Error: API key file '{filepath}' not found.")
        return None       
        
        

if __name__ == "__main__":
    """
    Main execution block of the habit tracking application.
    
    This block handles user interaction, menu display, and execution of different functionalities 
    based on user choices. It utilizes the Habit and User classes to manage habit tracking 
    and user data.
    """
    api_key = load_api_key()
    if api_key:
        genai.configure(api_key=api_key) 
    while True:
        
        choice = display_menu() # Display the main menu and get user choice

        if choice == 1:                         # 1
            # Handle user creation
            user_name = input("Enter your username: ")
            if user_name == 'menu':
                continue
            
            DOB = input("Enter your date of birth (YYYY-MM-DD): ")
            if DOB == 'menu':
                continue
            
            city = input("Enter your city: ")
            if city == 'menu':
                continue
            
            user_manager = User(user_name)    # Create a User instance
            user_manager.create_user(user_name, DOB, city)   # Create the user
            habit_tracker = Habit(user_name)   # Create a Habit instance for the user
            print(f"User {user_name} created!")
            
        elif choice == 2:                       # 2
            # Handle user login and display today's report
            user_name = input("Enter your username: ")
            if user_name == 'menu':
                continue
            
            user_data_filepath = os.path.join('data', f'user_data_{user_name}.csv')
            if not os.path.exists(user_data_filepath):
                print(f"Error: User data file for '{user_name}' NOT found.")
                retry = input("Try again? (y/n): ")
                if retry.lower() != 'y':
                    break 
            else:
                habit_tracker = Habit(user_name)
                user_manager = User(user_name)
                

            user_manager.llm_hello()
            print('\n')
            print('REPORT of habits:')
            print('\n')
            habit_tracker.today_report()   # Display today's report
            print('\n')
            print(f'Hello {user_name}!  What would you like to do today?')

        elif choice == 3:                       # 3
            # Handle adding a habit
            habit_name = input("Enter the habit name: ")
            if habit_name == 'menu':
                continue
            
            measured_in = input("What is the unit of measurement (e.g., hours, minutes, times): ")
            if measured_in == 'menu':
                continue
            
            period = input("How often is this habit tracked (daily or weekly): ")
            if period == 'menu':
                continue
            
            user_manager = User(user_name)  # Create a User instance
            user_manager.add_current_habit(habit_name, measured_in, period)
            print(f"Habit {habit_name} added!")

        elif choice == 4:                       # 4
            # Handle removing a habit
            habit_name = input("Enter the habit name to remove: ")
            if habit_name == 'menu':
                continue
            
            user_manager = User(user_name)
            user_manager.remove_current_habit(habit_name)
            print(f"Habit {habit_name} removed!")

        elif choice == 5:                       # 5
            # Handle tracking a habit
            habit_name = input("Enter the habit name to track: ")
            if habit_name == 'menu':
                continue
            
            tracked_value = float(input("Enter the value for tracking: "))
            habit_tracker.track_habit(habit_name, tracked_value)
            print(f"{habit_name} tracked!")
            
        elif choice == 6:                       # 6
            # Track a habit completed in the past.
            habit_name = input("Enter the habit name to track: ")
            if habit_name == 'menu':
                continue
            
            tracked_value = float(input("Enter the value for tracking: "))
            if tracked_value == 'menu':
                continue
            
            date_tracked = input("Enter the date you completed habit: YYYY-MM-DD  ")
            if date_tracked == 'menu':
                continue
            
            habit_tracker.track_historical_habit(habit_name, tracked_value, date_tracked)

        elif choice == 7:                       # 7
            # Handle correcting a tracked habit
            date_to_correct = input("Enter the date to correct (YYYY-MM-DD): ")
            if date_to_correct == 'menu':
                continue
            
            habit_to_correct = input("Enter the habit name to correct: ")
            if habit_to_correct == 'menu':
                continue
            
            new_value = float(input("Enter the new value: "))
            entry_number = int(input("Enter the entry number to correct (1 for first entry of day, 2 for the second, etc.): "))
            habit_tracker.correct_tracked_habit(date_to_correct, habit_to_correct, new_value, entry_number)
            print(f"{habit_to_correct} on {date_to_correct} corrected to {new_value}.")

        elif choice == 8:                       # 8
            # Handle analyzing the number of current habits
            habits = habit_tracker.get_current_habits()
            num_habits = len(habits)
            print(f"You are currently tracking {num_habits} habits.")
            print("Your current habits are:")
            for habit in habits:
                print(habit)

        elif choice == 9:                       # 9
            # Handle analyzing habits (specific, all, or current)
            analysis_type = input("Analyze (s)pecific habit, (a)ll habits, or (c)urrent habits? ")
            if analysis_type == 'menu':
                continue
            if analysis_type.lower() =='a':
                habit_tracker.analyze_all_habits(task='average', current=False)  
                habit_tracker.analyze_all_habits(task='total', current=False)   
                habit_tracker.analyze_all_habits(task='count', current=False) 
            elif analysis_type.lower() == 'c':
                habit_tracker.analyze_all_habits(task='average', current=True)
                habit_tracker.analyze_all_habits(task='total', current=True)  
                habit_tracker.analyze_all_habits(task='count', current=True) 
            elif analysis_type.lower() == 's':
                habit = input('Which habit\'s history do you want to see to see the history of: ')
                if habit == 'menu':
                    continue
                habit = habit.lower()
                units = habit_tracker.get_unit_of_measurement()      # get units of measurment json
                units = {k.lower(): v for k, v in units.items()}    # ensure all habit names are lower case
                habit_history, habit_past_values = habit_tracker.get_habit_history(habit)   # get habit history
                for hist, val in zip(habit_history, habit_past_values):
                    print(f'{habit} was tracked on {hist} for {val} {units[habit]}')
                    
                print(f'{habit} tracked {len(habit_history)} times and averaged {sum(habit_past_values)/len(habit_history):.1f} {units[habit]}')
                    
            else:
                print("Invalid choice.")

        elif choice == 10:                  # 10
            # Handle analyzing the longest streak
            habit_tracker.longest_streak()

        elif choice == 11:                  # 11
            # Handle analyzing if a habit is broken
            habit_name = input("Enter the habit name: ")
            if habit_name == 'menu':
                continue
            
            period = int(input("Enter the period to check for a broken streak: "))
            if period == 'menu':
                continue
            
            habit_tracker.is_broken(habit_name, period)

        elif choice == 12:                  # 12
            habit_tracker.today_report()

        elif choice == 13:                  # 13
            # Handle suggesting a habit
            user_manager.get_suggestions()

        elif choice == 14:                  # 14
            print("Exiting the Habit Tracker. Goodbye!")
            break
        
        # Add this condition to check for 'menu' input
        elif choice == 'menu': 
            print('You are currently on the main menu')
            continue  # Go back to the beginning of the loop and display the menu


