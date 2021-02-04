function refreshImg(element) {
    setTimeout(function() {
        element.src = element.src.split('?')[0] + '?' + new Date().getTime();
    }, 1000); 
}