function start_websocket(){
    let host = window.location.hostname;
    let url = "ws://"+host+":9999/";
    let ws = new WebSocket(url);

    ws.onopen = function() {
        console.log("Establish connection");
    };

    ws.onclose = function(event) {
        if (event.wasClean) {
            console.log("Close connection clearly!");
        } else {
            console.log("Close connection!");
        }
    };

    ws.onmessage = function(event) {
        let qr = document.getElementById("qr");
        qr.src = event.data;
    };

    ws.onerror = function(error) {
        console.log("Error: " + error.message);
    };
}

function draw_canvas(){
    // Not my code, just copy from Internet
    var c = document.getElementById("c");
    var ctx = c.getContext("2d");

    //making the canvas full screen
    c.height = window.innerHeight;
    c.width = window.innerWidth;

    //chinese characters - taken from the unicode charset
    var matrix = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
    //converting the string into an array of single characters
    matrix = matrix.split("");

    var font_size = 10;
    var columns = c.width/font_size; //number of columns for the rain
    //an array of drops - one per column
    var drops = [];
    //x below is the x coordinate
    //1 = y co-ordinate of the drop(same for every drop initially)
    for(var x = 0; x < columns; x++)
        drops[x] = 1; 

    //drawing the characters
    function draw()
    {
        //Black BG for the canvas
        //translucent BG to show trail
        ctx.fillStyle = "rgba(0, 0, 0, 0.03)";
        ctx.fillRect(0, 0, c.width, c.height);

        ctx.fillStyle = "#00ff00";//green text
        ctx.font = font_size + "px arial";
        //looping over drops
        for(var i = 0; i < drops.length; i++)
        {
            //a random chinese character to print
            var text = matrix[Math.floor(Math.random()*matrix.length)];
            //x = i*font_size, y = value of drops[i]*font_size
            ctx.fillText(text, i*font_size, drops[i]*font_size);

            //sending the drop back to the top randomly after it has crossed the screen
            //adding a randomness to the reset to make the drops scattered on the Y axis
            if(drops[i]*font_size > c.height && Math.random() > 0.975)
                drops[i] = 0;

            //incrementing Y coordinate
            drops[i]++;
        }
    }

    setInterval(draw, 35);

}

window.onload = function(){
    start_websocket();
    draw_canvas();
}
