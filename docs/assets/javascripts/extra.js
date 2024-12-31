/* The following makes all external links =open in a new tab*/
document$.subscribe(function() {
    for (const link of Array.from(document.querySelectorAll("a[href^=http]")))
        link.target = "_blank"
})
