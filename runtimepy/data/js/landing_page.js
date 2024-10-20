/* should check uri */
let lightMode = false;

function lightDarkClick(event) {
  lightMode = !lightMode;

  document.getElementById("runtimepy")
      .setAttribute("data-bs-theme", lightMode ? "light" : "dark");

  /* update uri */
}

let lightDarkButton = document.getElementById("theme-button");
if (lightDarkButton) {
  lightDarkButton.addEventListener("click", lightDarkClick.bind(this));
}
