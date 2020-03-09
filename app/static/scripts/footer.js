// Footer Management and AJAX loading to reduce page refreshes
$(window).scrollTop(0);

$("#footerScore").click(function() {
   $('#content').load('/scores');
   document.title="ExePlore - Scoreboard";
   $("#footerCards").removeClass("selected-footer");
   $("#footerMap").removeClass("selected-footer");
   $("#footerScore").addClass("selected-footer");
   $(window).scrollTop(0);
})

$("#footerMap").click(function() {
   $('#content').load('/map');
   document.title="ExePlore";
   $("#footerCards").removeClass("selected-footer");
   $("#footerMap").addClass("selected-footer");
   $("#footerScore").removeClass("selected-footer");
   $(window).scrollTop(0);
})

$("#footerCards").click(function() {
   $('#content').load('/cards');
   document.title="ExePlore - Cards";
   $("#footerCards").addClass("selected-footer");
   $("#footerMap").removeClass("selected-footer");
   $("#footerScore").removeClass("selected-footer");
   $(window).scrollTop(0);
})