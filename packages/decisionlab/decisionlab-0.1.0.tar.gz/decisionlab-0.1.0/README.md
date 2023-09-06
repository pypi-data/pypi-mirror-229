# decision_lab

`pip install decisionlab`

## Introduction

`decision_lab` is a Python library that provides a simple and intuitive interface for creating and managing "decisions" that can be accessed via APIs. With `decision_lab`, you can make code behavior changes without changing the code itself, saving time and money on development and maintenance.

## Key Features

- Create and edit decisions through a user-friendly interface.
- Access decisions via APIs to make code behavior changes without modifying the codebase.
- Improve user experience and business outcomes with flexible and scalable decision management.

## Use Cases

- Change the welcome message on a website header by editing a decision in the UI, and the change will be reflected on the website.
- Modify the user list in a backend Python code by calling `decision.user_list`, without making changes to the codebase.

## Getting Started

To get started with `decision_lab`, you need to provide the UUID for accessing decisions. The UUID can be set as an environment variable `DECISION_LAB_UUID` or passed as an argument when creating an instance of the `DecisionLab` class.

```python
from decisionlab import DecisionLab

# Create an instance of DecisionLab with UUID
decision_lab = DecisionLab(uuid='your-uuid')

# Get the list of decisions
decisions_list = decision_lab.get_decisions_list()

# Get a specific decision by name
decision = decision_lab.get_decision('decision_name')
``` 

If you are using the Team features, you can also use this library like this: 
```
team_decision = DecisionLab(token='api_token', auth_type='TEAMS')

``` 

With this object you can now list your decisions 
```
team_decision.list_decisions() 
```

Get the single value of a decision 
```
team_decision.get_decision('decision_name')
```

Or update the value of a decision 
```
team_decision.update_decision_value('decision_name', 'new decision value')
``` 

The library will guess the type of the decision and will try to convert the value to the right type.




