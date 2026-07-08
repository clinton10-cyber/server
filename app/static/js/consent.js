(function () {
  const CONSENT_KEY = "clinton-tech-cookie-consent"; // "accepted" | "declined"
  const banner = document.getElementById("cookie-consent-banner");
  const acceptBtn = document.getElementById("cookie-accept");
  const declineBtn = document.getElementById("cookie-decline");
  const config = window.CLINTON_TECH_CONFIG || {};

  function loadAdsense() {
    if (!config.adsenseClientId) return;
    if (document.getElementById("adsense-script")) return;

    const script = document.createElement("script");
    script.id = "adsense-script";
    script.async = true;
    script.src =
      "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
      encodeURIComponent(config.adsenseClientId);
    script.crossOrigin = "anonymous";
    document.head.appendChild(script);
  }

  function loadMellowtel() {
    if (!config.mellowtelConfigUuid) return;
    if (document.getElementById("mellowtel-script")) return;

    // Mellowtel requires explicit, separate opt-in consent (per their terms) —
    // it is loaded only after the visitor accepts cookies here.
    const script = document.createElement("script");
    script.id = "mellowtel-script";
    script.async = true;
    script.src = "https://mellowtel-cdn.web.app/mellowtel-sdk.js";
    script.setAttribute("data-config-uuid", config.mellowtelConfigUuid);
    document.head.appendChild(script);
  }

  function activateConsentedScripts() {
    loadAdsense();
    loadMellowtel();
  }

  const stored = localStorage.getItem(CONSENT_KEY);

  if (stored === "accepted") {
    activateConsentedScripts();
  } else if (stored !== "declined" && banner) {
    banner.classList.remove("hidden");
  }

  if (acceptBtn) {
    acceptBtn.addEventListener("click", () => {
      localStorage.setItem(CONSENT_KEY, "accepted");
      if (banner) banner.classList.add("hidden");
      activateConsentedScripts();
    });
  }

  if (declineBtn) {
    declineBtn.addEventListener("click", () => {
      localStorage.setItem(CONSENT_KEY, "declined");
      if (banner) banner.classList.add("hidden");
    });
  }
})();
