# ninetydf

90 Day Fiancé dataframes

## Example usage

```python
from ninetydf import couples, seasons


def main():
    print(couples.head())
    print(seasons.head())


if __name__ == "__main__":
    main()

```

**output**:

```bash
show_id      show_name  season      couple_name
0    90df  90 Day Fiancé       1     Russ & Paola
1    90df  90 Day Fiancé       1   Alan & Kirlyam
2    90df  90 Day Fiancé       1      Louis & Aya
3    90df  90 Day Fiancé       1     Mike & Aziza
4    90df  90 Day Fiancé       2  Chelsea & Yamir
  show_id      show_name  season  start_date    end_date
0    90df  90 Day Fiancé       1  2014-01-12  2014-02-23
1    90df  90 Day Fiancé       2  2014-10-19  2014-12-28
2    90df  90 Day Fiancé       3  2015-10-11  2015-12-06
3    90df  90 Day Fiancé       4  2016-08-22  2016-11-20
4    90df  90 Day Fiancé       5  2017-10-08  2017-12-18
```


