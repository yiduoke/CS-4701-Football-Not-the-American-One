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

//drawing the players
function draw_players(players){
    players.forEach(d => {
        field.append("circle")
             .attr("cx", d['x'])
             .attr("cy", d['y'])
             .attr("r", 10)
             .attr("fill", "red")
             .attr("stroke", "steelblue")
             .attr("stroke-width", 3)
        });
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

//receiving state information from Python through Ajax
function receiveState(){
     for (let i = 0; i < 3; i++) {
          $.ajax({
               url: '/sendState' + i,
               type: 'POST',
               }).done(function(response){
                       var obj = JSON.parse(response);
                       draw_players(obj.state);
                       draw_ball(obj.ball);
                       console.log(obj);
                       startTimer();
                       //await sleep(3000);
                       });   
     }  
}

receiveState();

$(document).ready(function(){
//      sending data from front to back end, will do this when user interaction is enabled
//            $('form').submit(function(event){
 //               ws.send($('#data').val())
//                return false;
//            });
    setInterval(function(){
      ws.send("meow!")
      return false;
    }, 1000);
    if ("WebSocket" in window) {
        ws = new WebSocket("ws://" + document.domain + ":5000/api");
        ws.onmessage = function (msg) {
            $("#log").append("<p>"+msg.data+"</p>")
        };
    } else {
        alert("WebSocket not supported");
    }
});




