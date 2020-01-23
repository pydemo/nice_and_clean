# nice_and_clean
Delete unwanted emails from your Gmail inbox.

![Nice And Clean](https://github.com/pydemo/nice_and_clean/blob/master/clean.jfif "Nice And Clean")

# Filters

## Delete filters


```Python
#Delete all emails with "Subject" or "Body" containing these tags
kws  = ['QlikView', 'Garden City, NY', 'Arizona', 'Washington DC']
```

## Label filters


```Python
#Label all emails with "From" containing these tags
lbls = ['Etsy']
```

# Usage

```

set FROM_EMAIL='test@gmail.com'
set FROM_PWD='test'
set IMAP_SERVER='imap.gmail.com'

python nac.py
```
## Output
```
2 Subj Washington DC
Trash deleted (1)
```

[<img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png">](https://www.buymeacoffee.com/0nJ32Xg)
