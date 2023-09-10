# nfllivepy

## About
Python package for obtaining live nfl play by play data

For pbp data for past games, view [nfl-data-py](https://pypi.org/project/nfl-data-py/) which gets its data from the [nflreadr](https://github.com/nflverse/nflreadr) package. This data contains postprocessing variables which are more detailed then the ones in the live data.

Much of this package is inspired by the work of [nfl-nerd](https://github.com/nntrn/nfl-nerd). For a full list of all the ESPN v2 NFL api endpoints, click [here](https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c#v2sportsfootballleaguesnflseasonsyeartypes).

## Installation
This project can be installed with pip by running:  
`pip install nfllivepy`

## Usage
nfllivepy is very simple and easy to use, wth two simple methods to obtain live data.

```python
from nfllivepy.requester.pbp_requester import PBPRequester

requester = PBPRequester()

# Get live data for all current games
requester.get_live_pbp_all_games()

# Get live data for the Chicago Bears
requester.get_live_pbp_for_team("CHI")
```