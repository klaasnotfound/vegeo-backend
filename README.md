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

This repository showcases a basic implementation of geo-referenced vegetation alerts. It analyzes open source satellite imagery from the [USDA National Agriculture Imagery Program](https://www.arcgis.com/home/item.html?id=e74cf6b0790e424489bbe84cbc0dc7ad) (NAIP), cross-references it with the geometry of low-voltage power lines in major US cities from [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Tag:power%3Dminor_line) and generates geo-referenced alerts where vegetation overlaps with power line segments. The results are exposed via a simple REST API.

Once the API server is running, you can use the [`vegeo-web-app`](https://github.com/klaasnotfound/vegeo-web-app) frontend to view the detection results on a map in your browser.

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

_Note:_ The Docker image supports `linux/arm64` and `linux/amd64`, so it should work on a Mac (both Apple Silicon and Intel) as well as on Windows and Linux. If your architecture doesn't match you will want to open the `docker-compose.yaml` file, replace `image: klaasnotfound/vegeo-backend:latest` with `build: .` and run `docker compose up` again. The build will take a few minutes.

---

<details>
<summary> <i>Alternative</i>: Local Setup</summary>
 

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

## Scripts

The API endpoints serve pre-computed results from the database. If you'd like to dig deeper and see how those results came about, there are a few individual scripts worth checking out.

Using Docker, the simplest way to execute one of these scripts is to connect to a running instance. Assuming the `vegeo-api-server` and `vegeo-db` containers are still up, you can:

```bash
docker exec -it vegeo-api-server bash
```

If you run a local setup you can skip this step. The scripts are located in `src/scripts/` and are excecuted as follows:

```bash
python3 -m src.scripts.<script_name>
```

### 🗺️  Fetch Cities and Power Lines

To populate the database with an initial set of regions and power lines, you can use the [`populate_db`](https://github.com/klaasnotfound/vegeo-backend/blob/main/src/scripts/populate_db.py) script. It will fetch all US cities with at least 500,000 residents from Wikidata, construct lat/long bounding boxes around their center and ask the fantastic [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) for low-voltage power line segments (OSM ways with the `"power"="minor_line"` attribute) in that region. Cities and power line segments are saved in the database for later processing.

![Screenshot of the `populate-db script` in action](/data/assets/img-populate-db.png)

_Note_: Running the `populate_db` script will drop all tables, including the image tiles and vegetation alerts.

### 🌳  Detect Vegetation

Once the database contains regions, the biggest chunk of "behind the scenes" work is detecting trees in the associated NAIP satellite images. The [`detect_vegetation`](https://github.com/klaasnotfound/vegeo-backend/blob/main/src/scripts/detect_vegetation.py) script does this. It will determine all level-17 tiles that intersect with power line segments, download their respective images from the NAIP tile server and run them through the pre-trained [DetectTree](https://github.com/martibosch/detectree) segmentation model. The resulting segmentation masks are saved as image tiles in the database.

![Screenshot of the `detect-vegetation` script in action](/data/assets/img-detect-vegetation.png)

_Note_: The detection process is rather slow and runs at about 1-2 tiles/s. If you just want to inspect some detection results, you might prefer working with the imported DB dump (see above), which contains 4,885 segmented tiles for 29 US cities.

The segmented tiles are 256x256 PNGs that can be overlayed onto the satellite image layer. For example, `GET /vegetation/tiles/17/50618/20926` returns this patch of land north of San Francisco:

<p align="center">
  <img src="data/assets/img-vegetation-tile.png" alt="A square image tile with segmented vegetation in magenta">
</p>

### ⚡️  Compute Vegetation Alerts

As a final step, the detected vegetation masks can be cross-checked against the power line geometry with the [`compute_alerts`](https://github.com/klaasnotfound/vegeo-backend/blob/main/src/scripts/compute_alerts.py) script. It will step through each polyline segment of the power line geometry with a pre-defined pixel radius, check the percentage of vegetation-occupied pixels within a circle of that radius and generate alerts where this percentage exceeds a certain threshold. The alerts are saved in the database.

![Screenshot of the `compute_alerts` script in action](/data/assets/img-compute-alerts.png)

## Miscellaneous

### Segmentation Model

Initial experiments for vegetation detection included training a [PyTorch Mask R-CNN](https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html) segmentation model. A set of 64 NAIP images was randomly sampled from a number of US cities and manually segmented and labeled as `tree` or `building` using [labelme](https://github.com/wkentaro/labelme). You can see the labeled images in the `data/NaipSat/labels` folder and the corresponding masks in the `data/NaipSat/masks` folder.

<p align="center">
  <img src="data/NaipSat/masks/naip_17_49677_34205_mask.png" alt="A square image with segmented tree and building areas in green and red">
</p>

The data was used to fine-tune a [COCO-pre-trained model](https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html#finetuning-from-a-pretrained-model). However, the results were disappointing, with labels and segmentation masks all over the place. This could be due to insufficient training set size, too little training epochs or - most likely - the relatively poor resolution of the NAIP tiles. If you'd like to further explore this approach, check out the `convert_labels` and `train_detector` scripts. Note that you will have to run a local setup (see above) and install the additional dependencies from `requirements-ml.txt`.

Projects like [TorchGeo](https://pytorch.org/blog/geospatial-deep-learning-with-torchgeo/#benchmark-datasets) and [DeepForest](https://github.com/weecology/DeepForest) suggest good detection performance is attainable when high-resolution imagery and large training sets are available. Neither was the case here, but fortunately further digging then led to the discovery of [DetecTree](https://github.com/martibosch/detectree), which seemed to perform well on satellite data with comparatively low resolution. Initial results with the pre-trained model were promising and some experimentation with image normalization (see this [Jupyter notebook](https://github.com/klaasnotfound/vegeo-backend/blob/main/notebooks/detectree.ipynb)) then yielded satisfactory performance for the purposes of this showcase.

### Troubleshooting

---

<details>
<summary> The <code>docker compose up</code> process crashes.</summary>
 

Carefully inspect the error. The startup process will roughly go through these phases:

1. Docker images are downloaded.

2. The `vegeo-db` container with the Postgres database process is started.

3. If the database is up and still empty, the backup is imported.

4. Once the filled database is available, the `vegeo-api-server` container is started.

5. The server tries to connect to the database.

Depending on where the error occurs, try the following:

1. Use `docker image ls` to check that the images have been properly downloaded. Use `arch` to determine whether your architecture matches `arm64` or `amd64`. If it doesn't, you should build the Docker image yourself (see above).

2. Has the Postgres service started up properly? The logs should show something like:

   ```bash
   vegeo-db          | 2025-04-23 14:53:30.238 UTC [1] LOG:  database system is ready to accept connections
   ```

   If not, what is the exact error? Is the port available? Has the database been created at all? Can you connect to it with `pgAdmin` or `psql`? Are you using the default connection (`postgres:postgres@postgres:5432/vegeo`) or a custom setup? Does the `.env` contain the correct connection string?

3. If the import of the database backup fails during `docker compose up`, see the next question.

4. What is the FastAPI error message? Does it find the entrance script `src/api.py`? You should see something like:

   ```
    vegeo-api-server  | 🏃 Starting API server ...
    vegeo-api-server  |
    vegeo-api-server  |    FastAPI   Starting production server 🚀
    vegeo-api-server  |
    vegeo-api-server  |              Searching for package file structure from directories with
    vegeo-api-server  |              __init__.py files
    vegeo-api-server  |              Importing from /app
    vegeo-api-server  |
    vegeo-api-server  |     module   📁 src
    vegeo-api-server  |              ├── 🐍 __init__.py
    vegeo-api-server  |              └── 🐍 api.py
   ```

5. If the connection fails, what is the exact error message? You will usually see a detailed SQLAlchemy error trace like:

   ```
    vegeo-api-server  | │ ╭───────────────────────────────── locals ─────────────────────────────────╮ │
    vegeo-api-server  | │ │ connection_factory = None                                                │ │
    vegeo-api-server  | │ │     cursor_factory = None                                                │ │
    vegeo-api-server  | │ │                dsn = 'host=localhost dbname=vegeo user=postgres          │ │
    vegeo-api-server  | │ │                      password=postgres port=5432'                        │ │
    vegeo-api-server  | │ │             kwargs = {                                                   │ │
    vegeo-api-server  | │ │                      │   'host': 'localhost',                            │ │
    vegeo-api-server  | │ │                      │   'dbname': 'vegeo',                              │ │
    vegeo-api-server  | │ │                      │   'user': 'postgres',                             │ │
    vegeo-api-server  | │ │                      │   'password': 'postgres',                         │ │
    vegeo-api-server  | │ │                      │   'port': 5432                                    │ │
    vegeo-api-server  | │ │                      }                                                   │ │
    vegeo-api-server  | │ │            kwasync = {}                                                  │ │
    vegeo-api-server  | │ ╰──────────────────────────────────────────────────────────────────────────╯ │
    vegeo-api-server  | ╰──────────────────────────────────────────────────────────────────────────────╯
    vegeo-api-server  | OperationalError: (psycopg2.OperationalError) connection to server at
    vegeo-api-server  | "localhost" (127.0.0.1), port 5432 failed: Connection refused
    vegeo-api-server  |         Is the server running on that host and accepting TCP/IP connections?
    vegeo-api-server  | connection to server at "localhost" (::1), port 5432 failed: Cannot assign
    vegeo-api-server  | requested address
    vegeo-api-server  |         Is the server running on that host and accepting TCP/IP connections?
   ```

   (In this case, `localhost` is incorrect and would have to be replaced with `postgres` because of how Docker network mapping inside containers works.)

   Again, check whether you can connect to the database with `pgAdmin` or `psql`.

</details>

---

<details>
<summary> Restoring the database backup fails.</summary>
 

Was the restore process started? Did it complete successfully? On the first launch, you should see something like:

```
vegeo-api-server  | 💾 Restoring DB backup ...
...
vegeo-api-server  | ✅ Done
```

If this fails because of pre-existing tables or inconsistent database content, you can _completely delete_ the `data/db/postgres` folder, kill the container (`docker compose down`) and then restart it (`docker compose up`). A fresh instance of the database will be created.

</details>

---

<details>
<summary> I have messed up the database.</summary>
 

No worries. You can _completely delete_ the `data/db/postgres` folder, kill the container (`docker compose down`) and then restart it (`docker compose up`). A fresh instance of the database will be created.

</details>

---

<details>
<summary> Both containers start, but the backend is unreachable.</summary>
 

Please double-check your browser URL, it should be [http://localhost:3000](http://localhost:3000). When the NextJS web app starts, it might offer you an alternative URL from the Docker network adapter:

```
vegeo-web-app-web-app-1  | > next start
vegeo-web-app-web-app-1  |
vegeo-web-app-web-app-1  |    ▲ Next.js 15.2.4
vegeo-web-app-web-app-1  |    - Local:        http://localhost:3000
vegeo-web-app-web-app-1  |    - Network:      http://172.21.0.2:3000
vegeo-web-app-web-app-1  |
vegeo-web-app-web-app-1  |  ✓ Starting...
vegeo-web-app-web-app-1  |  ✓ Ready in 249ms
```

If you accidentally use that URL, the web app requests will be blocked due to CORS.

</details>
