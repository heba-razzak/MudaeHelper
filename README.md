# Mudae Message Logger & Rolling Strategy

This project extracts, processes, and structures Mudae messages into a usable database. It helps automate data collection, convert messages into structured formats, and develop an optimized rolling strategy.

## **📂 Files & What They Do**
| Filename | Description |
|----------|------------|
| [`msg_hist_to_csv.py`](msg_hist_to_csv.py) | Fetches recent messages from a Discord channel and saves them as a CSV file. |
| [`mudae_pages_to_json.py`](mudae_pages_to_json.py) | Captures Mudae multi-page responses (e.g., `$top`) and saves them as structured JSON. |
| [`json_to_csv.py`](json_to_csv.py) | Converts the extracted JSON data into a CSV format for easier analysis. |
| [`example.env`](example.env) | Example environment file to configure the bot. Rename to `.env` and update with your credentials. |

---
