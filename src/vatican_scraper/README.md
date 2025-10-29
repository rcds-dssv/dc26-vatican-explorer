This directory contains code for scraping the Vatican website and generating the sqlite database. 

To retrieve the first 20 speeches from the default pope and year, run the code from the `src` directory with:

```
python -m vatican_scraper.step06_run_scraping_pipeline --max_n_speeches 20
```

You can also use the `--help` flag to see all the other options.
