const submitButton = document.querySelector('.btn-primary');
const host = "http://79.174.94.7:8000";
console.log(host);

submitButton.onclick = async(e) =>
{
    e.preventDefault();
    let email = document.querySelector('#typeEmailX-2').value;
    let password = document.querySelector('#typePasswordX-2').value;
    console.log(email, password);
    let paramsObj = {
        "username": email,
        "password": password,
    }
    result = await fetch(host + "/login", {
        method: "POST",
        
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams(paramsObj)
    })
    .then((response) => {
        return response.text()
    })
    .then(text => JSON.parse(text))
    .then(json =>
        {
            if ('detail' in json)
            console.log('Неправильно');
            else
            {
                localStorage.setItem('token', "bearer " + json.access_token);
                window.location.redirect = host + '/admin/';
            }
        });

    console.log(result);
    
}
