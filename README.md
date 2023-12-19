# Text-Analysis

Python-based text extraction and analysis tool leveraging web scraping and NLP techniques.

## Project Setup

### Clone the repository

```
git clone https://github.com/kamalkish0r/Text-Analysis.git
```

### Setup Virtual Environment

```
python -m venv env
source env/bin/activate  # For Windows, use env\Scripts\activate
```

### Install Dependencies

```
pip install -r requirements.txt
```

## Usage

```
python main.py
```

## Approach

- I started with reading the objective of the assignment.
- Then I explored the Input/Output files.
- Then I went through the given guide to text analysis, which helped me understand how can I compute values of required variables.
- Then one by one, taking the reference from the guide provided I wrote the logic to compute the variable values.
- Saved the extracted text into `data/extracted_text/{url_id}.txt`
- Saved the computed values of variable into `data/Output Data Structure.xlsx` in the corresponding row & column.
- **Difficulties Encoutered** :
  - Some of the web pages have different html structure, so I needed to handle that in order to scrape the `Title` & `Content` of the article. I used `try except` blocks to identify the errors and fixed them by providing different selectors for these kind of web pages.



Feel free to reachout if you have any queries regarding my solution!
