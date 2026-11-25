# WattWise – Electricity Consumption Intelligence System (Solar theme)

## Folder layout
```
project/
├── app.py
├── requirements.txt
├── .streamlit/config.toml     <- theme colours (keep this folder next to app.py)
├── outputs/                   <- copy from the notebook run
│   ├── hourly_dataset.csv
│   ├── daily_dataset.csv
│   └── dashboard_data/
└── models/model_metadata.json <- optional, from the notebook run
```

## Run
```
pip install -r requirements.txt
streamlit run app.py
```
Run the command from the project folder so Streamlit picks up `.streamlit/config.toml`.
