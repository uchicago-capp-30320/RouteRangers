function updateCards(buttonId, element) {
  var buttonText = element.textContent;
  document.getElementById(buttonId).textContent = buttonText;
  if (buttonId === "daysDropdown") {
    days = buttonText;
  } else if (buttonId === "seasonDropdown") {
    seasons = buttonText;
  } else {
    type = buttonText;
  }
  console.log(days, seasons, type);
  console.log(cityData);

  document.getElementById("totalRidersText").textContent =
    cityData[type][seasons][days]["TotalRiders"];
  document.getElementById("totalRoutesText").textContent =
    cityData[type][seasons][days]["TotalRoutes"];
  document.getElementById("averageCommuteTimeText").textContent =
    cityData[type][seasons][days]["AverageCommuteTime"];
}
