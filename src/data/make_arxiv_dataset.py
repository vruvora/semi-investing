# -*- coding: utf-8 -*-
import os
import arxivscraper as ax
import multiprocessing
import pandas as pd
import random
import logging

def grab_dates(arxiv_string):
     date1 = '-'.join(arxiv_string[1:4])
     date2 = '-'.join(arxiv_string[4:7])
     return date1, date2

def generate_date_pairs(starting_date, ending_date):
    date_from = pd.to_datetime(starting_date)
    ending_date = pd.to_datetime(ending_date)
    dates = []
    while date_from <= ending_date:
        date_to = date_from + pd.DateOffset(months=1)
        dates.append((str(date_from.date()), str(date_to.date())))
        date_from = date_to
    return dates


def generate_monthly_paper_data(dates, category='cs', filters={'categories': ['cs.ar', 'cs.dc', 'cs.et' 'cs.ro', 'cs.os', 'cs.pf']}):
    date_from, date_until = dates
    scraper = ax.Scraper(category=category, date_from=date_from, date_until=date_until, t=random.randint(10, 15),  filters=filters)
    output = scraper.scrape()
    try:
        cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
        df = pd.DataFrame(output,columns=cols)
        df.to_csv(f'data/raw/arxiv-{date_from}-{date_until}.csv')
        return df
    except ValueError:
        logging.debug(f"Failed to Extract Dates {date_from}, {date_until}")
        return pd.DataFrame()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    test_dates = generate_date_pairs('2010-01-01', '2022-05-01')
    arxiv_dates = [grab_dates(file.strip('.csv').split('-')) for file in os.listdir('data/raw/') if 'arxiv' in file]
    test_dates = set(test_dates) - set(arxiv_dates)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        paper_data = pool.map(generate_monthly_paper_data, test_dates)
    arxiv_papers = pd.concat(paper_data)
    arxiv_papers.to_csv('data/external/arxiv_dataset.csv')
    logging.info(f"Extracted {arxiv_papers.shape[0]} Records.")

