/* ES5 only. No account, network service, storage, sound or download APIs. */
(function () {
    'use strict';
    var tag = document.getElementById('zshop-bridge');
    var page = tag ? tag.getAttribute('data-page') : '';
    var mode = tag ? tag.getAttribute('data-native') : 'all';
    var pending = [];
    function report(stage, extra) {
        try {
            var img = new Image();
            pending.push(img);
            img.src = '/__zshop__/event?stage=' + stage + '&page=' + page + (extra || '');
        } catch (ignored) {}
    }
    function measure(stage) {
        try {
            var el = document.getElementById('wrapper');
            var w = el ? el.offsetWidth : 0;
            var h = el ? el.offsetHeight : 0;
            var broken = 0;
            var i;
            for (i = 0; i < document.images.length; i += 1) {
                if (document.images[i].complete && document.images[i].naturalWidth === 0) {
                    broken += 1;
                }
            }
            report(stage, '&w=' + w + '&h=' + h + '&visible=' + (w > 0 && h > 0 ? 1 : 0) +
                '&images=' + document.images.length + '&broken=' + broken +
                '&vw=' + (window.innerWidth || 0) + '&vh=' + (window.innerHeight || 0));
        } catch (ignored) {}
    }
    report('bridge');
    measure('dom');
    var state = document.getElementById('zshop-probe-state');
    if (state) { state.innerHTML = 'JavaScript OK'; }
    if (window.addEventListener) {
        window.addEventListener('load', function () { measure('load'); }, false);
        window.addEventListener('error', function () { report('script-error'); }, false);
    }
    if (mode === 'off') { report('native-off'); return; }
    var b;
    try { b = window.wiiuBrowser; } catch (ignored) { report('browser-error'); return; }
    if (!b) { report('browser-missing'); return; }
    // Independent catches: a recoverable startup error must not skip HOME unlock.
    if (mode === 'all' || mode === 'startup') {
        try {
            if (typeof b.endStartUp === 'function') {
                report('startup-before');
                b.endStartUp(true);
                report('startup-ok');
            } else { report('startup-missing'); }
        } catch (ignored) { report('startup-error'); }
    }
    if (mode === 'all' || mode === 'unlock') {
        try {
            if (typeof b.lockHomeButtonMenu === 'function') {
                report('unlock-before');
                b.lockHomeButtonMenu(false);
                report('unlock-ok');
            } else { report('unlock-missing'); }
        } catch (ignored) { report('unlock-error'); }
    }
}());
