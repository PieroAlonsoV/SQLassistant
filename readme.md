# Overview

This project on Streamlit allows you to analyze a PDF file that contains a table. The current structure of this demo table is *date, month, transaction, charges, and credits*.

# Parameters

The following JSON files should be stored in the "keys" folder.

1. Database in postgres (e.g. named 'exam').
- Parameters stored in a json file.
``` JSON
{
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}
```

2. OpenAi key.
- Stored in a json file e.g.
``` JSON
{"openai_api_key":"..."}
```

# Dependencies

Download the libraries according to **requirements.txt** file.

```bash
pip install -r requirements.txt
```

# Executing

Within the repository folder, execute:

```bash
streamlit run app.py
```

And go to http://localhost:8501/ to interact with the web IU.
