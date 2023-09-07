# Baskerville

Infer and validate data-type schemas in Python.

## Example

```csv
# mascots.csv
Name,LOC,Species
Ferris,42,Crab
Corro,7,Urchin
```

```python
>>> import baskerville
>>> baskerville.infer_csv("mascots.csv")
[Field(name=Name, valid_types=[Text(min_length=5, max_length=6)], nullable=False), Field(name=LOC, valid_types=[Integer(min_value=7, max_value=42), Float(min_value=7, max_value=42), Text(min_length=1, max_length=2)], nullable=False), Field(name=Species, valid_types=[Text(min_length=4, max_length=6)], nullable=False)]
```
