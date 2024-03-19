let socket = io.connect('127.0.0.1' + ':' + location.port)

function sendTextUpdate(){
    let text = document.getElementById('msg').value;
    socket.emit('text_update', {text: text})
}

socket.on('redirect', function (data){
    window.location.href = data.url;
});
