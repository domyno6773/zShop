/* Deliberately ES5-compatible: Wii U applet is an older WebKit environment.
   Native bridge calls below are guarded; never block stock HOME behavior. */
(function () {
    "use strict";
    function initializeNativeApplet() {
        try {
            if (typeof window.wiiuBrowser !== "undefined") {
                if (typeof window.wiiuBrowser.endStartUp === "function") {
                    window.wiiuBrowser.endStartUp(true);
                }
                if (typeof window.wiiuBrowser.lockHomeButtonMenu === "function") {
                    window.wiiuBrowser.lockHomeButtonMenu(false);
                }
            }
        } catch (ignored) {
            // Keep the HTTP-only interface usable on desktop and Wii U.
        }
    }

    function isTypingTarget(el) {
        if (!el || !el.tagName) { return false; }
        var name = el.tagName.toLowerCase();
        return name === "input" || name === "textarea" || name === "select";
    }

    function onKeyDown(event) {
        event = event || window.event;
        var key = event.which || event.keyCode;
        // Only handle keyboard Backspace/Escape, not undocumented GamePad
        // button mappings. "B" remains native until measured on hardware.
        if ((key === 8 || key === 27) && !isTypingTarget(event.target || event.srcElement)) {
            var back = document.getElementById("back-button");
            if (back && back.href) {
                if (event.preventDefault) { event.preventDefault(); }
                event.returnValue = false;
                window.location.href = back.href;
            }
        }
    }

    function init() {
        initializeNativeApplet();
        if (document.addEventListener) {
            document.addEventListener("keydown", onKeyDown, false);
        } else if (document.attachEvent) {
            document.attachEvent("onkeydown", onKeyDown);
        }
    }

    if (document.readyState === "loading") {
        if (document.addEventListener) {
            document.addEventListener("DOMContentLoaded", init, false);
        } else if (window.attachEvent) {
            window.attachEvent("onload", init);
        }
    } else {
        init();
    }
}());
