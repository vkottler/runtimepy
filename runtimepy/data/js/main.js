/* Load configuration data then run application entry. */
window.onload = async () => {
  await (new App(await (await fetch(window.location.origin + "/json")).json(),
                 worker))
      .main();
};
