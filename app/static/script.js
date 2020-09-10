var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++){
  coll[i].addEventListener("click", function() {
  /* Toggle between adding and removing the "active" class,to highlight the button that controls the panel */
  this.classList.toggle("active");
  var qw = this.nextElementSibling;
  /* Toggle between hiding and showing the active panel */
  if (qw.style.display === "block") {
    qw.style.display = "none";
    } else {
    qw.style.display = "block";
    } 
  })  
};

