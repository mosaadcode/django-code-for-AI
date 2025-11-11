const myInput = document.querySelector('select[id="type101"]');
myInput.addEventListener("change",getTime);

async function makeRequest(url,method,body) {
    let headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    }

    if (method == 'post') {
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
        headers['X-CSRFToken'] = csrf
    }
    let response = await fetch('',{
        method: method,
        headers: headers,
        body:body
    })

    return await response.json()
}

async function getTime(e) {
    // console.log(e.target.value)
    
    
    let from_time = document.getElementById('start_time')
    let to_time = document.getElementById('end_time')
    let type = e.target.value
    if( type =='داخلي') {
    from_time.readOnly = false
    end_time.readOnly = false
    from_time.value = ''
    to_time.value = ''
}else{
    let data = await makeRequest('/',method='post',body=JSON.stringify({'type':type}))

    from_time.value = await data ['start_time']
    to_time.value = await data ['end_time']
    from_time.readOnly = true
    end_time.readOnly = true

}}

  
  