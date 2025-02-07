# habit-tracking-app

This is a simple habit tracking app developed as a university project. It allows users to:

* Create and manage user profiles
* Add, track, and remove habits
* Analyze habit data (streaks, averages, totals)
* Get suggestions for new habits (using Google Gemini)

## Installation

1. Clone this repository: `git clone https://github.com/your-username/habit-tracking-app.git`
2. Install the required packages: `pip install -r requirements.txt`

## Usage

1. Run the app: `python habit_tracker.py`
2. Follow the on-screen menu to create a user profile or log in, add habits, track your progress, and analyze your data.
   *NOTE: testuser will only work in unit tests as today is moved from a stagnic position to activly tied to today*
   * this can be changed in habit class inititization*

### Example

To track a new habit:

1. From the main menu, select option 3 to add a new habit.
2. Enter the habit name, unit of measurement, and tracking frequency (daily or weekly).
3. Select option 5 to track the habit and enter the value for tracking.

## Testing

`test_habit.py` files contain unit tests for the app. To run the tests, use `pytest`.

## Known Issues

* The Google Gemini integration may not always provide relevant suggestions.
* Error handling for incorrect user input could be improved.

## Author

Brandyn Ewanek
brandyn.ewanek@gmail.com
