[Topics Comp Sci Report.pdf](https://github.com/user-attachments/files/24202954/Topics.Comp.Sci.Report.pdf)

# National-Park-Roadtrip-Planner-TSP
Julia N. (jnitting) - Algorithm Implementation 
Thanh N. (ThanhNguyen51) - Front-End Implementation
Mikael P. (MP018) - Data scraping, Quality Assurance
Melody A. (melsalghul) - OSRM API & Algorithm Implementation

### Run web application locally
1) Have Python installed in your computer
2) Open the terminal and install necessary modules by running pip install -r requirements.txt
3) Select app.py file and run it
4) In the terminal, it will show " * Running on http://127.0.0.1:5000", open the link
5) The web application will load into your browser for user to use


### Data Scraping
1) Open the terminal and install necessary modules by
2) pip install -r DataScraping/requirements.txt 
3) Have parkdata.kml in the same folder as the python file
4) Run AIO python file 
5) 4-outputs, 1-json file, 3-csv file
6) 

## Introduction

Our group developed a **National Park Roadtrip Planner Application**, solving the **Traveling Salesman Problem (TSP)** using an **Adaptive Evolutionary Algorithm** to create an optimal road trip route visiting all **51 national parks in the contiguous United States**. The project utilizes **geospatial data processing**, **evolutionary computation**, and **web-based visualization** to produce a realistic, drivable route that users can interactively explore.

Users select a starting national park, and the application generates an optimized route that visits all 51 contiguous U.S. national parks while minimizing total travel distance. The optimization is performed using an Adaptive Evolutionary Algorithm implemented with the **Chips-n-Salsa Java library**.

The TSP is an optimization problem that seeks the shortest possible route that visits each city exactly once and returns to the starting point. In this project, each national park represents a city. The algorithm evolves a population of candidate tours using permutation-based genetic operations such as mutation and crossover, adaptively favoring operators that perform well over time. This approach allows efficient exploration of the solution space without requiring exhaustive search.

The project is divided into three main components:

1. Data processing pipeline  
2. Adaptive evolutionary algorithm implementation  
3. Web-based application for route generation and visualization  

The data pipeline prepares geographic and distance data, the optimization algorithm computes the optimal tour, and the web application visualizes the final driving route.


## Functionality

The National Park Roadtrip Planner Application begins by filtering a KML file containing all U.S. national park names and coordinates to create a CSV file including only parks in the contiguous United States. From this CSV file, two additional CSV files are generated:

- A **straight-line distance matrix** accounting for Earth’s curvature  
- A **real-world drivable distance matrix** obtained using the **OSRM routing API**

An **Adaptive Evolutionary Algorithm** is implemented in Java using the Chips-n-Salsa library, taking the drivable distance matrix as input. The algorithm initializes a population of random tours and iteratively improves them through selection, crossover, and mutation. An inverse fitness function ensures that shorter routes receive higher fitness values.

After a fixed number of generations, the algorithm outputs the best tour found as a permutation of park indices and saves it to a text file.

A **Flask backend application** loads the TSP solution file and park location data. When a user selects a starting park, the backend rotates the optimized permutation to begin at the selected location without altering the overall tour. The corresponding latitude and longitude coordinates are sent to the OSRM API to generate the full drivable route.

The route is displayed on the frontend by mapping the park indices to their names.


## Frontend Implementation

The index.html file implements the frontend of the web application and handles:

- User interaction  
- API communication  
- Map visualization  

The page includes:

- A dropdown menu to select a starting national park  
- A **Plan Route** button  
- An interactive map rendered using **Leaflet**  
- A trip statistics panel displaying total distance, estimated driving time, and park visit order  

Embedded JavaScript asynchronously fetches JSON data from the Flask backend and dynamically updates the **DOM (Document Object Model)** and Leaflet map without requiring a page reload.


## OSRM API

The **Open Source Routing Machine (OSRM) API** is an open-source routing service that computes realistic driving routes using road network data from **OpenStreetMap**. Unlike Euclidean distance calculations, OSRM follows actual roads and provides accurate estimates of travel distance and duration.

In this project, OSRM is used to convert the optimized TSP solution into a practical driving route. While the TSP algorithm determines the optimal order of visiting parks, it does not account for road networks. OSRM bridges this gap by computing the shortest drivable route between each park in the optimized sequence.

The app.py file sends a request to the OSRM Route API containing the latitude and longitude coordinates of each park in TSP order. The request specifies a driving profile and returns route geometry in **GeoJSON format**, which is used for map visualization. The route is constructed as a closed tour, returning to the starting park to maintain TSP constraints.

From the OSRM response, the application extracts:

- Total route distance  
- Estimated travel duration  

These values are converted to miles and hours, respectively, and returned to the frontend along with the route geometry.


## Conclusion

The group successfully implemented a **National Park TSP Road Trip Planner web application** that can be run locally once the files are pulled from the GitHub repository. The application allows users to choose a starting national park and generates a mapped-out road trip route showing the visitation order, total drivable distance, and estimated travel time.

Throughout the project, the group gained a deeper understanding of **adaptive evolutionary algorithms** and the complexity of TSP problems. Challenges included scraping and filtering park data, generating realistic distance matrices, integrating multiple programming languages, and ensuring seamless interoperability between system components. These challenges were addressed by standardizing intermediate outputs as CSV and TXT files.

Overall, this project demonstrates a practical and interactive application of the Traveling Salesman Problem combined with real-world routing and visualization.
