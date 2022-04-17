const formatDate = (date) => {
    let d = new Date(date);
    let month = (d.getMonth() + 1).toString();
    let day = d.getDate().toString();
    let year = d.getFullYear();
    let hours = d.getHours().toString()
    let minutes = d.getMinutes().toString()
    let seconds = d.getSeconds().toString()
    if (hours.length < 2) {
        hours = '0' + hours;
    }

    if (minutes.length < 2) {
        minutes = '0' + minutes
    }

    if (seconds.length < 2) {
        seconds = '0' + seconds
    }

    if (month.length < 2) {
      month = '0' + month;
    }
    if (day.length < 2) {
      day = '0' + day;
    }
    return [year, month, day].join('-') + ' ' + [hours, minutes, seconds].join(":");
}

let fecha = formatDate(new Date());


var index;
var tickets = Number(document.querySelector('#n_seats').value)
var boton_actualizar = document.querySelector('#update');
var id_usuario = Number(document.querySelector('#usuario_id').value)
var id_tanda = Number(document.querySelector('#tanda_id').value)
var id_sala = Number(document.querySelector('#sala_id').value)
var asientos = Number(document.querySelector('#asientos').value)
const m = Math.sqrt(asientos)

boton_actualizar.addEventListener('click', () => {
    console.log("Actualizando asientos")
    updateSeats()
})
var count = 0;
const THEATER = document.getElementById("theater")
const ROWS = m
const SEATS_PER_ROW = m
const ROW_BLOCK_BACKGROUND_COLOR = "#eb7163"
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
            // Envia los asientos al servidor
            var s = ""
            for (let i = 0; i < seats_arr.length; i++) {
                s += `${seats_arr[i]},`
            }
            
            sendSeatsToServer(s)

            var interval = setInterval(redirect, 3000, `http://${location.host}/history`);
            
        }
    }
}

setup()
var feed_back = document.querySelector('#feedback')

async function sendSeatsToServer(seats) {

    var data = {
        "idUsuario": id_usuario,
        "idSala": id_sala,
        "idTanda": id_tanda,
        "asientos": seats
    };

    var data2 = {
        "idUsuario": id_usuario,
        "idSala": id_sala,
        "idTanda": id_tanda,
        "fecha": fecha,
        "boletos": tickets
    };

    fetch('/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {

        console.log('Servidor recibio los asientos:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    fetch('/checkout', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data2),
    })
    .then(response => response.json())
    .then(data => {

        console.log('Servidor recibio los datos del boleto', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

async function updateSeats() {
    
    var data = {
        "idTanda": id_tanda
    };
    
    fetch('/updateC', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(asientos => {
        for (var asiento in asientos) {
            var s_selector = document.getElementsByClassName(`seat ${asiento[0]} ${asiento[1]}`)
            s_selector[0].style.background = SEAT_NOT_AVAILABLE
            s_selector[0].style.color = "#FFF"
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

updateSeats()