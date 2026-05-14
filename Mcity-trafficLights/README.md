# Mcity Traffic Lights — setPhase

Send a traffic signal phase command to an Mcity intersection via the Octane Traffic Controller API.

## Prerequisites

- Python 3.8 or later
- An Mcity API key

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

- **Windows**
  ```bash
  venv\Scripts\activate
  ```
- **macOS / Linux**
  ```bash
  source venv/bin/activate
  ```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Open `setPhase.py` and replace the placeholder API key:

```python
API_KEY = "YOUR_API_KEY_HERE"
```

Set the target intersection by updating the `intersection` field in the payload. Supported intersections:

| Intersection       |
|--------------------|
| Main/Wolverine     |
| Main/State         |
| Main/Pontiac       |
| Liberty/State      |
| Liberty/Wolverine  |
| Liberty/Pontiac    |
| Access/Pontiac     |

Set each phase signal in the `phases` list. Each entry follows the pattern `phase_<N>_<state>` where `<state>` is `red`, `yellow`, or `green` and `<N>` is 1–8.

Example payload (all phases red):

```python
payload = {
    "intersection": "Main/Wolverine",
    "phases": [
        "phase_1_red",
        "phase_2_red",
        "phase_3_red",
        "phase_4_red",
        "phase_5_red",
        "phase_6_red",
        "phase_7_red",
        "phase_8_red"
    ]
}
```

## Execution

```bash
python setPhase.py
```

The script prints the HTTP status code, response headers, and the JSON body (or raw text if the response is not JSON).

```
Status: 200
Headers: {...}
JSON: {...}
```

## API endpoint

```
POST https://octane-tc.um.city/api/setphase
```

Authentication is via the `X-API-KEY` request header.
