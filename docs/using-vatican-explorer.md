# Core API

The `dc26_vatican_explorer` package provides tools for scraping, cleaning, querying, and analyzing speeches and texts from the Vatican website. This document lists all public functions and classes with their docstrings.

## Data Objects

::: dc26_vatican_explorer.data_cleaning.data_objects.Speech
::: dc26_vatican_explorer.data_cleaning.data_objects.Pope

## Search

Biblical citation search utilities.

::: dc26_vatican_explorer.search.search_biblical_citation.default_regex_pattern
::: dc26_vatican_explorer.search.search_biblical_citation.search_biblical_citations
::: dc26_vatican_explorer.search.search_biblical_citation.search_biblical_citations_db

## Data Cleaning

Pipeline for loading, cleaning, and validating Vatican speech metadata.

::: dc26_vatican_explorer.data_cleaning.cleaning_pipeline.clean_dates
::: dc26_vatican_explorer.data_cleaning.cleaning_pipeline.rearrange_pope_data
::: dc26_vatican_explorer.data_cleaning.cleaning_pipeline.get_clean_speech_metadata
::: dc26_vatican_explorer.data_cleaning.format_dates.format_pontificate_date
::: dc26_vatican_explorer.data_cleaning.format_dates.format_date_to_iso
::: dc26_vatican_explorer.data_cleaning.format_dates.extract_date_from_title
::: dc26_vatican_explorer.data_cleaning.query_speeches.fetch_speech_metadata
::: dc26_vatican_explorer.data_cleaning.adding_birthplace.add_birthplace_to_db

## Database Utilities

Helper functions for working with the Vatican SQLite database.

::: dc26_vatican_explorer.database_utils.database_helpers.connect_to_database
::: dc26_vatican_explorer.database_utils.database_helpers.get_tables_in_database
::: dc26_vatican_explorer.database_utils.database_helpers.get_column_names_in_table
::: dc26_vatican_explorer.database_utils.database_helpers.regexp
::: dc26_vatican_explorer.database_utils.database_helpers.register_regexp_function
::: dc26_vatican_explorer.database_utils.database_helpers.table_exists
::: dc26_vatican_explorer.database_utils.database_helpers.column_exists_in_table
::: dc26_vatican_explorer.database_utils.database_helpers.check_texts_table_schema
::: dc26_vatican_explorer.database_utils.database_helpers.fetch_rows_by_regexp
::: dc26_vatican_explorer.database_utils.database_helpers.sanitize_table_name
::: dc26_vatican_explorer.database_utils.database_helpers.speech_url_exists_in_db
::: dc26_vatican_explorer.database_utils.database_helpers.get_speech_text_by_url
::: dc26_vatican_explorer.database_utils.database_helpers.query_texts
::: dc26_vatican_explorer.database_utils.database_helpers.query_missing_fields
::: dc26_vatican_explorer.database_utils.database_helpers.print_content_diagnostic

## Vatican Scraper

### Argument Parsing

::: dc26_vatican_explorer.vatican_scraper.argparser.scraper_parser
::: dc26_vatican_explorer.vatican_scraper.argparser.get_scraper_args

### Step 01 — List Popes

::: dc26_vatican_explorer.vatican_scraper.step01_list_popes.papal_normalize_display_name
::: dc26_vatican_explorer.vatican_scraper.step01_list_popes.papal_extract_slug_from_content_url
::: dc26_vatican_explorer.vatican_scraper.step01_list_popes.vatican_fetch_pope_directory_recent
::: dc26_vatican_explorer.vatican_scraper.step01_list_popes.papal_find_by_display_name

### Step 02 — List Pope Year Links

::: dc26_vatican_explorer.vatican_scraper.step02_list_pope_year_links.parse_years
::: dc26_vatican_explorer.vatican_scraper.step02_list_pope_year_links.fetch_pope_main_html
::: dc26_vatican_explorer.vatican_scraper.step02_list_pope_year_links.extract_pope_metadata_from_main
::: dc26_vatican_explorer.vatican_scraper.step02_list_pope_year_links.extract_available_years_from_main
::: dc26_vatican_explorer.vatican_scraper.step02_list_pope_year_links.extract_year_links_from_main

### Step 03 — List Speeches

::: dc26_vatican_explorer.vatican_scraper.step03_list_speeches.fetch_html
::: dc26_vatican_explorer.vatican_scraper.step03_list_speeches.extract_speeches_from_year_index
::: dc26_vatican_explorer.vatican_scraper.step03_list_speeches.extract_month_links_for_speeches
::: dc26_vatican_explorer.vatican_scraper.step03_list_speeches.collect_speeches_for_year_index

### Step 04 — Fetch Speech Texts

::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.fetch_html
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.fetch_html_with_final_url
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.extract_location_and_text
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.extract_links_from_container
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.find_translation_url
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.make_speech_id
::: dc26_vatican_explorer.vatican_scraper.step04_fetch_speech_texts.fetch_speeches_to_feather

### Step 05 — Add to Database

::: dc26_vatican_explorer.vatican_scraper.step05_add_to_database.ensure_db_and_table
::: dc26_vatican_explorer.vatican_scraper.step05_add_to_database.add_content_to_db

### Step 06 — Run Scraping Pipeline

::: dc26_vatican_explorer.vatican_scraper.step06_run_scraping_pipeline.main

