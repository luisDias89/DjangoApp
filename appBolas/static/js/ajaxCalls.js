/*-------------------------------------------
          @ Luís Dias 2022
 O presente ficheiro implementa metodos para chamadas AJAX

-------------------------------------------*/

// https://docs.djangoproject.com/en/3.2/ref/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

function ajaxRequest(data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/ajax_request/');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhr.onload = function() {
        if (xhr.status === 200) {
            var dataReceived = JSON.parse(xhr.responseText);
            callback(dataReceived);
        }
        else{
            var dataReceived = JSON.parse(xhr.responseText);
            callback(dataReceived);
        }
    };
    xhr.send(JSON.stringify(data));
}

function callback(data) {
    
    alert(data.message);
}
