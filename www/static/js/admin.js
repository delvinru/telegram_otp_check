window.onload = function(){
    let to_time = document.getElementById("to_time");
    let from_time = document.getElementById("from_time");

    let x = new Date();
    x.setSeconds(0);
    x.setMilliseconds(0);
    let time = x.toISOString();
    to_time.value = time.split(':00.000Z')[0];

    x.setHours(x.getHours() - 2);
    time = x.toISOString();
    from_time.value = time.split(':00.000Z')[0];
}