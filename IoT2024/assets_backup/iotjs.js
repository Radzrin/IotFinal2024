function darkMode() {
   var element = document.body;
   element.classList.toggle("dark-mode");

   var navtog = document.getElementsByTagName("nav")[0];
   navtog.classList.toggle("dark-nav");

   var button = document.getElementById("modes");

   if(button.innerHTML == "☾"){
      button.innerHTML = "☼";
   }else{
      button.innerHTML = "☾";
   }
}