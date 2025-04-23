<p align="center">
  <img width="128" align="center" src="data/assets/img-vegeo-backend.png" alt="Vegeo Backend Logo">
</p>

<h1 align="center">Vegeo Backend</h1>

<p align="center">
  <img src="https://img.shields.io/badge/%F0%9F%90%8D_python-gray" alt="Python">
  <img src="https://img.shields.io/badge/%F0%9F%90%98_PostgreSQL-gray" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/%E2%9A%A1%EF%B8%8F_FastAPI-gray" alt="FastAPI">
  <img src="https://img.shields.io/badge/%F0%9F%A7%AA_SQLAlchemy-gray" alt="FastAPI">
  <img src="data/assets/tests.svg" alt="Tests" />
</p>

## Motivation

This repository showcases a basic implementation of geo-referenced vegetation alerts. It analyzes open source satellite imagery from the [USDA National Agriculture Imagery Program](https://www.arcgis.com/home/item.html?id=e74cf6b0790e424489bbe84cbc0dc7ad) (NAIP), cross-references it with the geometry of low-voltage power lines in major US cities from [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Tag:power%3Dminor_line) and generates geo-referenced alerts where vegetation overlaps with power line segments.

## Installation

First, clone the repository:

```bash
git clone git@github.com:klaasnotfound/vegeo-backend.git
cd vegeo-backend
```

The easiest way to get the Vegeo backend up and running is by using Docker:

```bash
docker compose up
```

_Note:_ The vegeo Docker image supports `linux/arm64` and `linux/amd64`, so it should work on a Mac (both Apple Silicon and Intel) as well as Windows and Linux. If you're architecture doesn't match, you will want to open the `docker-compose.yaml` file, replace `image: klaasnotfound/vegeo:latest` with `build: .` and run `docker compose up` again. The build will take a few minutes.

---

<details>
<summary><i>Alternative</i>: Local Setup</summary>
 

If you don't want to use Docker you'll have to set up the Python environment and a PostgreSQL database yourself. Install or update both with your favorite package manager (`brew`, `apt` etc.), then:

1. Make sure `python3 --version` returns `Python 3.12.3` or higher.

2. Make sure `psql --version` returns `psql (PostgreSQL) 16.8` or any other 16.x version. This is important for importing a database backup later on.

3. Inside the `vegeo-backend` directory, create a Python virtual environment and install the packages:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

4. Make sure the PostgreSQL service is running and that there's a user with full priviliges (usually `postgres`). Rename the `.sample.env` to `.env` and edit the connection string for your Postgres instance. For example, if your Postgres DB runs locally on port `5432` with user `postgres` and password `topsecret` your `.env` file should contain `DB_CONN=postgresql://postgres:topsecret@localhost:5432/vegeo`.

5. Add the connection string to your path and import the database dump from the DB folder.

   ```bash
   source .env
   PG_CONN=$(echo $DB_CONN | sed 's:/[^/]*$::')
   pg_restore -d $PG_CONN data/db/vegeo-db.dump -cC
   ```

   _Note_: `PG_CONN` is the connection string to your Postgres instance _without_ the `vegeo` DB, which needs to be dropped during the import.

6. Start the API server.

   ```bash
   python3 -m fastapi run src/api.py
   ```

</details>

---

If everything goes smoothly, the Vegeo API server should now respond at [localhost:8000](http://localhost:8000/):

```json
{
  "name": "Vegeo API",
  "version": "0.1.0"
}
```

## API Docs

The API provides a few endpoints with read access to the power line and vegetation detection data. Once the API server is running, detailed documentation is available at [localhost:8000/docs](https://localhost:8000/docs).

![Screenshot of the API documentation](/data/assets/img-api-docs.png)
