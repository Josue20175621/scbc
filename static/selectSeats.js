var index;
var tickets = Number(document.querySelector('#n_seats').value)
var count = 0;
var redirect_in_seconds = 3;
const THEATER = document.getElementById("theater")
const ROWS = 9
const SEATS_PER_ROW = 9
const ROW_BLOCK_BACKGROUND_COLOR = "#1E377F"
const SEAT_NOT_AVAILABLE = "#F52560"
const ROW_BLOCK_TEXT_COLOR = "#FFF"
const SEAT_SELECTED_BACKGROUND_COLOR = "#00CD2A"
const SEAT_SELECTED_TEXT_COLOR = "#FFF"
var seats_arr = []

var rowMap = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H", 8: "I"}

function createSeat(r_number, column) {
    var seat = document.createElement("div")
    seat.className = "seat " + rowMap[r_number] + " " + column
    seat.innerText = column
    seat.style.background = "#FFF";
    seat.addEventListener("click", function() {
        markSeat(rowMap[r_number], column)
    })
    return seat
}

function createRow(r_number) {
    // Create row
    var row = document.createElement("div")
    row.className = "row"

    // Create letter block
    var letter = document.createElement("div")
    letter.className = "seat NULL"
    letter.style.background = ROW_BLOCK_BACKGROUND_COLOR
    letter.style.color = ROW_BLOCK_TEXT_COLOR
    letter.innerText = "Fila " + rowMap[r_number]
    row.appendChild(letter)
    
    for (let i = 0; i < SEATS_PER_ROW; i++)
    {
        row.appendChild(createSeat(r_number, i))
    }

    // Add row to the theater
    THEATER.appendChild(row);
}

function redirect(url) {
    window.location.replace(url)
}

function setup() {
    for (let i = 0; i < ROWS; i++)
    {
        createRow(i)
    }
}

function markSeat(row, column) {
    if (count < tickets) {
        var seat = document.getElementsByClassName("seat " + row + " " + column)
        seat[0].style.background = SEAT_SELECTED_BACKGROUND_COLOR
        seat[0].style.color = SEAT_SELECTED_TEXT_COLOR
        count++;
        seats_arr.push(row+column)
        feed_back.innerText = "Asientos: " + seats_arr

        if (count == tickets)
        {
            // Redirect after 3 seconds
            console.log(`Redirecting in ${redirect_in_seconds} seconds`)
            //var interval = setInterval(redirect, redirect_in_seconds * 1000, `http://${location.hostname}:5000/success`);
            
            // send seats to server
            /*
            for (let i = 0; i < seats_arr.length; i++) {
                sendSeatToServer(seats_arr[i])
            }
            */
        }
    }
}

setup()
var feed_back = document.querySelector('#feedback')

async function sendSeatToServer(seat) {

    fetch(`/seat/${seat}`)
    .then(function (response) {
        return response.text();
    }).then(function (text) {
        console.log(text);
    });
}

async function updateSeats() {
    
    const requestURL = `http://${location.hostname}:3502/seats`;
    const request = new Request(requestURL);

    const response = await fetch(request);
    const seats = await response.json();

    for (var seat in seats) {
        // marked
        if (Number(seats[seat]) == 1 && !seats_arr.includes(seat)) {
            var s_selector = document.getElementsByClassName(`seat ${seat[0]} ${seat[1]}`)
            s_selector[0].style.background = SEAT_NOT_AVAILABLE
            s_selector[0].style.color = SEAT_SELECTED_TEXT_COLOR
        }
    }
}

// update seats every 10 seconds
// this is for the user
//var update = setInterval(updateSeats, 10000);