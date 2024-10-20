/* Dark is hard-coded initial state (in HTML). */
let lightMode = false;

function lightDarkClick(event) {
  lightMode = !lightMode;

  document.getElementById("runtimepy")
      .setAttribute("data-bs-theme", lightMode ? "light" : "dark");

  window.location.hash = lightMode ? "#light-mode" : "";
}

let lightDarkButton = document.getElementById("theme-button");
if (lightDarkButton) {
  lightDarkButton.addEventListener("click", lightDarkClick);
}

if (window.location.hash) {
  let parts = window.location.hash.slice(1).split(",");

  if (parts.includes("light-mode")) {
    lightDarkButton.click();
  }
}
