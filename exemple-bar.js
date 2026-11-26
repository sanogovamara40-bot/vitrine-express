/* Script externe — CSP stricte préservée (aucun JavaScript inline). */

(function () {
  "use strict";

  // 1. Les promotions expirées disparaissent automatiquement.
  var promos = document.querySelectorAll(".promo[data-fin]");
  for (var i = 0; i < promos.length; i++) {
    var fin = new Date(promos[i].getAttribute("data-fin") + "T23:59:59");
    if (!isNaN(fin.getTime()) && fin < new Date()) {
      promos[i].hidden = true;
    }
  }

  // 2. Animations discrètes au défilement, désactivées si l'utilisateur
  //    préfère réduire les mouvements (accessibilité).
  var reductions = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var elements = document.querySelectorAll(".reveal");

  if (reductions || !("IntersectionObserver" in window)) {
    for (var j = 0; j < elements.length; j++) {
      elements[j].classList.add("is-visible");
    }
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      for (var k = 0; k < entries.length; k++) {
        if (entries[k].isIntersecting) {
          entries[k].target.classList.add("is-visible");
          observer.unobserve(entries[k].target);
        }
      }
    },
    { threshold: 0.12 }
  );

  for (var m = 0; m < elements.length; m++) {
    observer.observe(elements[m]);
  }
})();
