# Historical Moments API

Backend API built with FastAPI and MongoDB to manage interactive historical moments and player progress.

## Features

- Create and manage historical moments
- Multi-step narrative flow (inicio → contexto → evento → suceso → reaccion → dato_curioso)
- Player progress tracking
- State validation
- MongoDB persistence

---

## Tech Stack

- Python
- FastAPI
- MongoDB
- PyMongo
- Pydantic

---

## Project Structure

app/
│
├── routers/
├── services/
├── models/
├── core/
└── main.py


## API Endpoints

### Moments
- `GET /moments`
- `GET /moments/{moment_id}`
- `POST /moments`
- `PUT /moments/{moment_id}`

### Player Progress
- `POST /progress/{player_id}/{moment_id}/start`
- `PUT /progress/{player_id}/{moment_id}/advance`
- `PUT /progress/{player_id}/{moment_id}/pause`

---

## Description

This project implements a narrative engine where players explore historical events step by step while tracking their progression state.

---

## Author

Yanedis Margarita Maza
