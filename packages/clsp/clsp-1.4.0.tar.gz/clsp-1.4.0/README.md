# CLSP

<img src="https://img.shields.io/badge/Version-1.4.0-orange"> <img src="https://img.shields.io/badge/Linux-yes-green"> <img src="https://img.shields.io/badge/MacOS-yes-green"> <img src="https://img.shields.io/badge/Windows-yes-green"><!-- <img src="https://img.shields.io/badge/FreeBSD-yes-green">-->

CLSP short for **C**ommand **L**ine **S**election **P**rompt, is a by fzf inspired, minimalistic, and fast to navigate single choice prompt.

```python
from clsp import select

user_choice = select([1, 2, 3], info="Prompt:")

print(f"Selected: {user_choice}")
print(f"Selected index: {user_choice.index}")

if user_choice.search:
    print(f"Searched for: {user_choice.search}")
    print(f"Search result: {user_choice.search_result}")
```

![Preview](https://raw.githubusercontent.com/DISTREAT/clsp/master/docs/preview.gif)

## Documentation

|      Name       | Type  |                                  Description                                        |
| --------------- | ----- | ----------------------------------------------------------------------------------- |
| title           | STR   | Information shown above the prompt.                                                 |
| prompt          | STR   | Text in front of user input.                                                        |
| search          | STR   | Pre-insert text into the input prompt.                                              |
| current         | INT   | Index as the default selection.                                                     |
| rows            | INT   | Amount of choices at a time.                                                        |
| cutoff          | FLOAT | Precision of search. (0 < x < 1).                                                   |
| amount_results  | INT   | The maximum amount of search results to return.                                     |
| highlight_color | STR   | Highlight color for search (black, red, green, yellow, blue, magenta, cyan, white). |
| full_exit       | BOOL  | Exit completely or pass None on KeyBoardInterrupt or ESC.                           |
| ignore_warnings | BOOL  | Ignore warnings.                                                                    |

