# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:49:07 2025

@author: maxx9
"""
import os
import pytest
import datetime
from habit_tracker import Habit, User
import io
from unittest.mock import patch
import re
from contextlib import redirect_stdout




# Test cases for user creation (menu option 1)
def test_create_user():
    user_manager = User("testuser")
    user_manager.create_user("testuser", "2000-01-01", "Test City")
    assert os.path.exists(os.path.join('data', 'user_data_testuser.csv'))
    assert os.path.exists(os.path.join('data', 'tracking_testuser.csv'))
    
# Helper function to create a test user and track habits
def setup_test_user(username, num_weeks=5):
    user_manager = User(username)
    user_manager.create_user(username, "2000-01-01", "Test City")
    habit_tracker = Habit(username, today= datetime.date.today().strftime("%Y-%m-%d"))

    # Add daily and weekly habits
    user_manager.add_current_habit("reading", "pages", "daily")
    user_manager.add_current_habit("exercise", "minutes", "weekly")
    user_manager.add_current_habit("drawing", "minutes", "daily")

    # Track habits for the past num_weeks
    today = datetime.date.today()
    for i in range(num_weeks * 7):
        current_date = today - datetime.timedelta(days=i)
        habit_tracker.track_historical_habit("reading", 10, current_date.strftime("%Y-%m-%d"))
        if i % 7 == 0:  # Track weekly habit once a week
            habit_tracker.track_historical_habit("exercise", 60, current_date.strftime("%Y-%m-%d"))
    return habit_tracker, user_manager

# Test cases for logging in (menu option 2)
def test_log_in():
    habit_tracker, user_manager = setup_test_user("testuser")
    habit_tracker, user_manager = setup_test_user("testuser")
    
    # Check if the Habit and User objects are created successfully
    assert isinstance(habit_tracker, Habit)
    assert isinstance(user_manager, User)
    
    # Check if the username is set correctly in both objects
    assert habit_tracker._Habit__username == "testuser"  # Accessing private attribute for testing
    assert user_manager._User__username == "testuser"

# Test cases for adding a habit (menu option 3)
def test_add_habit():
    habit_tracker, user_manager = setup_test_user("testuser")
    user_manager.add_current_habit("coding", "hours", "daily")
    assert "coding" in user_manager.get_current_habits()
    
    
# Test cases for removing a habit (menu option 4)
def test_remove_habit():
    habit_tracker, user_manager = setup_test_user("testuser")
    user_manager.remove_current_habit("drawing")
    assert "drawing" not in user_manager.get_current_habits()

# Test cases for tracking a habit (menu option 5)
def test_track_habit():
    habit_tracker, user_manager = setup_test_user("testuser")
    habit_tracker.track_habit("reading", 15)
    df_tracking = habit_tracker.load_tracking_data()
    tracked_value = df_tracking[(df_tracking['date'] == habit_tracker._Habit__today) & (df_tracking['habit'] == 'reading')].iloc[-1,2]
    print(f"Tracked value: {tracked_value}")
    assert tracked_value == 15

# Test cases for tracking a historical habit (menu option 6)
def test_track_historical_habit():
    habit_tracker, user_manager = setup_test_user("testuser")
    habit_tracker.track_historical_habit("reading", 20, "2025-01-15")
    df_tracking = habit_tracker.load_tracking_data()
    print( df_tracking[(df_tracking['date'] == '2025-01-15') & (df_tracking['habit'] == 'reading')])
    assert df_tracking[(df_tracking['date'] == '2025-01-15') & (df_tracking['habit'] == 'reading')].iloc[-1,2] == 20

# Test cases for correcting a tracked habit (menu option 7)
def test_correct_tracked_habit():
    habit_tracker, user_manager = setup_test_user("testuser")
    habit_tracker.correct_tracked_habit("2025-01-21", "reading", 25)
    df_tracking = habit_tracker.load_tracking_data()
    assert df_tracking[(df_tracking['date'] == '2025-01-21') & (df_tracking['habit'] == 'reading')].iloc[-1,2] == 25

# Test cases for analyzing the number of current habits (menu option 8)
def test_analyze_number_of_current_habits():
    habit_tracker, user_manager = setup_test_user("testuser")
    habits = habit_tracker.get_current_habits()
    num_habits = len(habits)
    assert num_habits == 3  # Initially 2 habits

# Test cases for analyzing habits (specific, all, or current) (menu option 9)
def my_function():
    print("This will be printed to the console.")

with io.StringIO() as buf, redirect_stdout(buf):
    my_function()  # Output of my_function is redirected to buf
    output = buf.getvalue()  # Get the captured output from the buffer

print("Captured output:", output)
def test_analyze_habits():
    habit_tracker, user_manager = setup_test_user("testuser")


    # # Capture printed output
    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.analyze_all_habits(task='average', current=True)
        output = buf.getvalue()
     
    assert "For Habit: reading, you AVERAGED 10.0 pages" in output
    assert "For Habit: exercise, you AVERAGED 60.0 minutes" in output

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.analyze_all_habits(task='total', current=False)
        output = buf.getvalue()
    
    assert "For Habit: reading, you TOTALLED 350 pages" in output
    assert "For Habit: exercise, you TOTALLED 300 minutes" in output

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.analyze_all_habits(task='count')  # current=True by default
        output = buf.getvalue()
    
    assert "For Habit: reading, you TRACKED 35 times" in output
    assert "For Habit: exercise, you TRACKED 5 times" in output

# Test cases for analyzing the longest streak (menu option 10)
def test_analyze_longest_streak():
    habit_tracker, user_manager = setup_test_user("testuser")

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.longest_streak()
        output = buf.getvalue()

    # Assert the expected output for daily and weekly streaks
    assert "Your current longest daily streak is 35 for reading since 2024-12-24" in output
    assert "Your current longest weekly streak is 5 for exercise since 2024-12-30" in output

    # Assert the output for the longest tracked habit
    assert "The habit your have been tracking for the longest time is reading since 2024-12-24" in output

# Test cases for analyzing if a habit is broken (menu option 11)
def test_analyze_if_habit_is_broken():
    habit_tracker, user_manager = setup_test_user("testuser")

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.is_broken("reading", 35)  # Daily habit, not broken
        output = buf.getvalue()
    assert "You had a streak for reading for the last 35 days" in output

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.is_broken("exercise", 6)  # Weekly habit, broken
        output = buf.getvalue()
    assert "You had a streak of 5" in output  # Check for partial output

# Test cases for today's report (menu option 12)
def test_todays_report():
    habit_tracker, user_manager = setup_test_user("testuser")

    with io.StringIO() as buf, redirect_stdout(buf):
        habit_tracker.today_report()
        output = buf.getvalue()
    # Add assertions based on the expected output of today_report
    # For example:
    assert "Habits Tracked today" in output
    assert "reading" in output
    assert "exercise" in output

# Test cases for suggesting a habit (menu option 13)
@patch('google.generativeai.GenerativeModel.generate_content')  # Mock the Gemini API call
def test_suggest_habit(mock_generate_content):
    habit_tracker, user_manager = setup_test_user("testuser")

    # Set up the mock return value
    mock_response = """
    Template:
        Here are some potential habits you might be interested in.
            Habit 1. You might be interested in Habit 1 because ......
            Habit 2. You might be interested in Habit 1 because ......
            Habit 3. You might be interested in Habit 1 because ......
            Habit 4. You might be interested in Habit 1 because ......
    """
    mock_generate_content.return_value.text = mock_response

    with io.StringIO() as buf, redirect_stdout(buf):
        user_manager.get_suggestions()
        output = buf.getvalue()

    # Check if the output matches the expected template
    # assert re.match(r"Template:\s*Here are some potential habits.*", output, re.DOTALL)  # Use regex for flexible matching
    # assert  "Habit 4. You might be interested in Habit 1 because" in output
    # assert output == mock_response
    # Assert that the output contains the expected habit strings
    assert "Habit 1." in output
    assert "Habit 2." in output
    assert "Habit 3." in output
    assert "Habit 4." in output

# Test cases for the Habit class methods
def test_calculate_streak_daily():
    habit_tracker, user_manager = setup_test_user("testuser")
    
    # Check the streak for the daily habit ("reading")
    # Assuming setup_test_user tracks "reading" daily for 5 weeks
    streak, _ = habit_tracker.calculate_streak("reading")  # Get streak and last_date_tracked
    assert streak == 5 * 7  # 5 weeks of daily habit

    # Add a new daily habit and track it for a few days
    user_manager.add_current_habit("writing", "hours", "daily")
    habit_tracker.track_habit("writing", 2)
    habit_tracker.track_historical_habit("writing", 1.5, (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")) 
    streak, _ = habit_tracker.calculate_streak("writing")  # Get streak and last_date_tracked
    assert streak == 2

def test_calculate_streak_weekly():
    habit_tracker, user_manager = setup_test_user("testuser")
    
    # Check the streak for the weekly habit ("exercise")
    # Assuming setup_test_user tracks "exercise" weekly for 5 weeks
    streak, _ = habit_tracker.calculate_streak("exercise")  # Get streak and last_date_tracked
    assert streak == 5  # 5 weeks of weekly habit

    # Add a new weekly habit and track it for a few weeks
    user_manager.add_current_habit("meditation", "minutes", "weekly")
    habit_tracker.track_historical_habit("meditation", 30, (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
    habit_tracker.track_habit("meditation", 45)
    streak, _ = habit_tracker.calculate_streak("meditation")  # Get streak and last_date_tracked
    assert streak == 2