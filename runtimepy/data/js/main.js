function changeFileName(urlObj, newFileName) {
  let pathParts = urlObj.pathname.split('/');
  pathParts[pathParts.length - 1] = newFileName;
  return pathParts.join('/');
}

/* Load configuration data then run application entry. */
window.onload = async () => {
  await (
      new App(
          await (await fetch(changeFileName(window.location, "json"))).json(),
          worker))
      .main();
};
