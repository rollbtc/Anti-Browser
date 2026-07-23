
// Proxy authentication handler for Manifest V3
chrome.webRequest.onAuthRequired.addListener(
    function(details, callback) {
        console.log('[Proxy Auth] Authentication required for:', details.url);
        callback({
            authCredentials: {
                username: "wGSM5",
                password: "SK5rx"
            }
        });
    },
    {urls: ["<all_urls>"]},
    ['asyncBlocking']
);

console.log('[Proxy Auth] Extension loaded');
