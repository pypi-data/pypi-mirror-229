This is a simple set of functions to compute probabilities for Risus: The
Anything RPG.

Risus was designed by S. John Ross and is currently published by Big Dice
games: https://www.risusrpg.com/

[![builds.sr.ht status](https://builds.sr.ht/~p0mf.svg)](https://builds.sr.ht/~p0mf?)

# Installing
This project is on pypi at https://pypi.org/project/risus-py/. It can be installed thus:

```
pip install risus-py
```

This `risus.engine` depends on `icepool`
(https://highdiceroller.github.io/icepool/), and `risus.table` depends
on `numpy` and `pandas`. These should all be automatically installed by `pip`.

# Testing
All the modules are tested from their docstring examples. After
installation, you can execute the tests by running `risus` as a
module:

```
python3 -m risus
```

If all goes well, this should appear to hang for an instant and return
nothing. It will complain in case of a problem.

# Development
Clone the git repository.

```
git clone https://git.sr.ht/~p0mf/risus-py
```

When trying out new features, I use `pip install -e` to install an
editable copy of risus in a virtual environment:

```
pip install -e .
```

I build `risus-py` using the PyPA `build`
(https://github.com/pypa/build) module and upload it to PyPI using
`twine` (https://twine.readthedocs.io/en/stable/):

```
python3 -m build && twine upload dist/*
```

This monster is the entire release pipeline: it installs locally,
tests, then builds for distribution and uploads.

```
pip install -e . && python -m risus && rm -rf dist/* && python -m build && twine upload dist/*
```

## Wishlist
### Features
* Pumps and double pumps.
* Factor out rule variations (explosions, breakthroughs).
* Web application using pyodide and chart.js, like the other `icepool`
  applications.

### Efficiency
* Parallelized computation, and other optimizations. Is it possible to
  do better than quadratic time (in the maximum value of the potencies
  considered) when constructing a table?
### Polish
* Clean up documentation: there's still some quirkiness to the way the
  README is integrated into the module documentation. Given how easy
  it is to pull up documentation locally with pdoc, static site
  hosting is a low priority.
* Rationalize rules variations: for now, the engine passes around a
  whole mess of configuration flags.
### Infrastructure
* Automate build test and release, potentially as a continuous integration
  job on sourcehut.


# Basic API Calls
See the documentation for the module for an overview of possible
calls. It can be accessed with pdoc (https://pdoc.dev/), from your
terminal once `risus-py` has been installed. This command will open
the documentation in your default browser:

```
pdoc risus
```

In short, there are functions to compute win/loss chances for
`combat`, `team_combat` (including inappropriate clichés),
`single_action_conflict`, and `target_number` rolls. All the calls
return `float`, and take a `bool` argument `percent` to indicate
whether the returned value should be scaled 0 to 100 (`True`) or 0 to
1 (`False`). The default is `False`.

# Tables
More complex variations are possible: the `risus.table` module contains
function to generate xarrays of victory probabilities. The file
`app/dataset.py` is an example of simple web interface using dtale. Here are
some example tables.

## Combat:
### Ordinary
As an example, here is how you could calculate an ordinary combat table for up to (10) versus (10).
```
>>> import pandas as pd
>>> from risus.table import make_combat_table
>>> make_combat_table(10, percent=True).round(1).to_pandas()

enemy_potency      1      2      3      4      5      6     7     8     9     10
attack_potency
1                50.0    5.0    0.1    0.0    0.0    0.0   0.0   0.0   0.0   0.0
2                95.0   50.0    8.2    0.3    0.0    0.0   0.0   0.0   0.0   0.0
3                99.9   91.8   50.0   10.5    0.7    0.0   0.0   0.0   0.0   0.0
4               100.0   99.7   89.5   50.0   12.2    1.1   0.0   0.0   0.0   0.0
5               100.0  100.0   99.3   87.8   50.0   13.7   1.5   0.1   0.0   0.0
6               100.0  100.0  100.0   98.9   86.3   50.0  14.8   1.9   0.1   0.0
7               100.0  100.0  100.0  100.0   98.5   85.2  50.0  15.8   2.3   0.1
8               100.0  100.0  100.0  100.0   99.9   98.1  84.2  50.0  16.7   2.7
9               100.0  100.0  100.0  100.0  100.0   99.9  97.7  83.3  50.0  17.5
10              100.0  100.0  100.0  100.0  100.0  100.0  99.9  97.3  82.5  50.0
```

### Boxcars and Breakthroughs
A similar series of manipulations produces one with boxcars and breakthroughs in effect.

```
>>> make_combat_table(10, percent=True, breakthrough=True).round(1).to_pandas()

enemy_potency      1      2      3      4      5      6     7     8     9     10
attack_potency
1                51.6    9.4    0.6    0.0    0.0    0.0   0.0   0.0   0.0   0.0
2                95.2   52.3    9.6    0.5    0.0    0.0   0.0   0.0   0.0   0.0
3                99.9   92.2   50.9   10.9    0.7    0.0   0.0   0.0   0.0   0.0
4               100.0   99.7   89.7   50.3   12.4    1.1   0.0   0.0   0.0   0.0
5               100.0  100.0   99.4   87.8   50.1   13.7   1.5   0.1   0.0   0.0
6               100.0  100.0  100.0   98.9   86.4   50.0  14.8   1.9   0.1   0.0
7               100.0  100.0  100.0  100.0   98.5   85.2  50.0  15.8   2.3   0.1
8               100.0  100.0  100.0  100.0   99.9   98.1  84.2  50.0  16.7   2.7
9               100.0  100.0  100.0  100.0  100.0   99.9  97.7  83.3  50.0  17.5
10              100.0  100.0  100.0  100.0  100.0  100.0  99.9  97.3  82.5  50.0
```


## Single-action conflict:
The function `make_single_action_conflict_table` takes a number representing to
size of the square table to produce.

### Ordinary
```
enemy_potency      1      2      3      4     5     6     7     8     9     10
attack_potency
1                50.0   10.0    1.2    0.1   0.0   0.0   0.0   0.0   0.0   0.0
2                90.0   50.0   16.3    3.7   0.6   0.1   0.0   0.0   0.0   0.0
3                98.8   83.7   50.0   20.5   6.3   1.5   0.3   0.0   0.0   0.0
4                99.9   96.3   79.5   50.0  23.5   8.6   2.6   0.6   0.1   0.0
5               100.0   99.4   93.7   76.5  50.0  25.7  10.7   3.7   1.1   0.3
6               100.0   99.9   98.5   91.4  74.3  50.0  27.5  12.6   4.9   1.6
7               100.0  100.0   99.7   97.4  89.3  72.5  50.0  28.9  14.2   6.0
8               100.0  100.0  100.0   99.4  96.3  87.4  71.1  50.0  30.1  15.7
9               100.0  100.0  100.0   99.9  98.9  95.1  85.8  69.9  50.0  31.2
10              100.0  100.0  100.0  100.0  99.7  98.4  94.0  84.3  68.8  50.0

```

### Boxcars and Breakthroughs
```
enemy_potency               1      2      3      4     5     6     7     8     9     10
attack_potency
1                         51.6   18.2    6.9    2.7   1.1   0.0   0.0   0.0   0.0   0.0
2                         90.0   50.0   17.4    5.4   2.1   0.9   0.4   0.1   0.1   0.0
3                         98.8   83.7   50.0   20.6   6.5   1.8   0.6   0.3   0.1   0.1
4                         99.9   96.3   79.5   50.0  23.5   8.6   2.6   0.7   0.2   0.1
5                        100.0   99.4   93.7   76.5  50.0  25.7  10.7   3.7   1.1   0.3
6                        100.0   99.9   98.5   91.4  74.3  50.0  27.5  12.6   4.9   1.6
7                        100.0  100.0   99.7   97.4  89.3  72.5  50.0  28.9  14.2   6.0
8                        100.0  100.0  100.0   99.4  96.3  87.4  71.1  50.0  30.1  15.7
9                        100.0  100.0  100.0   99.9  98.9  95.1  85.8  69.9  50.0  31.2
10                       100.0  100.0  100.0  100.0  99.7  98.4  94.0  84.3  68.8  50.0
```

## Target number:
Here's a target number table for games with big pumpers: you feelin' lucky, punk?
```
attack_potency     1      2      3      4      5      6      7      8      9      10     11     12
enemy_potency
1               100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
2                83.3  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
3                66.7   97.2  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
4                50.0   91.7   99.5  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
5                33.3   83.3   98.1   99.9  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
6                16.7   72.2   95.4   99.6  100.0  100.0  100.0  100.0  100.0  100.0  100.0  100.0
7                 0.0   58.3   90.7   98.8   99.9  100.0  100.0  100.0  100.0  100.0  100.0  100.0
8                 0.0   41.7   83.8   97.3   99.7  100.0  100.0  100.0  100.0  100.0  100.0  100.0
9                 0.0   27.8   74.1   94.6   99.3   99.9  100.0  100.0  100.0  100.0  100.0  100.0
10                0.0   16.7   62.5   90.3   98.4   99.8  100.0  100.0  100.0  100.0  100.0  100.0
11                0.0    8.3   50.0   84.1   96.8   99.5  100.0  100.0  100.0  100.0  100.0  100.0
12                0.0    2.8   37.5   76.1   94.1   99.0   99.9  100.0  100.0  100.0  100.0  100.0
13                0.0    0.0   25.9   66.4   90.2   98.0   99.7  100.0  100.0  100.0  100.0  100.0
14                0.0    0.0   16.2   55.6   84.8   96.4   99.4   99.9  100.0  100.0  100.0  100.0
15                0.0    0.0    9.3   44.4   77.9   93.9   98.8   99.8  100.0  100.0  100.0  100.0
16                0.0    0.0    4.6   33.6   69.5   90.4   97.8   99.6  100.0  100.0  100.0  100.0
17                0.0    0.0    1.9   23.9   60.0   85.5   96.2   99.3   99.9  100.0  100.0  100.0
18                0.0    0.0    0.5   15.9   50.0   79.4   93.9   98.6   99.8  100.0  100.0  100.0
19                0.0    0.0    0.0    9.7   40.0   72.1   90.6   97.6   99.5   99.9  100.0  100.0
20                0.0    0.0    0.0    5.4   30.5   63.7   86.3   96.1   99.1   99.9  100.0  100.0
21                0.0    0.0    0.0    2.7   22.1   54.6   80.8   93.9   98.5   99.7  100.0  100.0
22                0.0    0.0    0.0    1.2   15.2   45.4   74.3   90.9   97.5   99.5   99.9  100.0
23                0.0    0.0    0.0    0.4    9.8   36.3   66.8   87.0   96.1   99.1   99.8  100.0
24                0.0    0.0    0.0    0.1    5.9   27.9   58.6   82.1   94.0   98.4   99.7   99.9
25                0.0    0.0    0.0    0.0    3.2   20.6   50.0   76.2   91.3   97.5   99.4   99.9
26                0.0    0.0    0.0    0.0    1.6   14.5   41.4   69.5   87.7   96.1   99.0   99.8
27                0.0    0.0    0.0    0.0    0.7    9.6   33.2   62.0   83.3   94.2   98.4   99.6
28                0.0    0.0    0.0    0.0    0.3    6.1   25.7   54.0   78.0   91.7   97.5   99.4
29                0.0    0.0    0.0    0.0    0.1    3.6   19.2   46.0   71.8   88.4   96.2   99.0
30                0.0    0.0    0.0    0.0    0.0    2.0   13.7   38.0   65.0   84.3   94.4   98.3
31                0.0    0.0    0.0    0.0    0.0    1.0    9.4   30.5   57.6   79.5   92.0   97.5
32                0.0    0.0    0.0    0.0    0.0    0.5    6.1   23.8   50.0   73.9   89.0   96.2
33                0.0    0.0    0.0    0.0    0.0    0.2    3.8   17.9   42.4   67.6   85.3   94.6
34                0.0    0.0    0.0    0.0    0.0    0.1    2.2   13.0   35.0   60.8   80.9   92.4
35                0.0    0.0    0.0    0.0    0.0    0.0    1.2    9.1   28.2   53.6   75.8   89.6
36                0.0    0.0    0.0    0.0    0.0    0.0    0.6    6.1   22.0   46.4   70.0   86.2
37                0.0    0.0    0.0    0.0    0.0    0.0    0.3    3.9   16.7   39.2   63.6   82.2
38                0.0    0.0    0.0    0.0    0.0    0.0    0.1    2.4   12.3   32.4   56.9   77.4
39                0.0    0.0    0.0    0.0    0.0    0.0    0.0    1.4    8.7   26.1   50.0   72.1
40                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.7    6.0   20.5   43.1   66.2
41                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.4    3.9   15.7   36.4   59.9
42                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.2    2.5   11.6   30.0   53.3
43                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1    1.5    8.3   24.2   46.7
44                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.9    5.8   19.1   40.1
45                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.5    3.9   14.7   33.8
46                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.2    2.5   11.0   27.9
47                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1    1.6    8.0   22.6
48                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.9    5.6   17.8
49                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.5    3.8   13.8
50                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.3    2.5   10.4
51                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1    1.6    7.6
52                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1    1.0    5.4
53                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.6    3.8
54                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.3    2.5
55                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.2    1.7
56                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1    1.0
57                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.6
58                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.4
59                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.2
60                0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.0    0.1
```
