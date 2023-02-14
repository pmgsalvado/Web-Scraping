<h1>Apartment Renting Website - Web Scraping</h1>

<h2>Medium Article:</h2>
<p><a href="https://medium.com/@pmgsalvado/apartment-renting-website-web-scraping-40563c4c44c4">Apartment Renting Website — Web Scraping</a></p>


<h2>Motive:</h2>
<p>Moving to Bordeaux, France. It was necessary to have a quick way of finding apartments and their prices and locations.</p>
<h2>Project Description:</h2>
<p>The idea was to create a tool to find apartments from websites and scrap all the necessary information, price, typology,
price ranges, etc., and show all that information in a interactive way through a Plotly dash app.</p>

<h3>Project Structure:</h3>
<ol>
  <li><b>Main program:</b> Imovirtual_dash_bootstrap.py
    <p>Responsible part to run the Dash application</p>
  </li>
  <li>imovirtual_webscrapping_v2.py
    <p>This one to scrap information from the website, create DataFrame do some cleaning and preparing the data to be used by the Dash app.</p>
  </li>
  <li>external_functions.py
    <p>mainly for getting the Geo Coordinates, Latitude and Longitude, according the each address.</p>
  </li>
  
</ol>

