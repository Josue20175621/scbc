const THEATER = document.getElementById("theater")
const ROW_BLOCK_BACKGROUND_COLOR = "#eb7163"
const SEAT_NOT_AVAILABLE = "#F52560"
const ROW_BLOCK_TEXT_COLOR = "#FFF"
var id_tanda = Number(document.querySelector('#tanda_id').value)
var asientos = Number(document.querySelector('#asientos').value)

const m = Math.sqrt(asientos)
const ROWS = m
const SEATS_PER_ROW = m
var boton_actualizar = document.querySelector('#update');
boton_actualizar.addEventListener('click', () => {
    console.log("Actualizando asientos")
    updateSeats()
})
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

function setup() {
    for (let i = 0; i < ROWS; i++)
    {
        createRow(i)
    }
}

setup()

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
        console.log('Servidor recibio la data:', asientos);
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