# Mcity Traffic Lights — setPhase

Send a traffic signal phase command to an Mcity intersection via the Octane Traffic Controller API (Mcity OS).

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

| Intersection      | Map ID | Diagram |
|-------------------|--------|---------|
| Liberty/Wolverine | 2571   | I-1     |
| Liberty/State     | 2570   | I-2     |
| Main/State        | 2573   | I-3     |
| Main/Wolverine    | 2572   | I-4     |
| Access/Pontiac    | 2575   | I-6     |
| Main/Pontiac      | 2576   | I-7     |
| Liberty/Pontiac   | 2577   | I-8     |

Set each phase signal in the `phases` list. Each entry follows the pattern `phase_<N>_<state>` where `<state>` is `red`, `yellow`, or `green` and `<N>` is 1–8.

## Phase Map

Use the diagram below to identify which phase number controls each movement direction at each intersection.

![Phase Map](phase%20map%20updated%209-27-23.png)

Each box in the diagram shows a schematic of one intersection. Numbered arrows indicate the phase assigned to that movement direction. Phases not shown in a diagram are unused at that intersection and should be set to `red`.

### Phase assignments by intersection ID

#### I-1 — ID 2571 — `Liberty/Wolverine` (T-intersection, 3 legs)

| Phase | Direction |
|-------|-----------|
| 2 | Northbound (through) |
| 4 | Westbound (through) |
| 6 | Eastbound (through) |

#### I-2 — ID 2570 — `Liberty/State` (4-way)

| Phase | Direction |
|-------|-----------|
| 2 | Northbound (through) |
| 4 | Westbound (through) |
| 6 | Eastbound (through) |
| 8 | Southbound (through) |

#### I-3 — ID 2573 — `Main/State` (4-way with protected phases)

| Phase | Direction |
|-------|-----------|
| 2 | Northbound (through) |
| 3 | Northbound (protected) |
| 4 | Westbound (through) |
| 5 | Eastbound (protected) |
| 6 | Eastbound (through) |
| 7 | Westbound (protected) |
| 8 | Southbound (through) |

#### I-4 — ID 2572 — `Main/Wolverine` (4-way with protected phases)

| Phase | Direction |
|-------|-----------|
| 2 | Northbound (through) |
| 3 | Westbound (protected) |
| 5 | Eastbound (protected) |
| 6 | Eastbound (through) |
| 7 | Westbound (through) |
| 8 | Southbound (through) |

#### I-5 — ID 2574 (T-intersection, 3 legs — Mcity center, not an API intersection)

| Phase | Direction |
|-------|-----------|
| 2 | Southbound (through) |
| 6 | Eastbound (through) |

#### I-6 — ID 2575 — `Access/Pontiac` (T-intersection, 3 legs)

| Phase | Direction |
|-------|-----------|
| 2 | Eastbound (through) |
| 6 | Westbound (through) |
| 8 | Northbound (through) |

#### I-7 — ID 2576 — `Main/Pontiac` (T-intersection, 3 legs)

| Phase | Direction |
|-------|-----------|
| 2 | Southbound (through) |
| 4 | Westbound (through) |
| 8 | Northbound (through) |

#### I-8 — ID 2577 — `Liberty/Pontiac` (T-intersection, 3 legs)

| Phase | Direction |
|-------|-----------|
| 2 | Northbound (through) |
| 4 | Westbound (through) |

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
