const host = "http://localhost:8000";

function createInput(parent, text, inputId)
{
    let inputGroup = document.createElement('div');
    inputGroup.classList.add('input-group');
    inputGroup.classList.add('mb-3');
    let prepend = document.createElement('div');
    prepend.classList.add('input-group-prepend');
    inputGroup.appendChild(prepend);
    let textElem = document.createElement('span');
    textElem.classList.add('input-group-text');
    textElem.textContent = text;
    prepend.appendChild(textElem);
    let input = document.createElement('input');
    input.classList.add('form-control');
    input.name = inputId;
    inputGroup.appendChild(input);
    parent.appendChild(inputGroup);
}

function createSelect(parent, text, selectId)
{
    let inputGroup = document.createElement('div');
    inputGroup.classList.add('input-group');
    inputGroup.classList.add('mb-3');
    let prepend = document.createElement('div');
    prepend.classList.add('input-group-prepend');
    inputGroup.appendChild(prepend);
    let textElem = document.createElement('span');
    textElem.classList.add('input-group-text');
    textElem.textContent = text;
    prepend.appendChild(textElem);
    let select = document.createElement('select');
    select.classList.add('form-control');
    select.name = selectId;
    let selectedOption = document.createElement('option');
    selectedOption.value = "1";
    selectedOption.textContent = "Студент";
    let option2 = document.createElement('option');
    option2.value = "2";
    option2.textContent = "Сопровождающий";
    let option3 = document.createElement('option');
    option3.value = "3";
    option3.textContent = "Тимлидер";
    
    select.appendChild(selectedOption);
    select.appendChild(option2);
    select.appendChild(option3);

    inputGroup.appendChild(select);
    parent.appendChild(inputGroup);
}

function createForm(request, parent) {
    let form = document.createElement('form');
    form.id = request;
    switch(request) 
    {
        case 'role/change':
            createInput(form, 'email пользователя', 'email');
            createSelect(form, 'Новая роль', 'role_id');
        break;
        case 'buddy/confirm':
            createInput(form, 'email сопровождающего', 'email');
        break;
    }
    form.onsubmit = async(e) =>
    {
        let resultDiv = form.parentElement.parentElement.querySelector('.section-result');
        
        e.preventDefault();
        let formData = new FormData(form);
        let params = new URLSearchParams(formData);
        response = await fetch(host + '/admin/' + request +'?' + params, {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Authorization": localStorage.getItem('token')
            },
        })
        .then((response) => {
            return response.text()
        })
        .then(text => JSON.parse(text))
        .then(json => json);
        
        resultDiv.textContent = JSON.stringify(response);
    }
    let button = document.createElement('button');
    button.classList.add('btn');
    button.classList.add('btn-primary');
    button.textContent = 'Отправить';
    form.appendChild(button);
    parent.appendChild(form);

}

if (localStorage.getItem("token") == null)
{
        window.location.replace(host + '/admin/login/');
}

window.onload = function() {
    const funcBlocks = document.querySelectorAll(".function-block");
    const logoutButton = document.querySelector('a.dropdown-item');

    logoutButton.onclick = (e) =>
    {
        localStorage.clear();
    }
    funcBlocks.forEach(block => {
        block.onclick = e => {
            e.preventDefault();
            if (block.classList.contains('opened'))
            {
                let body = block.parentElement.querySelector('.function-body');
                let description = block.querySelector('.function-description');
                let iElem = description.querySelector('i');
                iElem.remove();
                newIElem = document.createElement('i');
                description.appendChild(newIElem);
                newIElem.classList.add('fas');
                newIElem.classList.add('fa-chevron-down');
                block.classList.remove('opened');
                
                block.parentElement.removeChild(body);
            }
            else {
                block.classList.add('opened');
                let func = block.parentElement;
                let description = block.querySelector('.function-description');
                let iElem = description.querySelector('i');
                iElem.remove();
                newIElem = document.createElement('i');
                description.appendChild(newIElem);
                newIElem.classList.add('fas');
                newIElem.classList.add('fa-chevron-up');

                let body = document.createElement('div');
                body.classList.add('function-body');
                block.parentElement.appendChild(body);
                let section = document.createElement('div');
                section.classList.add('function-section');
                let tab = document.createElement('div');
                tab.classList.add('section-tab');
                tab.textContent = 'Параметры';
                section.appendChild(tab);
                createForm(block.id, section);
                tab = document.createElement('div');
                tab.classList.add('section-tab');
                tab.textContent = 'Результат';
                section.appendChild(tab);
                body.appendChild(section);
                let response = document.createElement('div');
                response.classList.add('section-result');
                body.appendChild(response);
            }
        }
    });
}
