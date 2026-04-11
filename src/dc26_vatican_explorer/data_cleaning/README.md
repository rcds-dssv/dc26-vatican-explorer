>[!NOTE]
> -- UNDER CONSTRUCTION --

Example Usage

```python
db_path = Path('data/vatican_texts.db')
pope_speech_metadata = get_clean_speech_metadata(db_path)
print(pope_speech_metadata['Francis'].texts[465])
>> Speech(title='To the National Confederation of the "Misericordie d\' Italia" on the occasion of the anniversary of its meeting with Pope John Paul II on 14 June 1986 (14 June 2014)', date='2014-06-14', category='speeches')
```