function applySwaggerStyle() {
  var swaggerBoxes = document.querySelectorAll(
    'div[class^="opblock opblock-"]'
  );

  var tables = document.querySelectorAll("table");
  tables.forEach((table) => {
    table.setAttribute("hidden", "hidden");

  });
  var tables = document.querySelectorAll("table");
  var tablesPlaceHolders = document.querySelectorAll("h5");

  tables.forEach(function (table, index) {
    table.setAttribute("aria-expanded", "false");
    tablesPlaceHolders[index].style.borderRadius = "15px";
    tablesPlaceHolders[index].style.textTransform = "capitalize";
    tablesPlaceHolders[index].style.transition = "border-radius 0.4s linear";
    tablesPlaceHolders[index].style.cursor = "pointer";
    tablesPlaceHolders[index].addEventListener("click", function () {
      table.toggleAttribute("hidden");
      
      var toggleState = table.getAttribute("aria-expanded");
      if (toggleState === "true") {
        tablesPlaceHolders[index].style.borderTopLeftRadius = "15px";
        tablesPlaceHolders[index].style.borderTopRightRadius = "15px";
        tablesPlaceHolders[index].style.borderBottomLeftRadius = "15px";
        tablesPlaceHolders[index].style.borderBottomRightRadius = "15px";
        table.setAttribute("aria-expanded", "false");
      } else {
        tablesPlaceHolders[index].style.borderTopLeftRadius = "15px";
        tablesPlaceHolders[index].style.borderTopRightRadius = "15px";
        tablesPlaceHolders[index].style.borderBottomLeftRadius = "0px";
        tablesPlaceHolders[index].style.borderBottomRightRadius = "0px";
        table.setAttribute("aria-expanded", "true");
      }

    });
  });

  var validationErrorButtons = document.querySelectorAll(
    "button[class^='sc-jXcxbT jsdzMI']"
  );
  validationErrorButtons.forEach(function (button) {
    button.setAttribute("aria-expanded", "false");
    button.addEventListener("click", function () {
      var toggleState = button.getAttribute("aria-expanded");

      button.style.transition = "border-radius 0.4s linear";

      if (toggleState === "false") {
        button.style.borderRadius = "0px";
        button.style.borderTopLeftRadius = "15px";
        button.style.borderTopRightRadius = "15px";
        button.style.borderBottomLeftRadius = "0px";
        button.style.borderBottomRightRadius = "0px";
      } else {
        button.style.borderRadius = "0px";
        button.style.borderTopLeftRadius = "0px";
        button.style.borderTopRightRadius = "0px";
        button.style.borderBottomLeftRadius = "15px";
        button.style.borderBottomRightRadius = "15px";
      }
    });
  });

  const redocMethodsPlaceHolder = document.querySelectorAll("span[class^='sc-gIvpjk']");
  const tryMethodPlaceHolder = document.querySelectorAll("span[class^='sc-jHcXXw']");
  
  tryMethodPlaceHolder.forEach(place => {
    const type = place.getAttribute('type');
  
    const correspondingElement = Array.from(redocMethodsPlaceHolder).find(element =>
      element.getAttribute('type') === type
    );
  
    if (correspondingElement) {

      const backgroundColor = getComputedStyle(correspondingElement).backgroundColor;
      const color = getComputedStyle(correspondingElement).color;
  
      place.style.backgroundColor = backgroundColor;
      place.style.color = color;
      place.style.padding = "10px 10px 10px 10px";
      place.style.textTransform = "uppercase"
      place.style.margin = "10px";
      place.style.fontSize = "12px";
      place.style.transition = "brightness 0.3s ease";
    }
  });

  const container = document.querySelector(".sc-hKFxyN.gHYYBK.api-info");

  const vercelLogo = document.createElement("img");
  vercelLogo.src =
    "https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png";
  vercelLogo.alt = "elementalLogo";
  vercelLogo.height = "100";

  const elementalLogo = document.createElement("img");
  elementalLogo.src = "/static/docs/android-chrome-512x512.png";
  elementalLogo.alt = "elementalLogo";
  elementalLogo.height = "100";

  const dockerLogo = document.createElement("img");
  dockerLogo.src = "https://www.svgrepo.com/show/331370/docker.svg";
  dockerLogo.alt = "dockerLogo";
  dockerLogo.height = "100";

  const firstChild = container.firstChild;
  container.insertBefore(elementalLogo, firstChild);

  /*container.insertBefore(elementalLogo, firstChild);
  container.insertBefore(dockerLogo, firstChild);*/
}

setTimeout(function () {
  applySwaggerStyle();
}, 1000);
