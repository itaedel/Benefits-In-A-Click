# Benefits in a Click

Benefits in a Click is a user-friendly platform where users can search and compare credit card benefits based on the credit clubs they are members of and help them save money.
## Repository Structure

### Folders

- **_layouts/**
  - Contains layout file for the Github project page. The `default.html` file defines the main layout of the project page.

- **crawlers/**
  - Contains the code for the web crawlers that gather information from different credit club websites.
    - [crawler_amex.py](./crawlers/crawler_amex.py): Python code to gather information from American Express credit club.
    - [crawler_isracard.py](./crawlers/crawler_isracard.py): Python code to gather information from Isracard credit club.
    - [crawler_max.py](./crawlers/crawler_max.py): Python code to gather information from Max credit club.

- **images/**
  - Contains image files used in the project, including the favicon and other assets.

### Files
- **base_site.js**
  - JavaScript file for the back-end server functionality. It handles server-side operations and logic.

- **client_side.html**
  - HTML file for the client-side of the application.

- **database_handler.py**
  - Python script for handling database operations, including creating and managing the database of benefits and running the crawlers.

- **script.js**
  - JavaScript file for client-side functionality. It is included in `client_side.html` to handle interactive features on the user interface.

- **styles.css**
  - CSS file for styling the website.

- **index.md**
  - Markdown file used as the main content for the GitHub Pages site. It serves as the home page of the site.

- **_config.yml**
  - Configuration file for the Jekyll site. It includes settings and configurations for the GitHub Pages site.


## Getting Started

To get started with this project, clone the repository and follow the instructions in the individual files and folders.
You must Run base_site.js and database_handler.py to get the site up and running.

```bash
git clone https://github.com/itaedel/Benefits-In-A-Click.git
```

## Contact
To get in touch, please contact me at [ita.edel@pm.me](mailto:ita.edel@pm.me) or connect with me on [LinkedIn](https://www.linkedin.com/in/itamar-edelstein-868897204/).


© 2024 Benefits in a Click. All rights reserved.
