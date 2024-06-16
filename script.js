document.getElementById('main_search_button').addEventListener('click', handleSearch);

document.getElementById('main_search_box').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

/**
 * Reset the page to its initial state after a page reload
 */
function resetPage() {
    document.getElementById('main_search_box').value = '';
    document.getElementById('filter_max').checked = false;
    document.getElementById('filter_isracard').checked = false;
    document.getElementById('filter_amex').checked = false;
    document.getElementById('category_dropdown').selectedIndex = 0;
    localStorage.clear();
    sessionStorage.clear();
}

window.addEventListener('load', resetPage);

async function handleSearch() {
    // log search
    console.log('searching...');
    var search_box = document.getElementById('main_search_box');
    const category = document.getElementById('category_dropdown').value;
    if (category.trim() == '' && search_box.value.trim() === '') {
        search_box.classList.add('input-error');
        search_box.setAttribute('title', 'This field cannot be left empty');
        setTimeout(function () {
            search_box.classList.remove('input-error');
        }, 100);
        return;
    }
    const value1 = search_box.value;
    console.log('search value is: ', value1);

    const filterMax = document.getElementById('filter_max').checked;
    const filterIsracard = document.getElementById('filter_isracard').checked;
    const filterAmex = document.getElementById('filter_amex').checked;

    if (!filterMax && !filterIsracard && !filterAmex) {
        alert('אנא סמן לפחות חברת אשראי אחת');
        return;
    }

    try {
        const response = await fetch('http://localhost:3000/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                search_title: value1,
                category: category,
                filter_max: filterMax,
                filter_isracard: filterIsracard,
                filter_amex: filterAmex
            })
        });
        if (response.ok) {
            const data = await response.json();
            let cat = document.getElementById('category_dropdown').options[document.getElementById('category_dropdown').selectedIndex].text;
            search_box_text = value1 || cat;
            let msg = "נמצאו " + data.length + " תוצאות עבור: " + "\'" + search_box_text + "\'";
            document.getElementById("search-results-h2").innerText = msg;
            displaySearchResults(data);
        } else {
            console.error('HTTP error status:', response.status);
            const errorData = await response.text();
            console.error('Error data:', errorData);
            alert('הפנייה נכשלה');
            return;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('אירעה שגיאה, אנא נסה שנית מאוחר יותר');
    }
}

function displaySearchResults(results) {
    document.getElementById('search-results').style.display = 'block';
    const resultsList = document.getElementById('results-list');
    resultsList.innerHTML = '';
    if (results.length === 0) {
        resultsList.textContent = 'לא נמצאו תוצאות';
    } else {
        results.forEach(result => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            const img = document.createElement('img');
            if (result.company === 'max_company') {
                img.src = 'images/max_logo.svg';
                img.alt = 'Max logo';
            } else if (result.company === 'isracard') {
                img.src = 'images/isracard_logo.png';
                img.alt = 'Isracard logo';
            } else if (result.company === 'amex') {
                img.src = 'images/amex_logo.png';
                img.alt = 'Amex logo';
            }
            li.appendChild(img);
            a.href = result.url;
            a.textContent = result.benefit_name;
            a.target = '_blank';
            li.appendChild(a);
            li.classList.add('benefit_result');
            resultsList.appendChild(li);
        });
    }
}
