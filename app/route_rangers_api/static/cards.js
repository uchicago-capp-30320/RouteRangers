function updateCards(buttonId, element) {
  var buttonText = element.textContent;
  document.getElementById(buttonId).textContent = buttonText;
  // these buttons not currently active 
  // if (buttonId === "daysDropdown") {
  //   days = buttonText;
  // } else if (buttonId === "seasonDropdown") {
  //   seasons = buttonText;
  // } else {
  //   
  type = buttonText;
  //}

  document.getElementById("totalRidersText").textContent =
    cityData[type]["TotalRiders"];
  document.getElementById("totalRoutesText").textContent =
    cityData[type]["TotalRoutes"];
  document.getElementById("pctOfCommutersText").textContent =
    cityData[type]["PercentOfCommuters"];
}
