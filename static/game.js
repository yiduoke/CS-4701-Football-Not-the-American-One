//field
const field = d3.select("svg#field")
                .attr("width", 2000)
                .attr("height", 2000)

//field, but actually
field.append("rect")
     .attr("x", 80)
     .attr("y", 50)
     .attr("width", 1050)
     .attr("height", 680)
     .attr("fill", "#84BE6A")
     .attr()

//perimeter line
field.append("rect")
     .attr("x", 92)
     .attr("y", 62 )
     .attr("width", 1025)
     .attr("height", 655)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//middle circle
field.append("circle")
     .attr("cx", 612)
     .attr("cy", 390)
     .attr("r", 90)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//middle line
field.append("line")
     .attr("x1", 612)
     .attr("x2", 612)
     .attr("y1", 62)
     .attr("y2", 718)
     .attr("stroke", "white")
     .attr("stroke-width", 5)

//罚球弧，左
field.append("circle")
     .attr("cx", 202)
     .attr("cy", 389.5)
     .attr("r", 91.5)
     .attr("fill", "#84BE6A")
     .attr("stroke", "white")
     .attr("stroke-width", 5)

//罚球弧，右
field.append("circle")
     .attr("cx", 1007)
     .attr("cy", 389.5)
     .attr("r", 91.5)
     .attr("fill", "#84BE6A")
     .attr("stroke", "white")
     .attr("stroke-width", 5)

//大禁区，左
field.append("rect")
     .attr("x", 92)
     .attr("y", 224.5)
     .attr("height", 330)
     .attr("width", 165)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//大禁区，右
field.append("rect")
     .attr("x", 952)
     .attr("y", 224.5)
     .attr("height", 330)
     .attr("width", 165)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//小禁区，左
field.append("rect")
     .attr("x", 92)
     .attr("y", 298)
     .attr("height", 183)
     .attr("width", 55)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//小禁区，右
field.append("rect")
     .attr("x", 1062)
     .attr("y", 298)
     .attr("height", 183)
     .attr("width", 55)
     .attr("stroke", "white")
     .attr("stroke-width", 5)
     .attr("fill", "#84BE6A")

//点球点，左
field.append("circle")
     .attr("cx", 202)
     .attr("cy", 389.5)
     .attr("r", 2.5)
     .attr("fill", "white")

//点球点，右
field.append("circle")
     .attr("cx", 1007)
     .attr("cy", 389.5)
     .attr("r", 2.5)
     .attr("fill", "white")

// initializing the players so I can modify their coordinates later and not just tack on more and more circles

//field.append("circle")
//.attr("cx", 200)
//.attr("cy", 200)
//.attr("r", 10)
//.attr("fill", "red")
//.attr("stroke", "steelblue")
//.attr("stroke-width", 3)

var player_circles;

function initialize_players(){
    var num_players = 4
    players_data_dictionaries = [];
    for (var i = 0; i < num_players; i++){
//        var dictionary = {"x_axis": 200 + 10 * i,
//                          "y_axis": 300 + 10 * i,
//                          "radius": 10,
//                          "fill": "red",
//                          "stroke": "steelblue",
//                          "stroke-width": 3
        
        field.append("circle")
        .attr("cx", 200 + 10 * i)
        .attr("cy", 300 + 10 * i)
        .attr("r", 10)
        .attr("fill", "red")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 3)
        .attr("id", "player")

        };
}

//drawing the players
function draw_players(players){
    var player_circles = d3.selectAll("#player");
    x_coors = [];
    y_coors = [];

    for(var i = 0; i < players.length; i += 2) {
        x_coors.push(players[i]);
    }

    for(var i = 1; i < players.length; i += 2) {
        y_coors.push(players[i]);
    }
    
    player_circles.data(x_coors);
    player_circles.attr("cx", function(d){ return d; });
    
    player_circles.data(y_coors);
    player_circles.attr("cy", function(d){ return d; });
}

function draw_ball(ball){
    field.append("circle")
         .attr("cx", ball['x'])
         .attr("cy", ball['y'])
         .attr("r", 3)
         .attr("fill", "white")
         .attr("stroke", "black")
         .attr("stroke-width", 1)
}


// receiving player and ball coordinates every second (subject to change) from Flask through a websocket
$(document).ready(function(){
//      sending data from front to back end, will do this when user interaction is enabled
//            $('form').submit(function(event){
 //               ws.send($('#data').val())
//                return false;
//            });
    initialize_players();
    setInterval(function(){
      ws.send("meow!")
      return false;
    }, 500);
    if ("WebSocket" in window) {
        ws = new WebSocket("ws://" + document.domain + ":5000/api");
        ws.onmessage = function (msg) {
            var all_coors = msg.data.split(",");
            var int_coors = [];
            
            for (var i = 0; i < all_coors.length; i++){
              int_coors.push(parseInt(all_coors[i]));
            }
            draw_players(int_coors);
        };
    } else {
        alert("WebSocket not supported");
    }
});




