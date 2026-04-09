>[!NOTE]
> -- UNDER CONSTRUCTION --

Use the following order of operations:

```python
# after imports...
db_path = Path('data/vatican_texts.db')
raw_data = fetch_speech_metadata(db_path)
pope_speech_metadata = clean_dates(raw_data)
pope_speech_metadata = rearrange_pope_data(pope_speech_metadata)
```