# Coding Practices

## Before you start coding

### Environments: 

Always develop within an environment and be thoughtful about dependencies you are adding. It is frustrating to get into but becomes super helpful to ensure we are all developing with the same context and can reproduce the system upon deployment! 

### Backend environment: poetry + conda 

You can just use poetry if we are only using python dependencies, but I generally use conda + poetry to super isolate dependencies and in case some whacky backend dependencies come into play (fortran?)

Your first time getting set up:

1. Install miniconda on your machine

2. You may have to close the terminal and reopen or run `$source bash` to activate these new updates

3. Run `$conda config --set auto_activate_base false`  so you don’t accidentally have an active environment when you don’t want it (signified by `(base)` at the start of your command line) 

4. Create a conda environment `conda create -n <env_name> python=<version>` for example `conda create -n route_rangers_db_env python=3.11` 

5. Follow the steps in the cli to get activated, you will know when its active because you will see the name at the beginning of the command line `(route_rangers_db)megans_macbook…$`

6. Install poetry `pip install poetry`

7. From the backend folder (where there should be a `poetry.lock` file) run `poetry install` to install all of the python dependencies 

TODO: If there are other non-python backend dependencies we need to track those using a requirements.txt file and run `conda install` . Update if we get to that need

Begin development (see below)!! 

#### Environment usage for general development:

1.  Run `conda activate <env_name>`

2. From backend directory run `poetry install` to update your environment with any changes introduced from others

3. If you need to add a new dependency run `poetry add <new_python_package>` so the dependency will be recorded and others will update their environments accordingly

4. If you need to change environments (ex. changing from backend to frontend) run `conda deactivate` and then `conda activate <new_env_name>`

### Frontend environment: npm + conda (TODO update with learnings)

I think very similar process, following these instructions, see above for getting set up with conda the first time. 

### Keys and Secrets:

We will likely end up with some sort of keys and secrets for different secure components such as API keys for pulling data, AWS access, DB user and password credentials. WE DO NOT WANT THESE IN GITHUB. 

In the root of your repository create a `.env` file where you can store your secrets and passwords [longer instructions](https://dev.to/jakewitcher/using-env-files-for-environment-variables-in-python-applications-55a1). for example: 
```
GCP_PROJECT_ID=my-project-id
SERVICE_ACCOUNT_FILE=path/to/serviceAccountCredentials
STORAGE_BUCKET_NAME=my-super-important-data
```
because `.env` will be in the `.gitignore` preventing you from accidentally committing that information. Then when developing you can assume that each person will have a copy of the necessary keys in their own `.env` file, you can share them using a secure password sharing tool if needed. 

To then use the keys in python, it will look something like: 
```
import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
STORAGE_BUCKET_NAME = os.getenv('STORAGE_BUCKET_NAME')
```

TODO update with frontend usage needs

### Linting Practices:

#### Python Linting
Linting will be a blocking problem in backend PR’s because unnecessary reformatting due to newly linting or improperly linting can make it really hard to parse what the actual coding changes are in a PR, lots of unrelated changes will be added due to lines and spaces moving around if there is improper linting.

For Python we will be using [black](https://pypi.org/project/black/) and [flake8](https://flake8.pycqa.org/en/latest/) linting tooling using all of the declared defaults (there are ways to create config files and declare certain linting rules but we will leave that out for now). 

Setting up VSCode for linting. There are a lot of resources to set up vscode linting if you google around, I find it easiest to do the following things:

1. In the Extensions tab (left-most column in VS Code, the symbol with the four blocks), install `Flake8`  and `Black Formatter`  extensions (both licensed by Microsoft)
2. In main directory, create a folder named `.vscode`
3. In `.vscode` folder, create a `settings.json`  file
4. Paste the following inside the (empty) `settings.json` file:

   ```
   {
    "editor.formatOnSave": true,
    "black-formatter.args": [
        "--line-length",
        "88",
    ],
    "flake8.args": [
        "--max-line-length",
        "88",
    ]
   }
   ```
5. Done!

#### For JavaScript 

We likely want to have similar practices with [prettier](https://prettier.io/), TODO update as we learn more. 

<ins>Linting Summary:</ins> always lint before commiting and especially before PR’s 

### Typing:

Will not be a blocking problem in PR’s but the more you have the better, it helps avoid SO many bugs.

#### For Python
I highly encourage people to use [typing](https://docs.python.org/3/library/typing.html), particularly in their function declarations. This looks something like:
```
# some types you need to import, others you don't
# google when you get an error
from typing import Union, Optional, Dict, List

def my_func(list_of_names: List[str], 
            num: int, 
            mapping_dict: Dict, 
            multivar: Union[None: float] = None, 
            default_setting: Optional[str] = '') -> Tuple[int, str]:
  """
  This function does something with a lot of variables.
  
  Inputs:
    list_of_names(List[str]): list of all names to lookup
    num(int): age
    mapping_dict(Dict): dictionary to map age to year
    multivar(Union[None: float]): float value if you want to replace default
    default_setting(Optional[str]): optional string defaults to empty
  
  Returns:
    age_name_tup (Tuple[int, str]): age and name of person
  """
  # Do something
```


You can use types within a function, for example:
```
# function declared above
new_age: int = 32
# ... 
```
But I think its a bit overkill unless you have a lot of complex functionality you want to be clear about (but that may be a sign that you need to refactor anyway) 

Typing is not enforced by Python, so if you don’t comply nothing will break, but we can use [mypy](https://mypy-lang.org/) if folks want enforcement of explicit types like linting.

### For JavaScript

I recommend using [TypeScript](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html#typescript-a-static-type-checker) instead of JavaScript. There are ways to do both javascript and typescript in the same codebase that seem kind of complicated and there doesn’t seem to be a lighter touch way to do it like in python. If that is too much of a change though we can just do JS. 
UPDATE: just sticking w/ JS

### Testing:

After (or even before with [TDD](https://en.wikipedia.org/wiki/Test-driven_development#:~:text=Test%2Ddriven%20development%20(TDD),software%20against%20all%20test%20cases.)!!!) every new feature or bugfix, a test should be added (not needed for refactor PRs, but you do need to make sure all tests are still passing). There are a lot of different types of testing, unit tests, smoke tests, performance testing, etc. For our purposes we will likely just be doing unit tests which are generally very small and just ensure the one thing we built does the thing we expect. 

The idea with this is isolating the functionality as best we can, this often requires “mocking” or hard-coding things around it, for example using an ephemeral mocked database in order to fake retrieving the exact data we need every time so that we can test something else in a predictable way instead of interacting with a live db that may provide different information as new data comes into it. If you are stuck on how to frame a test, reach out! 

#### For Python

[pytest](https://docs.pytest.org/en/8.0.x/) is a great tool. See CAPP 122 HW assignments for some good test examples. 

But the <ins>process is as follows:</ins>

1. The repo will have a `test` folder, every file in this folder with the format `test_<thing_tested>.py` will be run automatically 

2. Every “function” in a test file will be run a test in the suite

3. As mentioned above, each test tries to test something very small, like a function so for a function like:
```
def add_nums_plus_one(num_a: int, num_b: int) -> int:
  # would ideally have a docstring
  return(num_a + num_b + 1)
```
You would then have a test in `tests/test_math.py` along the lines of:
```
from module.math import add_nums_plus_one

def test_add_nums_plus_one():
  assert add_nums_plus_one(1, 2) == 4
```
You can also configure one test to run through many different input examples [see the docs](https://docs.pytest.org/en/8.0.x/how-to/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions).

4. All tests can then be run by calling `pytest` from the command line

    a) There are some handy flags and ways to only specify specific tests, refer to the pytest docs for that

5. You will then have a report of all tests passing that you can screenshot and add to your PR, or build out automatic tests before opening a PR

#### For JavaScript

Frontend is a bit harder to write because you often need to visually inspect or test complex navigation, there are tools like [Selenium](https://www.selenium.dev/). I found this but I haven’t tried this [Selenium set up guide](https://medium.com/@oyetoketoby80/automating-your-front-end-application-testing-with-selenium-8e9d51f0f73c). 

For frontend I think testing will not be a blocking requirement in PR’s but a report that new functionality was inspected and manually tested will be helpful!

**Side note: Code Coverage - How good are the tests anyway? 

This seems maybe like a reach for the standards of this project, but we can discuss.

Code coverage tools [such as this](https://coverage.readthedocs.io/en/7.4.4/) evaluate how much of the code is covered by tests and sheds light on gaps where code has not been tested (and is there more at risk of having bugs). In long term projects it is a good mechanism for evaluating how well you are doing in evaluating the functionality of your code (though there is a fair amount of debate aroung the different methods and how they reflect the actual paths of exection in the code). TLDR we probably don’t need to do this now. 

## Ready to code?

Do you have your repo cloned, your environment activated, dependencies installed and VSCode configured? The following process will guide you through a structured development process. 

1. Assign an issue to yourself, the issue must be ready for development with all upstream work and designs done.

2. Create a branch from `main` and name it the issue name, for example, if you are taking issue “#13 Dropdown Menu Component” create a branch 13-dropdown-menu-component (you should be able to do this from the issue) 

3. Checkout the branch
```
$ git pull # to get all updates
$ git checkout 13-dropdown-menu-component
code . # to open in VSCode
```

4. Write a test for the work that you plan to do (yes, this is not always possible), trying to scope the test as small as possible. Make sure the test fails!

5. Begin development on the task to address only the scope of the issue, if you encounter something that needs to be dealt with, make it an issue!

6. Commit early, commit often! with meaningful commit messages 

7. Run the entire test suite to make sure you didn’t accidentally break something in the process

8. If you want to refactor the code you have added at this point, you can clean things up, and then retest. 

9. Document functions, Lint code, Screenshot Tests

10. Open PR with:

    a. Title states what you did “Dropdown Menu Component Added” 

    b. Description of main functionality (cross reference issue description)

    c. Note anything you want reviewers to take into account (can be comments on specific lines of code to explain or ask for a second opinion)

    d. Add screenshots of tests passing

    e. Make sure every file with changes is there for a reason 

    f. Request review from 2 people. 

    g. PRs should not be open for more than 2 business days 

11. Upon approval from all reviewers, merge and squash commits (to make it easier to see major changes) - <ins>Authors merge their own PRs</ins>


## Deployment Process
