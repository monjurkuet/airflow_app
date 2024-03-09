<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" alt="project-logo">
</p>
<p align="center">
    <h1 align="center">AIRFLOW_APP</h1>
</p>

<p align="center">
	<img src="https://img.shields.io/github/license/monjurkuet/airflow_app?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/monjurkuet/airflow_app?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/monjurkuet/airflow_app?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/monjurkuet/airflow_app?style=default&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>

<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [ Overview](#-overview)
- [ Features](#-features)
- [ Repository Structure](#-repository-structure)
- [ Modules](#-modules)
- [ Getting Started](#-getting-started)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Tests](#-tests)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)
</details>
<hr>

##  Overview

<code>This repo demonstrates how to use Selenium web driver, requests, bs4 etc to automate web scraping and create data pipeline in a Dockerized airflow environment. </code>

---

##  Features

1. Save output to CSV in a mounted directory.
 2. Save data to mongodb running on localhost.

---

##  Repository Structure

```sh
└── airflow_app/
    ├── Dockerfile
    ├── dags
    │   ├── NHL_team_stats.py
    │   ├── __pycache__
    │   ├── chef_jobs_bikroy.py
    │   ├── countries_data.py
    │   └── scrapethissite_tasks.py
    ├── docker-compose.yml
    ├── output
    │   ├── NHL_team_stats.csv
    │   └── countries_data.csv
    └── requirements.txt
```

---

##  Modules

<details closed><summary>.</summary>

| File                                                                                           | Summary                         |
| ---                                                                                            | ---                             |
| [requirements.txt](https://github.com/monjurkuet/airflow_app/blob/master/requirements.txt)     | <code>► Requirements and version control</code> |
| [docker-compose.yml](https://github.com/monjurkuet/airflow_app/blob/master/docker-compose.yml) | <code>► Docker YAML</code> |
| [Dockerfile](https://github.com/monjurkuet/airflow_app/blob/master/Dockerfile)                 | <code>► Dockerfile</code> |

</details>

<details closed><summary>dags</summary>

| File                                                                                                          | Summary                         |
| ---                                                                                                           | ---                             |
| [countries_data.py](https://github.com/monjurkuet/airflow_app/blob/master/dags/countries_data.py)             | <code>► Crawl Countries data as separate dag</code> |
| [NHL_team_stats.py](https://github.com/monjurkuet/airflow_app/blob/master/dags/NHL_team_stats.py)             | <code>► Crawl NHL team stats as separate dag</code> |
| [chef_jobs_bikroy.py](https://github.com/monjurkuet/airflow_app/blob/master/dags/chef_jobs_bikroy.py)         | <code>► Crawl bikroy.com jobs using selenium</code> |
| [scrapethissite_tasks.py](https://github.com/monjurkuet/airflow_app/blob/master/dags/scrapethissite_tasks.py) | <code>► Combine country and NHL scraping task as single dagE</code> |

</details>

---

##  Getting Started

**System Requirements:**

* **Docker <br>
  Follow this if not installed already
  https://docs.docker.com/engine/install/**<br>
*  **MongoDB Server <br>
  Follow this if not installed already
  https://www.mongodb.com/try/download/community**

###  Installation

<h4>From <code>source</code></h4>

> 1. Clone the airflow_app repository:
>
> ```console
> $ git clone https://github.com/monjurkuet/airflow_app
> ```
>
> 2. Change to the project directory:
> ```console
> $ cd airflow_app
> ```
>
> 3. Build docker image:
> ```console
> $ docker-compose up -d
> ```

###  Demo

<h4>From <code>source</code></h4>

